# Image de base Python
FROM python:3.10-slim

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requirements avant le reste du code
# pour optimiser le cache des couches Docker
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Création des répertoires nécessaires
RUN mkdir -p /app/data /app/mlruns

# Copie du reste du code
COPY . .

# Exposition des ports
EXPOSE 8501 5000

# Commande de démarrage
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 