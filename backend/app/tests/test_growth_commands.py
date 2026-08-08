"""Command routing, rendering, and the no-hallucination rule.

The last group is the important one: when a Runtime document is missing, the
answer must say which file was missing rather than produce a confident,
invented reply.
"""

from pathlib import Path

import pytest

from app.growth import commands, runtime_reader, system_status
from app.growth.system_status import Check


# ------------------------------------------------------------------- routing


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Статус", commands.CMD_STATUS),
        ("статус", commands.CMD_STATUS),
        ("  СТАТУС  ", commands.CMD_STATUS),
        ("/status", commands.CMD_STATUS),
        ("Что нового?", commands.CMD_NEWS),
        ("что нового", commands.CMD_NEWS),
        ("Что требует моего решения?", commands.CMD_DECISIONS),
        ("что требует моего решения", commands.CMD_DECISIONS),
        ("Что делаем дальше?", commands.CMD_NEXT),
        ("что делаем дальше", commands.CMD_NEXT),
        ("/start", commands.CMD_HELP),
    ],
)
def test_the_four_commands_route(text, expected):
    assert commands.route(text) == expected


def test_yo_is_normalised():
    """Russian keyboards produce both е and ё; the user should not have to care."""
    assert commands.route("Что нового?") == commands.route("Что нового?".replace("е", "ё"))


def test_anything_else_is_not_a_command():
    assert commands.route("привет") is None
    assert commands.route("") is None
    assert commands.route("статус деплоя пожалуйста") is None


def test_unknown_message_gets_the_command_list_back():
    answer = commands.unknown_answer("привет")

    assert "Не знаю команду" in answer
    assert "Статус" in answer


# -------------------------------------------------------------------- статус


def test_status_answer_renders_every_check(monkeypatch):
    monkeypatch.setattr(
        system_status,
        "collect_status",
        lambda root=None: [
            Check("Doctor", True, "SYSTEM HEALTHY"),
            Check("Deploy", True, "развёрнут текущий коммит abc1234"),
            Check("Git", False, "3 незакоммиченных файл(ов)", ["ветка main"]),
            Check("Docker", True, "4 контейнер(ов) работает"),
            Check("OpenAI", True, "настроен"),
            Check("Telegram", True, "настроен"),
            Check("Meta", False, "не настроен — META_VERIFY_TOKEN"),
            Check("Altegio", True, "настроен"),
            Check("n8n", None, "неизвестно: backend недоступен"),
        ],
    )

    answer = commands.status_answer()

    for name in ("Doctor", "Deploy", "Git", "Docker", "OpenAI", "Telegram", "Meta", "Altegio", "n8n"):
        assert name in answer

    assert "✅ Doctor: SYSTEM HEALTHY" in answer
    assert "❌ Git" in answer
    assert "⚪ n8n" in answer
    assert "Требует внимания: Git, Meta." in answer
    assert "Не удалось проверить: n8n." in answer


def test_status_says_all_clear_when_nothing_is_wrong(monkeypatch):
    monkeypatch.setattr(
        system_status,
        "collect_status",
        lambda root=None: [Check("Doctor", True, "SYSTEM HEALTHY")],
    )

    assert "Всё в порядке." in commands.status_answer()


def test_a_check_that_cannot_run_is_reported_as_unknown_not_as_ok():
    check = system_status.doctor_check(Path("/nonexistent/repo"))

    assert check.ok is None
    assert "неизвестно" in check.summary


def test_integration_status_reports_unknown_when_the_backend_is_unreachable():
    checks = system_status.integration_checks(api_base="http://127.0.0.1:9", timeout=1)

    assert {c.name for c in checks} == {"OpenAI", "Telegram", "Meta", "Altegio", "n8n"}
    assert all(c.ok is None for c in checks)
    assert all("недоступен" in c.summary for c in checks)


# ---------------------------------------------------- runtime document reads


