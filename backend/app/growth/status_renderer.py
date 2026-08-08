from __future__ import annotations

from app.growth.recommendation_renderer import RecommendationRenderer
from app.growth.response_builder import ResponseBuilder
from app.growth.system_status import Check


class StatusRenderer:
    def __init__(self, *, recommendation_renderer: RecommendationRenderer | None = None) -> None:
        self.recommendation_renderer = recommendation_renderer or RecommendationRenderer()

    def render(self, checks: list[Check], *, limit: int) -> str:
        builder = ResponseBuilder()
        builder.heading("📊 STATUS — COLORÉ OS")

        for check in checks:
            builder.line(f"{check.marker} {check.name}: {self._summary(check)}")
            for detail in check.detail:
                builder.detail(detail)

        problems = [c for c in checks if c.ok is False]
        unknown = [c for c in checks if c.ok is None]

        builder.section("Overview")
        if not problems and not unknown:
            builder.line("Everything looks healthy.")
        else:
            if problems:
                builder.line(f"Needs attention: {', '.join(c.name for c in problems)}.")
            if unknown:
                builder.line(f"Could not verify: {', '.join(c.name for c in unknown)}.")

        builder.section("Recommendations")
        for item in self.recommendation_renderer.for_status(checks):
            builder.bullet(item)

        return builder.build(limit=limit)

    def _summary(self, check: Check) -> str:
        if check.name == "Meta" and check.ok is False and "не настроен" in check.summary:
            return "I cannot analyze advertising because Meta Business is not connected."
        return check.summary
