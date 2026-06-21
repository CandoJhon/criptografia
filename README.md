# Generador Seguro de Contraseñas — Backend API REST

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Descripción

Backend API REST para generar contraseñas seguras utilizando **Cryptographically Secure Pseudo-Random Number Generator (CSPRNG)**. El sistema implementa cálculo de entropía según estándares NIST SP 800-63B y RFC 4086, con validación de fortaleza integrada.

### Características principales

- ✅ **CSPRNG genuino**: Generación criptográfica con `secrets.choice()` (no `Math.random`)
- ✅ **Cálculo de entropía**: Formula de Shannon: H = L × log₂(N)
- ✅ **Rate limiting**: Máximo 30 solicitudes/minuto por IP
- ✅ **CORS configurado**: Lista blanca de orígenes permitidos
- ✅ **Security headers**: Cabeceras HTTP de defensa en profundidad
- ✅ **Validación Pydantic**: Tipado fuerte y validación automática
- ✅ **Documentación interactiva**: Swagger UI integrado
- ✅ **Logging seguro**: Registra metadatos, nunca contraseñas

---

## 🔧 Requisitos previos

- **Python** 3.11 o superior
- **pip** (gestor de paquetes)
- Conexión a internet (para instalar dependencias)

### Verificar versión de Python

```bash
python --version
```

Si tienes múltiples versiones:
```bash
python3.11 --version
```

---

## 📦 Instalación

### 1. Descargar archivos

Descarga estos 5 archivos en una carpeta llamada `backend/`:

```
backend/
├── main.py              # Punto de entrada, servidor FastAPI
├── models.py            # Esquemas Pydantic (Request/Response)
├── security.py          # Motor criptográfico + validador de fuerza
├── config.py            # Configuración centralizada
└── requirements.txt     # Dependencias
```

### 2. Instalar dependencias

En la carpeta `backend/`, abre la terminal y ejecuta:

```bash
pip install -r requirements.txt
```

**Salida esperada:**
```
Successfully installed FastAPI-0.109.0 Uvicorn-0.27.0 Pydantic-2.6.1 ...
```

### 3. Verificar instalación

```bash
pip list | grep -E "FastAPI|Pydantic|Uvicorn"
```

Deberías ver las 5 librerías listadas.

---

## 🚀 Ejecutar el servidor

En la carpeta `backend/`, ejecuta:

```bash
python main.py
```

**Salida esperada:**
```
INFO:     Iniciando Generador Seguro de Contraseñas (v1.0.0) en modo development
INFO:     CORS permitido desde: ['http://localhost', 'http://localhost:3000', ...]
INFO:     Rate limit: 30/minute
INFO:     Servidor escuchando en http://127.0.0.1:8000
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

La terminal **permanecerá activa**. Para detener, presiona `CTRL + C`.

---

## 📡 API Endpoints

### Health Check

```http
GET /health
```

**Respuesta (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Generar contraseña segura

```http
POST /api/v1/password
Content-Type: application/json

{
  "length": 20,
  "useUppercase": true,
  "useLowercase": true,
  "useDigits": true,
  "useSymbols": true,
  "excludeAmbiguous": false
}
```

**Parámetros:**

| Parámetro | Tipo | Por defecto | Rango | Descripción |
|---|---|---|---|---|
| `length` | Integer | 16 | 8-128 | Longitud de la contraseña |
| `useUppercase` | Boolean | true | - | Incluir mayúsculas (A-Z) |
| `useLowercase` | Boolean | true | - | Incluir minúsculas (a-z) |
| `useDigits` | Boolean | true | - | Incluir dígitos (0-9) |
| `useSymbols` | Boolean | true | - | Incluir símbolos especiales |
| `excludeAmbiguous` | Boolean | false | - | Excluir caracteres ambiguos (i, l, 1, o, 0, O) |

**Respuesta (200 OK):**
```json
{
  "password": "k7$Wm2#qPxR9!nL4vB&t",
  "length": 20,
  "entropyBits": 131.1,
  "strength": "very_strong",
  "alphabetSize": 94
}
```

**Códigos de error:**

| Código | Descripción |
|---|---|
| 400 | Parámetros inválidos (ej. longitud fuera de rango) |
| 429 | Límite de tasa excedido (máximo 30 por minuto) |
| 500 | Error interno del servidor |

---

## 🧪 Probar la API

### Opción 1: Swagger UI (Recomendado)

1. Abre tu navegador en: `http://localhost:8000/api/docs`
2. Busca el endpoint `POST /api/v1/password`
3. Haz clic en **"Try it out"**
4. Edita los parámetros JSON (o déjalos por defecto)
5. Haz clic en **"Execute"**
6. Ver respuesta

### Opción 2: cURL (Terminal/PowerShell)

