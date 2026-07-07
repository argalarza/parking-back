from app.modules.persons.application.ports import PersonRepository


class CreatePersonUseCase:
    def __init__(self, repository: PersonRepository) -> None:
        self._repository = repository

    def execute(self, dni: str, name: str, last_names: str) -> dict:
        person_id = self._repository.create_person(dni=dni, name=name, last_names=last_names)
        return {
            "success": True,
            "message": "Persona creada correctamente.",
            "id": person_id,
        }
