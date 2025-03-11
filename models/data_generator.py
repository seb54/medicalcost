from faker import Faker
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import random
from loguru import logger
import uuid

class MedicalDataGenerator:
    def __init__(self):
        self.fake = Faker('fr_FR')
        self.engine = create_engine('sqlite:///data/medical_costs.db')
        
    def get_valid_references(self):
        """Récupère les IDs valides des tables de référence"""
        try:
            with self.engine.connect() as conn:
                sex_ids = pd.read_sql("SELECT id_sex FROM SEX", conn)['id_sex'].tolist()
                smoking_ids = pd.read_sql("SELECT id_smoking_status FROM SMOKING", conn)['id_smoking_status'].tolist()
                region_ids = pd.read_sql("SELECT id_region FROM REGION", conn)['id_region'].tolist()
                
                return {
                    'sex_ids': sex_ids,
                    'smoking_ids': smoking_ids,
                    'region_ids': region_ids
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des références : {str(e)}")
            return None
        
    def generate_synthetic_patient(self, refs):
        """Génère un patient avec des données synthétiques selon la structure existante"""
        return {
            'id_patient': str(uuid.uuid4()),  # Génère un ID unique
            'age': random.randint(18, 85),
            'nb_children': random.randint(0, 5),
            'bmi': round(random.uniform(18.5, 35.0), 1),
            'insurance_cost': round(random.uniform(1000, 50000), 2),
            'id_sex': random.choice(refs['sex_ids']),
            'id_smoking_status': random.choice(refs['smoking_ids']),
            'id_region': random.choice(refs['region_ids'])
        }
        
    def generate_dataset(self, n_records=1000):
        """Génère un nouveau dataset synthétique"""
        logger.info(f"Génération de {n_records} enregistrements synthétiques...")
        
        # Récupération des références valides
        refs = self.get_valid_references()
        if not refs:
            logger.error("Impossible de générer les données sans références valides")
            return None
        
        # Génération des données
        synthetic_data = [self.generate_synthetic_patient(refs) for _ in range(n_records)]
        df = pd.DataFrame(synthetic_data)
        
        # Sauvegarde dans la base de données
        try:
            df.to_sql('PATIENT', self.engine, if_exists='append', index=False)
            logger.success(f"{n_records} enregistrements synthétiques ajoutés à la base de données")
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données : {str(e)}")
            return None

    def generate_csv(self, n_records=1000, output_file='synthetic_data.csv'):
        """Génère un fichier CSV avec des données synthétiques"""
        refs = self.get_valid_references()
        if not refs:
            logger.error("Impossible de générer les données sans références valides")
            return None
            
        try:
            df = pd.DataFrame([self.generate_synthetic_patient(refs) for _ in range(n_records)])
            df.to_csv(output_file, index=False)
            logger.success(f"{n_records} enregistrements synthétiques sauvegardés dans {output_file}")
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la génération du CSV : {str(e)}")
            return None

if __name__ == "__main__":
    generator = MedicalDataGenerator()
    
    # Génération de données synthétiques et sauvegarde en CSV
    generator.generate_csv(n_records=100, output_file='data/synthetic_patients.csv')
    
    # Génération et ajout à la base de données
    generator.generate_dataset(n_records=100)