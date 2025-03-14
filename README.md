# InsureCost Analytics 🏥💰

Application d'analyse et de prédiction des coûts d'assurance santé basée sur l'intelligence artificielle.

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Sécurité](#sécurité)
- [Tests](#tests)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Licence](#licence)
- [Contact](#contact)

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
git clone https://github.com/votre-username/insurecost-analytics.git
cd insurecost-analytics
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

## 📚 Documentation

La documentation complète est disponible dans le dossier `docs/` :
- Guide d'utilisation
- Documentation API
- Guide de contribution
- Notes de version

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -am 'Ajout de fonctionnalité'`)
4. Push la branche (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📧 Contact

- Email : contact@insurecost-analytics.com
- Site web : https://insurecost-analytics.com
- GitHub : [@insurecost-analytics](https://github.com/insurecost-analytics)

---

Développé avec ❤️ par l'équipe InsureCost Analytics
