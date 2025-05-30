from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User

def admin_required(fn):
    """
    Décorateur pour vérifier si l'utilisateur est un administrateur
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            print(f"DEBUG - Checking admin rights for user: {identity}") 
            
            user = User.query.filter_by(email=identity).first()
            if not user:
                print(f"DEBUG - User not found: {identity}") 
                return jsonify(message="Utilisateur non trouvé"), 404
            
            print(f"DEBUG - User role: {user.role}")
            if user.role != 'admin':
                print(f"DEBUG - Access denied: user role is {user.role}") 
                return jsonify(message="Accès réservé aux administrateurs"), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"DEBUG - Error in admin_required: {str(e)}") 
            return jsonify(message="Erreur d'authentification"), 401
    
    return wrapper

def validate_product_data(data):
    """
    Valide les données d'un produit
    """
    errors = {}
    
    if not data.get('nom'):
        errors['nom'] = "Le nom du produit est requis"
    
    if not data.get('prix') or not isinstance(data.get('prix'), (int, float)) or data.get('prix') <= 0:
        errors['prix'] = "Le prix doit être un nombre positif"
    
    if not data.get('categorie'):
        errors['categorie'] = "La catégorie est requise"
    
    if 'quantite_stock' in data and (not isinstance(data['quantite_stock'], int) or data['quantite_stock'] < 0):
        errors['quantite_stock'] = "La quantité en stock doit être un nombre entier positif ou nul"
    
    return errors

def validate_category_data(data):
    """
    Valide les données d'une catégorie
    """
    errors = {}
    
    if not data.get('nom'):
        errors['nom'] = "Le nom de la catégorie est requis"
    
    return errors

def validate_order_data(data):
    """
    Valide les données d'une commande
    """
    errors = {}
    
    if not data.get('adresse_livraison'):
        errors['adresse_livraison'] = "L'adresse de livraison est requise"
    
    if not data.get('items') or not isinstance(data.get('items'), list) or len(data.get('items')) == 0:
        errors['items'] = "Au moins un article est requis dans la commande"
    else:
        for i, item in enumerate(data.get('items')):
            if not item.get('produit_id'):
                errors[f'items[{i}].produit_id'] = "L'identifiant du produit est requis"
            if not item.get('quantite') or not isinstance(item.get('quantite'), int) or item.get('quantite') <= 0:
                errors[f'items[{i}].quantite'] = "La quantité doit être un nombre entier positif"
    
    return errors

def validate_user_data(data, is_registration=True):
    """
    Valide les données d'un utilisateur
    """
    errors = {}
    
    if is_registration:
        if not data.get('email'):
            errors['email'] = "L'email est requis"
        
        if not data.get('mot_de_passe') or len(data.get('mot_de_passe')) < 6:
            errors['mot_de_passe'] = "Le mot de passe doit contenir au moins 6 caractères"
        
        if not data.get('nom'):
            errors['nom'] = "Le nom est requis"
    else:
        if not data.get('email'):
            errors['email'] = "L'email est requis"
        
        if not data.get('mot_de_passe'):
            errors['mot_de_passe'] = "Le mot de passe est requis"
    
    return errors