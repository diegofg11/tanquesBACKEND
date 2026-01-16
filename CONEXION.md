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
    public string game_token;   // NUEVO: Token de seguridad
}

[Serializable]
public class RankingItem
{
    public string username;
    public int score;
}

[Serializable]
public class GameTokenResponse
{
    public string game_token;
}
```

---

## 3. Ejemplos de Scripts (GameManager.cs)

### A. Login y Registro

*(Igual que antes...)*

### B. Flujo de Juego Seguro (Anti-Trampas)

**IMPORTANTE:** Ahora debes pedir un token al empezar la partida y enviarlo al final.

```csharp
private string currentGameToken; // Guardar aquí el token

// 1. Llamar al EMPEZAR la partida
public void EmpezarPartida(string username)
{
    StartCoroutine(GetGameToken(username));
}

IEnumerator GetGameToken(string username)
{
    string url = baseUrl + "/users/" + username + "/start-game";
    
    var request = new UnityWebRequest(url, "POST");
    request.downloadHandler = new DownloadHandlerBuffer();
    
    yield return request.SendWebRequest();

    if (request.result == UnityWebRequest.Result.Success)
    {
        // Parsear respuesta
        GameTokenResponse res = JsonUtility.FromJson<GameTokenResponse>(request.downloadHandler.text);
        currentGameToken = res.game_token;
        Debug.Log("Token recibido: " + currentGameToken);
    }
    else
    {
        Debug.LogError("Error consiguiendo token: " + request.error);
    }
}

// 2. Llamar al TERMINAR la partida
public void TerminarPartida(string username, int tiempo, int daño, int nivel) 
{
    if(string.IsNullOrEmpty(currentGameToken)) 
    {
        Debug.LogError("No tienes token! ¿Llamaste a EmpezarPartida?");
        return;
    }
    StartCoroutine(SubmitScore(username, tiempo, daño, nivel));
}

IEnumerator SubmitScore(string username, int tiempo, int daño, int nivel)
{
    string url = baseUrl + "/users/" + username + "/submit-score";
    
    ScoreSubmission data = new ScoreSubmission 
    { 
        tiempo_segundos = tiempo, 
        daño_recibido = daño, 
        nivel_alcanzado = nivel,
        game_token = currentGameToken // ENVIAMOS EL TOKEN
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
       currentGameToken = null; // Resetear token usado
    }
    else
    {
       Debug.LogError("Error enviando puntos: " + request.downloadHandler.text);
    }
}
```

### C. Obtener Mi Perfil (Récord)

Útil para el Menú Principal.

```csharp
IEnumerator GetUserProfile(string username)
{
    string url = baseUrl + "/users/" + username;
    var request = UnityWebRequest.Get(url);
    
    yield return request.SendWebRequest();

    if (request.result == UnityWebRequest.Result.Success)
    {
        UserResponse user = JsonUtility.FromJson<UserResponse>(request.downloadHandler.text);
        Debug.Log("Tu récord actual es: " + user.score);
        // Actualizar UI...
    }
}
```
