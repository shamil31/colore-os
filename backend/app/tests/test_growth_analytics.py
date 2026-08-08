"""Analytics: the metrics, and the refusal to invent them.

The central rule under test is that conversion is only ever reported for leads
that could actually be attributed to a booking. A ratio of total bookings to
total leads would look like an answer and mean nothing — most of the salon's
bookings have no connection to Growth AI at all.
"""

from datetime import date, datetime, timedelta

from app.growth import analytics, business_data
from app.growth.business_data import BusinessSnapshot, phone_key
from app.models.growth import STATUS_PROCESSED, GrowthEvent

TODAY = date(2026, 8, 8)


class FakeSession:
    def __init__(self, events, raises=None):
        self._events = events
        self._raises = raises

    def query(self, model):
        if self._raises:
            raise self._raises
        return self

    def filter(self, *args):
        return self

    def all(self):
        return self._events

    def close(self):
        pass


def session_factory_for(events, raises=None):
    return lambda: FakeSession(events, raises)


def lead(source="whatsapp", sender_ref="381641234567", days_ago=5):
    event = GrowthEvent(
        source=source,
        external_id=f"id-{source}-{sender_ref}-{days_ago}",
        sender_ref=sender_ref,
        text="Хочу записаться",
        status=STATUS_PROCESSED,
    )
    event.received_at = datetime(2026, 8, 8) - timedelta(days=days_ago)
    return event


def booking(phone="381641234567", created="2026-08-05T10:00:00+0200", attendance=1, **extra):
    record = {
        "id": 1,
        "attendance": attendance,
        "create_date": created,
        "date": "2026-08-06 09:00:00",
        "client": {"phone": phone, "is_new": extra.get("is_new", False)},
        "from_url": extra.get("from_url", ""),
    }
    return record


def snapshot_with(records, **kwargs):
    return BusinessSnapshot(
        company_id=1316083,
        company_title="Colore beauty lab",
        services=kwargs.get("services", [object()] * 90),
        staff=kwargs.get("staff", [object()] * 4),
        clients=kwargs.get("clients", [{}] * 334),
        records=records,
        date_from="2026-07-09",
        date_to="2026-08-08",
        errors=kwargs.get("errors", []),
        notes=kwargs.get("notes", []),
    )


# -------------------------------------------------------------- phone match


def test_phone_key_survives_country_code_and_formatting():
    assert phone_key("+381 64 123-45-67") == phone_key("381641234567")
    assert phone_key("381641234567") == phone_key("0641234567")


def test_phone_key_is_empty_for_a_non_phone():
    assert phone_key("IGSID_ANA") == ""
    assert phone_key(None) == ""


# ------------------------------------------------------------------- leads


def test_leads_are_counted_by_source():
    events = [lead(), lead(source="instagram", sender_ref="IGSID_A")]

    stats, returned = analytics.collect_leads(
        session_factory_for(events), since=datetime(2026, 7, 9)
    )

    assert stats.total == 2
    assert stats.by_source == {"whatsapp": 1, "instagram": 1}
    assert len(returned) == 2


def test_instagram_leads_are_marked_unattributable_with_the_reason():
    events = [lead(source="instagram", sender_ref="IGSID_A")]

    stats, _ = analytics.collect_leads(session_factory_for(events), since=datetime(2026, 7, 9))

    assert stats.attributable == 0
    assert "Instagram IGSID не является телефоном" in "".join(stats.unattributable)


def test_a_database_outage_is_reported_not_swallowed():
    stats, events = analytics.collect_leads(
        session_factory_for([], raises=RuntimeError("connection refused")),
        since=datetime(2026, 7, 9),
    )

    assert stats.total == 0
    assert "growth_events" in stats.error
    assert events == []


# ---------------------------------------------------------------- bookings


def test_bookings_are_split_by_official_attendance_codes():
    records = [
        booking(attendance=1),
        booking(attendance=1),
        booking(attendance=-1),
        booking(attendance=0),
    ]

    stats = analytics.collect_bookings(snapshot_with(records))

    assert stats.total == 4
    assert stats.arrived == 2
    assert stats.no_show == 1
    assert stats.by_attendance[business_data.ATTENDANCE_PENDING] == 1


def test_online_and_new_client_bookings_are_counted():
    records = [
        booking(from_url="https://n123456.alteg.io"),
        booking(is_new=True),
        booking(),
    ]

    stats = analytics.collect_bookings(snapshot_with(records))

    assert stats.online == 1
    assert stats.new_clients == 1


# ------------------------------------------------------------- attribution


def test_a_booking_made_after_the_lead_counts_as_converted():
    events = [lead(days_ago=5)]  # 2026-08-03
    records = [booking(created="2026-08-05T10:00:00+0200")]

    assert analytics.attribute(events, snapshot_with(records)) == 1


def test_a_booking_made_before_the_lead_does_not_count():
    """A client who already had an appointment did not convert because of a message."""
    events = [lead(days_ago=1)]  # 2026-08-07
    records = [booking(created="2026-08-05T10:00:00+0200")]

    assert analytics.attribute(events, snapshot_with(records)) == 0


