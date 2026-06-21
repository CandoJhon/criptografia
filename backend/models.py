from pydantic import BaseModel, Field
from typing import Literal


class PasswordRequest(BaseModel):
    """
    Esquema de validación para la solicitud de generación de contraseña.
    
    Atributos:
        length: Longitud de la contraseña (8 a 128 caracteres)
        useUppercase: Incluir mayúsculas (A-Z)
        useLowercase: Incluir minúsculas (a-z)
        useDigits: Incluir dígitos (0-9)
        useSymbols: Incluir símbolos ASCII imprimibles
        excludeAmbiguous: Excluir caracteres ambiguos (i, l, 1, L, o, 0, O, etc.)
    """
    length: int = Field(
        default=16,
        ge=8,
        le=128,
        description="Longitud de la contraseña"
    )
    useUppercase: bool = Field(
        default=True,
        description="Incluir mayúsculas"
    )
    useLowercase: bool = Field(
        default=True,
        description="Incluir minúsculas"
    )
    useDigits: bool = Field(
        default=True,
        description="Incluir dígitos"
    )
    useSymbols: bool = Field(
        default=True,
        description="Incluir símbolos"
    )
    excludeAmbiguous: bool = Field(
        default=False,
        description="Excluir caracteres ambiguos"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "length": 20,
                "useUppercase": True,
                "useLowercase": True,
                "useDigits": True,
                "useSymbols": True,
                "excludeAmbiguous": False
            }
        }


class PasswordResponse(BaseModel):
    """
    Esquema de respuesta con la contraseña generada y métricas de fuerza.
    
    Atributos:
        password: La contraseña generada
        length: Longitud de la contraseña
        entropyBits: Entropía en bits (H = L * log2(N))
        strength: Clasificación de fortaleza (very_weak, weak, reasonable, strong, very_strong)
        alphabetSize: Tamaño del alfabeto utilizado
    """
    password: str = Field(
        ...,
        description="Contraseña generada de forma segura"
    )
    length: int = Field(
        ...,
        description="Longitud de la contraseña"
    )
    entropyBits: float = Field(
        ...,
        description="Entropía en bits según H = L * log2(N)"
    )
    strength: Literal[
        "very_weak",
        "weak",
        "reasonable",
        "strong",
        "very_strong"
    ] = Field(
        ...,
        description="Clasificación de fortaleza"
    )
    alphabetSize: int = Field(
        ...,
        description="Tamaño del alfabeto utilizado"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "password": "k7$Wm2#qPxR9!nL4vB&t",
                "length": 20,
                "entropyBits": 131.1,
                "strength": "very_strong",
                "alphabetSize": 94
            }
        }


class ErrorResponse(BaseModel):
    """
    Esquema de respuesta para errores HTTP.
    
    Atributos:
        detail: Descripción del error
        status_code: Código HTTP del error
    """
    detail: str = Field(
        ...,
        description="Descripción del error"
    )
    status_code: int = Field(
        ...,
        description="Código HTTP"
    )