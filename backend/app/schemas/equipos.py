from pydantic import BaseModel, ConfigDict


class ComisionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: str
    materia_nombre: str
    cohorte_id: str
    cohorte_nombre: str
    rol: str
