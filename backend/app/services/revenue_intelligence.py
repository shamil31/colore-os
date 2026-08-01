from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy.orm import Session

from app.models.revenue_client import RevenueClient

SegmentLabel = Literal["regular", "delayed", "lost", "unknown"]


@dataclass(frozen=True)
class SegmentRule:
    delayed_days: int
    lost_days: int


@dataclass(frozen=True)
class RankedReactivationCandidate:
    revenue_client_id: int
    altegio_client_id: int
    full_name: str | None
    phone: str | None
    company_id: int
    last_service_name: str | None
    visit_count: int | None
    last_visit_at: datetime | None
    days_since_last_visit: int | None
    segment: SegmentLabel
    score: int


class RevenueSegmentationEngine:
    def __init__(self) -> None:
        self.default_rule = SegmentRule(
            delayed_days=int(os.getenv("REVENUE_DEFAULT_DELAYED_DAYS", "45")),
            lost_days=int(os.getenv("REVENUE_DEFAULT_LOST_DAYS", "90")),
        )
        self.service_rules = self._load_service_rules()

    def classify(self, client: RevenueClient, now: datetime | None = None) -> tuple[SegmentLabel, int | None]:
        rule = self._resolve_rule(client.last_service_name)

        if client.last_visit_at is None:
            return "lost", None

        current = now or datetime.utcnow()
        days = max((current - client.last_visit_at).days, 0)

        if days < rule.delayed_days:
            return "regular", days
        if days < rule.lost_days:
            return "delayed", days
        return "lost", days

    def rank_reactivation_candidates(
        self,
        db: Session,
        company_id: int | None = None,
        limit: int = 200,
        include_regular: bool = False,
    ) -> list[RankedReactivationCandidate]:
        query = db.query(RevenueClient).filter(RevenueClient.is_active.is_(True))

        if company_id is not None:
            query = query.filter(RevenueClient.company_id == company_id)

        rows = query.all()

        ranked: list[RankedReactivationCandidate] = []
        for row in rows:
            segment, days = self.classify(row)
            if segment == "regular" and not include_regular:
                continue

            score = self._score_candidate(segment=segment, days_since_last_visit=days, visit_count=row.visit_count)

            ranked.append(
                RankedReactivationCandidate(
                    revenue_client_id=row.id,
                    altegio_client_id=row.altegio_client_id,
                    full_name=row.full_name,
                    phone=row.phone,
                    company_id=row.company_id,
                    last_service_name=row.last_service_name,
                    visit_count=row.visit_count,
                    last_visit_at=row.last_visit_at,
                    days_since_last_visit=days,
                    segment=segment,
                    score=score,
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:limit]

    def _resolve_rule(self, service_name: str | None) -> SegmentRule:
        if not service_name:
            return self.default_rule

        normalized = service_name.lower()
        for keyword, rule in self.service_rules.items():
            if keyword in normalized:
                return rule

        return self.default_rule

    def _load_service_rules(self) -> dict[str, SegmentRule]:
        raw = os.getenv("REVENUE_SERVICE_RULES_JSON", "")
        if not raw:
            return {}

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}

        if not isinstance(payload, dict):
            return {}

        rules: dict[str, SegmentRule] = {}
        for key, value in payload.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue

            delayed = value.get("delayed_days")
            lost = value.get("lost_days")
            if not isinstance(delayed, int) or not isinstance(lost, int):
                continue
            if delayed <= 0 or lost <= delayed:
                continue

            rules[key.lower()] = SegmentRule(delayed_days=delayed, lost_days=lost)

        return rules

    @staticmethod
    def _score_candidate(
        segment: SegmentLabel,
        days_since_last_visit: int | None,
        visit_count: int | None,
    ) -> int:
        base = {
            "lost": 100,
            "delayed": 70,
            "regular": 20,
            "unknown": 10,
        }[segment]

        score = base

        if days_since_last_visit is not None:
            score += min(days_since_last_visit, 120)

        if visit_count is not None:
            score += min(max(visit_count, 0), 25)

        return score
