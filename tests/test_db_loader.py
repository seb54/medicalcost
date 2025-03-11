import pytest
import os
import pandas as pd
from sqlalchemy import create_engine, text
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.db_loader import create_database, load_reference_data, get_reference_id, load_patient_data

@pytest.fixture
def test_db():
    """Fixture pour créer une base de données de test"""
    test_db_path = 'data/test_medical_costs.db'
    engine = create_engine(f'sqlite:///{test_db_path}')
    yield engine
    # Nettoyage après les tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_create_database(test_db):
    """Test de la création de la base de données"""
    engine = create_database()
    assert engine is not None
    
    # Vérification de la création des tables
    with engine.connect() as conn:
        # Vérification de l'existence des tables
        tables = ['SEX', 'SMOKING', 'REGION', 'USER_TYPE', 'PATIENT', 'USER_ACCOUNT', 'manages']
        for table in tables:
            result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
            assert result.fetchone() is not None

def test_load_reference_data(test_db):
    """Test du chargement des données de référence"""
    load_reference_data(test_db)
    
    # Vérification des données de référence
    with test_db.connect() as conn:
        # Test SEX
        result = conn.execute(text("SELECT COUNT(*) FROM SEX")).fetchone()
        assert result[0] == 2
        
        # Test SMOKING
        result = conn.execute(text("SELECT COUNT(*) FROM SMOKING")).fetchone()
        assert result[0] == 2
        
        # Test REGION
        result = conn.execute(text("SELECT COUNT(*) FROM REGION")).fetchone()
        assert result[0] == 4
        
        # Test USER_TYPE
        result = conn.execute(text("SELECT COUNT(*) FROM USER_TYPE")).fetchone()
        assert result[0] == 2

def test_get_reference_id(test_db):
    """Test de la récupération des IDs de référence"""
    load_reference_data(test_db)
    
    # Test de récupération d'IDs existants
    sex_id = get_reference_id(test_db, 'sex', 'sex_type', 'male')
    assert sex_id is not None
    
    smoking_id = get_reference_id(test_db, 'smoking', 'smoking_status', 'yes')
    assert smoking_id is not None
    
    region_id = get_reference_id(test_db, 'region', 'region_name', 'southwest')
    assert region_id is not None
    
    # Test avec une valeur inexistante
    invalid_id = get_reference_id(test_db, 'sex', 'sex_type', 'invalid')
    assert invalid_id is None

def test_load_patient_data(test_db):
    """Test du chargement des données des patients"""
    # Préparation de la base de données
    load_reference_data(test_db)
    
    # Chargement des données des patients
    load_patient_data(test_db)
    
    # Vérification des données
    with test_db.connect() as conn:
        # Vérification du nombre de patients
        result = conn.execute(text("SELECT COUNT(*) FROM PATIENT")).fetchone()
        assert result[0] > 0
        
        # Vérification des contraintes de clés étrangères
        result = conn.execute(text("""
            SELECT COUNT(*) FROM PATIENT p
            WHERE NOT EXISTS (SELECT 1 FROM SEX s WHERE s.id_sex = p.id_sex)
            OR NOT EXISTS (SELECT 1 FROM SMOKING sm WHERE sm.id_smoking_status = p.id_smoking_status)
            OR NOT EXISTS (SELECT 1 FROM REGION r WHERE r.id_region = p.id_region)
        """)).fetchone()
        assert result[0] == 0  # Aucune violation de clé étrangère 