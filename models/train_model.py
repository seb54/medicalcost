import pandas as pd
import os
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import mlflow
import mlflow.sklearn
from loguru import logger
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

# Obtenir le chemin absolu du répertoire racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration MLflow avec chemin absolu
mlflow_dir = os.path.join(BASE_DIR, "mlruns")
mlflow.set_tracking_uri(f"file:{mlflow_dir}")
experiment = mlflow.set_experiment("cost_prediction")
experiment_dir = os.path.join(mlflow_dir, str(experiment.experiment_id))
os.makedirs(experiment_dir, exist_ok=True)


def save_production_model_uri(run_id):
    """Sauvegarde l'URI du modèle de production"""
    model_uri = f"runs:/{run_id}/model"
    production_path = os.path.join(
        mlflow_dir, experiment.experiment_id, "production_model_uri.txt"
    )
    with open(production_path, "w") as f:
        f.write(model_uri)
    print(f"URI du modèle de production sauvegardé : {model_uri}")


def load_data():
    """Charge les données depuis la base de données"""
    # Utiliser un chemin absolu pour la base de données
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "medical_costs.db")
    engine = create_engine(f"sqlite:///{db_path}")
    query = """
    SELECT
        p.age,
        p.nb_children,
        p.bmi,
        p.insurance_cost,
        s.sex_type as sex,
        sm.smoking_status as smoker,
        r.region_name as region
    FROM PATIENT p
    JOIN SEX s ON p.id_sex = s.id_sex
    JOIN SMOKING sm ON p.id_smoking_status = sm.id_smoking_status
    JOIN REGION r ON p.id_region = r.id_region
    """
    return pd.read_sql(query, engine)


def prepare_data(df):
    """Prépare les données pour l'entraînement"""
    # Feature Engineering
    df = df.copy()

    # Création des features catégorielles
    df["bmi_category"] = pd.cut(
        df["bmi"],
        bins=[0, 18.5, 25, 30, float("inf")],
        labels=["Underweight", "Normal", "Overweight", "Obese"],
    )

    df["age_group"] = pd.cut(
        df["age"],
        bins=[0, 25, 35, 45, 55, float("inf")],
        labels=["18-25", "26-35", "36-45", "46-55", "55+"],
    )

    # Création des features d'interaction
    df["is_smoker"] = (df["smoker"] == "yes").astype(int)
    df["bmi_smoker"] = df["bmi"] * df["is_smoker"]
    df["age_smoker"] = df["age"] * df["is_smoker"]

    # Définition des features
    numeric_features = ["age", "bmi", "nb_children", "bmi_smoker", "age_smoker"]
    categorical_features = ["sex", "smoker", "region", "bmi_category", "age_group"]

    # Sélection des colonnes pour X
    X = df[numeric_features + categorical_features]
    y = df["insurance_cost"]

    # Sauvegarde des colonnes pour la prédiction
    feature_columns = X.columns.tolist()

    return X, y, numeric_features, categorical_features, feature_columns


def create_model():
    """Crée le modèle RandomForest avec son pipeline de prétraitement"""
    numeric_features = ["age", "bmi", "nb_children", "bmi_smoker", "age_smoker"]
    categorical_features = ["sex", "smoker", "region", "bmi_category", "age_group"]

    # Création du préprocesseur
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            (
                "cat",
                OneHotEncoder(drop="first", sparse_output=False),
                categorical_features,
            ),
        ]
    )

    # Création du modèle
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
    )

    # Création du pipeline
    return Pipeline([("preprocessor", preprocessor), ("regressor", model)])


def log_results(
    model, X, y, X_test, y_test, numeric_features, categorical_features, feature_columns
):
    """Log les résultats et le modèle dans MLflow"""
    # Prédictions et métriques
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Log des paramètres et métriques
    mlflow.log_param("feature_columns", str(feature_columns))
    mlflow.log_param("numeric_features", str(numeric_features))
    mlflow.log_param("categorical_features", str(categorical_features))
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("r2", r2)

    # Log du modèle avec son pipeline
    mlflow.sklearn.log_model(model, "model")

    # Sauvegarde de l'URI du modèle
    run = mlflow.active_run()
    model_uri = f"runs:/{run.info.run_id}/model"

    # Sauvegarde de l'URI dans un fichier
    experiment = mlflow.get_experiment(run.info.experiment_id)
    production_path = os.path.join(
        mlflow_dir, experiment.experiment_id, "production_model_uri.txt"
    )
    with open(production_path, "w") as f:
        f.write(model_uri)

    logger.info(f"Modèle et résultats sauvegardés avec MLflow.")
    logger.info(f"URI du modèle de production sauvegardé : {model_uri}")

    return mse, r2


def main():
    """Fonction principale d'entraînement"""
    # Configuration de MLflow
    mlflow.set_tracking_uri(f"file:{mlflow_dir}")
    mlflow.set_experiment("cost_prediction")

    # Chargement et préparation des données
    logger.info("Chargement des données...")
    df = load_data()
    X, y, numeric_features, categorical_features, feature_columns = prepare_data(df)

    # Split des données
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Création et entraînement du modèle
    model = create_model()
    model.fit(X_train, y_train)

    # Log des résultats avec MLflow
    with mlflow.start_run():
        mse, r2 = log_results(
            model,
            X_train,
            y_train,
            X_test,
            y_test,
            numeric_features,
            categorical_features,
            feature_columns,
        )
        print("\nRésultats du modèle :")
        logger.info(f"MSE: {mse:.2f}")
        logger.info(f"R²: {r2:.4f}")


if __name__ == "__main__":
    main()
