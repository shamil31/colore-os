from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Coloré OS"
    VERSION: str = "0.1.0"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5"
    N8N_WEBHOOK_URL: str = ""
    N8N_TIMEOUT: int = 5

    ALTEGIO_BASE_URL: str = ""
    ALTEGIO_PARTNER_TOKEN: str = ""
    ALTEGIO_LOGIN: str = ""
    ALTEGIO_PASSWORD: str = ""
    ALTEGIO_TIMEOUT: int = 20
    # Declared so a stale value is visible and can be reported. The company id
    # is resolved from the API at runtime, never from this setting.
    ALTEGIO_COMPANY_ID: str = ""

    # Growth AI channels. Every one of these is optional: a connector without
    # its settings registers anyway, reports itself unconfigured, and turns
    # calls into recorded dry runs instead of failing (ADR-002 decision 7).
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_OPERATOR_CHAT_ID: str = ""
    # The only account the Growth AI bot answers. Falls back to the operator
    # chat id when unset.
    TELEGRAM_OWNER_ID: str = ""

    META_APP_SECRET: str = ""
    META_VERIFY_TOKEN: str = ""
    META_API_VERSION: str = "v23.0"
    # Conversions API. Both are needed to report confirmed outcomes back to
    # Meta; without them events are built and queued but never sent.
    META_ACCESS_TOKEN: str = ""
    META_DATASET_ID: str = ""
    # Sent with events so they land in Events Manager's Test Events view
    # without affecting ad delivery. Empty means real traffic.
    META_TEST_EVENT_CODE: str = ""

    # Currency of the amounts Altegio records. Deliberately empty by default:
    # the salon prices in RSD while the ad account bills in EUR, and a wrong
    # guess misstates every Purchase value by roughly 100x. When unset, events
    # carry no value at all rather than a value nobody verified.
    BUSINESS_CURRENCY: str = ""

    # Scheduler
    SCHEDULER_TICK_SECONDS: int = 60
    META_SYNC_INTERVAL_SECONDS: int = 900
    META_SYNC_DAYS: int = 14

    # Outbound: a workflow Coloré OS starts. Distinct from N8N_WEBHOOK_URL
    # above, which is where the event-bus adapter mirrors telemetry.
    N8N_WORKFLOW_URL: str = ""
    N8N_WORKFLOW_HEADER: str = "X-Colore-Token"
    N8N_WORKFLOW_TOKEN: str = ""

    # Shared secret for the n8n -> Coloré OS hop. Unset disables
    # POST /growth/events rather than leaving it open: :8000 is published.
    GROWTH_INBOUND_SECRET: str = ""

    TEST_DATABASE_URL: str = ""
    SQL_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()