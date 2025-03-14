"""Configuration des tests"""

import os
import sys
import glob
from pathlib import Path

# Ajout du répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def pytest_sessionfinish(session, exitstatus):
    """Nettoie les bases de données de test après l'exécution des tests"""
    data_dir = root_dir / "data"
    test_pattern = str(data_dir / "test_medical_costs_*.db")

    # Suppression des bases de test
    for db_file in glob.glob(test_pattern):
        try:
            os.remove(db_file)
            print(f"Base de test supprimée : {db_file}")
        except Exception as e:
            print(f"Erreur lors de la suppression de {db_file}: {e}")