```bash
curl -X POST "http://localhost:8000/api/v1/password" \
  -H "Content-Type: application/json" \
  -d '{
    "length": 20,
    "useUppercase": true,
    "useLowercase": true,
    "useDigits": true,
    "useSymbols": true,
    "excludeAmbiguous": false
  }'
```

### Opción 3: Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/password",
    json={
        "length": 20,
        "useUppercase": True,
        "useLowercase": True,
        "useDigits": True,
        "useSymbols": True,
        "excludeAmbiguous": False
    }
)

print(response.json())
```

---

## 🔐 Seguridad

### Generación criptográfica

El sistema utiliza **`secrets.choice()`** que implementa un CSPRNG (Cryptographically Secure Pseudo-Random Number Generator):

- **Fuente de entropía (Linux/macOS):** `/dev/urandom`
- **Fuente de entropía (Windows):** `CryptGenRandom`
- **Jamás usa `Math.random()`:** No es criptográfico (predecible)

### Cálculo de entropía

La fortaleza de cada contraseña se calcula usando la fórmula de entropía de Shannon:

```
H = L × log₂(N)

Donde:
  L = longitud de la contraseña
  N = tamaño del alfabeto utilizado
```

### Clasificación de fortaleza

| Rango (bits) | Clasificación | Tiempo estimado para crackear* |
|---|---|---|
| < 28 | `very_weak` | Segundos |
| 28-35 | `weak` | Minutos |
| 36-59 | `reasonable` | Horas a días |
| 60-127 | `strong` | Años a siglos |
| ≥ 128 | `very_strong` | Infactible |

*Asumiendo 10¹² intentos/segundo (GPU moderna, hash débil)

### Medidas de defensa

- **HTTPS/TLS 1.3** (recomendado en producción)
- **CORS restrictivo** (solo orígenes permitidos)
- **Rate limiting** (30 solicitudes/minuto)
- **Security headers** (Cache-Control, X-Frame-Options, HSTS)
- **Validación Pydantic** (entrada tipada y validada)
- **Logging seguro** (nunca registra contraseñas)

---

## 📂 Estructura del proyecto

```
backend/
├── main.py
│   ├── FastAPI app configuration
│   ├── CORS middleware
│   ├── Rate limiting
│   ├── Security headers
│   ├── Endpoints: GET /, GET /health, POST /api/v1/password
│   └── Uvicorn server startup
│
├── config.py
│   ├── CORS_ORIGINS (lista blanca)
│   ├── RATE_LIMIT (30/minute)
│   ├── PASSWORD_*_LENGTH (8-128)
│   ├── ALPHABETS (mayús, minús, dígitos, símbolos)
│   ├── STRENGTH_THRESHOLDS (clasificación)
│   └── setup_logging() (archivo rotativo)
│
├── models.py
│   ├── PasswordRequest (Pydantic model entrada)
│   ├── PasswordResponse (Pydantic model salida)
│   └── ErrorResponse (Pydantic model errores)
│
├── security.py
│   ├── PasswordGenerator.build_alphabet()
│   ├── PasswordGenerator.generate()
│   ├── PasswordStrengthValidator.calculate_entropy()
│   ├── PasswordStrengthValidator.classify_strength()
│   └── PasswordStrengthValidator.validate()
│
├── requirements.txt
│   └── FastAPI, Uvicorn, Pydantic, slowapi, python-multipart
│
└── logs/
    └── password_generator.log (creado automáticamente)
