"""Payload normalisation.

The shapes here are the ones in the official payload documentation, quoted in
`docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` §2 and §3.
"""

from app.growth.normalize import (
    SKIP_ECHO,
    SKIP_STATUS_ONLY,
    SKIP_UNKNOWN_SHAPE,
    SKIP_UNSUPPORTED_TYPE,
    SOURCE_INSTAGRAM,
    SOURCE_WHATSAPP,
    NormalisedEvent,
    SkippedEvent,
    normalise,
)


def whatsapp_payload(text="Сколько стоит окрашивание?", message_id="wamid.ABC"):
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "381600000000",
                                "phone_number_id": "PHONE_NUMBER_ID",
                            },
                            "contacts": [
                                {"profile": {"name": "Ана"}, "wa_id": "381641234567"}
                            ],
                            "messages": [
                                {
                                    "from": "381641234567",
                                    "id": message_id,
                                    "timestamp": "1754640000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def instagram_payload(text="Есть места на завтра?", mid="mid.XYZ", is_echo=False):
    message = {"mid": mid, "text": text}
    if is_echo:
        message["is_echo"] = True
    return {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_ACCOUNT_ID",
                "time": 1754640000,
                "messaging": [
                    {
                        "sender": {"id": "IGSID_CLIENT"},
                        "recipient": {"id": "IG_ACCOUNT_ID"},
                        "timestamp": 1754640000,
                        "message": message,
                    }
                ],
            }
        ],
    }


# ------------------------------------------------------------------ whatsapp


def test_whatsapp_text_message_is_normalised():
    result = normalise(whatsapp_payload())

    assert isinstance(result, NormalisedEvent)
    assert result.source == SOURCE_WHATSAPP
    assert result.external_id == "wamid.ABC"
    assert result.sender_ref == "381641234567"
    assert result.sender_name == "Ана"
    assert result.channel_ref == "PHONE_NUMBER_ID"
    assert result.text == "Сколько стоит окрашивание?"


def test_whatsapp_delivery_receipt_is_skipped_not_processed():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "P"},
                            "statuses": [
                                {"id": "wamid.OUT", "status": "delivered", "timestamp": "1"}
                            ],
                        },
                    }
                ],
            }
        ],
    }

    result = normalise(payload)

    assert isinstance(result, SkippedEvent)
    assert result.reason == SKIP_STATUS_ONLY


def test_whatsapp_non_text_message_is_skipped():
    payload = whatsapp_payload()
    message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
    message["type"] = "image"
    message.pop("text")

    result = normalise(payload)

    assert isinstance(result, SkippedEvent)
    assert result.reason == SKIP_UNSUPPORTED_TYPE
    assert result.external_id == "wamid.ABC"


# ----------------------------------------------------------------- instagram


def test_instagram_direct_message_is_normalised():
    result = normalise(instagram_payload())

    assert isinstance(result, NormalisedEvent)
    assert result.source == SOURCE_INSTAGRAM
    assert result.external_id == "mid.XYZ"
    assert result.sender_ref == "IGSID_CLIENT"
    assert result.text == "Есть места на завтра?"


def test_instagram_echo_is_skipped():
    """Without this the assistant answers its own outbound message, in a loop."""
    result = normalise(instagram_payload(is_echo=True))

    assert isinstance(result, SkippedEvent)
    assert result.reason == SKIP_ECHO


def test_instagram_self_flag_is_also_treated_as_an_echo():
    payload = instagram_payload()
    payload["entry"][0]["messaging"][0]["is_self"] = True

    result = normalise(payload)

    assert isinstance(result, SkippedEvent)
    assert result.reason == SKIP_ECHO


# --------------------------------------------------------------------- shape


def test_the_two_platforms_do_not_share_a_shape_and_both_still_parse():
    """A parser that assumed one nesting would silently drop the other."""
    whatsapp = normalise(whatsapp_payload())
    instagram = normalise(instagram_payload())

    assert isinstance(whatsapp, NormalisedEvent)
    assert isinstance(instagram, NormalisedEvent)
    assert whatsapp.source != instagram.source


