from app.integrations.gateway import (
    BaseConnector,
    CapabilityRegistry,
    ConnectorGateway,
    EventBus,
    IntegrationEvent,
    IntegrationRegistry,
)


class DummyConnector(BaseConnector):
    integration_name = "dummy"

    @property
    def capabilities(self) -> set[str]:
        return {"dummy.echo"}

    def execute(self, capability: str, *, payload: dict | None = None):
        if capability != "dummy.echo":
            raise ValueError("Unsupported capability")
        data = payload or {}
        return data.get("value")


def test_integration_registry_register_and_get():
    registry = IntegrationRegistry()
    connector = DummyConnector()

    registry.register(connector)

    assert registry.get("dummy") is connector
    assert registry.list_names() == ["dummy"]


def test_capability_registry_supports_lookup():
    registry = CapabilityRegistry()

    registry.register("dummy", "dummy.echo")

    assert registry.supports("dummy", "dummy.echo")
    assert registry.get_integrations("dummy.echo") == ["dummy"]


def test_event_bus_wildcard_subscription_receives_event():
    bus = EventBus()
    received = []

    def _handler(event: IntegrationEvent):
        received.append(event.name)

    bus.subscribe("*", _handler)
    bus.publish(IntegrationEvent(name="sample.event", source="unit-test"))

    assert received == ["sample.event"]


def test_gateway_executes_capability_and_publishes_events():
    gateway = ConnectorGateway()
    connector = DummyConnector()
    events = []

    def _handler(event: IntegrationEvent):
        events.append(event.name)

    gateway.event_bus.subscribe("*", _handler)
    gateway.register(connector)

    result = gateway.execute("dummy", "dummy.echo", payload={"value": "ok"})

    assert result == "ok"
    assert "integration.registered" in events
    assert "integration.request" in events
    assert "integration.request_succeeded" in events
