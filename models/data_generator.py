from faker import Faker
from sqlalchemy import text
import pandas as pd
from sqlalchemy import create_engine, inspect
from loguru import logger


class MedicalDataGenerator:
    def __init__(self):
        self.fake = Faker("fr_FR")
        self.engine = create_engine("sqlite:///data/medical_costs.db")
        self._initialize_name_columns()

    def _initialize_name_columns(self):
        """Initialise les colonnes prenom et nom et met à jour les valeurs manquantes"""
        try:
            inspector = inspect(self.engine)
            existing_columns = [col["name"] for col in inspector.get_columns("PATIENT")]

            with self.engine.connect() as conn:
                # Création des colonnes si nécessaire
                if "prenom" not in existing_columns:
                    logger.info("Ajout de la colonne 'prenom'")
                    conn.execute(text("ALTER TABLE PATIENT ADD COLUMN prenom TEXT"))

                if "nom" not in existing_columns:
                    logger.info("Ajout de la colonne 'nom'")
                    conn.execute(text("ALTER TABLE PATIENT ADD COLUMN nom TEXT"))

                # Mise à jour des valeurs NULL
                result = pd.read_sql(
                    "SELECT id_patient FROM PATIENT WHERE prenom IS NULL OR nom IS NULL",
                    conn,
                )

                if not result.empty:
                    logger.info(
                        f"Mise à jour de {len(result)} enregistrements sans nom..."
                    )
                    for _, row in result.iterrows():
                        conn.execute(
                            text(
                                "UPDATE PATIENT SET prenom = :prenom, nom = :nom WHERE id_patient = :id"
                            ),
                            {
                                "prenom": self.fake.first_name(),
                                "nom": self.fake.last_name(),
                                "id": row["id_patient"],
                            },
                        )

                conn.commit()

                # Afficher un exemple des données
                sample = pd.read_sql(
                    "SELECT id_patient, prenom, nom FROM PATIENT ORDER BY RANDOM() LIMIT 5",
                    conn,
                )
                if not sample.empty:
                    logger.info("Exemple d'enregistrements dans la base :")
                    logger.info(sample)

            logger.success("Initialisation des noms terminée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des noms : {str(e)}")

    def get_valid_references(self):
        """Récupère les IDs valides des tables de référence"""
        try:
            with self.engine.connect() as conn:
                sex_ids = pd.read_sql("SELECT id_sex FROM SEX", conn)["id_sex"].tolist()
                smoking_ids = pd.read_sql(
                    "SELECT id_smoking_status FROM SMOKING", conn
                )["id_smoking_status"].tolist()
                region_ids = pd.read_sql("SELECT id_region FROM REGION", conn)[
                    "id_region"
                ].tolist()

                return {
                    "sex_ids": sex_ids,
                    "smoking_ids": smoking_ids,
                    "region_ids": region_ids,
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des références : {str(e)}")
            return None


if __name__ == "__main__":
    """
    Initialisation du générateur de données médicales.
    Cette initialisation va :
    1. Vérifier l'existence des colonnes prenom et nom
    2. Les créer si elles n'existent pas
    3. Mettre à jour les valeurs NULL avec des noms générés
    """
    generator = MedicalDataGenerator()
