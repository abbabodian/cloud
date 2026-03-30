"""
=============================================================================
 SERVER.PY — Serveur local Flask (simule AWS Lambda + API Gateway)
=============================================================================
 Ce serveur :
   - Sert l'interface web (dossier frontend/)
   - Expose une API REST pour les recommandations
   - Simule le comportement de Lambda Function URL

 Endpoints :
   GET  /                              → Page web principale
   GET  /api/apprenants                → Liste de tous les apprenants
   GET  /api/recommend?apprenant_id=X  → Recommandations pour l'apprenant X
   GET  /api/courses                   → Liste de tous les cours
   GET  /api/stats                     → Statistiques du catalogue

 Lancer : python server.py
 Puis ouvrir : http://localhost:5000
=============================================================================
"""

from flask import Flask, jsonify, request, send_from_directory
import json
import os

# Importer notre moteur de recommandation
from recommendation import lambda_handler


# =============================================================================
# CONFIGURATION FLASK
# =============================================================================

# Créer l'application Flask
# static_folder pointe vers le dossier frontend/ pour servir les fichiers HTML/CSS/JS
app = Flask(
    __name__,
    static_folder='frontend',      # Dossier des fichiers statiques
    static_url_path=''             # URL de base pour les fichiers statiques
)


# =============================================================================
# ROUTE 1 : Page d'accueil (sert index.html)
# =============================================================================

@app.route('/')
def index():
    """
    Sert la page HTML principale.
    Quand l'utilisateur va sur http://localhost:5000, il reçoit index.html
    """
    return send_from_directory('frontend', 'index.html')


# =============================================================================
# ROUTE 2 : Liste des apprenants
# =============================================================================

@app.route('/api/apprenants')
def get_apprenants():
    """
    Retourne la liste de tous les apprenants en JSON.
    Utilisé par le frontend pour remplir la liste déroulante.
    
    Exemple de réponse :
    [
        {"apprenant_id": "APP-001", "nom": "Aminata Diallo", ...},
        {"apprenant_id": "APP-002", "nom": "Kwame Asante", ...},
        ...
    ]
    """
    try:
        with open("data/apprenants.json", "r", encoding="utf-8") as f:
            apprenants = json.load(f)
        return jsonify(apprenants)
    except FileNotFoundError:
        return jsonify({"error": "Fichier data/apprenants.json introuvable. Exécutez d'abord prepare_data.py"}), 404


# =============================================================================
# ROUTE 3 : Recommandations pour un apprenant
# =============================================================================

@app.route('/api/recommend')
def get_recommendations():
    """
    Génère et retourne les 5 recommandations pour un apprenant donné.
    
    Paramètre URL : apprenant_id (ex: /api/recommend?apprenant_id=APP-001)
    
    Exemple de réponse :
    {
        "apprenant": {"id": "APP-001", "nom": "Aminata Diallo", ...},
        "recommandations": [
            {"titre": "...", "score_pertinence": 0.82, ...},
            ...
        ]
    }
    """
    # Récupérer le paramètre apprenant_id depuis l'URL
    apprenant_id = request.args.get('apprenant_id', '')
    
    if not apprenant_id:
        return jsonify({"error": "Paramètre 'apprenant_id' manquant"}), 400
    
    # Appeler le moteur de recommandation (simule Lambda)
    result = lambda_handler({"apprenant_id": apprenant_id})
    
    return jsonify(result["body"]), result["statusCode"]


# =============================================================================
# ROUTE 4 : Liste des cours
# =============================================================================

@app.route('/api/courses')
def get_courses():
    """
    Retourne le catalogue complet des cours.
    """
    try:
        with open("data/courses.json", "r", encoding="utf-8") as f:
            courses = json.load(f)
        return jsonify(courses)
    except FileNotFoundError:
        return jsonify({"error": "Fichier data/courses.json introuvable"}), 404


# =============================================================================
# ROUTE 5 : Statistiques
# =============================================================================

@app.route('/api/stats')
def get_stats():
    """
    Retourne des statistiques sur le catalogue et les apprenants.
    Utile pour le dashboard du frontend.
    """
    try:
        with open("data/courses.json", "r", encoding="utf-8") as f:
            courses = json.load(f)
        with open("data/apprenants.json", "r", encoding="utf-8") as f:
            apprenants = json.load(f)
        with open("data/interactions.json", "r", encoding="utf-8") as f:
            interactions = json.load(f)
        
        # Compter les cours par catégorie
        categories = {}
        for c in courses:
            cat = c["categorie"]
            categories[cat] = categories.get(cat, 0) + 1
        
        return jsonify({
            "total_cours": len(courses),
            "total_apprenants": len(apprenants),
            "total_interactions": len(interactions),
            "cours_par_categorie": categories,
        })
    except FileNotFoundError:
        return jsonify({"error": "Fichiers de données introuvables"}), 404


# =============================================================================
# LANCEMENT DU SERVEUR
# =============================================================================

if __name__ == '__main__':
    # Vérifier que les données existent
    if not os.path.exists("data/courses.json"):
        print("⚠️  Fichiers de données introuvables !")
        print("   Exécutez d'abord : python prepare_data.py")
        print("   Puis relancez : python server.py")
        exit(1)
    
    print("=" * 60)
    print("🌍 EduPath Africa — Serveur Local")
    print("=" * 60)
    print(f"📍 Interface web : http://localhost:5000")
    print(f"📡 API apprenants : http://localhost:5000/api/apprenants")
    print(f"📡 API recommandations : http://localhost:5000/api/recommend?apprenant_id=APP-001")
    print(f"📡 API cours : http://localhost:5000/api/courses")
    print(f"📡 API stats : http://localhost:5000/api/stats")
    print("=" * 60)
    print("Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    # Démarrer le serveur en mode debug (recharge automatique si on modifie le code)
    app.run(debug=True, port=5000)