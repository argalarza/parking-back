from typing import Protocol
from uuid import UUID


class PersonRepository(Protocol):
    def create_person(self, dni: str, name: str, last_names: str) -> UUID: ...