def test_a_booking_by_a_different_person_does_not_count():
    events = [lead(sender_ref="381641234567")]
    records = [booking(phone="381609999999", created="2026-08-06T10:00:00+0200")]

    assert analytics.attribute(events, snapshot_with(records)) == 0


def test_instagram_leads_are_never_attributed():
    events = [lead(source="instagram", sender_ref="IGSID_A")]
    records = [booking(created="2026-08-06T10:00:00+0200")]

    assert analytics.attribute(events, snapshot_with(records)) == 0


# ------------------------------------------------------------- conversion


def test_conversion_is_reported_over_attributable_leads_only():
    events = [
        lead(sender_ref="381641234567", days_ago=5),
        lead(source="instagram", sender_ref="IGSID_A"),
    ]
    records = [booking(phone="381641234567", created="2026-08-06T10:00:00+0200")]

    report = analytics.build_report(
        session_factory=session_factory_for(events),
        snapshot=snapshot_with(records),
        today=TODAY,
    )

    assert report.leads.total == 2
    assert report.leads.attributable == 1
    assert report.converted == 1
    assert report.conversion == 1.0, "1 of 1 attributable, not 1 of 2 total"


def test_conversion_is_withheld_when_nothing_can_be_attributed():
    """The whole point: no attribution, no number."""
    events = [lead(source="instagram", sender_ref="IGSID_A")]

    report = analytics.build_report(
        session_factory=session_factory_for(events),
        snapshot=snapshot_with([booking()] * 47),
        today=TODAY,
    )

    assert report.conversion_measurable is False
    assert report.conversion is None

    rendered = analytics.render(report)
    assert "Конверсия: не рассчитывается." in rendered
    assert "было бы выдуманным" in rendered


def test_conversion_is_never_bookings_divided_by_leads():
    """47 bookings and 1 lead must not produce 4700%."""
    events = [lead(sender_ref="381641234567", days_ago=5)]
    records = [booking(phone="381600000000")] * 47

    report = analytics.build_report(
        session_factory=session_factory_for(events),
        snapshot=snapshot_with(records),
        today=TODAY,
    )

    assert report.bookings.total == 47
    assert report.converted == 0
    assert report.conversion == 0.0


# ------------------------------------------------------ unavailable data


def test_no_altegio_means_an_explanation_not_an_empty_report():
    snapshot = BusinessSnapshot(
        errors=["Altegio не настроен — отсутствует: ALTEGIO_PARTNER_TOKEN"]
    )

    report = analytics.build_report(
        session_factory=session_factory_for([]),
        snapshot=snapshot,
        today=TODAY,
    )
    rendered = analytics.render(report)

    assert "Бизнес-данные недоступны." in rendered
    assert "ALTEGIO_PARTNER_TOKEN" in rendered
    assert "Проверить доступ к Altegio" in rendered
    assert "%" not in rendered, "no percentages may appear when there is no data"


def test_a_partial_snapshot_names_the_dataset_that_failed():
    snapshot = snapshot_with([booking()], errors=["клиенты: HTTP 500"])

    report = analytics.build_report(
        session_factory=session_factory_for([]),
        snapshot=snapshot,
        today=TODAY,
    )

    assert any("клиенты: HTTP 500" in item for item in report.missing_data)


def test_a_stale_company_id_is_surfaced_as_missing_data():
    snapshot = snapshot_with(
        [booking()],
        notes=["ALTEGIO_COMPANY_ID=2403 не совпадает с реальным 1316083 — используется значение из API"],
    )

    report = analytics.build_report(
        session_factory=session_factory_for([]),
        snapshot=snapshot,
        today=TODAY,
    )

    assert any("2403" in item for item in report.missing_data)
    assert any("ALTEGIO_COMPANY_ID" in item for item in report.recommendations)


def test_missing_ad_data_is_always_stated():
    report = analytics.build_report(
        session_factory=session_factory_for([lead()]),
        snapshot=snapshot_with([booking()]),
        today=TODAY,
    )

    assert any("Marketing API" in item for item in report.missing_data)


def test_no_leads_explains_why_rather_than_showing_a_zero():
    report = analytics.build_report(
        session_factory=session_factory_for([]),
        snapshot=snapshot_with([booking()]),
        today=TODAY,
    )

    assert any("Meta не подключена" in item for item in report.missing_data)
    assert any("Подключить Meta" in item for item in report.recommendations)


# ------------------------------------------------------------------ command


def test_analytics_command_routes():
    from app.growth import commands

    assert commands.route("Аналитика") == commands.CMD_ANALYTICS
    assert commands.route("аналитика") == commands.CMD_ANALYTICS
    assert commands.route("/analytics") == commands.CMD_ANALYTICS


def test_analytics_command_reports_a_failure_instead_of_numbers(monkeypatch):
    from app.growth import commands

    def explode(**kwargs):
        raise RuntimeError("altegio unreachable")

    monkeypatch.setattr(analytics, "build_report", explode)

    answer = commands.analytics_answer()

    assert "Не удалось собрать данные" in answer
    assert "altegio unreachable" in answer
    assert "не выдумать цифры" in answer
