import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn
from sqlalchemy import create_engine, text
from loguru import logger
import os

class CostPredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        
    def train(self, experiment_name="cost_prediction"):
        """Entraîne le modèle et trace les métriques avec MLflow"""
        # Configuration de MLflow
        mlflow.set_experiment(experiment_name)
        
        # Chargement et préparation des données
        df = self.load_data()
        X, y = self.prepare_data(df)
        
        # Split des données
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Création du pipeline
        self.model = Pipeline([
            ('preprocessor', self.preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        # Entraînement avec tracking MLflow
        with mlflow.start_run():
            self.model.fit(X_train, y_train)
            
            # Prédictions et métriques
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Log des paramètres et métriques
            mlflow.log_param("n_estimators", 100)
            mlflow.log_metric("mse", mse)
            mlflow.log_metric("r2", r2)
            
            logger.info(f"Modèle entraîné avec MSE: {mse:.2f} et R²: {r2:.2f}")
            
            return mse, r2
    
    def load_production_model(self):
        """Charge le modèle de production depuis MLflow"""
        try:
            # Configuration MLflow
            mlflow.set_tracking_uri("file:./mlruns")
            experiment = mlflow.get_experiment_by_name("cost_prediction")
            if not experiment:
                raise ValueError("Expérience 'cost_prediction' non trouvée")
                
            # Lecture de l'URI du modèle de production
            production_path = os.path.join("mlruns", experiment.experiment_id, "production_model_uri.txt")
            if not os.path.exists(production_path):
                raise FileNotFoundError(f"Fichier URI du modèle non trouvé: {production_path}")
                
            with open(production_path, "r") as f:
                model_uri = f.read().strip()
                
            logger.info(f"Chargement du modèle depuis: {model_uri}")
            loaded_model = mlflow.sklearn.load_model(model_uri)
            self.model = loaded_model
            logger.info("Modèle chargé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
            return False
    
    def load_data(self):
        """Charge les données depuis la base de données"""
        engine = create_engine('sqlite:///data/medical_costs.db')
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
    
    def prepare_data(self, df):
        """Prépare les données pour l'entraînement"""
        # Séparation features et target
        X = df.drop('insurance_cost', axis=1)
        y = df['insurance_cost']
        
        # Définition des colonnes numériques et catégorielles
        numeric_features = ['age', 'bmi', 'nb_children']
        categorical_features = ['sex', 'smoker', 'region']
        
        # Création du preprocessor
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
            ])
        
        return X, y
    
    def predict(self, features):
        """Fait une prédiction avec le modèle chargé"""
        if self.model is None:
            if not self.load_production_model():
                raise ValueError("Impossible de charger le modèle de production")
        
        # Conversion en DataFrame si nécessaire
        if not isinstance(features, pd.DataFrame):
            features = pd.DataFrame([features])
            
        return self.model.predict(features)

if __name__ == "__main__":
    # Test du modèle
    predictor = CostPredictor()
    mse, r2 = predictor.train()
    
    # Test de prédiction
    sample = {
        'age': 30,
        'bmi': 25,
        'nb_children': 2,
        'sex': 'male',
        'smoker': 'no',
        'region': 'southwest'
    }
    
    prediction = predictor.predict(sample)
    logger.info(f"Prédiction pour l'échantillon: ${prediction[0]:.2f}") 