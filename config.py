import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '400'))

    # Pricing Bounds Configuration
    PRICE_INCREASE_MAX = float(os.getenv('PRICE_INCREASE_MAX', '1.3'))
    PRICE_DECREASE_MAX = float(os.getenv('PRICE_DECREASE_MAX', '0.7'))
    CONSERVATIVE_PRICE_ADJUSTMENT = float(os.getenv('CONSERVATIVE_PRICE_ADJUSTMENT', '1.05'))
    
    # Weight Configuration
    DEFAULT_INTERNAL_WEIGHT = float(os.getenv('DEFAULT_INTERNAL_WEIGHT', '0.6'))
    DEFAULT_EXTERNAL_WEIGHT = float(os.getenv('DEFAULT_EXTERNAL_WEIGHT', '0.4'))
    
    # Weather Thresholds
    HIGH_TEMPERATURE_THRESHOLD = float(os.getenv('HIGH_TEMPERATURE_THRESHOLD', '30'))
    LOW_TEMPERATURE_THRESHOLD = float(os.getenv('LOW_TEMPERATURE_THRESHOLD', '10'))
    EXTREME_HIGH_TEMPERATURE = float(os.getenv('EXTREME_HIGH_TEMPERATURE', '35'))
    EXTREME_LOW_TEMPERATURE = float(os.getenv('EXTREME_LOW_TEMPERATURE', '5'))
    
    # Event Configuration
    EVENT_PROXIMITY_THRESHOLD = float(os.getenv('EVENT_PROXIMITY_THRESHOLD', '5'))
    EVENT_FAR_DISTANCE = float(os.getenv('EVENT_FAR_DISTANCE', '5'))
    
    # Competitor Configuration
    HIGH_COMPETITOR_COUNT = int(os.getenv('HIGH_COMPETITOR_COUNT', '3'))
    
    # App Configuration
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', '5000'))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Default Values
    DEFAULT_LOCATION = os.getenv('DEFAULT_LOCATION', 'default')