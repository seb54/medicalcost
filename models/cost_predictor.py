from sklearn.model_selection import train_test_split, cross_val_predict
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import mlflow
import mlflow.sklearn
from loguru import logger
import os
from sklearn.model_selection import KFold


class CostPredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.target_transform = None
        self.feature_importances_ = None
        self.feature_columns = None
        self.numeric_features = None
        self.categorical_features = None

    def train(self, experiment_name="cost_prediction"):
        """Entraîne le modèle et trace les métriques avec MLflow"""
        # Configuration de MLflow
        mlflow.set_experiment(experiment_name)

        # Chargement et préparation des données
        df = self.load_data()
        X, y = self.prepare_data(df)

        # Split des données
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Création du pipeline
        self.model = Pipeline(
            [
                ("preprocessor", self.preprocessor),
                ("regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
            ]
        )

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

            # Récupération de l'expérience
            experiment = mlflow.get_experiment_by_name("cost_prediction")
            if not experiment:
                logger.error("Expérience 'cost_prediction' non trouvée")
                return False

            # Récupération de l'URI du modèle de production
            production_path = os.path.join(
                "mlruns", experiment.experiment_id, "production_model_uri.txt"
            )
            if not os.path.exists(production_path):
                logger.error(f"Fichier URI du modèle non trouvé: {production_path}")
                return False

            with open(production_path, "r") as f:
                model_uri = f.read().strip()

            logger.info(f"Chargement du modèle depuis : {model_uri}")

            # Chargement du modèle
            self.model = mlflow.sklearn.load_model(model_uri)

            # Récupération des runs pour obtenir les paramètres
            run_id = model_uri.split("/")[1]
            client = mlflow.tracking.MlflowClient()
            run = client.get_run(run_id)

            # Récupération des colonnes et features
            self.feature_columns = eval(run.data.params["feature_columns"])
            self.numeric_features = eval(run.data.params["numeric_features"])
            self.categorical_features = eval(run.data.params["categorical_features"])

            logger.info("Modèle et métadonnées chargés avec succès")
            logger.info(f"Features numériques : {self.numeric_features}")
            logger.info(f"Features catégorielles : {self.categorical_features}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
            return False

    def load_data(self):
        """Charge les données depuis la base de données"""
        engine = create_engine("sqlite:///data/medical_costs.db")
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
        # Validation initiale
        self.validate_data(df)
        logger.info("Début de la préparation des données")

        # Analyse des distributions
        self._analyze_distributions(df)

        # Gestion des valeurs manquantes et aberrantes
        df = self._handle_missing_and_outliers(df)

        # Feature Engineering
        df = self._create_features(df)

        # Transformation des variables
        df = self._transform_features(df)

        # Séparation features et target
        X = df.drop("insurance_cost", axis=1)
        y = df["insurance_cost"]

        # Transformation de la target si nécessaire
        if abs(y.skew()) > 1:
            logger.info("Application d'une transformation log à la target")
            self.target_transform = "log"
            y = np.log1p(y)

        return X, y

    def _analyze_distributions(self, df):
        """Analyse et log la distribution des variables"""
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

        for col in numeric_cols:
            skewness = df[col].skew()
            kurtosis = df[col].kurtosis()
            logger.info(f"Distribution de {col}:")
            logger.info(f"- Skewness: {skewness:.2f}")
            logger.info(f"- Kurtosis: {kurtosis:.2f}")

    def _handle_missing_and_outliers(self, df):
        """Gère les valeurs manquantes et aberrantes"""
        # Gestion des valeurs manquantes
        numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns
        for col in numeric_columns:
            if df[col].isnull().sum() > 0:
                logger.info(
                    f"Remplacement des valeurs manquantes dans {col} par la médiane"
                )
                df[col].fillna(df[col].median(), inplace=True)

        categorical_columns = df.select_dtypes(include=["object"]).columns
        for col in categorical_columns:
            if df[col].isnull().sum() > 0:
                logger.info(
                    f"Remplacement des valeurs manquantes dans {col} par le mode"
                )
                df[col].fillna(df[col].mode()[0], inplace=True)

        # Gestion des valeurs aberrantes
        for col in ["age", "bmi", "nb_children"]:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            if outliers_mask.any():
                n_outliers = outliers_mask.sum()
                logger.warning(f"{n_outliers} valeurs aberrantes détectées dans {col}")
                # Remplacement par les bornes
                df.loc[df[col] < lower_bound, col] = lower_bound
                df.loc[df[col] > upper_bound, col] = upper_bound

        return df

    def _create_features(self, df):
        """Création de nouvelles features"""
        # BMI Categories
        df["bmi_category"] = pd.cut(
            df["bmi"],
            bins=[0, 18.5, 25, 30, float("inf")],
            labels=["Underweight", "Normal", "Overweight", "Obese"],
        )

        # Age Groups
        df["age_group"] = pd.cut(
            df["age"],
            bins=[0, 25, 35, 50, 65, float("inf")],
            labels=["Young", "Adult", "Middle", "Senior", "Elderly"],
        )

        # Interactions
        df["bmi_smoker"] = df["bmi"] * (df["smoker"] == "yes").astype(int)
        df["age_bmi"] = df["age"] * df["bmi"]

        logger.info("Nouvelles features créées")
        return df

    def _transform_features(self, df):
        """Transformation des variables numériques"""
        numeric_cols = ["age", "bmi"]

        for col in numeric_cols:
            skewness = df[col].skew()
            if abs(skewness) > 1:
                logger.info(
                    f"Application d'une transformation log à {col} (skewness: {skewness:.2f})"
                )
                df[col] = np.log1p(df[col])

        return df

    def _check_target_distribution(self, y):
        """Vérifie la distribution de la target et applique une transformation si nécessaire"""
        skewness = y.skew()
        logger.info(f"Distribution de la target - skewness: {skewness:.2f}")

        if abs(skewness) > 1:
            logger.info("Application d'une transformation log à la target")
            self.target_transform = "log"
            return np.log1p(y)

        self.target_transform = None
        return y

    def fit(self, X, y):
        """Entraîne le modèle avec validation croisée"""
        numeric_features = ["age", "bmi", "nb_children"]
        categorical_features = ["sex", "smoker", "region", "bmi_category", "age_group"]

        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                (
                    "cat",
                    OneHotEncoder(drop="first", sparse_output=False),
                    categorical_features,
                ),
            ]
        )

        # Nouveaux hyperparamètres pour réduire l'overfitting
        model = RandomForestRegressor(
            n_estimators=150,  # Augmenté de 100 à 150 pour plus de stabilité
            max_depth=8,  # Maintenu à 8
            min_samples_split=6,  # Réduit de 8 à 6 pour plus de flexibilité
            min_samples_leaf=3,  # Réduit de 4 à 3
            max_features="sqrt",  # Maintenu
            bootstrap=True,
            oob_score=True,  # Ajouté pour avoir une estimation supplémentaire
            random_state=42,
        )

        pipeline = Pipeline([("preprocessor", self.preprocessor), ("model", model)])

        logger.info("Évaluation du modèle avec validation croisée (5-fold)...")
        logger.info("\nHyperparamètres du modèle:")
        logger.info("- n_estimators: 150")
        logger.info("- max_depth: 8")
        logger.info("- min_samples_split: 6")
        logger.info("- min_samples_leaf: 3")
        logger.info("- max_features: sqrt")

        # Obtenir les prédictions de validation croisée
        y_pred_cv = cross_val_predict(pipeline, X, y, cv=5)

        # Si nous avons appliqué une transformation log, retransformer les valeurs
        if self.target_transform == "log":
            y_true = np.exp(y) - 1
            y_pred_cv = np.exp(y_pred_cv) - 1
        else:
            y_true = y

        # Calcul des métriques
        r2 = r2_score(y_true, y_pred_cv)
        mse = mean_squared_error(y_true, y_pred_cv)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred_cv)

        # Calcul des métriques par fold pour obtenir les intervalles de confiance
        kf = KFold(n_splits=5, shuffle=True, random_state=42)

        metrics_by_fold = {"r2": [], "mse": [], "rmse": [], "mae": []}

        train_scores = []
        test_scores = []
        feature_importances = []

        for train_idx, test_idx in kf.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Entraînement sur le fold
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)

            # Retransformation si nécessaire
            if self.target_transform == "log":
                y_test_orig = np.exp(y_test) - 1
                y_pred_orig = np.exp(y_pred) - 1
            else:
                y_test_orig = y_test
                y_pred_orig = y_pred

            # Calcul des métriques pour ce fold
            metrics_by_fold["r2"].append(r2_score(y_test_orig, y_pred_orig))
            metrics_by_fold["mse"].append(mean_squared_error(y_test_orig, y_pred_orig))
            metrics_by_fold["rmse"].append(
                np.sqrt(mean_squared_error(y_test_orig, y_pred_orig))
            )
            metrics_by_fold["mae"].append(mean_absolute_error(y_test_orig, y_pred_orig))

            # Scores train et test pour ce fold
            train_scores.append(r2_score(y_train, pipeline.predict(X_train)))
            test_scores.append(r2_score(y_test, pipeline.predict(X_test)))

            # Importance des features pour ce fold
            feature_importances.append(
                pd.Series(
                    pipeline.named_steps["model"].feature_importances_,
                    index=numeric_features
                    + [
                        f"{feat}_{val}"
                        for feat, vals in zip(
                            categorical_features,
                            pipeline.named_steps["preprocessor"]
                            .named_transformers_["cat"]
                            .categories_,
                        )
                        for val in vals[1:]
                    ],
                )
            )

        # Calcul des intervalles de confiance
        confidence_intervals = {
            metric: np.std(values) * 2 for metric, values in metrics_by_fold.items()
        }

        # Moyenne des importances des features sur tous les folds
        mean_importances = (
            pd.concat(feature_importances, axis=1)
            .mean(axis=1)
            .sort_values(ascending=False)
        )

        # Affichage des résultats
        logger.info("\n=== Résultats de la validation croisée ===")

        logger.info(f"R² Score: {r2:.3f} (+/- {confidence_intervals['r2']:.3f})")
        logger.info(
            f"Mean Squared Error: {mse:,.0f} (+/- {confidence_intervals['mse']:,.0f})"
        )
        logger.info(
            f"Root Mean Squared Error: {rmse:,.0f} (+/- {confidence_intervals['rmse']:,.0f})"
        )
        logger.info(
            f"Mean Absolute Error: {mae:,.0f} (+/- {confidence_intervals['mae']:,.0f})"
        )

        r2_train = np.mean(train_scores)
        r2_test = np.mean(test_scores)
        r2_diff = r2_train - r2_test

        logger.info(f"\nAnalyse de l'overfitting:")
        logger.info(f"R² Train: {r2_train:.3f} (+/- {np.std(train_scores) * 2:.3f})")
        logger.info(f"R² Test:  {r2_test:.3f} (+/- {np.std(test_scores) * 2:.3f})")
        logger.info(f"Différence Train-Test: {r2_diff:.3f}")

        logger.info("\n=== Top 10 Features les plus importantes ===")
        for feat, imp in mean_importances.head(10).items():
            logger.info(f"- {feat}: {imp:.3f}")
        if r2_diff > 0.1:
            logger.warning(
                f"Possible overfitting détecté! (différence Train-Test: {r2_diff:.3f})"
            )
            if r2_diff > 0.2:
                logger.warning("Suggestions pour réduire l'overfitting:")
                logger.warning("1. Réduire le nombre d'arbres")
                logger.warning("2. Augmenter min_samples_split/leaf")
                logger.warning("3. Réduire max_depth")

        # Entraînement final sur toutes les données
        pipeline.fit(X, y)
        self.model = pipeline

        # Sauvegarde des métriques pour MLflow
        self.cv_results = {
            "r2": r2,
            "mse": float(mse),
            "rmse": float(rmse),
            "mae": float(mae),
            "r2_train": r2_train,
            "r2_test": r2_test,
        }

        return self

    def _analyze_feature_importance(self, X):
        """Analyse et log l'importance des features"""
        feature_names = (
            self.preprocessor.named_transformers_["num"]
            .get_feature_names_out()
            .tolist()
            + self.preprocessor.named_transformers_["cat"]
            .get_feature_names_out()
            .tolist()
        )

        importances = self.model.named_steps["model"].feature_importances_
        self.feature_importances_ = pd.Series(importances, index=feature_names)

        logger.info("Top 5 features les plus importantes:")
        for feat, imp in self.feature_importances_.nlargest(5).items():
            logger.info(f"- {feat}: {imp:.3f}")

    def predict(self, input_data):
        """Fait une prédiction à partir des données d'entrée"""
        if self.model is None:
            raise ValueError(
                "Le modèle n'est pas chargé. Appelez load_production_model() d'abord."
            )

        try:
            # Conversion en DataFrame si nécessaire
            if not isinstance(input_data, pd.DataFrame):
                if isinstance(input_data, dict):
                    input_data = pd.DataFrame([input_data])
                else:
                    input_data = pd.DataFrame(input_data)

            # Copie pour éviter les modifications sur les données d'origine
            df = input_data.copy()

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

            # Prédiction en utilisant le pipeline MLflow
            prediction = self.model.predict(df)

            return prediction

        except Exception as e:
            logger.error(f"Erreur lors de la prédiction : {str(e)}")
            raise

    def validate_data(self, df):
        """Valide la structure et le contenu des données"""
        logger.info("Validation des données...")

        required_columns = {
            "age": "numeric",
            "bmi": "numeric",
            "nb_children": "numeric",
            "sex": "categorical",
            "smoker": "categorical",
            "region": "categorical",
            "insurance_cost": "numeric",
        }

        # Vérification des colonnes requises
        missing_columns = set(required_columns.keys()) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Colonnes manquantes: {missing_columns}")

        # Vérification des types de données
        for col, dtype in required_columns.items():
            if dtype == "numeric":
                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise ValueError(f"La colonne {col} doit être numérique")
            elif dtype == "categorical":
                if not pd.api.types.is_object_dtype(df[col]):
                    raise ValueError(f"La colonne {col} doit être catégorielle")

        logger.info("Validation des données réussie")
        return True

    def analyze_errors(self, X, y, y_pred):
        """Analyse détaillée des erreurs de prédiction"""
        errors = y - y_pred
        abs_errors = np.abs(errors)

        logger.info("\n=== Analyse détaillée des erreurs ===")

        # Distribution des erreurs
        logger.info(f"Distribution des erreurs absolues:")
        logger.info(f"- Médiane: ${np.median(abs_errors):,.0f}")
        logger.info(f"- 75e percentile: ${np.percentile(abs_errors, 75):,.0f}")
        logger.info(f"- 90e percentile: ${np.percentile(abs_errors, 90):,.0f}")
        logger.info(f"- 95e percentile: ${np.percentile(abs_errors, 95):,.0f}")

        # Analyse des erreurs par catégorie
        for cat in ["smoker", "age_group", "bmi_category"]:
            mae_by_cat = (
                pd.DataFrame({"abs_error": abs_errors, "category": X[cat]})
                .groupby("category")["abs_error"]
                .mean()
            )

            logger.info(f"\nMAE par {cat}:")
            for cat_name, mae_value in mae_by_cat.items():
                logger.info(f"- {cat_name}: ${mae_value:,.0f}")


if __name__ == "__main__":
    # Test du modèle
    predictor = CostPredictor()
    mse, r2 = predictor.train()

    # Test de prédiction
    sample = {
        "age": 30,
        "bmi": 25,
        "nb_children": 2,
        "sex": "male",
        "smoker": "no",
        "region": "southwest",
    }

    prediction = predictor.predict(sample)
    logger.info(f"Prédiction pour l'échantillon: ${prediction[0]:.2f}")