def test_payload_wrapped_by_n8n_is_unwrapped():
    result = normalise({"body": whatsapp_payload()})

    assert isinstance(result, NormalisedEvent)
    assert result.external_id == "wamid.ABC"


def test_doubly_wrapped_payload_is_unwrapped():
    result = normalise({"payload": {"body": instagram_payload()}})

    assert isinstance(result, NormalisedEvent)
    assert result.external_id == "mid.XYZ"


def test_unknown_shape_is_reported_not_guessed():
    result = normalise({"object": "adaccount", "entry": []})

    assert isinstance(result, SkippedEvent)
    assert result.reason == SKIP_UNKNOWN_SHAPE


# -------------------------------------------------- P1-003: bundled deliveries


def test_a_real_message_bundled_with_an_echo_is_not_dropped():
    """Meta can deliver more than one messaging item in a single POST. An
    early return on the first skippable item would silently lose a real
    message sitting right behind an echo of our own reply — exactly the
    scenario a first live Instagram lead cannot survive being wrong about."""
    payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_ACCOUNT_ID",
                "time": 1754640000,
                "messaging": [
                    {
                        "sender": {"id": "IG_ACCOUNT_ID"},
                        "recipient": {"id": "IGSID_CLIENT"},
                        "message": {"mid": "mid.ECHO", "text": "our earlier reply", "is_echo": True},
                    },
                    {
                        "sender": {"id": "IGSID_CLIENT"},
                        "recipient": {"id": "IG_ACCOUNT_ID"},
                        "message": {"mid": "mid.REAL", "text": "Хочу записаться завтра"},
                    },
                ],
            }
        ],
    }

    result = normalise(payload)

    assert isinstance(result, NormalisedEvent), "the real message must still be found"
    assert result.external_id == "mid.REAL"
    assert result.text == "Хочу записаться завтра"
    assert result.sender_ref == "IGSID_CLIENT"


def test_a_real_message_after_a_non_text_item_is_not_dropped():
    payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_ACCOUNT_ID",
                "messaging": [
                    {
                        "sender": {"id": "IGSID_CLIENT"},
                        "recipient": {"id": "IG_ACCOUNT_ID"},
                        "message": {"mid": "mid.STICKER", "attachments": [{"type": "image"}]},
                    },
                    {
                        "sender": {"id": "IGSID_CLIENT"},
                        "recipient": {"id": "IG_ACCOUNT_ID"},
                        "message": {"mid": "mid.REAL2", "text": "Здравствуйте!"},
                    },
                ],
            }
        ],
    }

    result = normalise(payload)

    assert isinstance(result, NormalisedEvent)
    assert result.external_id == "mid.REAL2"


def test_a_real_message_in_a_second_entry_is_not_dropped():
    """Entries, not just messaging items, can arrive bundled in one delivery."""
    echoed = instagram_payload(text="our reply", mid="mid.ECHO2", is_echo=True)
    real = instagram_payload(text="Сколько стоит стрижка?", mid="mid.REAL3")
    payload = {"object": "instagram", "entry": echoed["entry"] + real["entry"]}

    result = normalise(payload)

    assert isinstance(result, NormalisedEvent)
    assert result.external_id == "mid.REAL3"


def test_when_nothing_actionable_exists_the_first_skip_reason_is_reported():
    payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_ACCOUNT_ID",
                "messaging": [
                    {
                        "sender": {"id": "IG_ACCOUNT_ID"},
                        "recipient": {"id": "IGSID_CLIENT"},
                        "message": {"mid": "mid.ECHO3", "text": "our reply", "is_echo": True},
                    },
                    {
                        "sender": {"id": "IGSID_CLIENT"},
                        "recipient": {"id": "IG_ACCOUNT_ID"},
                        "message": {"mid": "mid.STICKER2", "attachments": [{"type": "image"}]},
                    },
                ],
            }
        ],
    }

    result = normalise(payload)

    assert isinstance(result, SkippedEvent)
    assert result.reason == SKIP_ECHO, "the first skip encountered is the one reported"
    assert result.external_id == "mid.ECHO3"
