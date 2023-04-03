FROM python:3.8

# Créer le répertoire de travail de l'application
WORKDIR /app

# Copier le fichier requirements.txt et l'installer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code source de l'application
COPY . .

# Charger les variables d'environnement à partir du fichier .env
RUN apt-get update && apt-get install -y dos2unix
COPY .env .env
RUN dos2unix .env && \
    pip install python-dotenv && \
    export $(grep -v '^#' .env | xargs)

# Exécuter l'application
CMD ["streamlit", "run", "app.py"]
