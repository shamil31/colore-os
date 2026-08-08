from __future__ import annotations

from app.growth.system_status import Check


class RecommendationRenderer:
    """Convert observed system checks into short operator recommendations."""

    def for_status(self, checks: list[Check]) -> list[str]:
        recommendations: list[str] = []

        by_name = {check.name: check for check in checks}

        doctor = by_name.get("Doctor")
        if doctor and doctor.ok is False:
            recommendations.append("Run scripts/doctor.sh and resolve reported failures.")

        deploy = by_name.get("Deploy")
        if deploy and deploy.ok is False:
            recommendations.append("Run ./deploy.sh from repository root to align runtime with HEAD.")

        git_check = by_name.get("Git")
        if git_check and git_check.ok is False:
            recommendations.append("Review, commit, or stash local git changes before the next release.")

        docker = by_name.get("Docker")
        if docker and docker.ok is False:
            recommendations.append("Start required colore-* containers and re-run Status.")

        meta = by_name.get("Meta")
        if meta and meta.ok is False:
            recommendations.append("Connect Meta Business to enable advertising analysis.")

        if not recommendations:
            recommendations.append("No action required now.")

        return recommendations
