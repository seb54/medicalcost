import os
import sys
from pathlib import Path
import uuid
import pytest
from sqlalchemy import text
from modules.db_loader import create_database, get_reference_id, load_patient_data

# Ajout du chemin du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_db():
    """Crée une base de test temporaire"""
    # Création d'un nom unique pour la base de test
    test_db_name = f"test_medical_costs_{uuid.uuid4()}.db"
    test_db_path = Path("data") / test_db_name

    # Création de la base
    engine = create_database(
        test_mode=True, force_recreate=True, db_path=str(test_db_path)
    )

    yield engine

    # Fermeture des connexions
    if engine is not None:
        engine.dispose()

    # Nettoyage après les tests
    try:
        if test_db_path.exists():
            os.remove(test_db_path)
    except Exception as e:
        print(f"Erreur lors du nettoyage de la base de test : {e}")


def test_create_database(test_db):
    """Test de la création de la base de données"""
    assert test_db is not None

    # Vérification de la création des tables
    with test_db.connect() as conn:
        tables = [
            "SEX",
            "SMOKING",
            "REGION",
            "USER_TYPE",
            "PATIENT",
            "USER_ACCOUNT",
            "manages",
        ]
        result = conn.execute(
            text(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ("
                + ",".join([f"'{t}'" for t in tables])
                + ")"
            )
        ).fetchone()
        assert result[0] == len(tables)


def test_reference_data_loaded(test_db):
    """Test que les données de référence sont bien chargées"""
    # Vérification des données de référence
    expected_counts = {
        "SEX": [("male",), ("female",)],
        "SMOKING": [("yes",), ("no",)],
        "REGION": [("southwest",), ("southeast",), ("northwest",), ("northeast",)],
        "USER_TYPE": [("admin",), ("user",)],
    }

    # Mapping des noms de colonnes pour chaque table
    column_names = {
        "SEX": "sex_type",
        "SMOKING": "smoking_status",
        "REGION": "region_name",
        "USER_TYPE": "type_name",
    }

    with test_db.connect() as conn:
        for table, expected_data in expected_counts.items():
            # Vérification du nombre d'enregistrements
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
            assert count == len(
                expected_data
            ), f"Nombre incorrect d'enregistrements dans {table}"

            # Vérification des valeurs
            column = column_names[table]
            values = conn.execute(
                text(f"SELECT {column} FROM {table} ORDER BY {column}")
            ).fetchall()
            assert sorted(values) == sorted(
                expected_data
            ), f"Valeurs incorrectes dans {table}"


def test_get_reference_id(test_db):
    """Test de la récupération des IDs de référence"""
    # Test de récupération d'IDs existants
    test_cases = [
        ("sex", "sex_type", "male"),
        ("smoking", "smoking_status", "yes"),
        ("region", "region_name", "southwest"),
    ]

    for table, column, value in test_cases:
        assert get_reference_id(test_db, table, column, value) is not None

    # Test avec une valeur inexistante
    assert get_reference_id(test_db, "sex", "sex_type", "invalid") is None


def test_load_patient_data(test_db):
    """Test du chargement des données des patients"""
    load_patient_data(test_db)

    with test_db.connect() as conn:
        # Vérification en une seule requête
        result = conn.execute(
            text(
                """
            SELECT
                (SELECT COUNT(*) FROM PATIENT) as patient_count,
                (SELECT COUNT(*) FROM PATIENT p
                WHERE NOT EXISTS (SELECT 1 FROM SEX s WHERE s.id_sex = p.id_sex)
                OR NOT EXISTS (SELECT 1 FROM SMOKING sm WHERE sm.id_smoking_status = p.id_smoking_status)
                OR NOT EXISTS (SELECT 1 FROM REGION r WHERE r.id_region = p.id_region)) as invalid_count
            """
            )
        ).fetchone()

        assert result[0] > 0  # Il y a des patients
        assert result[1] == 0  # Pas de violations de clés étrangères


def test_admin_account_created(test_db):
    """Test que le compte admin est bien créé"""
    with test_db.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT ua.*, ut.type_name
                FROM USER_ACCOUNT ua
                JOIN USER_TYPE ut ON ua.id_user_type = ut.id_user_type
                WHERE ua.username = 'seb'
                """
            )
        ).fetchone()

        assert result is not None
        assert result.username == "seb"
        assert result.type_name == "admin"
