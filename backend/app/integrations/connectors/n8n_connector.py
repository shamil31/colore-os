"""n8n workflow trigger connector.

Contract verified 2026-08-08 against
https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/ —
see `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` §6.

Not to be confused with `gateway/n8n_adapter.py`. The adapter is a fire-and-
forget subscriber that mirrors internal integration events onto a webhook for
observability. This connector is the deliberate outbound direction: Coloré OS
starting a named workflow and caring about the answer.

The public n8n REST API (`X-N8N-API-KEY`, `/api/v1`) is for *managing*
workflows. Nothing today needs that, so it is not wired.
"""

from __future__ import annotations

from typing import Any

import requests

from app.integrations.gateway import capabilities
from app.integrations.gateway.base_connector import BaseConnector


class N8nWorkflowError(Exception):
    pass


class N8nConnector(BaseConnector):
    integration_name = "n8n"

    TRIGGER_CAPABILITY = "n8n.trigger_workflow"

    def __init__(
        self,
        *,
        workflow_url: str = "",
        auth_header: str = "",
        auth_token: str = "",
        timeout: int = 10,
        session: requests.Session | None = None,
    ) -> None:
        self.workflow_url = workflow_url.strip()
        self.auth_header = auth_header.strip()
        self.auth_token = auth_token.strip()
        self.timeout = timeout
        self._session = session or requests.Session()

    @property
    def capabilities(self) -> set[str]:
        return {capabilities.WORKFLOW_TRIGGER, self.TRIGGER_CAPABILITY}

    def is_configured(self) -> bool:
        return bool(self.workflow_url)

    def missing_configuration(self) -> tuple[str, ...]:
        return () if self.workflow_url else ("N8N_WORKFLOW_URL",)

    def execute(self, capability: str, *, payload: dict[str, Any] | None = None) -> Any:
        if capability not in self.capabilities:
            raise ValueError(f"Unsupported capability for n8n connector: {capability}")

        body = dict(payload or {})
        url = body.pop("workflow_url", None) or self.workflow_url

        headers = {}
        if self.auth_header and self.auth_token:
            headers[self.auth_header] = self.auth_token

        try:
            response = self._session.post(url, json=body, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise N8nWorkflowError(f"workflow request failed: {exc}") from exc

        # The single most likely cause of "the flow stopped working" is a
        # workflow that was never published, not a bug in our code. n8n answers
        # 404 on the production URL of a deactivated workflow, so say that
        # plainly instead of reporting a generic HTTP error.
        if response.status_code == 404:
            raise N8nWorkflowError(
                f"n8n returned 404 for {url} — the workflow is probably not "
                "published, or this is a test URL that is not currently listening"
            )

        if response.status_code >= 400:
            raise N8nWorkflowError(
                f"n8n returned HTTP {response.status_code} for {url}: "
                f"{response.text[:200]}"
            )

        try:
            return response.json()
        except ValueError:
            # "Respond immediately" answers with a plain message, not JSON.
            return {"status_code": response.status_code, "body": response.text[:500]}
