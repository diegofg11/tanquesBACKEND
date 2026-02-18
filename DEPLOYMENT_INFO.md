# 🌐 Información de Despliegue: Backend y Dashboard

Este documento resume las direcciones de acceso al servidor de producción y cómo acceder al panel de administración.

## 1. Dirección del Backend (API)
El backend está desplegado en **Render**. Esta es la URL base para todas las peticiones de la API (Login, Registro, Puntuaciones, etc.).

- **URL Base:** `https://tanques-api.onrender.com`
- **Estado:** ✅ Activo (Capa Gratuita)

### 📍 Configuración en Unity
En el proyecto de Unity (`tanques_potter`), la dirección se define en:
- **Archivo:** `Assets/MisScripts/Core/AppConfig.cs`
- **Variable:** `CLOUD_URL`

---

## 2. Dashboard de Métricas
El dashboard es una interfaz web visual para ver estadísticas de juego, usuarios registrados y actividad en tiempo real.

- **URL de Acceso:** `https://tanques-api.onrender.com/dashboard`
- **Características:**
  - Estadísticas Globales (Total usuarios, partidas).
  - Actividad Reciente (Gráficos).
  - Ranking en vivo.
  
### 📍 Configuración en Backend
En este proyecto (`tanquesBACKEND`), la ruta se sirve como un archivo estático HTML:
- **Archivo:** `app/main.py`
- **Ruta:** `/dashboard`

---

> [!IMPORTANT]
> **Nota sobre Render (Capa Gratuita):**
> Al usar el plan gratuito de Render, el servicio entra en "suspensión" tras 15 minutos de inactividad.
> 
> *   **Primera petición:** Puede tardar entre **30 y 50 segundos** en responder mientras el servidor "despierta".
> *   **Peticiones siguientes:** Respuesta inmediata.
