"""Read the Runtime documents in `.colore/` and report what they actually say.

Nothing here summarises by inference. Every value returned is a line lifted
from a file, or an explicit statement that the file or section was not found.
That constraint is the point: the Product Owner is going to act on these
answers, and a plausible-sounding invention is worse than "не найдено".

Runs on the host — `.colore/` is not in the backend image.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from app.growth.system_status import repo_root


@dataclass
class ChangelogEntry:
    entry_id: str
    date: str
    event: str
    status: str = ""


@dataclass
class ReviewItem:
    item_id: str
    title: str
    when: str
    status: str


@dataclass
class SprintView:
    name: str = ""
    goal: str = ""
    kpi: str = ""
    in_scope: list[str] = field(default_factory=list)


@dataclass
class NextView:
    task: str = ""
    status: str = ""
    remaining: list[str] = field(default_factory=list)
    do_not: list[str] = field(default_factory=list)


def colore_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / ".colore"


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


# ---------------------------------------------------------------- changelog


def read_changelog(root: Path | None = None, *, limit: int = 6) -> tuple[list[ChangelogEntry], str]:
    """Newest entries first. Second value is an error message, empty when fine."""
    path = colore_dir(root) / "changelog.md"
    text = _read(path)
    if text is None:
        return [], f"{path} не найден"

    entries: list[ChangelogEntry] = []
    blocks = re.split(r"^### ", text, flags=re.MULTILINE)[1:]

    for block in blocks:
        lines = block.splitlines()
        entry_id = lines[0].strip()
        if entry_id.upper().startswith("VH-XXX"):
            continue  # the template at the bottom of the file

        fields = {}
        for line in lines[1:]:
            match = re.match(r"^-\s*(Date|Event|Status|Evidence|Note):\s*(.*)$", line.strip())
            if match:
                fields[match.group(1).lower()] = match.group(2).strip()

        if "event" not in fields:
            continue

        entries.append(
            ChangelogEntry(
                entry_id=entry_id,
                date=fields.get("date", ""),
                event=fields["event"],
                status=fields.get("status", ""),
            )
        )

    entries.reverse()
    return entries[:limit], ""


def entries_for(entries: list[ChangelogEntry], day: str) -> list[ChangelogEntry]:
    return [entry for entry in entries if entry.date == day]


def commits_since(root: Path | None = None, *, day: str = "", limit: int = 15) -> list[str]:
    """Commit subjects from a given day. Facts from git, not a narrative."""
    root = root or repo_root()
    day = day or date.today().isoformat()
    try:
        proc = subprocess.run(
            [
                "git", "-C", str(root), "log",
                f"--since={day} 00:00", "--format=%h %s", f"-{limit}",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception:  # noqa: BLE001
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


# ------------------------------------------------------------------ research


def read_review_queue(root: Path | None = None) -> tuple[list[ReviewItem], str]:
    """Parse the Review Queue table in research.md."""
    path = colore_dir(root) / "research.md"
    text = _read(path)
    if text is None:
        return [], f"{path} не найден"

    section = re.search(
        r"^##\s*Review Queue\s*$(.*?)^##\s", text, flags=re.MULTILINE | re.DOTALL
    )
    if not section:
        return [], "раздел «Review Queue» не найден в research.md"

    items: list[ReviewItem] = []
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0].upper() == "ID":
            continue
        items.append(ReviewItem(item_id=cells[0], title=cells[1], when=cells[2], status=cells[3]))

    return items, ""


def read_unknowns(root: Path | None = None) -> tuple[list[str], str]:
    """The "Unknowns" list in state.md — open questions the project has recorded."""
    path = colore_dir(root) / "state.md"
    text = _read(path)
    if text is None:
        return [], f"{path} не найден"

    section = re.search(
        r"^##\s*Unknowns\s*$(.*?)(^##\s|\Z)", text, flags=re.MULTILINE | re.DOTALL
    )
    if not section:
        return [], "раздел «Unknowns» не найден в state.md"

    return _bullets(section.group(1)), ""


# -------------------------------------------------------------------- sprint


def read_sprint(root: Path | None = None) -> tuple[SprintView, str]:
    path = colore_dir(root) / "sprint.md"
    text = _read(path)
    if text is None:
        return SprintView(), f"{path} не найден"

    view = SprintView()

    name = re.search(r"^-\s*\*\*Name:\*\*\s*(.+)$", text, flags=re.MULTILINE)
    if name:
        view.name = name.group(1).strip()

    status = re.search(r"^-\s*\*\*Status:\*\*\s*(.+)$", text, flags=re.MULTILINE)
    if status and view.name:
        view.name = f"{view.name} ({status.group(1).strip()})"

    goal = re.search(r"^##\s*Main Goal\s*$(.*?)^##\s", text, flags=re.MULTILINE | re.DOTALL)
    if goal:
        view.goal = _first_paragraph(goal.group(1))

    kpi = re.search(r"^##\s*Main KPI\s*$(.*?)^##\s", text, flags=re.MULTILINE | re.DOTALL)
    if kpi:
        view.kpi = _first_paragraph(kpi.group(1))

    scope = re.search(r"^##\s*In Scope Now\s*$(.*?)^##\s", text, flags=re.MULTILINE | re.DOTALL)
    if scope:
        view.in_scope = _numbered(scope.group(1))

    return view, ""


def read_next(root: Path | None = None) -> tuple[NextView, str]:
    path = colore_dir(root) / "next.md"
    text = _read(path)
    if text is None:
        return NextView(), f"{path} не найден"

    view = NextView()

    task = re.search(r"^##\s*Active Task\s*$(.*?)^(-|\#\#)", text, flags=re.MULTILINE | re.DOTALL)
    if task:
        view.task = _first_paragraph(task.group(1))

    status = re.search(r"^-\s*\*\*Status:\*\*\s*(.+)$", text, flags=re.MULTILINE)
    if status:
        view.status = status.group(1).strip()

    remaining = re.search(
        r"^##\s*(What remains[^\n]*|Steps)\s*$(.*?)(^##\s|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if remaining:
        view.remaining = _bullets(remaining.group(2)) or _numbered(remaining.group(2))
        if not view.remaining:
            paragraph = _first_paragraph(remaining.group(2))
            if paragraph:
                view.remaining = [paragraph]

    do_not = re.search(
        r"^##\s*Do Not Work On\s*$(.*?)(^##\s|\Z)", text, flags=re.MULTILINE | re.DOTALL
    )
    if do_not:
        view.do_not = _bullets(do_not.group(1)) or _paragraphs(do_not.group(1))

    return view, ""


# ------------------------------------------------------------------- helpers


def _clean(line: str) -> str:
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)  # markdown links
    line = line.replace("**", "").replace("`", "")
    return line.strip()


def _bullets(block: str) -> list[str]:
    out = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            cleaned = _clean(stripped[2:])
            if cleaned:
                out.append(cleaned)
    return out


def _numbered(block: str) -> list[str]:
    out = []
    for line in block.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s", stripped):
            cleaned = _clean(re.sub(r"^\d+\.\s*", "", stripped))
            if cleaned:
                out.append(cleaned)
    return out


def _paragraphs(block: str) -> list[str]:
    """Whole paragraphs, not first lines.

    A sentence wrapped across two source lines must not be reported truncated —
    "we are not working on X" that stops mid-clause reads as a different rule.
    """
    out: list[str] = []
    current: list[str] = []

    for raw in block.strip().splitlines():
        line = _clean(raw)
        if not line or line.startswith("#") or line.startswith("|"):
            if current:
                out.append(" ".join(current))
                current = []
            continue
        current.append(line)

    if current:
        out.append(" ".join(current))

    return out


def _first_paragraph(block: str) -> str:
    for raw in block.strip().splitlines():
        line = _clean(raw)
        if line and not line.startswith("|") and not line.startswith("#"):
            return line
    return ""
