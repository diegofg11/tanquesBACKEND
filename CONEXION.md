# Guía de Conexión: Unity -> Backend (Python + Firebase)

Este documento sirve como referencia para conectar tu proyecto de Unity con este Backend.
**Mantén este archivo actualizado si cambias nombres de variables o rutas en la API.**

---

## 1. Configuración Básica

### URLs del Servidor
*   **Local (Tu PC):** `http://127.0.0.1:8000`
*   **WebSocket Local:** `ws://127.0.0.1:8000/ws/game/{SALA}/{USUARIO}`
*   **Nube (Futuro):** *Aquí pondrás la URL cuando lo subas a Render/Heroku*

### Librerías Necesarias en Unity
*   **JsonUtility** (Viene con Unity): Para convertir objetos a texto y viceversa.
*   **UnityWebRequest** (Viene con Unity): Para Login/Registro.
*   **NativeWebSocket** (Descargar de GitHub): Necesaria porque los WebSockets de Unity por defecto son limitados.
    *   *Link:* https://github.com/endel/NativeWebSocket

---

## 2. Estructuras de Datos (C#)

Copia estas clases en tu proyecto de Unity para que coincidan con el Backend.

```csharp
using System;

[Serializable]
public class UserLoginData
{
    public string username;
    public string password;
}

[Serializable]
public class UserResponse
{
    public string username;
    public bool is_active;
    public int score;
}

[Serializable]
public class TankState
{
    public int x;
    public int y;
    public int rotacion;
    public int vida;
}

[Serializable]
public class GameMessage
{
    public string tipo;      // "movimiento", "sistema", etc.
    public string jugador;   // Nombre del usuario que manda el dato
    public TankState datos;  // Sus coordenadas
    public string contenido; // Solo para mensajes de texto (sistema)
}
```

---

## 3. Ejemplo de Script de Conexión (GameManager.cs)

### A. Login y Registro (HTTP)

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

public class BackendConnector : MonoBehaviour
{
    private string baseUrl = "http://127.0.0.1:8000";

    public void IntentarLogin(string user, string pass)
    {
        StartCoroutine(SendLoginRequest(user, pass));
    }

    IEnumerator SendLoginRequest(string username, string password)
    {
        string url = baseUrl + "/users/login";
        
        // 1. Crear el JSON
        UserLoginData data = new UserLoginData { username = username, password = password };
        string jsonData = JsonUtility.ToJson(data);

        // 2. Configurar la petición
        var request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        // 3. Enviar y Esperar
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Login OK: " + request.downloadHandler.text);
            // AQUÍ: Guardar el username y cambiar a la escena de juego
        }
        else
        {
            Debug.LogError("Error Login: " + request.error + " | " + request.downloadHandler.text);
        }
    }
}
```

### B. Juego en Tiempo Real (WebSockets)

```csharp
using UnityEngine;
using NativeWebSocket;

public class GameNetwork : MonoBehaviour
{
    WebSocket websocket;
    public string roomId = "Sala1";
    public string myUsername = "Player1"; // Esto vendría del Login

    async void Start()
    {
        // Conexión
        string url = $"ws://127.0.0.1:8000/ws/game/{roomId}/{myUsername}";
        websocket = new WebSocket(url);

        websocket.OnOpen += () => Debug.Log("Conectado al servidor!");
        websocket.OnError += (e) => Debug.Log("Error: " + e);
        websocket.OnClose += (e) => Debug.Log("Desconectado");

        websocket.OnMessage += (bytes) =>
        {
            // RECIBIR DATOS
            string message = System.Text.Encoding.UTF8.GetString(bytes);
            GameMessage msg = JsonUtility.FromJson<GameMessage>(message);

            if (msg.tipo == "movimiento" && msg.jugador != myUsername)
            {
                Debug.Log($"El jugador {msg.jugador} se ha movido a {msg.datos.x}, {msg.datos.y}");
                // AQUÍ: Actualizar la posición del objeto Unity enemigo
            }
        };

        await websocket.Connect();
    }

    void Update()
    {
        #if !UNITY_WEBGL || UNITY_EDITOR
            websocket.DispatchMessageQueue();
        #endif
        
        // ENVIAR MOVIMIENTO (Ejemplo simple)
        if (Input.GetKeyDown(KeyCode.Space)) 
        {
            TankState miEstado = new TankState { x = 10, y = 10, rotacion = 90, vida = 100 };
            SendState(miEstado);
        }
    }

    async void SendState(TankState state)
    {
        if (websocket.State == WebSocketState.Open)
        {
            string json = JsonUtility.ToJson(state);
            await websocket.SendText(json);
        }
    }

    private async void OnApplicationQuit()
    {
        await websocket.Close();
    }
}
```
