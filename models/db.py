from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

# Un seul moteur pour toute l'application
engine = create_engine(Config.db_url(), pool_recycle=3600)

# Fabrique de sessions : chaque requête HTTP utilisera sa propre session
Session = sessionmaker(bind=engine)