from pydantic import BaseModel, Field

# Pydantic es como un "Filtro" o "Contrato". 
# Obliga a que los datos tengan un tipo y un formato específico.
class TankState(BaseModel):
    """
    Define exactamente qué datos esperamos de un tanque.
    Si falta uno o el tipo es incorrecto, Pydantic lanzará un error.
    """
    x: int = Field(..., description="Posición horizontal en el mapa")
    y: int = Field(..., description="Posición vertical en el mapa")
    
    # ge=0 (Greater or Equal) y le=360 (Less or Equal)
    rotacion: int = Field(..., ge=0, le=360, description="Grados de rotación")
    
    vida: int = Field(..., ge=0, le=100, description="Porcentaje de vida")

    # Esta clase interna ayuda a generar documentación automática y ejemplos.
    class Config:
        schema_extra = {
            "example": {
                "x": 100,
                "y": 200,
                "rotacion": 90,
                "vida": 100
            }
        }
