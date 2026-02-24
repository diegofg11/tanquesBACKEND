# Arcane Beasts Arena - Backend

Servidor backend para **Arcane Beasts Arena**, un juego de tanques desarrollado por **Nizam, Marco y Diego**. Este repositorio, construido con **FastAPI** y **Firebase**, gestiona la infraestructura central del juego, incluyendo la autenticación, el sistema de ranking y la seguridad de las partidas.

## 🚀 Características Principales

- **Gestión de Usuarios**: Registro e inicio de sesión seguro para los jugadores.
- **Sistema de Ranking**: Top 10 de mejores puntuaciones global en tiempo real.
- **Seguridad (Anti-Cheat)**: Generación y validación de tokens de juego para proteger la integridad de las puntuaciones.
- **Integración con Firebase**: Persistencia de datos de perfil, estadísticas e historial de partidas.
- **API Documentada**: Documentación interactiva automática a través de Swagger UI.

## 🛠️ Tecnologías

- **Lenguaje**: Python 3.9+
- **Framework**: FastAPI
- **Servidor**: Uvicorn
- **Base de Datos**: Firebase Firestore (NoSQL)
- **Seguridad**: JWT (JSON Web Tokens) y Hashing de contraseñas (BCrypt)

## 💻 Instalación y Uso Local

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd tanquesBACKEND
   ```

2. **Entorno Virtual**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Lanzar Servidor**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Accede a la API en `http://127.0.0.1:8000` y a la documentación en `/docs`.

## 📂 Estructura y Configuración

- `app/`: Lógica principal del backend.
- `firebase-key.json`: Archivo con las credenciales de Firebase (necesario para el funcionamiento).
- `requirements.txt`: Dependencias del proyecto.
- `Procfile`: Configuración para despliegue en la nube (Render/Heroku).

## 🤝 Créditos

Este proyecto ha sido desarrollado por:
- **Nizam**
- **Marco**
- **Diego**

---
*Proyecto Ret 4 DAM - Arcane Beasts Arena*
