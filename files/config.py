import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'telegram_data')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Scanning Settings
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
    WAIT_TIME = int(os.getenv('WAIT_TIME', 600))  # 10 dakika
    FLOOD_WAIT_TIME = int(os.getenv('FLOOD_WAIT_TIME', 60))
    
    # Database Connection String
    @staticmethod
    def get_db_connection_string():
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
