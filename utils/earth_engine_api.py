"""
Google Earth Engine API Integration
Obtiene datos de terreno, vegetación y cobertura para predicción de incendios
"""

import ee
import os
from typing import Dict, Optional, Tuple


class EarthEngineAPI:
    """Cliente para interactuar con Google Earth Engine"""
    
    def __init__(self):
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Inicializa la conexión con Earth Engine"""
        try:
            # Opción 1: Service Account desde variable de entorno (Railway/Render)
            gee_key_json = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
            if gee_key_json:
                import json
                import tempfile
                
                # Crear archivo temporal con las credenciales
                credentials_dict = json.loads(gee_key_json)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(credentials_dict, f)
                    temp_key_file = f.name
                
                credentials = ee.ServiceAccountCredentials(
                    email=credentials_dict['client_email'],
                    key_file=temp_key_file
                )
                ee.Initialize(credentials)
                print("✅ Earth Engine inicializado con Service Account (env var)")
                self.initialized = True
                return
            
            # Opción 2: Service Account desde archivo local
            if os.path.exists('earth-engine-credentials.json'):
                credentials = ee.ServiceAccountCredentials(
                    email=os.getenv('EE_SERVICE_ACCOUNT'),
                    key_file='earth-engine-credentials.json'
                )
                ee.Initialize(credentials)
                print("✅ Earth Engine inicializado con Service Account (archivo)")
                self.initialized = True
                return
            
            # Opción 3: Autenticación interactiva (desarrollo)
            try:
                # Intentar sin proyecto primero (más compatible)
                ee.Initialize()
                print("✅ Earth Engine inicializado con credenciales por defecto")
                self.initialized = True
            except Exception as e1:
                # Si falla, intentar con proyecto
                try:
                    project = os.getenv('GOOGLE_CLOUD_PROJECT', 'earthengine-legacy')
                    ee.Initialize(project=project)
                    print(f"✅ Earth Engine inicializado con proyecto: {project}")
                    self.initialized = True
                except Exception as e2:
                    print(f"⚠️ Earth Engine no autenticado - usando datos simulados")
                    print(f"   Error: {e2}")
                    print("   Solución: Crea un proyecto en https://console.cloud.google.com/")
                    print("   Luego actualiza GOOGLE_CLOUD_PROJECT en .env")
                    self.initialized = False
            
        except Exception as e:
            print(f"⚠️ Error inicializando Earth Engine: {e}")
            print("   Usando datos de terreno simulados")
            self.initialized = False
    
    def get_terrain_data(self, lat: float, lon: float) -> Dict:
        """
        Obtiene datos de terreno para un punto específico
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Dict con elevation, slope, aspect
        """
        if not self.initialized:
            return self._get_simulated_terrain_data(lat, lon)
        
        try:
            point = ee.Geometry.Point([lon, lat])
            
            # Dataset: SRTM Digital Elevation (30m resolution)
            dem = ee.Image('USGS/SRTMGL1_003')
            
            # Obtener elevación
            elevation = dem.select('elevation').reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=30
            ).getInfo()
            
            # Calcular pendiente
            slope = ee.Terrain.slope(dem).reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=30
            ).getInfo()
            
            # Validar que tenemos datos (no None)
            elev_value = elevation.get('elevation')
            slope_value = slope.get('slope')
            
            if elev_value is None or slope_value is None:
                # Punto sin datos (agua, fuera de cobertura)
                return self._get_simulated_terrain_data(lat, lon)
            
            return {
                'elevation': round(float(elev_value), 1),
                'slope': round(float(slope_value), 1)
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de terreno: {e}")
            return self._get_simulated_terrain_data(lat, lon)
    
    def get_vegetation_data(self, lat: float, lon: float) -> Dict:
        """
        Obtiene índice de vegetación (NDVI) para un punto
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Dict con ndvi y density
        """
        if not self.initialized:
            return self._get_simulated_vegetation_data(lat, lon)
        
        try:
            point = ee.Geometry.Point([lon, lat])
            
            # Dataset ACTUALIZADO: MODIS Terra Vegetation Indices 061 (nueva versión)
            ndvi_collection = ee.ImageCollection('MODIS/061/MOD13A2') \
                .filterDate('2023-01-01', '2025-12-31') \
                .select('NDVI')
            
            # Obtener última imagen disponible
            ndvi_image = ndvi_collection.sort('system:time_start', False).first()
            
            # Verificar que la imagen existe
            if ndvi_image is None:
                print("⚠️ No hay imágenes NDVI disponibles para esta fecha")
                return self._get_simulated_vegetation_data(lat, lon)
            
            ndvi_value = ndvi_image.reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=1000  # 1km resolution
            ).getInfo()
            
            # MODIS NDVI viene escalado por 10000
            ndvi_raw = ndvi_value.get('NDVI')
            if ndvi_raw is None:
                # Punto fuera del área de cobertura (ej: océano)
                return self._get_simulated_vegetation_data(lat, lon)
            
            ndvi = ndvi_raw / 10000.0
            ndvi = max(0.0, min(1.0, ndvi))  # Clamp 0-1
            
            # Clasificar densidad
            if ndvi > 0.6:
                density = "high"
            elif ndvi > 0.3:
                density = "medium"
            else:
                density = "low"
            
            return {
                'density': density
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de vegetación: {e}")
            return self._get_simulated_vegetation_data(lat, lon)
    
    def get_land_cover(self, lat: float, lon: float) -> str:
        """
        Obtiene tipo de cobertura terrestre
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Tipo de cobertura (forest, grassland, urban, etc.)
        """
        if not self.initialized:
            return self._get_simulated_land_cover(lat, lon)
        
        try:
            point = ee.Geometry.Point([lon, lat])
            
            # Dataset ACTUALIZADO: MODIS Land Cover Type 061 (nueva versión)
            land_cover = ee.ImageCollection('MODIS/061/MCD12Q1') \
                .filterDate('2022-01-01', '2024-12-31') \
                .first()
            
            # Verificar que existe
            if land_cover is None:
                print("⚠️ No hay datos de cobertura terrestre disponibles")
                return self._get_simulated_land_cover(lat, lon)
            
            land_cover = land_cover.select('LC_Type1')
            
            lc_value = land_cover.reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=500
            ).getInfo()
            
            # Mapeo IGBP Classification
            lc_classes = {
                1: "forest", 2: "forest", 3: "forest", 4: "forest", 5: "forest",
                6: "shrubland", 7: "shrubland", 8: "woodland", 9: "savanna",
                10: "grassland", 11: "wetland", 12: "cropland", 13: "urban",
                14: "cropland", 15: "snow_ice", 16: "barren", 17: "water"
            }
            
            lc_code = lc_value.get('LC_Type1')
            if lc_code is None:
                # Punto fuera del área de cobertura
                return self._get_simulated_land_cover(lat, lon)
            
            return lc_classes.get(lc_code, "unknown")
            
        except Exception as e:
            print(f"⚠️ Error obteniendo cobertura terrestre: {e}")
            return self._get_simulated_land_cover(lat, lon)
    
    def get_complete_terrain_info(self, lat: float, lon: float) -> Dict:
        """
        Obtiene información completa del terreno para un punto
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Dict completo con terrain solamente (sin vegetation)
        """
        terrain = self.get_terrain_data(lat, lon)
        land_cover = self.get_land_cover(lat, lon)
        
        return {
            'terrain': {
                'elevation': terrain['elevation'],
                'slope': terrain['slope'],
                'land_cover': land_cover
            }
        }
    
    # Métodos de simulación (fallback cuando GEE no está disponible)
    
    def _get_simulated_terrain_data(self, lat: float, lon: float) -> Dict:
        """Genera datos simulados basados en ubicación aproximada"""
        import random
        
        # Simulación básica basada en latitud
        base_elevation = abs(lat) * 50  # Más elevación cerca de polos
        elevation = base_elevation + random.uniform(-200, 500)
        slope = random.uniform(0, 25)
        
        return {
            'elevation': round(max(0, elevation), 1),
            'slope': round(slope, 1)
        }
    
    def _get_simulated_vegetation_data(self, lat: float, lon: float) -> Dict:
        """Genera densidad simulada (sin NDVI)"""
        import random
        
        # NDVI más alto en zonas ecuatoriales
        base_ndvi = max(0, 0.7 - abs(lat) / 90)
        ndvi = base_ndvi + random.uniform(-0.2, 0.1)
        ndvi = max(0.0, min(1.0, ndvi))
        
        if ndvi > 0.6:
            density = "high"
        elif ndvi > 0.3:
            density = "medium"
        else:
            density = "low"
        
        return {
            'density': density
        }
    
    def _get_simulated_land_cover(self, lat: float, lon: float) -> str:
        """Genera cobertura simulada"""
        import random
        
        # Distribución aproximada por latitud
        if abs(lat) < 23:  # Trópicos
            types = ['forest', 'grassland', 'savanna', 'cropland']
        elif abs(lat) < 50:  # Templadas
            types = ['forest', 'grassland', 'cropland', 'urban']
        else:  # Polares
            types = ['barren', 'snow_ice', 'grassland']
        
        return random.choice(types)


# Instancia global
earth_engine_client = EarthEngineAPI()
