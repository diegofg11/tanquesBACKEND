# Documentación de Cumplimiento de Requisitos (ADAT)

Este documento justifica cómo el proyecto **Arcane Beasts Arena (Backend)** cumple con los requisitos técnicos exigidos para la asignatura de Acceso a Datos.

---

## 1. Despliegue y Accesibilidad
**Requisito:** *El backend (API) está desplegado y accesible de forma estable.*

*   **Implementación:**
    *   La aplicación está construida con **FastAPI** y preparada para despliegue en la nube (Render/Heroku/Railway).
    *   Se incluye un archivo `Procfile` para la gestión de procesos en entornos de producción.
    *   La configuración de puerto y host es dinámica, permitiendo adaptarse al entorno de despliegue.

## 2. Documentación OpenAPI / Swagger
**Requisito:** *OpenAPI / Swagger funciona y permite probar los endpoints.*

*   **Implementación:**
    *   **Archivo:** `app/main.py`
    *   **Detalle:** FastAPI genera automáticamente la documentación interactiva.
    *   **Acceso:**
        *   Swagger UI: `/docs` (Personalizado para evitar problemas de CDN).
        *   ReDoc: `/redoc`
    *   **Evidencia en código:**
        ```python
        # app/main.py
        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html(): ...
        ```

## 3. Persistencia de Datos (Firestore)
**Requisito:** *Los datos persisten en Firestore (u otra BD justificada), no en memoria.*

*   **Implementación:**
    *   **Archivo:** `app/database.py`
    *   **Motor:** Google Firebase Firestore (NoSQL).
    *   **Conexión:** Se realiza mediante el SDK `firebase-admin`.
    *   **Seguridad:** Las credenciales se cargan de forma segura desde variables de entorno (`FIREBASE_CREDENTIALS`) en producción o archivo JSON local en desarrollo.
    *   **Evidencia:** No se utilizan listas o diccionarios globales para almacenar datos críticos; todo se lee y escribe en las colecciones `users`, `scores` y `events`.

## 4. Flujo Completo de Juego
**Requisito:** *Existe un flujo mínimo completo: jugador → partida → eventos → estadísticas.*

*   **Implementación:**
    1.  **Jugador:** Registro e inicio de sesión (`UserService.register_user`, `UserService.authenticate_user`).
    2.  **Partida:** Inicio de sesión de juego (`ScoreService.create_game_token`) que genera un JWT único para la partida.
    3.  **Eventos:** Registro de acciones durante el juego (`EventService.log_event`), como daño recibido o enemigos eliminados.
    4.  **Estadísticas:** Envío de puntuación final (`ScoreService.submit_score`), que valida la partida y actualiza los rankings.

## 5. Registro de Eventos y Métricas Derivadas
**Requisito:** *El backend registra eventos del juego y genera métricas/estadísticas derivadas.*

*   **Implementación:**
    *   **Servicio:** `EventService` (`app/services/event_service.py`)
    *   **Funcionalidad:**
        *   Endpoint `/events/log` recibe eventos crudos (`ENEMY_KILLED`, `LEVEL_START`, etc.).
        *   El Dashboard (`DashboardService`) agrega estos datos para mostrar "Actividad Reciente" y "Muro de Actividad" en tiempo real.
    *   **Métricas Derivadas:**
        *   Promedio de nivel de jugadores.
        *   Distribución de partidas por hora/día.
        *   Récords diarios y globales calculados al vuelo desde los datos brutos.

## 6. Lógica en el Backend (Anti-Cheat)
**Requisito:** *El backend calcula la lógica y las métricas clave (el cliente no “piensa”).*

*   **Implementación:**
    *   **Archivo:** `app/services/score_service.py`
    *   **Cálculo de Score:** El cliente envía "tiempo" y "daño", pero es el servidor quien aplica la fórmula matemática:
        ```python
        score_final = puntos_base - (tiempo * 2) - (daño * 5)
        ```
    *   **Sanity Check:** El método `_sanity_check` verifica si el tiempo enviado es humanamente posible para el nivel. Si es sospechoso, aplica penalizaciones o marca la partida, evitando que clientes modificados rompan el ranking.

## 7. Dashboard con Datos Reales
**Requisito:** *El dashboard muestra datos reales y se actualiza a partir del backend.*

*   **Implementación:**
    *   **Backend:** `app/services/dashboard_service.py` realiza consultas de agregación complejas en Firestore para servir datos consolidados.
    *   **Frontend:** `static/dashboard/index.html` consume la API REST (`/api/dashboard/stats`).
    *   **Veracidad:** No hay datos "mockeados"; si se borra la base de datos, el dashboard queda vacío. Si se juega una partida, el dashboard se actualiza al instante.

## 8. Seguridad y Acceso Indirecto a BD
**Requisito:** *El cliente no accede directamente a la base de datos; todo pasa por la API.*

*   **Implementación:**
    *   **Arquitectura:** Cliente Unity y Dashboard Web -> API Gateway (FastAPI) -> Servicios -> Firestore.
    *   **Seguridad:** Las credenciales de Firebase nunca viajan al cliente. El cliente se autentica con JWT (Json Web Tokens).

## 9. Capa de Acceso a Datos (Arquitectura Limpia)
**Requisito:** *Existe una capa clara de acceso a datos (repository / service / similar).*

*   **Implementación:**
    *   **Estructura del Proyecto:**
        *   `app/api/`: Controladores (Endpoints HTTP).
        *   `app/schemas/`: DTOs (Data Transfer Objects) para entrada/salida.
        *   `app/services/`: **Lógica de Negocio y Acceso a Datos**. Aquí se encapsulan todas las llamadas a `firestore.client()`.
    *   **Beneficio:** Si mañana cambiáramos Firestore por SQL, solo habría que modificar la carpeta `services/`, sin tocar los controladores.

## 10. Validación de Datos (Robustez)
**Requisito:** *El backend valida los datos de entrada y no confía en el cliente.*

*   **Implementación:**
    *   **Herramienta:** **Pydantic**.
    *   **Archivo:** `app/schemas/` (ej. `user.py`, `event.py`).
    *   **Funcionamiento:** Cualquier dato que entra a la API es validado estrictamente (tipos, campos obligatorios, longitud). Si el cliente envía datos mal formados, la API responde con `422 Unprocessable Entity` automáticamente, protegiendo la lógica interna.

## 11. Logs y Monitorización
**Requisito:** *Existen logs útiles para errores y eventos relevantes.*

*   **Implementación:**
    *   **Archivo:** `app/core/logger.py`
    *   **Uso:** Se ha sustituido `print()` por un logger estructurado estándar de Python.
    *   **Eventos Registrados:** Inicio de servidor, errores de conexión a BD, intentos de login fallidos (Seguridad), registros de cheat detectados y excepciones no controladas.
