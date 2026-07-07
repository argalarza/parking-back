from paho.mqtt import publish


class MqttAccessControlGateway:
    def __init__(self, broker: str, port: int) -> None:
        self._broker = broker
        self._port = port

    def grant_access(self, topic: str) -> None:
        self._publish(topic=topic, payload="abrir")

    def deny_access(self, topic: str) -> None:
        self._publish(topic=topic, payload="denegado")

    def _publish(self, topic: str, payload: str) -> None:
        publish.single(
            topic=topic,
            payload=payload,
            hostname=self._broker,
            port=self._port,
        )
