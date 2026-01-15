# Guía de Conexión: Unity -> Backend (Python + Firebase)

Este documento sirve como referencia para conectar tu proyecto de Unity con este Backend.
**Mantén este archivo actualizado si cambias nombres de variables o rutas en la API.**

---

## 1. Configuración Básica

### URLs del Servidor
*   **Local (Tu PC):** `http://127.0.0.1:8000`
*   **Nube (Futuro):** *Aquí pondrás la URL cuando lo subas a Render/Heroku*

### Librerías Necesarias en Unity
*   **JsonUtility** (Viene con Unity): Para convertir objetos a texto y viceversa.
*   **UnityWebRequest** (Viene con Unity): Para todas las peticiones (Login, Ranking).

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
public class ScoreSubmission
{
    public int tiempo_segundos;
    public int daño_recibido;
    public int nivel_alcanzado; // 1, 2, o 3
}

[Serializable]
public class RankingItem
{
    public string username;
    public int score;
}
```

---

## 3. Ejemplos de Scripts (GameManager.cs)

### A. Login y Registro

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

### B. Enviar Puntuación (Al terminar)

```csharp
IEnumerator SubmitScore(string username, int tiempo, int daño, int nivel)
{
    string url = baseUrl + "/users/" + username + "/submit-score";
    
    ScoreSubmission data = new ScoreSubmission 
    { 
        tiempo_segundos = tiempo, 
        daño_recibido = daño, 
        nivel_alcanzado = nivel 
    };
    
    string jsonData = JsonUtility.ToJson(data);
    var request = new UnityWebRequest(url, "POST");
    byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
    request.uploadHandler = new UploadHandlerRaw(bodyRaw);
    request.downloadHandler = new DownloadHandlerBuffer();
    request.SetRequestHeader("Content-Type", "application/json");

    yield return request.SendWebRequest();
    
    if (request.result == UnityWebRequest.Result.Success)
    {
       Debug.Log("Puntos enviados: " + request.downloadHandler.text);
    }
}
```

---

## 4. Sistema de Ranking

### A. Estructuras de Datos (Ranking)

```csharp
[Serializable]
public class ScoreSubmission
{
    public int tiempo_segundos;
    public int daño_recibido;
    public int nivel_alcanzado; // 1, 2, o 3
}

[Serializable]
public class RankingItem
{
    public string username;
    public int score;
}
```

### B. Ejemplo: Enviar Puntuación (Al terminar partida)

```csharp
// Método dentro de tu BackendConnector.cs o GameManager.cs
IEnumerator SubmitScore(string username, int tiempo, int daño, int nivel)
{
    string url = baseUrl + "/users/" + username + "/submit-score";
    
    ScoreSubmission data = new ScoreSubmission 
    { 
        tiempo_segundos = tiempo, 
        daño_recibido = daño, 
        nivel_alcanzado = nivel 
    };
    
    // ... Creación de UnityWebRequest igual que el Login ...
    // ... SendWebRequest() ...
}
```
```
