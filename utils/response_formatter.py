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
    Valida las coordenadas del bbox y auto-detecta el formato [lon, lat] vs [lat, lon]
    
    Args:
        bbox_corners: dict con top_left y bottom_right
        
    Returns:
        tuple: (is_valid, error_message, normalized_bbox)
        normalized_bbox estará en formato [lat, lon]
    """
    try:
        if not bbox_corners or not isinstance(bbox_corners, dict):
            return False, "bbox_corners debe ser un diccionario", None
        
        if 'top_left' not in bbox_corners or 'bottom_right' not in bbox_corners:
            return False, "bbox_corners debe contener 'top_left' y 'bottom_right'", None
        
        top_left = bbox_corners['top_left']
        bottom_right = bbox_corners['bottom_right']
        
        if not isinstance(top_left, list) or len(top_left) != 2:
            return False, "top_left debe ser una lista [lat, lon] o [lon, lat]", None
        
        if not isinstance(bottom_right, list) or len(bottom_right) != 2:
            return False, "bottom_right debe ser una lista [lat, lon] o [lon, lat]", None
        
        # Auto-detectar formato: Si el primer valor está fuera del rango de latitud,
        # asumimos que el formato es [lon, lat] (como Cesium)
        coord1_0, coord1_1 = top_left
        coord2_0, coord2_1 = bottom_right
        
        # Verificar si parece formato [lon, lat] (Cesium/GeoJSON)
        if abs(coord1_0) > 90 or abs(coord2_0) > 90:
            # Formato [lon, lat] detectado, invertir a [lat, lon]
            print(f"🔄 Formato [lon, lat] detectado, convirtiendo a [lat, lon]...")
            normalized_bbox = {
                'top_left': [coord1_1, coord1_0],      # [lat, lon]
                'bottom_right': [coord2_1, coord2_0]   # [lat, lon]
            }
        else:
            # Formato [lat, lon] ya correcto
            normalized_bbox = bbox_corners
        
        # Validar rangos con formato normalizado [lat, lon]
        norm_tl = normalized_bbox['top_left']
        norm_br = normalized_bbox['bottom_right']
        
        # Validar latitudes (índice 0)
        if not (-90 <= norm_tl[0] <= 90) or not (-90 <= norm_br[0] <= 90):
            return False, "Latitud debe estar entre -90 y 90", None
        
        # Validar longitudes (índice 1)
        if not (-180 <= norm_tl[1] <= 180) or not (-180 <= norm_br[1] <= 180):
            return False, "Longitud debe estar entre -180 y 180", None
        
        return True, None, normalized_bbox
        
    except Exception as e:
        return False, f"Error validando coordenadas: {str(e)}", None
        
    except Exception as e:
        return False, f"Error validando coordenadas: {str(e)}"
