"""
Exemple de configuration pour l'application InsureCost Analytics.
Copiez ce fichier vers config.py et modifiez les valeurs selon vos besoins.
"""

from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "static"

# Configuration de la base de données
DB_PATH = "data/medical_costs.db"

# Configuration de la base de données (format dictionnaire pour les tests)
DB_CONFIG = {
    "path": DB_PATH,
    "backup_path": "data/backups/medical_costs_backup.db",
    "max_connections": 10,
    "timeout": 30,
    "echo": False,
}

# Configuration de l'authentification
AUTH_CONFIG = {
    "ADMIN_USERNAME": "seb",
    "ADMIN_PASSWORD": "password123",
    "ADMIN_EMAIL": "admin@example.com",
    "LOGIN_ATTEMPTS_LIMIT": 3,
    "LOGIN_TIMEOUT_SECONDS": 300,
}

# Configuration de sécurité
SECURITY_CONFIG = {
    "secret_key": "CHANGEZ_MOI_EN_PRODUCTION",  # À remplacer par une vraie clé secrète
    "session_expiry": 1800,  # 30 minutes
    "max_login_attempts": 3,
    "lockout_duration": 300,  # 5 minutes
    "password_min_length": 12,  # Longueur minimale recommandée
    "require_special_chars": True,
    "require_numbers": True,
    "require_uppercase": True,
}

# Configuration du modèle
MODEL_CONFIG = {
    "production_model_path": str(MODELS_DIR / "production_model.pkl"),
    "model_version": "1.0.0",
    "input_features": ["age", "sex", "bmi", "nb_children", "smoker", "region"],
    "categorical_features": ["sex", "smoker", "region"],
    "numerical_features": ["age", "bmi", "nb_children"],
    "target_feature": "insurance_cost",
}

# Configuration des validations
VALIDATION_CONFIG = {
    "age": {
        "min": 18,
        "max": 100,
        "type": (int, float),
    },
    "bmi": {
        "min": 10.0,
        "max": 50.0,
        "type": float,
        "warning_low": 18.5,
        "warning_high": 30.0,
    },
    "children": {
        "min": 0,
        "max": 10,
        "type": int,
    },
    "sex": {
        "values": ["male", "female"],
        "type": str,
    },
    "smoker": {
        "values": ["yes", "no"],
        "type": str,
    },
    "region": {
        "values": ["southwest", "southeast", "northwest", "northeast"],
        "type": str,
    },
}

# Configuration des messages (peut être personnalisé selon la langue)
MESSAGES = {
    "errors": {
        "auth": {
            "invalid_credentials": "Identifiants invalides",
            "account_locked": "Compte temporairement verrouillé",
            "session_expired": "Session expirée",
        },
        "validation": {
            "age_range": "L'âge doit être compris entre {min} et {max} ans",
            "bmi_range": "L'IMC doit être compris entre {min:.1f} et {max:.1f}",
            "children_range": "Le nombre d'enfants doit être compris entre {min} et {max}",
            "invalid_sex": "Le sexe doit être 'male' ou 'female'",
            "invalid_smoker": "Le statut tabagique doit être 'yes' ou 'no'",
            "invalid_region": "La région n'est pas valide",
        },
        "model": {
            "load_error": "Erreur lors du chargement du modèle",
            "prediction_error": "Erreur lors de la prédiction",
        },
    },
    "warnings": {
        "bmi_low": "IMC inférieur à la normale (< {value})",
        "bmi_high": "IMC indiquant une obésité (> {value})",
        "smoker": "Le tabagisme augmente significativement les coûts d'assurance",
    },
    "success": {
        "prediction": "Prédiction calculée avec succès",
        "login": "Connexion réussie",
        "logout": "Déconnexion réussie",
    },
}

# Configuration des exports
EXPORT_CONFIG = {
    "allowed_formats": ["csv", "xlsx", "json"],
    "max_export_rows": 5000,  # Limite par défaut réduite
    "export_dir": str(DATA_DIR / "exports"),
}
