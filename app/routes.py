from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import app, db
from app.models import User, Product, Order, OrderItem
from app.utils import admin_required, validate_product_data, validate_order_data, validate_user_data

# Routes d'authentification
@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur
    """
    data = request.get_json()
    errors = validate_user_data(data)
    
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Vérifier si l'email existe déjà
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"errors": {"email": "Cet email est déjà utilisé"}}), 400
    
    # Créer le nouvel utilisateur
    user = User(
        email=data['email'],
        nom=data['nom'],
        role=data.get('role', 'client')  # Prendre en compte le rôle s'il est fourni
    )
    user.set_password(data['mot_de_passe'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Utilisateur créé avec succès", "user": user.to_dict()}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Connexion et génération de token JWT
    """
    data = request.get_json()
    errors = validate_user_data(data, is_registration=False)
    
    if errors:
        return jsonify({"errors": errors}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['mot_de_passe']):
        return jsonify({"message": "Email ou mot de passe incorrect"}), 401
    
    access_token = create_access_token(identity=user.email)
    
    return jsonify({
        "message": "Connexion réussie",
        "token": access_token,
        "user": user.to_dict()
    }), 200

# Routes pour les produits
@app.route('/api/produits', methods=['GET'])
def get_products():
    """
    Liste des produits
    Paramètres optionnels:
        - categorie: Filtre les produits par catégorie
    """
    categorie = request.args.get('categorie')
    
    if categorie:
        products = Product.query.filter_by(categorie=categorie).all()
    else:
        products = Product.query.all()
    
    return jsonify([product.to_dict() for product in products]), 200

@app.route('/api/produits/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Détails d'un produit spécifique
    """
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@app.route('/api/produits', methods=['POST'])
@admin_required
def create_product():
    """
    Création d'un nouveau produit (admin uniquement)
    """
    data = request.get_json()
    errors = validate_product_data(data)
    
    if errors:
        return jsonify({"errors": errors}), 400
    
    product = Product(
        nom=data['nom'],
        description=data.get('description', ''),
        prix=data['prix'],
        categorie=data['categorie'],
        quantite_stock=data.get('quantite_stock', 0)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({"message": "Produit créé avec succès", "product": product.to_dict()}), 201

@app.route('/api/produits/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """
    Modification d'un produit existant (admin uniquement)
    """
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if data.get('nom'):
        product.nom = data['nom']
    
    if 'description' in data:
        product.description = data['description']
    
    if data.get('prix'):
        if not isinstance(data['prix'], (int, float)) or data['prix'] <= 0:
            return jsonify({"errors": {"prix": "Le prix doit être un nombre positif"}}), 400
        product.prix = data['prix']
    
    if 'quantite_stock' in data:
        if not isinstance(data['quantite_stock'], int) or data['quantite_stock'] < 0:
            return jsonify({"errors": {"quantite_stock": "La quantité doit être un nombre entier positif ou nul"}}), 400
        product.quantite_stock = data['quantite_stock']
    
    if data.get('categorie'):
        product.categorie = data['categorie']
    
    db.session.commit()
    
    return jsonify({"message": "Produit modifié avec succès", "product": product.to_dict()}), 200

@app.route('/api/produits/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """
    Suppression d'un produit (admin uniquement)
    """
    product = Product.query.get_or_404(product_id)
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"message": "Produit supprimé avec succès"}), 200

# Routes pour les commandes
@app.route('/api/commandes', methods=['GET'])
@jwt_required()
def get_orders():
    """
    Liste des commandes (admin voit tout, client voit ses commandes)
    """
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404
    
    if user.role == 'admin':
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(utilisateur_id=user.id).all()
    
    return jsonify([order.to_dict() for order in orders]), 200

@app.route('/api/commandes/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """
    Détails d'une commande spécifique
    """
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    order = Order.query.get_or_404(order_id)
    
    # Vérifier si l'utilisateur a le droit de voir cette commande
    if user.role != 'admin' and order.utilisateur_id != user.id:
        return jsonify({"message": "Accès refusé"}), 403
    
    return jsonify(order.to_dict()), 200

@app.route('/api/commandes', methods=['POST'])
@jwt_required()
def create_order():
    """
    Création d'une nouvelle commande
    """
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    data = request.get_json()
    errors = validate_order_data(data)
    
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Créer la commande
    order = Order(
        utilisateur_id=user.id,
        adresse_livraison=data['adresse_livraison']
    )
    
    db.session.add(order)
    db.session.flush()  # Pour obtenir l'ID de la commande avant de créer les lignes
    
    # Ajouter les articles de la commande
    for item_data in data['items']:
        product = Product.query.get(item_data['produit_id'])
        
        if not product:
            db.session.rollback()
            return jsonify({"errors": {f"items.produit_id": f"Produit {item_data['produit_id']} non trouvé"}}), 400
        
        # Vérifier le stock
        if product.quantite_stock < item_data['quantite']:
            db.session.rollback()
            return jsonify({"errors": {f"items.quantite": f"Stock insuffisant pour {product.nom}"}}), 400
        
        # Créer la ligne de commande
        order_item = OrderItem(
            commande_id=order.id,
            produit_id=product.id,
            quantite=item_data['quantite'],
            prix_unitaire=product.prix
        )
        
        # Mettre à jour le stock
        product.quantite_stock -= item_data['quantite']
        
        db.session.add(order_item)
    
    db.session.commit()
    
    return jsonify({"message": "Commande créée avec succès", "order": order.to_dict()}), 201

@app.route('/api/commandes/<int:order_id>', methods=['PATCH'])
@admin_required
def update_order_status(order_id):
    """
    Modification du statut d'une commande (admin uniquement)
    """
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if 'statut' not in data or data['statut'] not in ['en_attente', 'validée', 'expédiée', 'annulée']:
        return jsonify({"errors": {"statut": "Statut invalide"}}), 400
    
    order.statut = data['statut']
    db.session.commit()
    
    return jsonify({"message": "Statut de la commande modifié avec succès", "order": order.to_dict()}), 200

@app.route('/api/commandes/<int:order_id>/lignes', methods=['GET'])
@jwt_required()
def get_order_items(order_id):
    """
    Consultation des lignes d'une commande spécifique
    """
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    order = Order.query.get_or_404(order_id)
    
    # Vérifier si l'utilisateur a le droit de voir cette commande
    if user.role != 'admin' and order.utilisateur_id != user.id:
        return jsonify({"message": "Accès refusé"}), 403
    
    # Récupérer les lignes de la commande
    order_items = OrderItem.query.filter_by(commande_id=order_id).all()
    
    return jsonify({
        "commande_id": order_id,
        "statut": order.statut,
        "total": sum(item.prix_unitaire * item.quantite for item in order_items),
        "lignes": [item.to_dict() for item in order_items]
    }), 200