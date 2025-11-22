import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # API Settings
    API_TITLE = "EyeSense API"
    API_VERSION = "1.0.0"
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Model Settings
    MODEL_PATH = os.getenv("MODEL_PATH", "models/best_eyesense_model.pth")
    IMAGE_SIZE = (224, 224)
    
    # Database Settings (for future use)
    DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/eyesense")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # File Upload
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp'}

config = Config()