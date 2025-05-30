from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relation avec commandes
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def __init__(self, email, nom, role='client'):
        self.email = email
        self.nom = nom
        self.role = role
        self.date_creation = datetime.utcnow()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nom': self.nom,
            'role': self.role,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None
        }


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(50), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    quantite_stock = db.Column(db.Integer, default=0)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relation avec lignes de commande
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __init__(self, nom, categorie, prix, description=None, quantite_stock=0):
        self.nom = nom
        self.description = description
        self.categorie = categorie
        self.prix = prix
        self.quantite_stock = quantite_stock
        self.date_creation = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'prix': self.prix,
            'categorie': self.categorie,
            'quantite_stock': self.quantite_stock,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)
    adresse_livraison = db.Column(db.String(200), nullable=False)
    statut = db.Column(db.String(20), default='en_attente')  # 'en_attente', 'validée', 'expédiée', 'annulée'
    
    # Relation avec lignes de commande
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'utilisateur_id': self.utilisateur_id,
            'utilisateur': self.user.nom,
            'date_commande': self.date_commande.isoformat(),
            'adresse_livraison': self.adresse_livraison,
            'statut': self.statut,
            'total': sum(item.prix_unitaire * item.quantite for item in self.items)
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'commande_id': self.commande_id,
            'produit_id': self.produit_id,
            'produit': self.product.nom,
            'quantite': self.quantite,
            'prix_unitaire': self.prix_unitaire,
            'prix_total': self.prix_unitaire * self.quantite
        }