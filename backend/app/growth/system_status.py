"""Collect real system state for the "Статус" command.

Everything here is observed, never inferred. When a check cannot run — the
command is missing, it times out, a file is absent — that is reported as
"неизвестно" with the reason, because a status report that quietly guesses is
worse than one that admits a gap.

This module runs on the **host**, not inside the backend container. The
container has no repository mount, no `.colore/`, and no docker socket, so it
cannot see the git tree, the runtime documents, or its own siblings.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_TIMEOUT = 90

UNKNOWN = "неизвестно"


def repo_root() -> Path:
    override = os.getenv("COLORE_REPO_ROOT", "").strip()
    if override:
        return Path(override)
    # app/growth/system_status.py -> app/growth -> app -> backend -> repo
    return Path(__file__).resolve().parents[3]


@dataclass
class Check:
    """One observed fact, or an explicit admission that it could not be observed."""

    name: str
    ok: bool | None  # None means "could not determine"
    summary: str
    detail: list[str] = field(default_factory=list)

    @property
    def marker(self) -> str:
        if self.ok is None:
            return "⚪"
        return "✅" if self.ok else "❌"


def _run(args: list[str], *, cwd: Path | None = None, timeout: int = 20) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", f"команда не найдена: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"превышено время ожидания ({timeout}s)"
    except Exception as exc:  # noqa: BLE001
        return 1, "", f"{type(exc).__name__}: {exc}"
    return proc.returncode, proc.stdout, proc.stderr


# ------------------------------------------------------------------- doctor


def doctor_check(root: Path | None = None) -> Check:
    root = root or repo_root()
    script = root / "scripts" / "doctor.sh"

    if not script.is_file():
        return Check("Doctor", None, f"{UNKNOWN}: {script} не найден")

    code, out, err = _run([str(script)], cwd=root, timeout=DEFAULT_TIMEOUT)

    if code == 0:
        return Check("Doctor", True, "SYSTEM HEALTHY")

    problems = [
        line.strip().lstrip("- ").strip()
        for line in out.splitlines()
        if line.strip().startswith("-")
    ]
    if not problems and err:
        return Check("Doctor", None, f"{UNKNOWN}: {err.strip()[:200]}")

    return Check(
        "Doctor",
        False,
        f"{len(problems) or 'есть'} проблем(ы)",
        detail=problems[:10],
    )


# ---------------------------------------------------------------------- git


def git_check(root: Path | None = None) -> Check:
    root = root or repo_root()

    code, branch, err = _run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"])
    if code != 0:
        return Check("Git", None, f"{UNKNOWN}: {err.strip()[:150]}")
    branch = branch.strip()

    _, head, _ = _run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"])
    _, subject, _ = _run(["git", "-C", str(root), "log", "-1", "--format=%s"])
    _, porcelain, _ = _run(["git", "-C", str(root), "status", "--porcelain"])

    dirty = len([line for line in porcelain.splitlines() if line.strip()])

    detail = [f"ветка {branch}, HEAD {head.strip()} — {subject.strip()[:60]}"]

    code, counts, _ = _run(
        ["git", "-C", str(root), "rev-list", "--left-right", "--count", f"origin/{branch}...HEAD"]
    )
    if code == 0 and counts.strip():
        parts = counts.split()
        if len(parts) == 2:
            behind, ahead = parts
            if ahead != "0" or behind != "0":
                detail.append(
                    f"относительно origin/{branch} (по последним известным данным): "
                    f"+{ahead} / -{behind}"
                )

    if dirty == 0:
        return Check("Git", True, "чисто, всё закоммичено", detail)

    return Check("Git", False, f"{dirty} незакоммиченных файл(ов)", detail)


# ------------------------------------------------------------------- docker


def docker_check() -> Check:
    code, out, err = _run(
        ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
        timeout=20,
    )
    if code != 0:
        return Check("Docker", None, f"{UNKNOWN}: {err.strip()[:150]}")

    rows = [line.split("\t", 1) for line in out.splitlines() if line.strip()]
    colore = [(name, status) for name, status in rows if name.startswith("colore-")]

    if not colore:
        return Check("Docker", False, "ни один контейнер colore-* не запущен")

    detail = [f"{name}: {status}" for name, status in sorted(colore)]
    return Check("Docker", True, f"{len(colore)} контейнер(ов) работает", detail)


# ------------------------------------------------------------------- deploy


def deploy_check(root: Path | None = None, container: str = "colore-backend") -> Check:
    root = root or repo_root()

    code, head, _ = _run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"])
    if code != 0:
        return Check("Deploy", None, f"{UNKNOWN}: не удалось прочитать HEAD репозитория")
    head = head.strip()

    code, image_commit, err = _run(
        ["docker", "exec", container, "printenv", "GIT_COMMIT"], timeout=20
    )
    if code != 0:
        return Check("Deploy", None, f"{UNKNOWN}: контейнер {container} недоступен")

    image_commit = image_commit.strip()

    if not image_commit or image_commit == "unknown":
        return Check("Deploy", None, f"{UNKNOWN}: образ не записал GIT_COMMIT")

    if image_commit == head:
        return Check("Deploy", True, f"развёрнут текущий коммит {head}")

    return Check(
        "Deploy",
        False,
        "контейнер отстаёт от репозитория",
        [f"в контейнере {image_commit}, в репозитории {head} — нужен ./deploy.sh"],
    )


# ------------------------------------------------------------- integrations


INTEGRATION_LABELS = {
    "openai": "OpenAI",
    "telegram": "Telegram",
    "meta": "Meta",
    "altegio": "Altegio",
    "n8n": "n8n",
}


def integration_checks(api_base: str = "", timeout: int = 10) -> list[Check]:
    """Ask the running backend what it actually has configured.

    Single source of truth: the same `/growth/integrations` the gateway builds
    from live settings. Reading env files here would report what *should* be
    loaded rather than what is.
    """
    api_base = api_base or os.getenv("COLORE_API_BASE", "http://localhost:8000")

    try:
        import requests

        response = requests.get(f"{api_base}/growth/integrations", timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        return [
            Check(
                label,
                None,
                f"{UNKNOWN}: backend недоступен ({type(exc).__name__})",
            )
            for label in INTEGRATION_LABELS.values()
        ]

    by_name = {item["name"]: item for item in payload.get("integrations", [])}
    checks: list[Check] = []

    for name, label in INTEGRATION_LABELS.items():
        item = by_name.get(name)
        if item is None:
            checks.append(Check(label, None, f"{UNKNOWN}: коннектор не зарегистрирован"))
            continue

        if item.get("configured"):
            checks.append(Check(label, True, "настроен"))
        else:
            missing = ", ".join(item.get("missing_configuration") or []) or "нет настроек"
            checks.append(Check(label, False, f"не настроен — {missing}"))

    return checks


def collect_status(root: Path | None = None) -> list[Check]:
    root = root or repo_root()
    return [
        doctor_check(root),
        deploy_check(root),
        git_check(root),
        docker_check(),
        *integration_checks(),
    ]


def status_payload(root: Path | None = None) -> dict[str, Any]:
    return {
        check.name: {"ok": check.ok, "summary": check.summary, "detail": check.detail}
        for check in collect_status(root)
    }


def as_json(root: Path | None = None) -> str:
    return json.dumps(status_payload(root), ensure_ascii=False, indent=2)
