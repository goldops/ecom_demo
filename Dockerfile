# Build stage
FROM python:3.11-alpine AS build

RUN apk add --no-cache --virtual .build-deps \
        g++ \
        python3-dev \
        libffi-dev \
        openssl-dev
RUN pip install --upgrade pip setuptools

COPY requirements.txt .
# Installer les paquets dans /root/.local avec --user
RUN pip install --user --no-cache-dir -r requirements.txt
#Installer gunicorn
RUN pip install --user --no-cache-dir gunicorn

# Final stage
FROM python:3.11-alpine

# Récuperer les librairies indispensables à l'OS
RUN apk add --no-cache libffi openssl

# Récuperer les packages Python à partir du build dans /root/.local
COPY --from=build /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Configurer et se déplacer vers le repertoire /app
WORKDIR /app

# Copier les fichiers du projet
COPY .env .env
COPY . .

# Exposer le port 5000
EXPOSE 5000

# Lancer l'application avec 3 workers
CMD ["gunicorn", "run:app", "-b", "0.0.0.0:5000", "-w", "3"]
