from pydantic import BaseModel, Field

# Me creo este "Filtro" (o Contrato) para no tener sustos con los datos.
# Me aseguro de que cada tanque mande exactamente lo que yo espero.
class TankState(BaseModel):
    """
    Aquí defino los datos que espero recibir de cada tanque.
    Si me falta algo o me mandan basura, Pydantic me avisará.
    """
    x: int = Field(..., description="Posición horizontal en mi mapa")
    y: int = Field(..., description="Posición vertical en mi mapa")
    
    # Restrinjo la rotación entre 0 y 360 para que no me pasen cosas raras.
    rotacion: int = Field(..., ge=0, le=360, description="Grados de rotación")
    
    # La vida tiene que estar entre 0 y 100 sí o sí.
    vida: int = Field(..., ge=0, le=100, description="Porcentaje de salud")

    # Esto me sirve para que en la documentación (/docs) se vea un ejemplo real.
    class Config:
        schema_extra = {
            "example": {
                "x": 100,
                "y": 200,
                "rotacion": 90,
                "vida": 100
            }
        }
