from __future__ import annotations


class ResponseBuilder:
    """Reusable plain-text response assembler for Telegram answers."""

    def __init__(self) -> None:
        self._lines: list[str] = []

    def heading(self, text: str) -> "ResponseBuilder":
        self._lines.append(text)
        return self

    def section(self, title: str) -> "ResponseBuilder":
        self._ensure_gap()
        self._lines.append(title)
        return self

    def line(self, text: str = "") -> "ResponseBuilder":
        self._lines.append(text)
        return self

    def bullet(self, text: str) -> "ResponseBuilder":
        self._lines.append(f"• {text}")
        return self

    def detail(self, text: str) -> "ResponseBuilder":
        self._lines.append(f"  - {text}")
        return self

    def build(self, *, limit: int | None = None) -> str:
        text = "\n".join(self._lines).strip()
        if limit is None or len(text) <= limit:
            return text

        notice = "\n\n… ответ сокращён"
        return text[: limit - len(notice)] + notice

    def _ensure_gap(self) -> None:
        if self._lines and self._lines[-1] != "":
            self._lines.append("")
