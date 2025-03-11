import mlflow
import mlflow.sklearn
from cost_predictor import CostPredictor
from loguru import logger
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

def train_and_save_model():
    """Entraîne et sauvegarde le modèle en production"""
    # Configuration MLflow pour utiliser le stockage local
    mlflow.set_tracking_uri("file:./mlruns")
    experiment = mlflow.set_experiment("cost_prediction")
    
    try:
        # Entraînement (sans MLflow pour l'instant)
        predictor = CostPredictor()
        mse, r2 = predictor.train()
        
        # Si le modèle est suffisamment bon, on l'enregistre avec MLflow
        if r2 > 0.85:
            # Création d'un nouveau run MLflow
            with mlflow.start_run() as run:
                # Log des métriques
                mlflow.log_metrics({
                    "mse": mse,
                    "r2": r2,
                    "rmse": mse ** 0.5
                })
                
                # Log des paramètres
                mlflow.log_params({
                    "model_type": "RandomForestRegressor",
                    "n_estimators": 100,
                    "random_state": 42
                })
                
                # Enregistrement du modèle
                mlflow.sklearn.log_model(
                    predictor.model,
                    "cost_predictor"
                )
                
                # Sauvegarde du chemin du modèle pour la production
                model_uri = f"runs:/{run.info.run_id}/cost_predictor"
                production_path = os.path.join("mlruns", experiment.experiment_id, "production_model_uri.txt")
                os.makedirs(os.path.dirname(production_path), exist_ok=True)
                with open(production_path, "w") as f:
                    f.write(model_uri)
                
                logger.info(f"Nouveau modèle enregistré avec R²: {r2:.2f}")
                logger.info(f"URI du modèle: {model_uri}")
                return True
            
        else:
            logger.warning(f"Modèle non enregistré car R² ({r2:.2f}) < 0.85")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement : {str(e)}")
        return False

if __name__ == "__main__":
    train_and_save_model() 