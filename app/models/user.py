# He quitado SQLAlchemy porque ahora usamos Firestore (NoSQL).
# En Firestore, los datos se guardan como documentos (como JSON/Diccionarios).

class User:
    """
    Esta clase representa a un usuario en mi juego.
    Ya no es una tabla rígida de SQL, es mi guía para saber qué tiene cada usuario.
    """
    def __init__(self, username: str, hashed_password: str, is_active: bool = True, score: int = 0):
        self.username = username
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.score = score

    def to_dict(self):
        """
        Convierto el objeto a un diccionario para guardarlo fácil en Firestore.
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
        Creo un objeto User a partir de lo que me devuelva Firebase.
        """
        return User(
            username=data.get("username"),
            hashed_password=data.get("hashed_password"),
            is_active=data.get("is_active", True),
            score=data.get("score", 0)
        )
