FROM python:3.12-slim

WORKDIR /app

# Installer uv
RUN pip install uv

# Copier le fichier de dépendances
COPY pyproject.toml .

# Installer les dépendances avec uv
RUN uv pip install . --system

# Copier le reste de l'application
COPY . .

# Exposer le port utilisé par le serveur
EXPOSE 8000

# Commande de lancement du serveur
CMD ["uv", "run", "server.py"] 