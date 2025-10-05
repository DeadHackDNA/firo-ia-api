import pickle
from flask import request, jsonify, Blueprint
import joblib
from app.controllers.home_controller import home
import numpy as np
import traceback

home_bp = Blueprint('home', __name__)

MODEL_PATH = "model_1.pkl"
with open(MODEL_PATH, "rb") as f:
    model_data = joblib.load(f)
regional_models = model_data["regional_models"]
print("Regiones disponibles:", list(regional_models.keys()))

for region, info in regional_models.items():
    print(f"\n🌍 Región: {region}")
    print("Claves internas:", list(info.keys()))
print(regional_models["south_america"]["features"])

@home_bp.route('/')
def index():
    return home()

@home_bp.route('/predict')
def predict():
    try:
        data = {
            "bbox_corners": {
                "top_left": [-14.219889, -71.271138],
                "bottom_right": [-14.306682, -71.176567]
            },
            "forecast_date": "2025-10-06"
        }

        # Promediamos el área como punto de referencia
        lat = (data["bbox_corners"]["top_left"][0] + data["bbox_corners"]["bottom_right"][0]) / 2
        lon = (data["bbox_corners"]["top_left"][1] + data["bbox_corners"]["bottom_right"][1]) / 2

        # Valores simulados o predeterminados (ajusta según tu dataset real)
        elevation = 1200.0
        slope = 5.0
        land_cover = 2.0  # puede representar un tipo de vegetación, por ejemplo

        X_input = np.array([[lat, lon, elevation, slope, land_cover]])

        region_name = "south_america"
        model = regional_models[region_name]["models"]

        preds = model.predict(X_input)

        return jsonify({
            "prediction_metadata": {
                "analysis_date": "2025-10-05T07:51:52.873474",
                "forecast_date": "2025-10-06",
                "area_analyzed": {
                "top_left": [
                    -14.219889,
                    -71.271138
                ],
                "bottom_right": [
                    -14.306682,
                    -71.176567
                ]
                },
                "total_points_analyzed": 25,
                "high_risk_points_found": 0,
                "model_version": "IMPROVED_v4"
            },
            "risk_summary": {
                "overall_risk_level": "MEDIUM",
                "average_fire_probability": 34.5,
                "max_fire_probability": 42.7,
                "critical_zones": 0,
                "high_risk_zones": 0
            },
            "high_risk_locations": [],
            "recommendations": [
                "✅ Condiciones de riesgo bajo - mantener vigilancia rutinaria"
            ],
            "weather_conditions": {
                "temperature_avg": 6.9,
                "humidity_avg": 67.3,
                "wind_speed_avg": 0.9,
                "precipitation_total": 0.0
            },
            "regional_info": {
                "models_used": {
                "Regional-Sudamérica": 25
                },
                "total_regions": 1,
                "prediction_method": "regional_specialized_models"
            },
            "detailed_predictions": [
                {
                "latitude": -14.306682,
                "longitude": -71.271138,
                "fire_probability": 44.41230259356072,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 13.51535248125385,
                "humidity": 75.71366731431088,
                "wind_speed": 13.920993731907444,
                "precipitation": 3.878563120040723,
                "elevation": 3418.1574627140612
                },
                {
                "latitude": -14.306682,
                "longitude": -71.24749525,
                "fire_probability": 44.439103108812596,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 10.7967794037726,
                "humidity": 55.469699516985166,
                "wind_speed": 10.41674986326547,
                "precipitation": 0.3521657318100724,
                "elevation": 3484.8659645661724
                },
                {
                "latitude": -14.306682,
                "longitude": -71.22385249999999,
                "fire_probability": 37.536450344435615,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 21.233718158947937,
                "humidity": 42.56177255318228,
                "wind_speed": 8.956272017716467,
                "precipitation": 4.14850597918903,
                "elevation": 3515.7901354454043
                },
                {
                "latitude": -14.306682,
                "longitude": -71.20020975,
                "fire_probability": 31.707369539859936,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 12.301042353443808,
                "humidity": 58.39228074594327,
                "wind_speed": 13.585056342693466,
                "precipitation": 2.2221894048401687,
                "elevation": 3590.816658623181
                },
                {
                "latitude": -14.306682,
                "longitude": -71.176567,
                "fire_probability": 30.067678709994162,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 16.693428318803807,
                "humidity": 55.56673338492317,
                "wind_speed": 7.897381048778977,
                "precipitation": 4.506613760068268,
                "elevation": 3542.486921639767
                },
                {
                "latitude": -14.28498375,
                "longitude": -71.271138,
                "fire_probability": 43.01814252632613,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 13.864186423892075,
                "humidity": 48.697076057540805,
                "wind_speed": 11.689659561632268,
                "precipitation": 2.3377713803103077,
                "elevation": 3393.5122662148915
                },
                {
                "latitude": -14.28498375,
                "longitude": -71.24749525,
                "fire_probability": 27.39606655588364,
                "risk_level": "LOW",
                "model_used": "Regional-Sudamérica",
                "temperature": 23.395064100961747,
                "humidity": 63.35182300836898,
                "wind_speed": 7.86194143143349,
                "precipitation": 3.5312731452805797,
                "elevation": 3621.8731888451925
                },
                {
                "latitude": -14.28498375,
                "longitude": -71.22385249999999,
                "fire_probability": 32.27365163931689,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 22.279077971626208,
                "humidity": 43.09391726837853,
                "wind_speed": 7.829648317462138,
                "precipitation": 3.6966050535354307,
                "elevation": 3508.600160377228
                },
                {
                "latitude": -14.28498375,
                "longitude": -71.20020975,
                "fire_probability": 41.1377855994673,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 21.57632532370765,
                "humidity": 61.77223776717574,
                "wind_speed": 10.987317199915811,
                "precipitation": 0.4776933242609982,
                "elevation": 3457.142499637683
                },
                {
                "latitude": -14.28498375,
                "longitude": -71.176567,
                "fire_probability": 34.076673675652515,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 16.102875739422092,
                "humidity": 65.28995139206793,
                "wind_speed": 11.10937487786468,
                "precipitation": 2.094303055079718,
                "elevation": 3371.0475627136993
                },
                {
                "latitude": -14.2632855,
                "longitude": -71.271138,
                "fire_probability": 37.09150444402678,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 19.735599100647924,
                "humidity": 44.71620870418515,
                "wind_speed": 5.284378635430095,
                "precipitation": 0.06590557947130982,
                "elevation": 3531.772362207515
                },
                {
                "latitude": -14.2632855,
                "longitude": -71.24749525,
                "fire_probability": 40.24258378552456,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 20.95306779552743,
                "humidity": 40.77270037121081,
                "wind_speed": 12.549223398368825,
                "precipitation": 4.258383730627685,
                "elevation": 3427.3578060357277
                },
                {
                "latitude": -14.2632855,
                "longitude": -71.22385249999999,
                "fire_probability": 39.96207804178231,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 23.429949986115027,
                "humidity": 66.56031264967683,
                "wind_speed": 10.548989624033684,
                "precipitation": 1.551421775472814,
                "elevation": 3672.8022988386847
                },
                {
                "latitude": -14.2632855,
                "longitude": -71.20020975,
                "fire_probability": 33.37454496026639,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 15.79807818105392,
                "humidity": 62.707949272068426,
                "wind_speed": 7.900947418974303,
                "precipitation": 1.9654360294780637,
                "elevation": 3536.3234185867805
                },
                {
                "latitude": -14.2632855,
                "longitude": -71.176567,
                "fire_probability": 39.32856676999876,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 20.561836565843223,
                "humidity": 68.14490590619744,
                "wind_speed": 8.728062907326569,
                "precipitation": 1.2861150555080263,
                "elevation": 3366.3022758150096
                },
                {
                "latitude": -14.24158725,
                "longitude": -71.271138,
                "fire_probability": 39.44826563044923,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 10.479366720983613,
                "humidity": 71.078151660198,
                "wind_speed": 11.357194928159759,
                "precipitation": 0.7521487148322836,
                "elevation": 3427.661317769435
                },
                {
                "latitude": -14.24158725,
                "longitude": -71.24749525,
                "fire_probability": 36.82787557895907,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 17.035432998332276,
                "humidity": 73.57365702272686,
                "wind_speed": 12.335827356098436,
                "precipitation": 3.9838309814849184,
                "elevation": 3560.2826237812023
                },
                {
                "latitude": -14.24158725,
                "longitude": -71.22385249999999,
                "fire_probability": 36.1720447300396,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 12.692448826669278,
                "humidity": 50.1413684653446,
                "wind_speed": 11.780068257792895,
                "precipitation": 2.0011246052481093,
                "elevation": 3567.6100031852498
                },
                {
                "latitude": -14.24158725,
                "longitude": -71.20020975,
                "fire_probability": 28.434948496913393,
                "risk_level": "LOW",
                "model_used": "Regional-Sudamérica",
                "temperature": 14.72554837787313,
                "humidity": 60.597389970282684,
                "wind_speed": 13.852702751980221,
                "precipitation": 1.5584573676452718,
                "elevation": 3408.683047226757
                },
                {
                "latitude": -14.24158725,
                "longitude": -71.176567,
                "fire_probability": 36.597265617411516,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 13.883663752184663,
                "humidity": 41.08226288897544,
                "wind_speed": 12.239062535692375,
                "precipitation": 0.27793491577393414,
                "elevation": 3413.2592080980935
                },
                {
                "latitude": -14.219889,
                "longitude": -71.271138,
                "fire_probability": 37.976390281186994,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 13.552017080626845,
                "humidity": 48.77818312567839,
                "wind_speed": 5.8720678115980585,
                "precipitation": 4.6830049268260865,
                "elevation": 3581.798687376432
                },
                {
                "latitude": -14.219889,
                "longitude": -71.24749525,
                "fire_probability": 40.23274646000705,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 13.858823961526365,
                "humidity": 72.49129405692263,
                "wind_speed": 7.5236409431167,
                "precipitation": 4.456007739403889,
                "elevation": 3535.3353437734577
                },
                {
                "latitude": -14.219889,
                "longitude": -71.22385249999999,
                "fire_probability": 40.53477163297192,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 13.325468846799417,
                "humidity": 79.6708318403089,
                "wind_speed": 8.106231705478415,
                "precipitation": 3.653476847980804,
                "elevation": 3406.439941766862
                },
                {
                "latitude": -14.219889,
                "longitude": -71.20020975,
                "fire_probability": 42.7084825003441,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 11.566254174851087,
                "humidity": 79.82012214630421,
                "wind_speed": 14.110426426216787,
                "precipitation": 2.2326909332434237,
                "elevation": 3442.672890565309
                },
                {
                "latitude": -14.219889,
                "longitude": -71.176567,
                "fire_probability": 38.26977456762454,
                "risk_level": "MEDIUM",
                "model_used": "Regional-Sudamérica",
                "temperature": 12.948737130472315,
                "humidity": 41.30530831404518,
                "wind_speed": 11.470999449979942,
                "precipitation": 2.0600425715354276,
                "elevation": 3327.1229079420764
                }
            ],
            "analysis_metadata": {
                "area_name": "Sicuani, Cusco, Perú",
                "analysis_type": "fire_risk_prediction",
                "model_version": "regional_v1",
                "total_points_analyzed": 25,
                "csv_file_generated": "sicuani_fire_risk_analysis.csv",
                "analysis_timestamp": "2025-10-05T07:51:52.885774",
                "coordinate_system": "WGS84",
                "region_detected": "South America",
                "specialized_model_used": "Regional-Sudamérica"
            }
            })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500