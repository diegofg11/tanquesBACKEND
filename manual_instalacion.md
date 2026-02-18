# 🛠️ Manual de Despliegue Local (Desde GitHub) - Arcane Beasts Arena

Esta guía está dirigida a desarrolladores o colaboradores que han descargado el código fuente desde GitHub y desean ejecutar el proyecto en su entorno local.

## 📋 Requisitos Previos

*   **Git:** ([Descargar](https://git-scm.com/downloads)) Para clonar el repositorio.
*   **Python:** Versión 3.10 o superior. ([Descargar](https://www.python.org/downloads/)) - Asegúrate de marcar "Add Python to PATH" durante la instalación.
*   **Unity Hub y Editor:** Versión **2022.3 LTS** (o la indicada en `ProjectSettings/ProjectVersion.txt`).
*   **Credenciales de Firebase (`firebase-key.json`):**
    *   ⚠️ **IMPORTANTE:** Este archivo contiene claves secretas y **NO está incluido en el repositorio** por seguridad.
    *   Debes solicitar este archivo al administrador del proyecto o profesor responsable.
    *   Sin él, el backend no funcionará.

---

## 📥 1. Clonar el Repositorio

Abre una terminal en la carpeta donde quieras guardar el proyecto y ejecuta:

```bash
git clone <URL_DEL_REPOSITORIO>
cd Tanques
```

*(La estructura del proyecto debería contener las carpetas `tanquesBACKEND` y `tanques_potter`)*.

---

## 🚀 2. Configuración del Backend (API)

### 2.1 Colocar Credenciales
1.  Navega a la carpeta `tanquesBACKEND`.
2.  **Paso Crítico:** Toma el archivo `firebase-key.json` que te han entregado por separado y pégalo **en la raíz** de esta carpeta.
    *   Ruta final esperada: `.../Tanques/tanquesBACKEND/firebase-key.json`
    
    > *Nota: Git ignorará este archivo automáticamente para evitar que se suba al repositorio por accidente.*

### 2.2 Entorno Virtual e Instalación

Abre una terminal (CMD o PowerShell) en `tanquesBACKEND` y ejecuta los siguientes comandos en orden:

1.  **Crear el entorno virtual:**
    ```bash
    python -m venv venv
    ```

2.  **Activar el entorno:**
    *   **Windows:** `venv\Scripts\activate`
    *   **Mac/Linux:** `source venv/bin/activate`
    
    *(Verás `(venv)` al inicio de tu línea de comandos)*.

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### 2.3 Ejecutar el Servidor
Con el entorno activado, lanza el servidor localmente:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> ✅ **Verificación:** Abre [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Deberías ver la documentación Swagger de la API. Mantén esta terminal abierta.

---

## 🎮 3. Configuración de Unity (Cliente)

### 3.1 Abrir el Proyecto
1.  Abre **Unity Hub**.
2.  Haz clic en **Add** (Añadir) y selecciona la carpeta `tanques_potter` dentro del repositorio clonado.
3.  Abre el proyecto (esto puede tardar unos minutos la primera vez mientras importa assets).

### 3.2 Conectar a LocalHost
Por defecto, el juego está configurado para la nube. Para usar tu servidor local:

1.  En Unity, ve a leer carpeta: `Assets > MisScripts > Core`.
2.  Abre el script **`AppConfig.cs`**.
3.  Localiza `USE_CLOUD_SERVER` y cámbialo a `false`:

    ```csharp
    // AppConfig.cs
    public const bool USE_CLOUD_SERVER = false; 
    ```
4.  Guarda (`Ctrl + S`) y vuelve a Unity.

---

## 🧪 4. Cómo Probar

1.  Verifica que el **Backend** corre en el puerto 8000.
2.  En Unity, abre la escena **MenuInicial**.
3.  Dale al botón ▶️ **Play**.
4.  Intenta registrar un usuario:
    *   Si funciona, recibirás un "Registro OK".
    *   Si falla, revisa la consola del backend.

---

## ❓ Solución de Problemas

*   **Error "No se encontraron credenciales válidas":**
    *   El archivo `firebase-key.json` no está en la carpeta `tanquesBACKEND` o tiene otro nombre.
*   **`ModuleNotFoundError`:**
    *   Activa el entorno virtual (`venv`) antes de ejecutar.
*   **Unity no conecta:**
    *   Asegúrate de haber guardado el cambio en `AppConfig.cs`.
