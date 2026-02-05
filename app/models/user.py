"""
Definición del modelo de dominio para el Usuario.
"""

class User:
    """
    Representación de un usuario en el sistema.
    
    Esta clase maneja la estructura de datos que se almacena en Firestore,
    incluyendo credenciales y estadísticas básicas.
    """
    def __init__(self, username: str, hashed_password: str, is_active: bool = True, score: int = 0):
        """
        Inicializa una nueva instancia de User.
        """
        self.username = username
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.score = score

    def to_dict(self):
        """
        Serializa el objeto User a un diccionario compatible con Firestore.
        
        Returns:
            dict: Representación en diccionario del usuario.
        """
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "score": self.score
        }

    @staticmethod
    def from_dict(data: dict):
        """
        Deserializa un diccionario de Firestore para crear un objeto User.
        
        Args:
            data (dict): Datos provenientes de Firestore.
            
        Returns:
            User: Una instancia de la clase User poblada con los datos del dict.
        """
        return User(
            username=data.get("username"),
            hashed_password=data.get("hashed_password"),
            is_active=data.get("is_active", True),
            score=data.get("score", 0)
        )
