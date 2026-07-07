from pydantic import BaseModel, Field


class PersonCreateRequest(BaseModel):
    dni: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    last_names: str = Field(..., min_length=1)
