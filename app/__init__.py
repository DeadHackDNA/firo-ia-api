from flask import Flask
from app.routes.home_routes import home_bp

def create_app():
    app = Flask(__name__)

    # Registrar el blueprint de las rutas
    app.register_blueprint(home_bp)

    return app
