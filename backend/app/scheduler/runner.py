"""The scheduler process, and the command line that drives it.

    python -m app.scheduler.runner                 # loop forever (systemd)
    python -m app.scheduler.runner --once          # run everything due, exit
    python -m app.scheduler.runner --job meta_conversions --mode manual
    python -m app.scheduler.runner --job meta_conversions --mode dry_run
    python -m app.scheduler.runner --job meta_conversions --mode test
    python -m app.scheduler.runner --status        # JSON, used by the doctor

Runs on the host, like the bot: the jobs read `.colore/`-adjacent state, the
database and external APIs, and a container gives no advantage.
"""

from __future__ import annotations

import argparse
import json
import logging
import signal
import sys
import time

from app.core.config import settings
from app.scheduler.job import ALL_MODES, MODE_INTERVAL

logger = logging.getLogger("colore.scheduler")

_running = True


def _stop(*_: object) -> None:
    global _running
    logger.info("stopping after the current tick")
    _running = False


def build_service():
    from app.db.database import SessionLocal
    from app.growth.meta_job import build_registry
    from app.scheduler.service import SchedulerService

    return SchedulerService(build_registry(), SessionLocal)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coloré OS integration scheduler")
    parser.add_argument("--once", action="store_true", help="run everything due, then exit")
    parser.add_argument("--job", help="run one job by name")
    parser.add_argument("--mode", default=MODE_INTERVAL, choices=ALL_MODES)
    parser.add_argument("--status", action="store_true", help="print status as JSON and exit")
    parser.add_argument("--list", action="store_true", help="list registered jobs")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    service = build_service()

    if args.status:
        print(json.dumps(service.status(), ensure_ascii=False, indent=2))
        return 0

    if args.list:
        for job in service.registry.all():
            available, reason = job.is_available()
            state = "available" if available else f"unavailable ({reason})"
            print(f"{job.name}: every {job.interval_seconds}s — {state}")
        return 0

    if args.job:
        result = service.run_job(args.job, mode=args.mode)
        print(json.dumps(
            {
                "job": args.job,
                "mode": args.mode,
                "status": result.status,
                "message": result.message,
                "error": result.error,
                "summary": result.summary,
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0 if result.ok else 1

    if args.once:
        results = service.run_due()
        for name, result in results.items():
            print(f"{name}: {result.status} — {result.message or result.error}")
        return 0

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    tick = max(5, settings.SCHEDULER_TICK_SECONDS)
    logger.info(
        "scheduler ready: %s job(s), tick %ss",
        len(service.registry.names()),
        tick,
    )
    for job in service.registry.all():
        available, reason = job.is_available()
        logger.info(
            "  %s: every %ss — %s",
            job.name,
            job.interval_seconds,
            "available" if available else f"unavailable ({reason})",
        )

    while _running:
        try:
            results = service.run_due()
            for name, result in results.items():
                logger.info("%s: %s — %s", name, result.status, result.message or result.error)
        except Exception:  # noqa: BLE001 — the loop must outlive any single tick
            logger.exception("scheduler tick failed")

        for _ in range(tick):
            if not _running:
                break
            time.sleep(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
