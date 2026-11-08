from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads dir exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.categories import categories_bp
    from .routes.halls import halls_bp
    from .routes.packages import packages_bp
    from .routes.bookings import bookings_bp
    from .routes.payments import payments_bp
    from .routes.owner import owner_bp
    from .routes.admin import admin_bp
    from .routes.common import common_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(halls_bp, url_prefix='/api/halls')
    app.register_blueprint(packages_bp, url_prefix='/api/packages')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(owner_bp, url_prefix='/api/owner')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(common_bp, url_prefix='/api/common')

    @app.route('/api/health', methods=['GET'])
    def health():
        return {"status": "ok", "message": "Function Mall API is live and healthy"}

    return app
