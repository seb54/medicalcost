"""Tests pour le module auth.py"""

import pytest
import uuid
import os
from pathlib import Path
from sqlalchemy import text
from modules.auth import hash_password, verify_password, create_user, verify_user
from modules.db_loader import create_database


@pytest.fixture
def test_db():
    """Fixture pour créer une base de test"""
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


def test_hash_password():
    """Test du hashage de mot de passe"""
    # Test avec un mot de passe simple
    password = "test123"
    hashed = hash_password(password)

    # Vérifications
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password
    assert len(hashed) > 0


def test_verify_password():
    """Test de la vérification de mot de passe"""
    # Test avec un mot de passe correct
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

    # Test avec un mauvais mot de passe
    wrong_password = "wrong123"
    assert verify_password(wrong_password, hashed) is False


def test_create_user(test_db):
    """Test de la création d'utilisateur"""
    # Test création d'un utilisateur normal
    username = "testuser"
    password = "testpass"
    email = "test@test.com"

    # Création de l'utilisateur
    create_user(test_db, username, password, email)

    # Vérification en base
    with test_db.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT ua.username, ua.email, ut.type_name
                FROM USER_ACCOUNT ua
                JOIN USER_TYPE ut ON ua.id_user_type = ut.id_user_type
                WHERE ua.username = :username
            """
            ),
            {"username": username},
        ).fetchone()

        assert result is not None
        assert result[0] == username
        assert result[1] == email
        assert result[2] == "user"  # type par défaut

    # Test création d'un admin
    admin_username = "testadmin"
    create_user(test_db, admin_username, password, email, is_admin=True)

    with test_db.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT ut.type_name
                FROM USER_ACCOUNT ua
                JOIN USER_TYPE ut ON ua.id_user_type = ut.id_user_type
                WHERE ua.username = :username
            """
            ),
            {"username": admin_username},
        ).fetchone()

        assert result is not None
        assert result[0] == "admin"


def test_create_user_duplicate(test_db):
    """Test de la création d'un utilisateur en doublon"""
    username = "duplicate"
    password = "testpass"

    # Première création
    create_user(test_db, username, password)

    # Deuxième création avec le même username
    with pytest.raises(Exception):
        create_user(test_db, username, password)


def test_verify_user(test_db):
    """Test de la vérification d'utilisateur"""
    # Création d'un utilisateur de test
    username = "testuser"
    password = "testpass"
    email = "test@test.com"
    create_user(test_db, username, password, email)

    # Test avec identifiants corrects
    user_info = verify_user(test_db, username, password)
    assert user_info is not None
    assert user_info["username"] == username
    assert user_info["email"] == email
    assert user_info["is_admin"] is False

    # Test avec mauvais mot de passe
    assert verify_user(test_db, username, "wrongpass") is None

    # Test avec utilisateur inexistant
    assert verify_user(test_db, "nonexistent", password) is None


def test_verify_user_admin(test_db):
    """Test de la vérification d'un utilisateur admin"""
    # Création d'un admin
    username = "testadmin"
    password = "adminpass"
    email = "admin@test.com"
    create_user(test_db, username, password, email, is_admin=True)

    # Vérification
    user_info = verify_user(test_db, username, password)
    assert user_info is not None
    assert user_info["username"] == username
    assert user_info["email"] == email
    assert user_info["is_admin"] is True
