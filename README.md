# InsureCost Analytics 🏥💰

Application d'analyse et de prédiction des coûts d'assurance santé basée sur l'intelligence artificielle.

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Sécurité](#sécurité)
- [Tests](#tests)

## 🎯 Aperçu

InsureCost Analytics est une application web moderne qui utilise l'apprentissage automatique pour prédire les coûts d'assurance santé. Elle offre une interface utilisateur intuitive et des fonctionnalités avancées d'analyse de données.

## ✨ Fonctionnalités

- 🔐 Système d'authentification sécurisé
- 📊 Visualisation interactive des données
- 🤖 Modèle de prédiction ML optimisé
- 📈 Analyse des tendances
- 📱 Interface responsive
- 🔍 Recherche avancée
- 📤 Export des données
- 📝 Journalisation détaillée

## 🚀 Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/seb54/medicalcost.git
cd medicalcost
```

2. Créer un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer l'application :
```bash
cp config.example.py config.py
# Éditer config.py avec vos paramètres
```

## ⚙️ Configuration

1. Copier le fichier de configuration exemple :
```bash
cp config.example.py config.py
```

2. Modifier les paramètres dans `config.py` :
- Configuration de la base de données
- Clés secrètes
- Paramètres du modèle
- Options d'interface

## 💻 Utilisation

1. Démarrer l'application :
```bash
streamlit run home.py
```

2. Accéder à l'interface web :
```
http://localhost:8501
```

## 📁 Structure du projet

```
insurecost-analytics/
├── home.py                 # Point d'entrée de l'application
├── pages/                  # Pages de l'application
│   ├── login.py           # Authentification
│   ├── prediction_couts.py # Prédiction des coûts
│   └── ...
├── models/                # Modèles ML
├── data/                  # Données
├── tests/                # Tests unitaires et d'intégration
├── docs/                 # Documentation
├── config.example.py     # Configuration exemple
├── requirements.txt      # Dépendances
└── README.md            # Documentation principale
```

## 🔒 Sécurité

- Authentification multi-facteurs
- Protection contre les injections SQL
- Validation des entrées
- Chiffrement des données sensibles
- Rate limiting
- Journalisation des accès

## 🧪 Tests

Exécuter les tests :
```bash
pytest tests/
```

Vérifier la couverture :
```bash
pytest --cov=. tests/
```
