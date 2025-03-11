# Analyse et Gestion des Coûts Médicaux

Ce projet vise à créer une application pour analyser et gérer les coûts médicaux, en utilisant un jeu de données existant (Kaggle Medical Cost Personal Datasets) et en l'enrichissant avec des informations personnelles synthétiques.

## Fonctionnalités

- Analyse des coûts médicaux basée sur différents facteurs (âge, IMC, tabagisme, etc.)
- Génération de données synthétiques pour enrichir le jeu de données
- Visualisations interactives des données avec Plotly
- Interface utilisateur avec Streamlit
- Modèle de Machine Learning pour la prédiction des coûts
- Suivi des expériences avec MLflow
- Base de données SQLite pour le stockage des données

## Prérequis

- Python 3.8+
- Environnement virtuel Python
- SQLite

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_REPO]
```

2. Créer et activer l'environnement virtuel :
```bash
python -m venv .venv
# Sur Windows
.venv\Scripts\activate
# Sur Unix/MacOS
source .venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Structure du Projet

```
.
├── data/                  # Données brutes et SQL
│   ├── base.sql          # Schéma de la base de données
│   ├── insurance.csv     # Données Kaggle
│   └── medical_costs.db  # Base de données SQLite
├── models/               # Modèles de données et ML
│   └── cost_predictor.py # Modèle de prédiction des coûts
├── modules/              # Modules métier
│   └── db_loader.py     # Chargement des données
├── tests/               # Tests unitaires et d'intégration
├── .env                 # Variables d'environnement
├── .gitignore          # Fichiers à ignorer par Git
├── app.py              # Application Streamlit
├── README.md           # Documentation
└── requirements.txt    # Dépendances Python
```

## Utilisation

1. Charger les données dans la base :
```bash
python modules/db_loader.py
```

2. Lancer l'application Streamlit :
```bash
streamlit run app.py
```

3. Accéder à l'interface MLflow :
```bash
mlflow ui
```

## Fonctionnalités de l'Application

### Analyse Descriptive
- Statistiques générales sur les coûts d'assurance
- Distribution des coûts
- Analyse par facteur (âge, IMC, tabagisme, etc.)
- Visualisations interactives
- Matrice de corrélation
- Graphiques de dispersion personnalisables

### Prédiction des Coûts
- Formulaire de saisie des informations patient
- Prédiction instantanée des coûts
- Visualisation des facteurs influents
- Comparaison avec les moyennes de la base de données

## Tests

Pour exécuter les tests :
```bash
pytest
```

Pour générer un rapport de couverture :
```bash
pytest --cov=./ --cov-report=html
```

## Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Auteurs

- [Votre Nom]

## Remerciements

- Kaggle pour le jeu de données original
- La communauté Python pour les bibliothèques utilisées 