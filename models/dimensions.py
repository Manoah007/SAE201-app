# Import de tous les modules nécessaires
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

# Initialisation de la classe de base dont tous nos modèles vont hériter
Base = declarative_base()

# ── Dimensions géographiques ────────────────────────────────────────────

class Region(Base):
    __tablename__ = "region"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True)
    libelle = Column(String(100), nullable=False)
    departements = relationship("Departement", backref="region")
    
    def __repr__(self): 
        return f"{self.code} – {self.libelle}"

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "libelle": self.libelle
        }

class Departement(Base):
    __tablename__ = "departement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True)
    libelle = Column(String(100), nullable=False)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    
    def __repr__(self): 
        return f"{self.code} – {self.libelle}"

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "libelle": self.libelle,
            "region_id": self.region_id
        }

# ── Dimensions métier ────────────────────────────────────────────────

class ProfessionSante(Base):
    __tablename__ = "profession_sante"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)
    
    def __repr__(self): 
        return self.libelle

    def to_dict(self):
        return {
            "id": self.id,
            "libelle": self.libelle
        }

class TrancheAge(Base):
    __tablename__ = "tranche_age"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(100), nullable=False, unique=True)
    
    def __repr__(self): 
        return self.libelle

    def to_dict(self):
        return {
            "id": self.id,
            "libelle": self.libelle
        }

class Sexe(Base):
    __tablename__ = "sexe"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(50), nullable=False, unique=True)
    
    def __repr__(self): 
        return self.libelle

    def to_dict(self):
        return {
            "id": self.id,
            "libelle": self.libelle
        }

# ── Dimensions d’activité ──────────────────────────────────────────────

class TypeExercice(Base):
    __tablename__ = "type_exercice"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)
    
    def __repr__(self): 
        return self.libelle

    def to_dict(self):
        return {
            "id": self.id,
            "libelle": self.libelle
        }

class TypeSecteur(Base):
    __tablename__ = "type_secteur"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    libelle = Column(String(200), nullable=False)
    
    def __repr__(self): 
        return f"{self.code} – {self.libelle}"

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "libelle": self.libelle
        }

# ── Dimensions financières ──────────────────────────────────────────────

class TypeHonoraire(Base):
    __tablename__ = "type_honoraire"
    id = Column(Integer, primary_key=True, autoincrement=True)
    niveau_1 = Column(String(200), nullable=False)
    niveau_2 = Column(String(200), nullable=True)
    niveau_3 = Column(String(200), nullable=True)
    __table_args__ = (UniqueConstraint("niveau_1", "niveau_2", "niveau_3"),)
    
    def __repr__(self): 
        return " > ".join(filter(None, [self.niveau_1, self.niveau_2, self.niveau_3]))

    def to_dict(self):
        return {
            "id": self.id,
            "niveau_1": self.niveau_1,
            "niveau_2": self.niveau_2,
            "niveau_3": self.niveau_3
        }

class TypePrescription(Base):
    __tablename__ = "type_prescription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(200), nullable=False, unique=True)
    
    def __repr__(self): 
        return self.libelle

    def to_dict(self):
        return {
            "id": self.id,
            "libelle": self.libelle
        }