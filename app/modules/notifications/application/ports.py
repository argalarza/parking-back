from typing import Protocol


class EmailSender(Protocol):
    def send_email(self, to: str, subject: str, html: str) -> None: ...
