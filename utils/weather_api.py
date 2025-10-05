import requests
import pandas as pd
import numpy as np


class MeteomaticsWeatherAPI:
    """API para obtener datos meteorológicos en tiempo real"""
    
    def __init__(self, username, password, base_url):
        self.username = username
        self.password = password
        self.base_url = base_url
        
    def get_weather_for_area(self, bbox_corners, forecast_date):
        """
        Obtiene datos meteorológicos para un área específica
        
        Args:
            bbox_corners: {"top_left": [lat, lon], "bottom_right": [lat, lon]}
            forecast_date: "YYYY-MM-DD"
            
        Returns:
            DataFrame con datos meteorológicos
        """
        try:
            # Parámetros meteorológicos críticos
            weather_params = [
                "t_2m:C",
                "relative_humidity_2m:p",
                "wind_speed_10m:ms",
                "wind_dir_10m:d",
                "precip_1h:mm"
            ]
            
            # Construir URL de la API
            date_iso = f"{forecast_date}T12:00:00Z"
            parameters_str = ",".join(weather_params)
            
            # Crear grilla de 5x5 puntos
            lat_min = min(bbox_corners['top_left'][0], bbox_corners['bottom_right'][0])
            lat_max = max(bbox_corners['top_left'][0], bbox_corners['bottom_right'][0])
            lon_min = min(bbox_corners['top_left'][1], bbox_corners['bottom_right'][1])
            lon_max = max(bbox_corners['top_left'][1], bbox_corners['bottom_right'][1])
            
            location_str = f"{lat_max},{lon_min}_{lat_min},{lon_max}:5x5"
            api_url = f"{self.base_url}/{date_iso}/{parameters_str}/{location_str}/json"
            
            print(f"📡 Consultando API meteorológica...")
            
            # Realizar petición HTTP
            response = requests.get(api_url, auth=(self.username, self.password), timeout=30)
            response.raise_for_status()
            
            # Procesar respuesta JSON
            data = response.json()
            weather_df = self._process_meteomatics_response(data)
            
            if weather_df is not None:
                print(f"Datos obtenidos: {len(weather_df)} puntos")
                return weather_df
            else:
                print("Error procesando datos meteorológicos")
                return None
                
        except Exception as e:
            print(f"Error API Meteomatics: {e}")
            return None
    
    def _process_meteomatics_response(self, api_data):
        """Convierte respuesta JSON de Meteomatics en DataFrame"""
        try:
            # Extraer coordenadas
            first_param = api_data['data'][0]
            coordinates = first_param['coordinates']
            
            # Crear puntos base
            weather_points = []
            for coord in coordinates:
                point = {'latitude': coord['lat'], 'longitude': coord['lon']}
                weather_points.append(point)
            
            df = pd.DataFrame(weather_points)
            
            # Agregar datos meteorológicos
            for param_data in api_data['data']:
                param_name = param_data['parameter']
                values = [coord['dates'][0]['value'] for coord in param_data['coordinates']]
                df[param_name] = values
            
            return df
            
        except Exception as e:
            print(f"❌ Error procesando JSON: {e}")
            return None


def generate_synthetic_weather_data(bbox_corners):
    """Genera datos meteorológicos sintéticos si la API falla (Fallback)"""
    print("Usando datos sintéticos (fallback)...")

    lat_min = min(bbox_corners['top_left'][0], bbox_corners['bottom_right'][0])
    lat_max = max(bbox_corners['top_left'][0], bbox_corners['bottom_right'][0])
    lon_min = min(bbox_corners['top_left'][1], bbox_corners['bottom_right'][1])
    lon_max = max(bbox_corners['top_left'][1], bbox_corners['bottom_right'][1])
    
    lats = np.linspace(lat_min, lat_max, 5)
    lons = np.linspace(lon_min, lon_max, 5)
    
    weather_points = []
    for lat in lats:
        for lon in lons:
            point = {
                'latitude': lat,
                'longitude': lon,
                't_2m:C': np.random.uniform(15, 35),
                'relative_humidity_2m:p': np.random.uniform(30, 80),
                'wind_speed_10m:ms': np.random.uniform(2, 15),
                'wind_dir_10m:d': np.random.uniform(0, 360),
                'precip_1h:mm': np.random.uniform(0, 5)
            }
            weather_points.append(point)
    
    return pd.DataFrame(weather_points)
