# Utiliser une image Python officielle légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Empêcher Python d'écrire des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Désactiver le buffering pour voir les logs immédiatement
ENV PYTHONUNBUFFERED 1

# Installer les dépendances système pour PostgreSQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copier le projet
COPY . /app/

# Exposer le port
EXPOSE 8000

# Script d'entrée pour exécuter les migrations et lancer le serveur
CMD ["sh", "-c", "python manage.py migrate && python manage.py shell < seed_data.py && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
