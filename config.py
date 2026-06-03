import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de l'application."""
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
 
    @classmethod
    def db_url(cls):
        """Construit l'URL de connexion MySQL."""
        return (f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}"
                f"@{cls.DB_HOST}/{cls.DB_NAME}")