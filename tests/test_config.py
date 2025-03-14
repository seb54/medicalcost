"""Tests pour le module config.py"""

import os
from pathlib import Path
import pytest
from config import (
    BASE_DIR,
    DATA_DIR,
    MODELS_DIR,
    STATIC_DIR,
    DB_CONFIG,
    SECURITY_CONFIG,
    MODEL_CONFIG,
    VALIDATION_CONFIG,
    MESSAGES,
    EXPORT_CONFIG,
)


def test_base_paths():
    """Test des chemins de base"""
    # Vérification que les chemins sont des objets Path
    assert isinstance(BASE_DIR, Path)
    assert isinstance(DATA_DIR, Path)
    assert isinstance(MODELS_DIR, Path)
    assert isinstance(STATIC_DIR, Path)

    # Vérification que les répertoires sont bien relatifs à BASE_DIR
    assert DATA_DIR == BASE_DIR / "data"
    assert MODELS_DIR == BASE_DIR / "models"
    assert STATIC_DIR == BASE_DIR / "static"

    # Vérification que BASE_DIR pointe vers le répertoire du projet
    # Accepter soit "sas-ia-projet" (local) soit "medicalcost" (GitHub Actions)
    assert BASE_DIR.name in ["sas-ia-projet", "medicalcost"]


def test_db_config():
    """Test de la configuration de la base de données"""
    # Vérification des clés requises
    required_keys = ["path", "backup_path", "max_connections", "timeout"]
    for key in required_keys:
        assert key in DB_CONFIG

    # Vérification des types
    assert isinstance(DB_CONFIG["path"], str)
    assert isinstance(DB_CONFIG["backup_path"], str)
    assert isinstance(DB_CONFIG["max_connections"], int)
    assert isinstance(DB_CONFIG["timeout"], int)

    # Vérification des valeurs
    assert DB_CONFIG["max_connections"] > 0
    assert DB_CONFIG["timeout"] > 0
    # Accepter soit "patients.db" (config.py original) soit "medical_costs.db" (config.example.py)
    assert any(
        db_name in DB_CONFIG["path"] for db_name in ["patients.db", "medical_costs.db"]
    )
    # Vérifier que le chemin de backup contient "backup" ou "backups"
    assert any(
        backup_dir in DB_CONFIG["backup_path"] for backup_dir in ["backup", "backups"]
    )


def test_security_config():
    """Test de la configuration de sécurité"""
    # ... reste du code inchangé ...
