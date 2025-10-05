# 🔥 API de Predicción de Incendios Forestales

API Flask para predicción de riesgo de incendios forestales usando Machine Learning (LightGBM).

---

## 🚀 Instalación

### 1. Clonar repositorio
```bash
git clone <repo-url>
cd firo-ia-api
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Crear archivo `.env` con:
```
METEOMATICS_USER=tu_usuario
METEOMATICS_PASS=tu_password
MODEL_PATH=models/fire_prediction_models_complete.pkl
FLASK_ENV=production
```

---

## Ejecución

### Modo Desarrollo
```bash
python app.py
```
La API estará disponible en: `http://localhost:5000`

---

## 📡 Endpoints

### 1. **Health Check**
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "Fire Risk Prediction API",
  "version": "1.0",
  "model_loaded": true,
  "timestamp": "2025-10-05T12:00:00"
}
```

---

### 2. **Información del Modelo**
```http
GET /model-info
```

**Respuesta:**
```json
{
  "model_metadata": {
    "version": "2.0_optimized",
    "training_date": "2025-10-05",
    "total_models": 7
  },
  "regions_available": ["africa", "asia", "north_america", ...],
  "total_models": 7
}
```

---

### 3. **Validar Coordenadas**
```http
POST /validate-coordinates
Content-Type: application/json

{
  "bbox_corners": {
    "top_left": [-14.219889, -71.271138],
    "bottom_right": [-14.306682, -71.176567]
  }
}
```

**Respuesta:**
```json
{
  "valid": true,
  "message": "Coordenadas válidas",
  "bbox_corners": {...}
}
```

---

### 4. **Predicción de Riesgo de Incendios**
```http
POST /predict-fire-risk
Content-Type: application/json

{
  "bbox_corners": {
    "top_left": [-14.219889, -71.271138],
    "bottom_right": [-14.306682, -71.176567]
  },
  "forecast_date": "2025-10-06"
}
```

**Respuesta:**
```json
{
  "fire_risk_assessment": {
    "overall_risk_level": "LOW",
    "alert_level": 1,
    "statistics": {
      "average_risk_percentage": 20.4,
      "maximum_risk_percentage": 24.8
    }
  },
  "risk_grid": [
    {
      "lat": -14.284984,
      "lon": -71.247495,
      "fire_risk_percentage": 18.8,
      "risk_category": "LOW"
    }
  ],
  "recommendations": {
    "primary_action": "MONITOREO_RUTINARIO",
    "alert_authorities": false
  }
}
```

---

## 🧪 Prueba con cURL

```bash
curl -X POST http://localhost:5000/predict-fire-risk \
  -H "Content-Type: application/json" \
  -d @test_data/example_request.json
```

---

## Estructura del Proyecto

```
firo-ia-api/
├── app.py                    # API Flask principal
├── requirements.txt          # Dependencias
├── .env                      # Variables de entorno (NO versionar)
├── models/
│   └── fire_prediction_models_complete.pkl
├── utils/
│   ├── __init__.py
│   ├── fire_predictor.py    # Clase OptimizedFirePredictor
│   ├── weather_api.py       # API meteorológica
│   └── response_formatter.py # Formateo de respuestas
└── test_data/
    └── example_request.json # Ejemplo de petición
```

---

## Dependencias Principales

- **Flask** 2.3.3 - Framework web
- **Flask-CORS** 4.0.0 - CORS
- **pandas** ≥2.1.4 - Manipulación de datos
- **numpy** ≥1.26.0 - Operaciones numéricas
- **lightgbm** 3.3.5 - Modelo ML
- **requests** 2.31.0 - Cliente HTTP
- **gunicorn** 21.2.0 - Servidor WSGI (producción)

---

## Regiones Soportadas

El modelo tiene 7 modelos regionales entrenados:

- África
- Asia
- América del Norte
- América del Sur
- Europa
- Oceanía
- Otras regiones

---

## Niveles de Riesgo

| Nivel | Porcentaje | Alert Level | Acción |
|-------|------------|-------------|--------|
| **LOW** | 0-30% | 1 | Monitoreo rutinario |
| **MEDIUM** | 31-70% | 2 | Monitoreo intensivo |
| **HIGH** | 71-100% | 3 | Alerta máxima |

---