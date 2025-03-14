import os

# import pandas as pd  # Non utilisé, commenté pour éviter l'erreur F401
from sqlalchemy import create_engine, text
from loguru import logger

# import bcrypt  # Non utilisé, commenté pour éviter l'erreur F401

from faker import Faker
from sqlalchemy import Engine

# Configuration du Faker
fake = Faker()


def get_db_path(test_mode: bool = False, db_path: str = None) -> str:
    """Détermine le chemin de la base de données.

    Args:
        test_mode: Si True, utilise la base de test
        db_path: Chemin personnalisé de la base de données

    Returns:
        Le chemin de la base de données
    """
    if db_path is None:
        db_path = "data/test_medical_costs.db" if test_mode else "data/medical_costs.db"

    # Création du dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    return db_path


def remove_database(db_path: str) -> bool:
    """Supprime la base de données existante.

    Args:
        db_path: Chemin de la base de données

    Returns:
        True si la suppression a réussi, False sinon
    """
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Ancienne base supprimée")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'ancienne base : {e}")
        return False


def is_database_valid(engine: Engine) -> bool:
    """Vérifie si la base de données est valide.

    Args:
        engine: Connexion à la base de données

    Returns:
        True si la base est valide, False sinon
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).fetchall()
            return bool(result)
    except Exception as e:
        logger.error(f"Base existante mais invalide : {str(e)}")
        return False


def initialize_database(engine: Engine) -> bool:
    """Initialise la base de données avec les tables et les données.

    Args:
        engine: Connexion à la base de données

    Returns:
        True si l'initialisation a réussi, False sinon
    """
    try:
        # Lecture et exécution du script SQL
        with open("data/base.sql", "r", encoding="utf-8") as f:
            sql_commands = f.read()

        # Création des tables
        with engine.connect() as conn:
            for command in sql_commands.split(";"):
                if command.strip():
                    conn.execute(text(command))
                    conn.commit()

            logger.info("Tables créées avec succès")

            # Chargement des données de référence d'abord
            load_reference_data(engine)
            logger.info("Données de référence chargées")

            # Puis création du compte admin
            create_admin_account(engine)
            logger.info("Compte admin créé")

            # Enfin chargement des données patients
            load_patient_data(engine)
            logger.info("Données patients chargées")

            logger.info("Base de données créée et initialisée avec succès")

        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création de la base : {str(e)}")
        return False


def create_database(
    test_mode: bool = False, force_recreate: bool = False, db_path: str = None
) -> Engine:
    """Crée la base de données si elle n'existe pas.

    Args:
        test_mode: Si True, utilise la base de test
        force_recreate: Si True, force la recréation de la base
        db_path: Chemin personnalisé de la base de données

    Returns:
        Engine: Connexion à la base de données ou None en cas d'erreur
    """
    logger.info("Début de la création/vérification de la base de données")

    # Détermination du chemin de la base
    db_path = get_db_path(test_mode, db_path)

    # Suppression de l'ancienne base si demandé
    if force_recreate and not remove_database(db_path):
        return None

    # Création de l'engine
    engine = create_engine(f"sqlite:///{db_path}")

    # Si la base existe et qu'on ne force pas la recréation, on vérifie juste si elle est valide
    if os.path.exists(db_path) and not force_recreate:
        if is_database_valid(engine):
            logger.info("Base de données existante et valide")
            return engine
        else:
            # On va recréer la base
            force_recreate = True
            if not remove_database(db_path):
                return None

    # Initialisation de la base de données
    if initialize_database(engine):
        return engine
    else:
        # Nettoyage en cas d'échec
        remove_database(db_path)
        return None


def create_admin_account(engine):
    """Crée le compte administrateur"""
    logger.info("Création du compte administrateur")

    # Mot de passe par défaut pour l'admin (à changer en production)
    admin_username = "seb"
    admin_password = "password123"  # En pratique, utiliser un mot de passe fort
    admin_email = "admin@example.com"

    with engine.connect() as conn:
        try:
            # Vérification de l'existence du type admin
            admin_type = conn.execute(
                text("SELECT id_user_type FROM USER_TYPE WHERE type_name = 'admin'")
            ).fetchone()

            if not admin_type:
                logger.error("Type admin non trouvé dans USER_TYPE")
                return

            admin_type_id = admin_type[0]

            # Vérification si le compte admin existe déjà
            existing_admin = conn.execute(
                text(
                    "SELECT id_user_account FROM USER_ACCOUNT WHERE username = :username"
                ),
                {"username": admin_username},
            ).fetchone()

            if existing_admin:
                logger.info("Le compte admin existe déjà")
                return

            # Création d'un hash de mot de passe (simulé ici)
            # En production, utiliser bcrypt ou un autre algorithme sécurisé
            password_hash = f"hashed_{admin_password}"

            # Insertion du compte admin
            conn.execute(
                text(
                    """
                INSERT INTO USER_ACCOUNT (username, email, password_hash, id_user_type)
                VALUES (:username, :email, :password_hash, :id_user_type)
                """
                ),
                {
                    "username": admin_username,
                    "email": admin_email,
                    "password_hash": password_hash,
                    "id_user_type": admin_type_id,
                },
            )

            conn.commit()
            logger.info("Compte administrateur créé avec succès")

        except Exception as e:
            logger.error(f"Erreur lors de la création du compte admin: {str(e)}")
            conn.rollback()


def load_reference_data(engine):
    """Charge les données de référence dans la base de données.

    Cette fonction insère les données de référence (sexe, statut tabagique, région)
    dans les tables correspondantes.

    Args:
        engine: Connexion à la base de données
    """
    logger.info("Chargement des données de référence")
    with engine.connect() as conn:
        # Insertion des données de sexe
        conn.execute(text("INSERT INTO SEX (sex_type) VALUES ('male')"))
        conn.execute(text("INSERT INTO SEX (sex_type) VALUES ('female')"))

        # Insertion des données de statut tabagique
        conn.execute(text("INSERT INTO SMOKING (smoking_status) VALUES ('yes')"))
        conn.execute(text("INSERT INTO SMOKING (smoking_status) VALUES ('no')"))

        # Insertion des données de région
        conn.execute(text("INSERT INTO REGION (region_name) VALUES ('southwest')"))
        conn.execute(text("INSERT INTO REGION (region_name) VALUES ('southeast')"))
        conn.execute(text("INSERT INTO REGION (region_name) VALUES ('northwest')"))
        conn.execute(text("INSERT INTO REGION (region_name) VALUES ('northeast')"))

        # Insertion des types d'utilisateurs
        conn.execute(text("INSERT INTO USER_TYPE (type_name) VALUES ('admin')"))
        conn.execute(text("INSERT INTO USER_TYPE (type_name) VALUES ('user')"))

        conn.commit()


def load_patient_data(engine):
    """Charge les données des patients dans la base de données.

    Cette fonction génère des données aléatoires pour les patients
    et les insère dans la table PATIENT.

    Args:
        engine: Connexion à la base de données
    """
    logger.info("Chargement des données des patients")

    # Nombre de patients à générer
    nb_patients = 1000

    with engine.connect() as conn:
        # Récupération des IDs de référence
        sex_ids = conn.execute(text("SELECT id_sex FROM SEX")).fetchall()
        smoking_ids = conn.execute(
            text("SELECT id_smoking_status FROM SMOKING")
        ).fetchall()
        region_ids = conn.execute(text("SELECT id_region FROM REGION")).fetchall()

        # Génération et insertion des données patients
        for _ in range(nb_patients):
            # Génération de données aléatoires
            age = fake.random_int(min=18, max=65)
            bmi = round(fake.random_number(digits=2, fix_len=False) % 35 + 15, 1)
            nb_children = fake.random_int(min=0, max=5)

            # Sélection aléatoire des IDs de référence
            id_sex = fake.random_element(sex_ids)[0]
            id_smoking = fake.random_element(smoking_ids)[0]
            id_region = fake.random_element(region_ids)[0]

            # Calcul d'un coût d'assurance fictif
            base_cost = 5000
            age_factor = age * 50
            bmi_factor = bmi * 300
            children_factor = nb_children * 500
            smoking_factor = 15000 if id_smoking == 1 else 0

            insurance_cost = (
                base_cost + age_factor + bmi_factor + children_factor + smoking_factor
            )
            insurance_cost = round(
                insurance_cost * (0.8 + fake.random.random() * 0.4), 2
            )

            # Insertion dans la base
            conn.execute(
                text(
                    """
                INSERT INTO PATIENT (age, bmi, nb_children, insurance_cost, id_sex, id_smoking_status, id_region)
                VALUES (:age, :bmi, :nb_children, :insurance_cost, :id_sex, :id_smoking, :id_region)
                """
                ),
                {
                    "age": age,
                    "bmi": bmi,
                    "nb_children": nb_children,
                    "insurance_cost": insurance_cost,
                    "id_sex": id_sex,
                    "id_smoking": id_smoking,
                    "id_region": id_region,
                },
            )

        conn.commit()


def get_reference_id(engine, table, column, value):
    """Récupère l'ID d'une valeur de référence dans une table.

    Cette fonction permet de récupérer l'ID correspondant à une valeur
    dans une table de référence (sex, smoking, region, etc.).

    Args:
        engine: Connexion à la base de données
        table: Nom de la table de référence
        column: Nom de la colonne contenant la valeur
        value: Valeur à rechercher

    Returns:
        int: L'ID correspondant à la valeur, ou None si la valeur n'existe pas
    """
    logger.info(f"Récupération de l'ID pour {value} dans {table}.{column}")

    try:
        with engine.connect() as conn:
            # Construction de la requête SQL sécurisée avec paramètres
            # Correction du nom de la colonne ID en fonction de la table
            id_column = f"id_{table}"
            if table == "smoking":
                id_column = "id_smoking_status"

            query = text(
                f"SELECT {id_column} FROM {table.upper()} WHERE {column} = :value"
            )
            result = conn.execute(query, {"value": value}).fetchone()

            if result:
                return result[0]
            else:
                logger.warning(f"Aucun ID trouvé pour {value} dans {table}.{column}")
                return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'ID: {str(e)}")
        return None