@pytest.fixture
def fake_repo(tmp_path):
    colore = tmp_path / ".colore"
    colore.mkdir()

    (colore / "changelog.md").write_text(
        "# Changelog\n\n"
        "### VH-001\n"
        "- Date: 2020-01-01\n"
        "- Event: Что-то старое.\n"
        "- Status: DONE\n\n"
        "### VH-002\n"
        "- Date: 2026-08-08\n"
        "- Event: Сегодняшняя работа.\n"
        "- Status: DONE\n\n"
        "## Entry Template\n\n"
        "### VH-XXX\n"
        "- Date: TODO\n"
        "- Event: TODO\n",
        encoding="utf-8",
    )

    (colore / "research.md").write_text(
        "# Research\n\n"
        "## Review Queue\n\n"
        "| ID | Title | When to return | Status |\n"
        "|---|---|---|---|\n"
        "| R-001 | Открытая находка | Before Altegio | Pending |\n"
        "| R-009 | Закрытая находка | — | Closed |\n\n"
        "## Rules\n\nтекст\n",
        encoding="utf-8",
    )

    (colore / "state.md").write_text(
        "# State\n\n## Unknowns\n\n- Базовая конверсия кампании: TODO\n- SLA доставки: TODO\n",
        encoding="utf-8",
    )

    (colore / "sprint.md").write_text(
        "# Sprint\n\n"
        "## Active Sprint\n\n"
        "- **Name:** FIRST REVENUE\n"
        "- **Status:** ACTIVE\n\n"
        "## Main Goal\n\nПолучить первую запись.\n\n"
        "## Main KPI\n\nПервая выручка.\n\n"
        "## In Scope Now\n\n1. Первое\n2. Второе\n\n"
        "## Out of Scope\n\nничего\n",
        encoding="utf-8",
    )

    (colore / "next.md").write_text(
        "# Next\n\n"
        "## Active Task\n\nСобрать Growth AI.\n\n"
        "- **Status:** DOING\n\n"
        "## What remains before this is DONE\n\n- Нужен токен\n\n"
        "## Do Not Work On\n\nAltegio write-back и исходящие сообщения\nклиентам в любом канале.\n",
        encoding="utf-8",
    )

    return tmp_path


def test_changelog_is_read_and_the_template_is_skipped(fake_repo):
    entries, error = runtime_reader.read_changelog(fake_repo)

    assert error == ""
    assert [e.entry_id for e in entries] == ["VH-002", "VH-001"]
    assert all("XXX" not in e.entry_id for e in entries)


def test_news_reports_todays_entry(fake_repo, monkeypatch):
    monkeypatch.setattr(runtime_reader, "commits_since", lambda root=None, **kw: ["abc123 Тест"])
    import datetime

    class FixedDate(datetime.date):
        @classmethod
        def today(cls):
            return cls(2026, 8, 8)

    monkeypatch.setattr(commands, "date", FixedDate)

    answer = commands.news_answer(fake_repo)

    assert "Сегодняшняя работа." in answer
    assert "abc123 Тест" in answer
    assert "Что-то старое" not in answer


def test_review_queue_lists_open_entries_only(fake_repo):
    answer = commands.decisions_answer(fake_repo)

    assert "R-001" in answer
    assert "R-009" not in answer, "Closed entries are not open decisions"


def test_decisions_include_project_unknowns_and_blockers(fake_repo):
    answer = commands.decisions_answer(fake_repo)

    assert "Базовая конверсия кампании" in answer
    assert "Нужен токен" in answer
    assert ".colore/research.md" in answer, "the answer must name its sources"


def test_next_reports_sprint_and_active_task(fake_repo):
    answer = commands.next_answer(fake_repo)

    assert "FIRST REVENUE (ACTIVE)" in answer
    assert "Получить первую запись." in answer
    assert "Первая выручка." in answer
    assert "Собрать Growth AI." in answer
    assert "DOING" in answer
    # A rule wrapped across two source lines must arrive whole: a sentence cut
    # at "и исходящие сообщения" states a different rule than the real one.
    assert "Altegio write-back и исходящие сообщения клиентам в любом канале." in answer


# ------------------------------------------------------- no hallucinations


def test_missing_runtime_files_are_admitted_not_invented(tmp_path):
    """The whole point: no source, no answer — and say which file was missing."""
    news = commands.news_answer(tmp_path)
    decisions = commands.decisions_answer(tmp_path)
    upcoming = commands.next_answer(tmp_path)

    assert "changelog.md не найден" in news
    assert "research.md не найден" in decisions
    assert "state.md не найден" in decisions
    assert "sprint.md не найден" in upcoming
    assert "next.md не найден" in upcoming


def test_empty_review_queue_says_nothing_is_pending(tmp_path):
    colore = tmp_path / ".colore"
    colore.mkdir()
    (colore / "research.md").write_text(
        "## Review Queue\n\n| ID | Title | When to return | Status |\n|---|---|---|---|\n\n## Rules\n",
        encoding="utf-8",
    )
    (colore / "state.md").write_text("## Unknowns\n\n", encoding="utf-8")
    (colore / "next.md").write_text("## Active Task\n\nX\n", encoding="utf-8")

    assert "Ничего не ждёт вашего решения." in commands.decisions_answer(tmp_path)


def test_answers_are_trimmed_to_the_telegram_limit():
    trimmed = commands._fit("x" * 5000)

    assert len(trimmed) <= commands.TELEGRAM_LIMIT
    assert trimmed.endswith("… ответ сокращён")
