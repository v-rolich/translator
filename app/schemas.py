from typing import Optional

from pydantic import BaseModel, field_validator, ConfigDict, BeforeValidator
from typing_extensions import Annotated


PyObjectId = Annotated[str, BeforeValidator(str)]


class WordInfo(BaseModel):
    """
    Container for a single word record.
    """
    word: str
    translations: Optional[list[str]]
    definitions: Optional[list[str]]
    synonyms: Optional[list[str]]
    examples: Optional[list[str]]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "word": "Application",
                "translations": ["la aplicación", "la solicitud", "la petición"],
                "definitions": [
                    "a formal request to an authority for something.",
                    "the action of putting something into operation.",
                    "the action of putting something on a surface.",
                ],
                "synonyms": ["request", "implementation", "putting on"],
                "examples": [
                    "una solicitud para ingresar en el cuerpo de bomberos",
                    "Cualidad de la persona solícita o dispuesta a servir y satisfacer a los demás.",
                    "Acción de solicitar algo.",
                ],
            }]
        })
