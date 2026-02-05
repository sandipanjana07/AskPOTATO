import os
from pathlib import Path

# base directory of the app
BASE_DIR = Path(__file__).parent


class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Database
    DATABASE = os.getenv('DATABASE_PATH', str(BASE_DIR / 'potato.db'))
    
    # File upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt', 'docx'}
    
    # Ollama settings
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
    OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '120'))
    
    # Pagination
    SCENARIOS_PER_PAGE = 20
    
    # Default step count for new scenarios
    DEFAULT_STEPS_COUNT = 10
