from __future__ import annotations

import argparse

from app.db.database import SessionLocal
from app.services.revenue_intelligence import RevenueSegmentationEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank RevenueClient reactivation candidates")
    parser.add_argument("--company-id", type=int, default=None, help="Filter by company_id")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of ranked candidates")
    parser.add_argument(
        "--include-regular",
        action="store_true",
        help="Include regular segment in output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    engine = RevenueSegmentationEngine()

    with SessionLocal() as db:
        ranked = engine.rank_reactivation_candidates(
            db=db,
            company_id=args.company_id,
            limit=args.limit,
            include_regular=args.include_regular,
        )

    print(f"CANDIDATES: {len(ranked)}")
    for item in ranked:
        print(
            " | ".join(
                [
                    f"score={item.score}",
                    f"segment={item.segment}",
                    f"revenue_client_id={item.revenue_client_id}",
                    f"altegio_client_id={item.altegio_client_id}",
                    f"company_id={item.company_id}",
                    f"days={item.days_since_last_visit}",
                    f"visits={item.visit_count}",
                    f"service={item.last_service_name}",
                    f"phone={item.phone}",
                    f"name={item.full_name}",
                ]
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
