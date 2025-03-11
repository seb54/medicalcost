import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text
import os
from loguru import logger

# Configuration du Faker
fake = Faker()

def create_database():
    """Crée la base de données et les tables"""
    db_path = 'data/medical_costs.db'
    
    # Suppression de la base de données si elle existe
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("Base de données existante supprimée")
    
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Lecture du fichier SQL
    with open('data/base.sql', 'r') as file:
        sql_commands = file.read()
    
    # Exécution des commandes SQL
    with engine.connect() as conn:
        for command in sql_commands.split(';'):
            if command.strip():
                conn.execute(text(command))
                conn.commit()
    
    return engine

def load_reference_data(engine):
    """Charge les données de référence (sex, smoking, region)"""
    # Données de référence
    sex_data = [('male',), ('female',)]
    smoking_data = [('yes',), ('no',)]
    region_data = [('southwest',), ('southeast',), ('northwest',), ('northeast',)]
    user_type_data = [('admin',), ('user',)]
    
    # Insertion des données
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO SEX (sex_type) VALUES (:sex)"), 
                    [{"sex": sex[0]} for sex in sex_data])
        conn.execute(text("INSERT INTO SMOKING (smoking_status) VALUES (:status)"), 
                    [{"status": status[0]} for status in smoking_data])
        conn.execute(text("INSERT INTO REGION (region_name) VALUES (:region)"), 
                    [{"region": region[0]} for region in region_data])
        conn.execute(text("INSERT INTO USER_TYPE (type_name) VALUES (:type)"), 
                    [{"type": type[0]} for type in user_type_data])
        conn.commit()

def get_reference_id(engine, table, column, value):
    """Récupère l'ID d'une valeur de référence"""
    id_column = {
        'sex': 'id_sex',
        'smoking': 'id_smoking_status',
        'region': 'id_region',
        'user_type': 'id_user_type'
    }
    
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT {id_column[table]} FROM {table.upper()} WHERE {column} = :value"),
            {"value": value}
        ).fetchone()
        return result[0] if result else None

def load_patient_data(engine):
    """Charge les données des patients depuis le CSV"""
    # Lecture du CSV
    df = pd.read_csv('data/insurance.csv')
    
    # Pour chaque ligne du CSV
    for _, row in df.iterrows():
        # Génération d'un ID unique pour le patient
        patient_id = fake.uuid4()
        
        # Récupération des IDs de référence
        sex_id = get_reference_id(engine, 'sex', 'sex_type', row['sex'])
        smoking_id = get_reference_id(engine, 'smoking', 'smoking_status', row['smoker'])
        region_id = get_reference_id(engine, 'region', 'region_name', row['region'])
        
        # Insertion du patient
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO PATIENT 
                    (id_patient, age, nb_children, bmi, insurance_cost, 
                     id_region, id_smoking_status, id_sex)
                    VALUES 
                    (:id, :age, :children, :bmi, :cost, 
                     :region_id, :smoking_id, :sex_id)
                """),
                {
                    "id": patient_id,
                    "age": row['age'],
                    "children": row['children'],
                    "bmi": row['bmi'],
                    "cost": row['charges'],
                    "region_id": region_id,
                    "smoking_id": smoking_id,
                    "sex_id": sex_id
                }
            )
            conn.commit()

def main():
    """Fonction principale"""
    try:
        logger.info("Début du chargement de la base de données")
        
        # Création de la base de données
        engine = create_database()
        logger.info("Base de données créée avec succès")
        
        # Chargement des données de référence
        load_reference_data(engine)
        logger.info("Données de référence chargées avec succès")
        
        # Chargement des données des patients
        load_patient_data(engine)
        logger.info("Données des patients chargées avec succès")
        
        logger.info("Chargement de la base de données terminé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la base de données: {str(e)}")
        raise

if __name__ == "__main__":
    main() 