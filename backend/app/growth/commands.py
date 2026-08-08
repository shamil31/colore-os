"""The four Product Owner commands, and how they are answered.

Answers are assembled from observed state (`system_status`) and from the
Runtime documents (`runtime_reader`). Nothing is invented. Where a source is
missing the answer says which file was missing, so the fix is obvious.

Plain text on purpose — the Telegram connector sends without `parse_mode`, so
a stray `_` or `*` in a commit subject cannot break the reply.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path

from app.growth import runtime_reader, system_status
from app.growth.response_builder import ResponseBuilder
from app.growth.status_renderer import StatusRenderer

logger = logging.getLogger("colore.commands")

TELEGRAM_LIMIT = 4096

CMD_STATUS = "status"
CMD_NEWS = "news"
CMD_DECISIONS = "decisions"
CMD_NEXT = "next"
CMD_ANALYTICS = "analytics"
CMD_HELP = "help"

ANALYTICS_DAYS = 30

# Statuses that mean an entry is still open. Matches the definition in
# .colore/bootstrap.md: Rejected and Closed are not reported.
OPEN_STATUSES = ("pending", "under review", "adopted")

_status_renderer = StatusRenderer()

_ALIASES: dict[str, tuple[str, ...]] = {
    CMD_STATUS: ("статус", "status", "/status", "/статус"),
    CMD_NEWS: (
        "что нового",
        "что нового?",
        "новости",
        "news",
        "/news",
    ),
    CMD_DECISIONS: (
        "что требует моего решения",
        "что требует моего решения?",
        "что требует решения",
        "решения",
        "decisions",
        "/decisions",
    ),
    CMD_NEXT: (
        "что делаем дальше",
        "что делаем дальше?",
        "дальше",
        "next",
        "/next",
    ),
    CMD_ANALYTICS: (
        "аналитика",
        "analytics",
        "/analytics",
        "/аналитика",
        "цифры",
    ),
    CMD_HELP: ("help", "/help", "/start", "помощь", "команды"),
}


def normalise(text: str) -> str:
    text = (text or "").strip().lower().replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .!?")


def route(text: str) -> str | None:
    """Map a message to a command, or None when it is not one of ours."""
    cleaned = normalise(text)
    if not cleaned:
        return None

    for command, aliases in _ALIASES.items():
        for alias in aliases:
            if cleaned == normalise(alias):
                return command

    return None


def handle(command: str, root: Path | None = None) -> str:
    if command == CMD_STATUS:
        return status_answer(root)
    if command == CMD_NEWS:
        return news_answer(root)
    if command == CMD_DECISIONS:
        return decisions_answer(root)
    if command == CMD_NEXT:
        return next_answer(root)
    if command == CMD_ANALYTICS:
        return analytics_answer()
    return help_answer()


def analytics_answer(days: int = ANALYTICS_DAYS) -> str:
    """Leads, bookings, conversion, gaps and advice — from real data only.

    Imported lazily: this is the only command that reaches the database and
    Altegio, and the other three must keep working when either is down.
    """
    from app.growth import analytics

    try:
        report = analytics.build_report(days=days)
    except Exception as exc:  # noqa: BLE001
        logger.exception("analytics failed")
        return (
            "📈 АНАЛИТИКА\n"
            "\n"
            f"Не удалось собрать данные: {type(exc).__name__}: {exc}\n"
            "\n"
            "Ничего не показываю, чтобы не выдумать цифры."
        )

    return _fit(analytics.render(report))


# ------------------------------------------------------------------- статус


def status_answer(root: Path | None = None) -> str:
    checks = system_status.collect_status(root)
    return _status_renderer.render(checks, limit=TELEGRAM_LIMIT)


# --------------------------------------------------------------- что нового


def news_answer(root: Path | None = None) -> str:
    today = date.today().isoformat()
    entries, error = runtime_reader.read_changelog(root)
    commits = runtime_reader.commits_since(root, day=today)

    builder = ResponseBuilder().heading(f"🆕 WHAT'S NEW — {today}")

    if error:
        builder.section("Project changelog").line(f"Cannot read changelog: {error}")
    else:
        todays = runtime_reader.entries_for(entries, today)
        if todays:
            builder.section("Project changelog")
            builder.line("Recorded today:")
            for entry in todays:
                builder.bullet(f"{entry.entry_id} — {entry.event}")
                if entry.status:
                    builder.detail(f"status: {entry.status}")
        else:
            builder.section("Project changelog")
            builder.line("No new changelog entries today.")
            if entries:
                last = entries[0]
                builder.line(f"Latest entry: {last.entry_id} ({last.date})")
                builder.detail(last.event)

    builder.section("Git commits")
    if commits:
        builder.line(f"Commits today: {len(commits)}")
        for commit in commits:
            builder.bullet(commit)
    else:
        builder.line("No commits today.")

    return builder.build(limit=TELEGRAM_LIMIT)


# --------------------------------------------- что требует моего решения


def decisions_answer(root: Path | None = None) -> str:
    builder = ResponseBuilder().heading("🤔 DECISIONS NEEDED")
    found_any = False

    items, error = runtime_reader.read_review_queue(root)
    if error:
        builder.section("Research queue").line(f"Unavailable: {error}")
    else:
        open_items = [
            item for item in items if item.status.strip().lower().startswith(OPEN_STATUSES)
        ]
        if open_items:
            found_any = True
            builder.section("Open research")
            builder.line("Need your decision: accept, reject, or postpone.")
            for item in open_items:
                builder.bullet(f"{item.item_id} — {item.title}")
                builder.detail(f"return: {item.when} | status: {item.status}")

    unknowns, error = runtime_reader.read_unknowns(root)
    if error:
        builder.section("Open questions").line(f"Unavailable: {error}")
    elif unknowns:
        found_any = True
        builder.section("Open questions")
        builder.line("Missing data that needs your input:")
        for unknown in unknowns:
            builder.bullet(unknown)

    next_view, error = runtime_reader.read_next(root)
    if not error and next_view.remaining:
        found_any = True
        builder.section("Current blockers")
        for item in next_view.remaining:
            builder.bullet(item)

    if not found_any:
        builder.section("Summary").line("No pending decisions for now.")

    builder.section("Sources")
    builder.line(".colore/research.md, .colore/state.md, .colore/next.md")
    return builder.build(limit=TELEGRAM_LIMIT)


# ----------------------------------------------------------- что дальше


def next_answer(root: Path | None = None) -> str:
    builder = ResponseBuilder().heading("🎯 WHAT'S NEXT")

    sprint, error = runtime_reader.read_sprint(root)
    if error:
        builder.section("Sprint").line(f"Unavailable: {error}")
    else:
        builder.section("Sprint")
        if sprint.name:
            builder.line(f"Sprint: {sprint.name}")
        if sprint.goal:
            builder.line(f"Goal: {sprint.goal}")
        if sprint.kpi:
            builder.line(f"KPI: {sprint.kpi}")
        if sprint.in_scope:
            builder.line("In scope now:")
            for item in sprint.in_scope:
                builder.bullet(item)

    next_view, error = runtime_reader.read_next(root)
    if error:
        builder.section("Active task").line(f"Unavailable: {error}")
    else:
        builder.section("Active task")
        if next_view.task:
            builder.line(f"Task: {next_view.task}")
        if next_view.status:
            builder.line(f"Status: {next_view.status}")
        if next_view.remaining:
            builder.line("Remaining:")
            for item in next_view.remaining:
                builder.bullet(item)
        if next_view.do_not:
            builder.section("Do not work on")
            for item in next_view.do_not:
                builder.bullet(item)

    builder.section("Sources")
    builder.line(".colore/sprint.md, .colore/next.md")
    return builder.build(limit=TELEGRAM_LIMIT)


# --------------------------------------------------------------------- help


def help_answer() -> str:
    return (
        "🤖 GROWTH AI — COMMANDS\n"
        "\n"
        "• Статус — doctor, deploy, git, docker and integrations\n"
        "• Что нового? — today's changelog and commits\n"
        "• Что требует моего решения? — open research and unknowns\n"
        "• Что делаем дальше? — sprint and active task\n"
        "• Аналитика — leads, bookings, conversion, and gaps\n"
        "\n"
        "I only answer with facts from repository files and live checks. "
        "If data is missing, I say so directly."
    )


def unknown_answer(text: str) -> str:
    return (
        f"Не знаю команду «{text.strip()[:60]}».\n"
        "\n" + help_answer()
    )


def _fit(text: str, limit: int = TELEGRAM_LIMIT) -> str:
    """Telegram rejects anything over 4096 characters."""
    if len(text) <= limit:
        return text
    notice = "\n\n… ответ сокращён"
    return text[: limit - len(notice)] + notice
