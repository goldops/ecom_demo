import pytest
import json
import sys
import os

# Ajout du chemin parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models import User, Product, Order, OrderItem

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def admin_token(client):
    # Créer un utilisateur admin
    admin = User(
        email='admin@example.com',
        nom='Admin User',
        role='admin'
    )
    admin.set_password('admin123')
    with app.app_context():
        db.session.add(admin)
        db.session.commit()
    
    # Obtenir le token
    response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'mot_de_passe': 'admin123'
    })
    return json.loads(response.data)['token']

@pytest.fixture
def user_token(client):
    # Créer un utilisateur normal
    user = User(
        email='user@example.com',
        nom='Regular User'
    )
    user.set_password('user123')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    
    # Obtenir le token
    response = client.post('/api/auth/login', json={
        'email': 'user@example.com',
        'mot_de_passe': 'user123'
    })
    return json.loads(response.data)['token']

def test_register(client):
    """
    Test l'inscription d'un nouvel utilisateur
    """
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'mot_de_passe': 'password123',
        'nom': 'New User'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['user']['email'] == 'new@example.com'
    assert data['user']['nom'] == 'New User'

def test_login(client):
    """
    Test la connexion d'un utilisateur
    """
    # Créer d'abord un utilisateur
    user = User(email='test@example.com', nom='Test User')
    user.set_password('password123')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    
    # Tester la connexion
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'mot_de_passe': 'password123'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert data['user']['email'] == 'test@example.com'

def test_get_products(client):
    """
    Test la récupération de la liste des produits
    """
    # Ajouter quelques produits
    with app.app_context():
        product1 = Product(nom='Laptop 1', categorie='Ordinateurs', prix=999.99)
        product2 = Product(nom='Laptop 2', categorie='Ordinateurs', prix=1299.99)
        db.session.add(product1)
        db.session.add(product2)
        db.session.commit()
    
    response = client.get('/api/produits')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['nom'] == 'Laptop 1'
    assert data[1]['nom'] == 'Laptop 2'

def test_create_product(client, admin_token):
    """
    Test la création d'un produit (admin)
    """
    response = client.post(
        '/api/produits',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'nom': 'Nouveau Laptop',
            'description': 'Un super laptop',
            'prix': 1499.99,
            'categorie': 'Ordinateurs',
            'quantite_stock': 5
        }
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['product']['nom'] == 'Nouveau Laptop'
    assert data['product']['prix'] == 1499.99

def test_create_order(client, user_token):
    """
    Test la création d'une commande
    """
    # Créer d'abord un produit
    with app.app_context():
        product = Product(
            nom='Test Product',
            categorie='Test',
            prix=99.99,
            quantite_stock=10
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    
    response = client.post(
        '/api/commandes',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'adresse_livraison': '123 Test St',
            'items': [
                {
                    'produit_id': product_id,
                    'quantite': 2
                }
            ]
        }
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['order']['statut'] == 'en_attente'

def test_get_orders(client, admin_token, user_token):
    """
    Test la récupération des commandes
    """
    # Test en tant qu'admin (voit toutes les commandes)
    response = client.get(
        '/api/commandes',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    
    # Test en tant qu'utilisateur (voit uniquement ses commandes)
    response = client.get(
        '/api/commandes',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 200

def test_update_product_unauthorized(client, user_token):
    """
    Test la modification d'un produit par un utilisateur non admin
    """
    response = client.put(
        '/api/produits/1',
        headers={'Authorization': f'Bearer {user_token}'},
        json={'prix': 99.99}
    )
    assert response.status_code == 403
