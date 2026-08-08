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

    lines = ["📊 СТАТУС COLORÉ OS", ""]
    for check in checks:
        lines.append(f"{check.marker} {check.name}: {check.summary}")
        for detail in check.detail:
            lines.append(f"     • {detail}")

    problems = [c for c in checks if c.ok is False]
    unknown = [c for c in checks if c.ok is None]

    lines.append("")
    if not problems and not unknown:
        lines.append("Всё в порядке.")
    else:
        if problems:
            lines.append(f"Требует внимания: {', '.join(c.name for c in problems)}.")
        if unknown:
            lines.append(f"Не удалось проверить: {', '.join(c.name for c in unknown)}.")

    return _fit("\n".join(lines))


# --------------------------------------------------------------- что нового


def news_answer(root: Path | None = None) -> str:
    today = date.today().isoformat()
    entries, error = runtime_reader.read_changelog(root)
    commits = runtime_reader.commits_since(root, day=today)

    lines = [f"🆕 ЧТО НОВОГО — {today}", ""]

    if error:
        lines.append(f"Журнал изменений прочитать не удалось: {error}")
    else:
        todays = runtime_reader.entries_for(entries, today)
        if todays:
            lines.append("Записано в журнал проекта сегодня:")
            lines.append("")
            for entry in todays:
                lines.append(f"• {entry.entry_id} — {entry.event}")
                if entry.status:
                    lines.append(f"   статус: {entry.status}")
                lines.append("")
        else:
            lines.append("Сегодня в журнал проекта записей не добавлено.")
            lines.append("")
            if entries:
                last = entries[0]
                lines.append(f"Последняя запись — {last.entry_id} от {last.date}:")
                lines.append(f"{last.event}")
                lines.append("")

    if commits:
        lines.append(f"Коммитов сегодня: {len(commits)}")
        for commit in commits:
            lines.append(f"• {commit}")
    else:
        lines.append("Коммитов за сегодня нет.")

    return _fit("\n".join(lines))


# --------------------------------------------- что требует моего решения


def decisions_answer(root: Path | None = None) -> str:
    lines = ["🤔 ТРЕБУЕТ ВАШЕГО РЕШЕНИЯ", ""]
    found_any = False

    items, error = runtime_reader.read_review_queue(root)
    if error:
        lines.append(f"Очередь исследований недоступна: {error}")
        lines.append("")
    else:
        open_items = [
            item for item in items if item.status.strip().lower().startswith(OPEN_STATUSES)
        ]
        if open_items:
            found_any = True
            lines.append("Открытые исследования (нужно решение: принять, отклонить или отложить):")
            lines.append("")
            for item in open_items:
                lines.append(f"• {item.item_id} — {item.title}")
                lines.append(f"   вернуться: {item.when} | статус: {item.status}")
                lines.append("")

    unknowns, error = runtime_reader.read_unknowns(root)
    if error:
        lines.append(f"Список открытых вопросов недоступен: {error}")
        lines.append("")
    elif unknowns:
        found_any = True
        lines.append("Открытые вопросы проекта (нет данных — нужны от вас):")
        lines.append("")
        for unknown in unknowns:
            lines.append(f"• {unknown}")
        lines.append("")

    next_view, error = runtime_reader.read_next(root)
    if not error and next_view.remaining:
        found_any = True
        lines.append("Блокирует закрытие текущей задачи:")
        lines.append("")
        for item in next_view.remaining:
            lines.append(f"• {item}")
        lines.append("")

    if not found_any:
        lines.append("Ничего не ждёт вашего решения.")

    lines.append("Источники: .colore/research.md, .colore/state.md, .colore/next.md")
    return _fit("\n".join(lines))


# ----------------------------------------------------------- что дальше


def next_answer(root: Path | None = None) -> str:
    lines = ["🎯 ЧТО ДЕЛАЕМ ДАЛЬШЕ", ""]

    sprint, error = runtime_reader.read_sprint(root)
    if error:
        lines.append(f"Спринт прочитать не удалось: {error}")
    else:
        if sprint.name:
            lines.append(f"Спринт: {sprint.name}")
        if sprint.goal:
            lines.append(f"Цель: {sprint.goal}")
        if sprint.kpi:
            lines.append(f"KPI: {sprint.kpi}")
        if sprint.in_scope:
            lines.append("")
            lines.append("В работе сейчас:")
            for item in sprint.in_scope:
                lines.append(f"• {item}")

    lines.append("")

    next_view, error = runtime_reader.read_next(root)
    if error:
        lines.append(f"Активную задачу прочитать не удалось: {error}")
    else:
        if next_view.task:
            lines.append(f"Активная задача: {next_view.task}")
        if next_view.status:
            lines.append(f"Статус: {next_view.status}")
        if next_view.remaining:
            lines.append("")
            lines.append("Осталось:")
            for item in next_view.remaining:
                lines.append(f"• {item}")
        if next_view.do_not:
            lines.append("")
            lines.append("Не берём в работу:")
            for item in next_view.do_not:
                lines.append(f"• {item}")

    lines.append("")
    lines.append("Источники: .colore/sprint.md, .colore/next.md")
    return _fit("\n".join(lines))


# --------------------------------------------------------------------- help


def help_answer() -> str:
    return (
        "🤖 Growth AI Coloré\n"
        "\n"
        "Команды:\n"
        "\n"
        "• Статус — доктор, деплой, git, docker и все интеграции\n"
        "• Что нового? — что сделано сегодня по журналу проекта и коммитам\n"
        "• Что требует моего решения? — открытые исследования и вопросы\n"
        "• Что делаем дальше? — текущий спринт и активная задача\n"
        "• Аналитика — лиды, записи, конверсия и чего не хватает\n"
        "\n"
        "Отвечаю только на факты из репозитория и живых проверок. "
        "Если данных нет — так и скажу."
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
