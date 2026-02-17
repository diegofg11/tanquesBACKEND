# 🛡️ Sistema de Auditoría - Tanques Backend

Este documento detalla el funcionamiento, arquitectura y uso del sistema de auditoría implementado en el backend de Tanques. El sistema permite registrar acciones clave de los usuarios, así como exportar e importar estos historiales.

## 🏗️ Arquitectura

El sistema utiliza una **Arquitectura de Persistencia Políglota**:
- **Firebase Firestore**: Se mantiene como base de datos principal para el juego (tiempo real).
- **SQLite (SQLAlchemy)**: Se utiliza exclusivamente para el registro de auditoría, garantizando que los logs sean estructurados, relacionales y fáciles de exportar.

### Componentes Clave

1.  **Base de Datos (`app/db_sql.py`)**: Configura la conexión a una base de datos SQLite local (`audit.db`).
2.  **Modelo (`app/models/audit.py`)**: Define la estructura de la tabla `audits` (ID, usuario, acción, fecha).
3.  **Servicio (`app/services/audit_service.py`)**: Contiene la lógica de negocio para registrar acciones, y procesar archivos CSV/JSON.
4.  **API (`app/api/audit.py`)**: Expone endpoints para consultar y gestionar los logs.
5.  **Inyección (`app/api/users.py`)**: Integra sutilmente el registro de logs en los endpoints existentes de Firebase.

---

## 🚀 Funcionalidad

### Registro Automático
El sistema captura automáticamente las siguientes acciones sin intervención del usuario:
- **User Registered**: Cuando un usuario se da de alta.
- **User Login**: Cuando un usuario inicia sesión.
- **Game Started**: Cuando un usuario pide un token para jugar.
- **Score Submitted**: Cuando un usuario envía una puntuación.

### Exportación e Importación
El sistema permite extraer e inyectar datos para backups o análisis externo.

#### Exportar
- **CSV**: Descarga un archivo compatible con Excel/Sheets.
- **JSON**: Descarga un archivo estructurado para uso programático.

#### Importar
- Permite subir archivos CSV o JSON previamente exportados para restaurar historial o migrar datos de otro entorno.

---

## 🔌 API Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/audits/` | Lista las últimas auditorías (paginado). |
| `GET` | `/audits/export/csv` | Descarga el historial completo en CSV. |
| `GET` | `/audits/export/json` | Descarga el historial completo en JSON. |
| `POST` | `/audits/import/csv` | Sube un archivo CSV para importar registros. |
| `POST` | `/audits/import/json` | Sube un archivo JSON para importar registros. |

---

## 🛠️ Tecnologías

- **SQLAlchemy**: ORM para gestión de base de datos SQL.
- **Pydantic**: Validación de esquemas de datos.
- **FastAPI Dependency Injection**: Gestión eficiente de sesiones de base de datos.
- **CSV/JSON libs**: Manejo nativo de formatos de archivo.
