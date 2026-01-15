"""
Definición del modelo de Usuario.
"""

class User:
    """
    Representación de un usuario para Firestore (NoSQL).
    """
    def __init__(self, username: str, hashed_password: str, is_active: bool = True, score: int = 0):
        self.username = username
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.score = score

    def to_dict(self):
        """
        Serializa el objeto User a un diccionario para Firestore.
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
        Deserializa un diccionario de Firestore a un objeto User.
        """
        return User(
            username=data.get("username"),
            hashed_password=data.get("hashed_password"),
            is_active=data.get("is_active", True),
            score=data.get("score", 0)
        )