```

---

## 📊 Flujo de ejecución

flowchart TD
    INICIO([Inicio: Usuario abre la aplicacion])
    UI["Renderizar interfaz de usuario<br/>- Input de longitud<br/>- Checkboxes de tipos de caracteres<br/>- Botones de generacion y copiar"]
    INPUT["Usuario ingresa parametros<br/>- Longitud deseada<br/>- Tipos de caracteres: mayusculas, minusculas, digitos, simbolos"]
    VALIDA_FE{Validacion Frontend<br/>parametros correctos?}
    ERROR_FE["Mostrar error en UI:<br/>Longitud entre 8 y 128"]
    HTTPREQ["Enviar solicitud HTTPS POST<br/>a /api/v1/password<br/>Body: JSON con parametros"]
    VALIDA_BE{Validacion Backend<br/>schema Pydantic OK?}
    ERROR_BE["Responder 400 Bad Request<br/>con mensaje de error"]
    GENERA["Motor Criptografico<br/>secrets.choice sobre alfabeto<br/>para cada posicion de longitud"]
    CONTRASEÑA["Contraseña generada<br/>en memoria del servidor"]
    ENTROPIA["Calcular entropia<br/>H = L * log2 N"]
    FUERZA["Clasificar fuerza segun entropia<br/>- Debil: 28-35 bits<br/>- Razonable: 36-59 bits<br/>- Fuerte: 60-127 bits<br/>- Muy Fuerte: mayor a 128 bits"]
    RESPONSE["Responder 200 OK<br/>JSON: password, entropyBits, strength"]
    HTTPRESP["Cliente HTTP recibe respuesta"]
    UPDATE_STATE["Actualizar controlador de estado<br/>con contraseña y metadatos"]
    RENDERIZAR["Renderizar en UI:<br/>- Campo de contraseña<br/>- Medidor de fuerza<br/>- Mostrar bits de entropia"]
    COPIAR{Usuario presiona<br/>copiar?}
    COPIAR_SI["Copiar contraseña<br/>al portapapeles del navegador"]
    NOTIFICACION["Mostrar notificacion:<br/>Copiado al portapapeles"]
    REGENERAR{Usuario presiona<br/>regenerar?}
    SI_REGENERAR["Volver a paso HTTPREQ<br/>con mismos parametros"]
    NO_REGENERAR["Fin: Usuario cierra sesion"]
    FIN([Fin])

    INICIO --> UI
    UI --> INPUT
    INPUT --> VALIDA_FE
    VALIDA_FE -->|No| ERROR_FE
    ERROR_FE --> INPUT
    VALIDA_FE -->|Si| HTTPREQ
    HTTPREQ --> VALIDA_BE
    VALIDA_BE -->|No| ERROR_BE
    ERROR_BE --> HTTPREQ
    VALIDA_BE -->|Si| GENERA
    GENERA --> CONTRASEÑA
    CONTRASEÑA --> ENTROPIA
    ENTROPIA --> FUERZA
    FUERZA --> RESPONSE
    RESPONSE --> HTTPRESP
    HTTPRESP --> UPDATE_STATE
    UPDATE_STATE --> RENDERIZAR
    RENDERIZAR --> COPIAR
    COPIAR -->|Si| COPIAR_SI
    COPIAR_SI --> NOTIFICACION
    NOTIFICACION --> REGENERAR
    COPIAR -->|No| REGENERAR
    REGENERAR -->|Si| SI_REGENERAR
    REGENERAR -->|No| NO_REGENERAR
    SI_REGENERAR --> HTTPREQ
    NO_REGENERAR --> FIN


---

## 📝 Logging

Los logs se guardan en `backend/logs/password_generator.log`.

**Archivo rotativo:** máximo 10MB por archivo, mantiene 5 archivos históricos.

**Formato:**
```
2026-06-20 21:32:03 - password_generator - INFO - Solicitud recibida desde 127.0.0.1: longitud=20, mayus=True, minus=True, digs=True, syms=True
```

**⚠️ Nota importante:** Las contraseñas generadas **NUNCA** se registran en logs. Solo metadatos (longitud, tipos de carácter, entropía).

### Ver logs en tiempo real

```bash
# Linux/macOS
tail -f logs/password_generator.log

# Windows PowerShell
Get-Content logs/password_generator.log -Wait
```

---

## 🐛 Solución de problemas

### Error: ModuleNotFoundError: No module named 'fastapi'

**Causa:** Dependencias no instaladas.

**Solución:**
```bash
pip install -r requirements.txt
```

---

### Error: Port 8000 already in use

**Causa:** Otro proceso usa el puerto 8000.

**Opción A:** Detener la otra aplicación.

**Opción B:** Cambiar puerto en `config.py`:
```python
PORT = 8001  # en lugar de 8000
```

---

### Error: Failed to build installable wheels for pydantic-core (Windows)

**Causa:** Versión de Python no soportada.

**Solución:**
- Verificar: `python --version`
- Usar Python 3.11 o 3.12
- O reinstalar Python marcando "Add Python to PATH"

---

### El servidor inicia pero no puedo acceder desde otro dispositivo

**Causa:** Servidor escucha solo en localhost.

**Solución** en `config.py`:
```python
HOST = "0.0.0.0"  # Permite cualquier IP en la red
```

---

## 📚 Referencias técnicas

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Pydantic Documentation:** https://docs.pydantic.dev/
- **RFC 4086 (Randomness Requirements):** https://tools.ietf.org/html/rfc4086
- **NIST SP 800-63B (Password Guidelines):** https://pages.nist.gov/800-63-3/sp800-63b.html
- **Python secrets module:** https://docs.python.org/3/library/secrets.html

---

## 🤝 Próximos pasos

- [ ] Implementar Frontend (HTML + CSS + JavaScript)
- [ ] Integración Frontend-Backend vía API REST
- [ ] Despliegue en servidor (Render, Railway, Heroku)
- [ ] Certificado SSL/TLS (Let's Encrypt)
- [ ] Tests unitarios (pytest)
- [ ] CI/CD (GitHub Actions)

---

## 📄 Licencia

MIT License — Ver LICENSE.txt

---

**Versión:** 1.0.0 | **Última actualización:** Junio 2026