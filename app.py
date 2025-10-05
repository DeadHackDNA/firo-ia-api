"""
API Flask para Predicción de Incendios Forestales
NASA Space Apps Challenge 2025
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from utils.fire_predictor import OptimizedFirePredictor
from utils.weather_api import MeteomaticsWeatherAPI, generate_synthetic_weather_data
from utils.response_formatter import create_optimized_api_response, validate_bbox_coordinates

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Configuración
MODEL_PATH = os.getenv('MODEL_PATH', 'models/fire_prediction_models_complete.pkl')
METEOMATICS_USER = os.getenv('METEOMATICS_USER')
METEOMATICS_PASS = os.getenv('METEOMATICS_PASS')
METEOMATICS_URL = 'https://api.meteomatics.com'

# Cargar modelo al iniciar
print("🚀 Inicializando API de Predicción de Incendios...")
predictor = OptimizedFirePredictor(MODEL_PATH)

if not predictor.is_loaded:
    print("❌ ERROR: No se pudo cargar el modelo")
    exit(1)

# Inicializar API meteorológica
weather_api = MeteomaticsWeatherAPI(
    METEOMATICS_USER,
    METEOMATICS_PASS,
    METEOMATICS_URL
)

print("API lista para recibir peticiones")


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de estado"""
    return jsonify({
        "status": "healthy",
        "service": "Fire Risk Prediction API",
        "version": "1.0",
        "model_loaded": predictor.is_loaded,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/model-info', methods=['GET'])
def model_info():
    """Endpoint con información del modelo"""
    if not predictor.is_loaded:
        return jsonify({"error": "Modelo no cargado"}), 500
    
    return jsonify({
        "model_metadata": predictor.system_metadata,
        "regions_available": list(predictor.regional_models.keys()),
        "total_models": len(predictor.regional_models)
    }), 200


@app.route('/validate-coordinates', methods=['POST'])
def validate_coordinates():
    """Endpoint para validar coordenadas del bbox"""
    try:
        data = request.get_json()
        
        if not data or 'bbox_corners' not in data:
            return jsonify({
                "error": "Falta el campo 'bbox_corners' en la petición"
            }), 400
        
        is_valid, error_message = validate_bbox_coordinates(data['bbox_corners'])
        
        if not is_valid:
            return jsonify({
                "valid": False,
                "error": error_message
            }), 400
        
        return jsonify({
            "valid": True,
            "message": "Coordenadas válidas",
            "bbox_corners": data['bbox_corners']
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Error validando coordenadas: {str(e)}"
        }), 500


@app.route('/predict-fire-risk', methods=['POST'])
def predict_fire_risk():
    """
    Endpoint principal de predicción de riesgo de incendios
    
    Entrada JSON:
    {
        "bbox_corners": {
            "top_left": [-14.219889, -71.271138],
            "bottom_right": [-14.306682, -71.176567]
        },
        "forecast_date": "2025-10-06"
    }
    
    Salida JSON:
    {
        "fire_risk_assessment": {...},
        "risk_grid": [...],
        "recommendations": {...}
    }
    """
    try:
        # 1. Validar petición
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibió JSON en la petición"}), 400
        
        if 'bbox_corners' not in data:
            return jsonify({"error": "Falta el campo 'bbox_corners'"}), 400
        
        if 'forecast_date' not in data:
            return jsonify({"error": "Falta el campo 'forecast_date'"}), 400
        
        bbox_corners = data['bbox_corners']
        forecast_date = data['forecast_date']
        
        # 2. Validar coordenadas
        is_valid, error_message = validate_bbox_coordinates(bbox_corners)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # 3. Validar modelo
        if not predictor.is_loaded:
            return jsonify({"error": "Modelo no cargado"}), 500
        
        print(f"\n🎯 Nueva predicción solicitada:")
        print(f"   Área: {bbox_corners}")
        print(f"   Fecha: {forecast_date}")
        
        # 4. Obtener datos meteorológicos
        weather_data = weather_api.get_weather_for_area(bbox_corners, forecast_date)
        
        # Fallback a datos sintéticos si API falla
        if weather_data is None:
            print("API meteorológica falló, usando datos sintéticos...")
            weather_data = generate_synthetic_weather_data(bbox_corners)
        
        # 5. Hacer predicciones
        print("Realizando predicciones...")
        predictions = predictor.predict_risk_optimized(weather_data)
        
        if not predictions:
            return jsonify({
                "error": "No se pudieron generar predicciones"
            }), 500
        
        # 6. Crear respuesta optimizada
        response = create_optimized_api_response(
            predictions,
            forecast_date,
            bbox_corners
        )
        
        print(f"Predicción completada: {response['fire_risk_assessment']['overall_risk_level']}")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error en predicción: {e}")
        return jsonify({
            "error": f"Error procesando predicción: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Manejo de rutas no encontradas"""
    return jsonify({
        "error": "Endpoint no encontrado",
        "available_endpoints": [
            "GET /health",
            "GET /model-info",
            "POST /validate-coordinates",
            "POST /predict-fire-risk"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos"""
    return jsonify({
        "error": "Error interno del servidor",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    # Modo desarrollo
    print("\Iniciando servidor Flask...")
    print("- Endpoints disponibles:")
    print("   GET  /health")
    print("   GET  /model-info")
    print("   POST /validate-coordinates")
    print("   POST /predict-fire-risk")
    print("\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
