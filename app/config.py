import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'function-mall-super-secret-key-gold-luxury-2025')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-super-secret-mall-key-2025')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Database config: default to SQLite for robust local out-of-the-box running, configurable to PostgreSQL/MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'function_mall.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
