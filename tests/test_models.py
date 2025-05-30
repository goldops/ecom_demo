import pytest
from datetime import datetime
import sys
import os

# Ajout du chemin parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app
from app.models import User, Product, Order, OrderItem

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_user():
    user = User(
        email='test@example.com',
        nom='Test User'
    )
    user.set_password('password123')
    return user

@pytest.fixture
def sample_product():
    return Product(
        nom='Laptop Test',
        description='Un laptop pour les tests',
        categorie='Ordinateurs',
        prix=999.99,
        quantite_stock=10
    )

@pytest.fixture
def sample_order(sample_user):
    return Order(
        utilisateur_id=sample_user.id,
        adresse_livraison='123 Test Street',
        statut='en_attente'
    )

def test_new_user():
    """
    Test la création d'un nouvel utilisateur
    """
    user = User(
        email='test@test.com',
        nom='Test User'
    )
    user.set_password('password123')
    
    assert user.email == 'test@test.com'
    assert user.nom == 'Test User'
    assert user.role == 'client'  # rôle par défaut
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')

def test_user_to_dict(sample_user):
    """
    Test la sérialisation d'un utilisateur
    """
    user_dict = sample_user.to_dict()
    assert user_dict['email'] == 'test@example.com'
    assert user_dict['nom'] == 'Test User'
    assert user_dict['role'] == 'client'
    assert 'password_hash' not in user_dict

def test_new_product(sample_product):
    """
    Test la création d'un nouveau produit
    """
    assert sample_product.nom == 'Laptop Test'
    assert sample_product.prix == 999.99
    assert sample_product.quantite_stock == 10
    assert sample_product.categorie == 'Ordinateurs'

def test_product_to_dict(sample_product):
    """
    Test la sérialisation d'un produit
    """
    product_dict = sample_product.to_dict()
    assert product_dict['nom'] == 'Laptop Test'
    assert product_dict['prix'] == 999.99
    assert product_dict['categorie'] == 'Ordinateurs'
    assert product_dict['quantite_stock'] == 10

def test_new_order(client, sample_user, sample_product):
    """
    Test la création d'une nouvelle commande
    """
    with app.app_context():
        db.session.add(sample_user)
        db.session.commit()
        
        order = Order(
            utilisateur_id=sample_user.id,
            adresse_livraison='123 Test Street',
            statut='en_attente'
        )
        
        assert order.utilisateur_id == sample_user.id
        assert order.statut == 'en_attente'
        assert order.adresse_livraison == '123 Test Street'

def test_order_to_dict(client, sample_user, sample_product):
    """
    Test la sérialisation d'une commande
    """
    with app.app_context():
        db.session.add(sample_user)
        db.session.commit()
        
        order = Order(
            utilisateur_id=sample_user.id,
            adresse_livraison='123 Test Street',
            statut='en_attente'
        )
        db.session.add(order)
        db.session.commit()
        
        order_dict = order.to_dict()
        assert order_dict['utilisateur_id'] == sample_user.id
        assert order_dict['statut'] == 'en_attente'
        assert order_dict['adresse_livraison'] == '123 Test Street'
        assert order_dict['total'] == 0  # pas d'items encore

def test_order_item(client, sample_user, sample_product):
    """
    Test la création d'une ligne de commande
    """
    with app.app_context():
        db.session.add(sample_user)
        db.session.add(sample_product)
        db.session.commit()
        
        order = Order(
            utilisateur_id=sample_user.id,
            adresse_livraison='123 Test Street'
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            commande_id=order.id,
            produit_id=sample_product.id,
            quantite=2,
            prix_unitaire=sample_product.prix
        )
        
        assert order_item.quantite == 2
        assert order_item.prix_unitaire == 999.99
        
        db.session.add(order_item)
        db.session.commit()
        
        # Test le calcul du total de la commande
        order_dict = order.to_dict()
        assert order_dict['total'] == 1999.98  # 2 * 999.99
