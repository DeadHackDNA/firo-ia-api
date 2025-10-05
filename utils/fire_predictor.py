import pickle
import numpy as np
import lightgbm as lgb


class OptimizedFirePredictor:
    """Predictor que carga modelos desde PKL para inferencia rápida"""
    
    def __init__(self, pkl_path=None):
        self.regional_models = {}
        self.preprocessing_params = {}
        self.system_metadata = {}
        self.region_boundaries = {}
        self.is_loaded = False
        
        if pkl_path:
            self.load_models_from_pkl(pkl_path)
    
    def load_models_from_pkl(self, pkl_path):
        """Carga modelos entrenados desde archivo PKL"""
        try:
            print(f"Cargando modelos desde: {pkl_path}")
            
            with open(pkl_path, 'rb') as f:
                model_package = pickle.load(f)
            
            # Deserializar modelos desde string
            deserialized_models = {}
            for region, model_info in model_package['regional_models'].items():
                model_copy = model_info.copy()
                # Reconstruir modelo desde string
                if isinstance(model_info['model'], str):
                    model_copy['model'] = lgb.Booster(model_str=model_info['model'])
                else:
                    model_copy['model'] = model_info['model']  # Compatibilidad con PKL viejos
                deserialized_models[region] = model_copy
            
            self.regional_models = deserialized_models
            self.preprocessing_params = model_package['preprocessing_params']
            self.system_metadata = model_package['system_metadata']
            self.region_boundaries = self.preprocessing_params.get('region_boundaries', {})
            
            print(f"Modelos cargados correctamente")
            print(f"   {len(self.regional_models)} modelos regionales disponibles")
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"Error cargando PKL: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def detect_region(self, lat, lon):
        """Detecta región geográfica"""
        if not self.region_boundaries:
            return 'other'
            
        for region, bounds in self.region_boundaries.items():
            if region == 'other':
                continue
            lat_range, lon_range = bounds['lat'], bounds['lon']
            if (lat_range[0] <= lat <= lat_range[1] and lon_range[0] <= lon <= lon_range[1]):
                return region
        return 'other'
    
    def preprocess_weather_data(self, weather_df):
        """Preprocesa datos meteorológicos"""
        if not self.is_loaded:
            raise ValueError("Modelos no cargados")
        
        processed_df = weather_df.copy()
        
        # Agregar elevation y slope sintéticos si no existen
        if 'elevation' not in processed_df.columns:
            np.random.seed(42)
            processed_df['elevation'] = np.maximum(0, 
                1000 + (processed_df['latitude'] * 50) + 
                np.random.uniform(-500, 500, len(processed_df))
            )
        
        if 'slope' not in processed_df.columns:
            processed_df['slope'] = np.minimum(45, 
                processed_df['elevation'] / 100 + 
                np.random.uniform(0, 10, len(processed_df))
            )
        
        return processed_df
    
    def predict_risk_optimized(self, weather_df):
        """Predice riesgo usando modelos cargados desde PKL"""
        if not self.is_loaded:
            raise ValueError("Modelos no cargados")
        
        # Preprocesar datos
        processed_df = self.preprocess_weather_data(weather_df)
        predictions = []
        
        for idx, row in processed_df.iterrows():
            lat, lon = row['latitude'], row['longitude']
            
            # Detectar región
            region = self.detect_region(lat, lon)
            
            # Obtener modelo regional
            if region in self.regional_models:
                model_info = self.regional_models[region]
                model = model_info['model']
            else:
                # Fallback al primer modelo disponible
                model_info = list(self.regional_models.values())[0]
                model = model_info['model']
            
            # Preparar features
            temp_col = 't_2m:C' if 't_2m:C' in row else 'temperature'
            humid_col = 'relative_humidity_2m:p' if 'relative_humidity_2m:p' in row else 'humidity'
            wind_col = 'wind_speed_10m:ms' if 'wind_speed_10m:ms' in row else 'wind_speed'
            
            temperature = row.get(temp_col, 25)
            humidity = row.get(humid_col, 60)
            wind_speed = row.get(wind_col, 5)
            elevation = row.get('elevation', 1000)
            slope = row.get('slope', 10)
            
            # Features en el orden del entrenamiento
            features = np.array([[
                lat, lon,
                temperature + 273.15,  # bright_t31 simulado
                humidity,              # confidence simulado
                wind_speed * 10,       # frp simulado
                elevation,
                slope
            ]])
            
            # Hacer predicción
            fire_probability = model.predict(features)[0]
            fire_probability = max(0, min(100, fire_probability))
            
            # Clasificar riesgo
            if fire_probability > 70:
                risk_level = 'HIGH'
            elif fire_probability > 30:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            prediction = {
                'latitude': lat,
                'longitude': lon,
                'fire_probability': round(fire_probability, 2),
                'risk_level': risk_level
            }
            
            predictions.append(prediction)
        
        return predictions
