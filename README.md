# 🛒 API E-commerce DigiMarket

Une API REST développée avec Flask pour gérer une plateforme e-commerce de matériel informatique.

## 🛠 Technologies utilisées

- Python 3.x
- Flask
- SQLAlchemy (ORM)
- JWT (JSON Web Tokens)
- SQLite
- Pytest

## 📁 Structure du projet

```
ecom_flask/
│
├── app/
│   ├── __init__.py      # Configuration Flask et extensions
│   ├── models.py        # Modèles de données
│   ├── routes.py        # Routes API
│   └── utils.py         # Utilitaires (validations, décorateurs)
│
├── tests/
│   ├── test_models.py   # Tests des modèles
│   └── test_routes.py   # Tests des routes
│
├── instance/           # Base de données SQLite
├── config.py          # Configuration
├── requirements.txt   # Dépendances
└── run.py            # Point d'entrée de l'application
```

## 📊 Modèles de données

### User
- id: Integer (Primary Key)
- email: String (Unique)
- password_hash: String
- nom: String
- role: String ('client' ou 'admin')
- date_creation: DateTime

### Product
- id: Integer (Primary Key)
- nom: String
- description: Text
- categorie: String
- prix: Float
- quantite_stock: Integer
- date_creation: DateTime

### Order
- id: Integer (Primary Key)
- utilisateur_id: Integer (Foreign Key)
- date_commande: DateTime
- adresse_livraison: String
- statut: String ('en_attente', 'validée', 'expédiée', 'annulée')

### OrderItem
- id: Integer (Primary Key)
- commande_id: Integer (Foreign Key)
- produit_id: Integer (Foreign Key)
- quantite: Integer
- prix_unitaire: Float

## 🚀 Installation

1. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Installer les dépendances

```bash
pip install -r requirements.txt
```

3. Créer le fichier .env

```env
SECRET_KEY=votre_secret_key
JWT_SECRET_KEY=votre_jwt_secret
FLASK_APP=run.py
FLASK_ENV=development
```

4. Lancer l'application

```bash
python run.py
```

5. Lancer Postman

## 🔌 API Endpoints

### Authentification
- POST /api/auth/register - Inscription
- POST /api/auth/login - Connexion

### Produits
- GET /api/produits - Liste des produits
- GET /api/produits/<id> - Détails d'un produit
- POST /api/produits - Créer un produit (Admin)
- PUT /api/produits/<id> - Modifier un produit (Admin)
- DELETE /api/produits/<id> - Supprimer un produit (Admin)

### Commandes
- GET /api/commandes - Liste des commandes
- GET /api/commandes/<id> - Détails d'une commande
- POST /api/commandes - Créer une commande
- PATCH /api/commandes/<id> - Modifier le statut (Admin)

## 💻 Guide d'utilisation avec Postman

### 1. Création des utilisateurs

#### Créer un admin

```http
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
    "email": "admin@gmail.com",
    "mot_de_passe": "admin123",
    "nom": "Admin User",
    "role": "admin"
}
```

#### Créer un client

```http
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
    "email": "client@gmail.com",
    "mot_de_passe": "client123",
    "nom": "Client Pilote"
}
```

### 2. Connexion et obtention du token

```http
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
    "email": "admin@example.com",
    "mot_de_passe": "admin123"
}
```

### 3. Gestion des produits (Admin)

#### Ajouter un produit

```http
POST http://localhost:5000/api/produits
Authorization: Bearer <votre_token>
Content-Type: application/json

{
    "nom": "Laptop XPS 15",
    "description": "Dell XPS 15 doté d'un écran InfinityEdge 16:10 sur 4 côtés et de 100 % des couleurs Adobe RGB",
    "prix": 1499.99,
    "categorie": "PC Portable",
    "quantite_stock": 10
}
```

#### Modifier un produit

```http
PUT http://localhost:5000/api/produits/1
Authorization: Bearer <votre_token>
Content-Type: application/json

{
    "prix": 1399.99,
    "quantite_stock": 15
}
```

### 4. Gestion des commandes

#### Créer une commande (Client)

```http
POST http://localhost:5000/api/commandes
Authorization: Bearer <votre_token>
Content-Type: application/json

{
    "adresse_livraison": "13 Rue du 4 Septembre, Paris",
    "items": [
        {
            "produit_id": 1,
            "quantite": 2
        }
    ]
}
```

#### Modifier le statut d'une commande (Admin)

```http
PATCH http://localhost:5000/api/commandes/1
Authorization: Bearer <votre_token>
Content-Type: application/json

{
    "statut": "validée"
}
```

## 🧪 Tests

Exécuter les tests :

```bash
pytest
```

Pour voir la couverture des tests :

```bash
pytest --cov=app tests/
```