import numpy as np


def create_optimized_api_response(predictions, forecast_date, bbox_corners):
    """
    Crea respuesta JSON optimizada según el formato especificado
    
    Args:
        predictions: Lista de predicciones
        forecast_date: Fecha de predicción
        bbox_corners: Coordenadas del área analizada
        
    Returns:
        dict: Respuesta JSON estructurada
    """
    if not predictions:
        return {
            "error": "No se pudieron generar predicciones",
            "fire_risk_assessment": {
                "overall_risk_level": "UNKNOWN",
                "alert_level": 0,
                "statistics": {
                    "average_risk_percentage": 0,
                    "maximum_risk_percentage": 0
                }
            }
        }
    
    # Calcular estadísticas
    fire_probs = [p['fire_probability'] for p in predictions]
    avg_prob = np.mean(fire_probs)
    max_prob = np.max(fire_probs)
    
    # Determinar nivel general de riesgo
    if avg_prob > 70:
        overall_level = 'HIGH'
        alert_level = 3
    elif avg_prob > 30:
        overall_level = 'MEDIUM'
        alert_level = 2
    else:
        overall_level = 'LOW'
        alert_level = 1
    
    # Construir risk_grid
    risk_grid = []
    for pred in predictions:
        risk_grid.append({
            "lat": pred['latitude'],
            "lon": pred['longitude'],
            "fire_risk_percentage": pred['fire_probability'],
            "risk_category": pred['risk_level']
        })
    
    # Generar recomendaciones
    if overall_level == 'HIGH':
        primary_action = "ALERTA_MAXIMA"
        alert_authorities = True
    elif overall_level == 'MEDIUM':
        primary_action = "MONITOREO_INTENSIVO"
        alert_authorities = True
    else:
        primary_action = "MONITOREO_RUTINARIO"
        alert_authorities = False
    
    # Construir respuesta final
    response = {
        "fire_risk_assessment": {
            "overall_risk_level": overall_level,
            "alert_level": alert_level,
            "statistics": {
                "average_risk_percentage": round(avg_prob, 1),
                "maximum_risk_percentage": round(max_prob, 1)
            }
        },
        "risk_grid": risk_grid,
        "recommendations": {
            "primary_action": primary_action,
            "alert_authorities": alert_authorities
        }
    }
    
    return response


def validate_bbox_coordinates(bbox_corners):
    """
    Valida las coordenadas del bbox
    
    Args:
        bbox_corners: dict con top_left y bottom_right
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not bbox_corners or not isinstance(bbox_corners, dict):
            return False, "bbox_corners debe ser un diccionario"
        
        if 'top_left' not in bbox_corners or 'bottom_right' not in bbox_corners:
            return False, "bbox_corners debe contener 'top_left' y 'bottom_right'"
        
        top_left = bbox_corners['top_left']
        bottom_right = bbox_corners['bottom_right']
        
        if not isinstance(top_left, list) or len(top_left) != 2:
            return False, "top_left debe ser una lista [lat, lon]"
        
        if not isinstance(bottom_right, list) or len(bottom_right) != 2:
            return False, "bottom_right debe ser una lista [lat, lon]"
        
        # Validar rangos de coordenadas
        if not (-90 <= top_left[0] <= 90) or not (-90 <= bottom_right[0] <= 90):
            return False, "Latitud debe estar entre -90 y 90"
        
        if not (-180 <= top_left[1] <= 180) or not (-180 <= bottom_right[1] <= 180):
            return False, "Longitud debe estar entre -180 y 180"
        
        return True, None
        
    except Exception as e:
        return False, f"Error validando coordenadas: {str(e)}"
