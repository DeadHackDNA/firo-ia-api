# 🚀 Guía de Deployment para Render

## 📋 Archivos necesarios (ya incluidos):
- ✅ `app.py` - API Flask principal
- ✅ `requirements.txt` - Dependencias
- ✅ `gunicorn_config.py` - Configuración de Gunicorn
- ✅ `Procfile` - Comando de inicio (Heroku/Render)
- ✅ `.gitignore` - Archivos a ignorar

---

## 🎯 Pasos para Deploy en Render:

### 1️⃣ Sube tu código a GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2️⃣ Crea cuenta en Render
- Ve a https://render.com
- Regístrate (gratis)

### 3️⃣ Crea un nuevo Web Service
1. Click en "New +" → "Web Service"
2. Conecta tu repositorio de GitHub
3. Selecciona el repo `firo-ia-api`

### 4️⃣ Configuración del servicio:

**Name:** `firo-ia-api` (o el nombre que quieras)

**Environment:** `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn -c gunicorn_config.py app:app
```

### 5️⃣ Variables de Entorno (Environment Variables):

En la sección "Environment", agrega:

```
METEOMATICS_USER = tu_usuario_aqui
METEOMATICS_PASS = tu_password_aqui
MODEL_PATH = models/fire_prediction_models_complete.pkl
FLASK_ENV = production
PYTHON_VERSION = 3.13.0
```

### 6️⃣ Plan:
- Selecciona **"Free"** (gratis)

### 7️⃣ Deploy:
- Click en "Create Web Service"
- Render automáticamente:
  - ✅ Clona tu repo
  - ✅ Instala dependencias
  - ✅ Inicia tu API con Gunicorn
  - ✅ Te da una URL pública (ej: `https://firo-ia-api.onrender.com`)

---

## 🧪 Probar tu API deployada:

Una vez que el deploy termine, prueba:

```bash
# Health check
curl https://tu-app.onrender.com/health

# Predicción
curl -X POST https://tu-app.onrender.com/predict-fire-risk \
  -H "Content-Type: application/json" \
  -d '{
    "bbox_corners": {
      "top_left": [-14.219889, -71.271138],
      "bottom_right": [-14.306682, -71.176567]
    },
    "forecast_date": "2025-10-06"
  }'
```

---

## ⚠️ Notas Importantes:

### Limitaciones del Plan Free de Render:
- ⏰ Se duerme después de 15 min sin uso
- ⏳ Primera petición después de dormir tarda ~1 min
- 💾 750 horas gratis al mes
- 🔄 Auto-deploy al hacer push a GitHub

### Archivos Grandes:
Si el PKL es muy grande (>100 MB):
- Considera usar Git LFS
- O sube el modelo a Google Drive/S3 y descárgalo en startup

---

## 🔧 Comandos útiles de Render:

- **Ver logs:** En el dashboard de Render → Logs
- **Re-deploy manual:** En dashboard → Manual Deploy
- **Variables de entorno:** Settings → Environment

---

## 🎉 ¡Listo!

Tu API estará disponible en:
```
https://tu-app-name.onrender.com
```

Endpoints:
- GET  https://tu-app-name.onrender.com/health
- GET  https://tu-app-name.onrender.com/model-info
- POST https://tu-app-name.onrender.com/predict-fire-risk
- POST https://tu-app-name.onrender.com/validate-coordinates

---

## 🆘 Troubleshooting:

**Error: "Application failed to respond"**
- Verifica las variables de entorno
- Revisa los logs en Render

**Error: "ModuleNotFoundError"**
- Verifica que `requirements.txt` esté completo

**API muy lenta en primera petición:**
- Normal en plan free (cold start)
- Considera upgrade a plan de pago si es crítico

---

## 📚 Alternativas:

Si tienes problemas con Render, también puedes usar:
- **Railway.app** - Similar a Render
- **Fly.io** - Más rápido pero requiere CLI
- **PythonAnywhere** - Especializado en Python

---

**¡Tu API está lista para producción! 🚀**
