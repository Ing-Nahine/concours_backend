# 🎓 Couldiat Backend API

Backend complet pour la plateforme Couldiat - Gestion de concours et formation QCM

## 📋 Table des matières

- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Structure du projet](#structure)
- [API Endpoints](#api-endpoints)
- [Tests](#tests)
- [Déploiement](#déploiement)

## 🛠️ Technologies

- **Django 4.2** - Framework web
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de données
- **JWT** - Authentification
- **AWS S3** / **Cloudflare R2** - Stockage fichiers
- **Swagger** - Documentation API

## 📦 Installation

### Prérequis

- Python 3.10+
- PostgreSQL 14+
- pip et virtualenv

### Étapes d'installation

```bash
# 1. Cloner le repository
git clone <repo-url>
cd couldiat_backend

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# 5. Créer la base de données PostgreSQL
createdb couldiat_db

# 6. Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 9. Lancer le serveur
python manage.py runserver
```

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=couldiat_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME_DAYS=7
JWT_REFRESH_TOKEN_LIFETIME_DAYS=30

# AWS S3 (Production)
USE_S3=False
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=eu-west-1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📁 Structure du projet

```
couldiat_backend/
├── accounts/              # Gestion utilisateurs
├── concours/              # Concours et inscriptions
├── formation/             # Matières, chapitres, QCM
├── admin_dashboard/       # API admin
├── core/                  # Utilitaires communs
├── couldiat_project/      # Configuration Django
├── media/                 # Fichiers uploadés
└── requirements.txt
```

## 🔌 API Endpoints

### Authentication

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/register/` | Inscription |
| POST | `/api/auth/login/` | Connexion |
| POST | `/api/auth/logout/` | Déconnexion |
| GET | `/api/auth/profile/` | Profil utilisateur |
| PUT | `/api/auth/profile/update/` | Mise à jour profil |
| POST | `/api/auth/profile/change-password/` | Changer mot de passe |
| POST | `/api/auth/token/refresh/` | Rafraîchir token |

### Concours (Mobile)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/concours/` | Liste des concours |
| GET | `/api/concours/{id}/` | Détail concours |
| POST | `/api/concours/inscriptions/create/` | Créer inscription |
| GET | `/api/concours/inscriptions/mes-inscriptions/` | Mes inscriptions |
| GET | `/api/concours/inscriptions/{id}/` | Détail inscription |
| POST | `/api/concours/paiements/valider/` | Soumettre paiement |
| GET | `/api/concours/paiements/inscription/{id}/` | Détail paiement |

### Formation (QCM)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/formation/matieres/` | Liste matières |
| GET | `/api/formation/matieres/{id}/chapitres/` | Chapitres matière |
| GET | `/api/formation/chapitres/{id}/questions/` | Questions chapitre |
| POST | `/api/formation/submit-qcm/` | Soumettre QCM |
| GET | `/api/formation/progression/` | Ma progression |

### Admin Dashboard

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/admin/dashboard/stats/` | Statistiques |
| GET | `/api/admin/inscriptions/en-attente/` | Inscriptions en attente |
| PATCH | `/api/admin/inscriptions/{id}/valider/` | Valider inscription |
| GET | `/api/admin/paiements/en-attente/` | Paiements en attente |
| PATCH | `/api/admin/paiements/{id}/valider/` | Valider paiement |

### Documentation

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test accounts
python manage.py test concours

# Avec coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🚀 Déploiement

### Avec Docker

```bash
# Build l'image
docker build -t couldiat-backend .

# Lancer le conteneur
docker run -p 8000:8000 --env-file .env couldiat-backend
```

### Sur Heroku

```bash
heroku create couldiat-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY="your-secret-key"
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Sur VPS (Ubuntu)

```bash
# Installer dépendances
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx

# Configurer PostgreSQL
sudo -u postgres createuser couldiat_user
sudo -u postgres createdb couldiat_db

# Configurer Gunicorn + Nginx
# Suivre la documentation Django officielle
```

## 📊 Commandes utiles

```bash
# Créer une migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Vider la base de données
python manage.py flush

# Exporter les données
python manage.py dumpdata > data.json

# Importer les données
python manage.py loaddata data.json
```

## 🔒 Sécurité

- Les mots de passe sont hashés avec PBKDF2
- JWT pour l'authentification
- CORS configuré
- Protection CSRF
- Validation des fichiers uploadés
- Rate limiting (à configurer en production)

## 📝 License

Propriétaire - Couldiat © 2024

## 👥 Contact

Pour toute question: contact@couldiat.com

---

**Version**: 1.0.0  
**Dernière mise à jour**: Octobre 2024