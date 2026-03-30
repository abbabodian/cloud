"""
=============================================================================
 RECOMMENDATION.PY — Moteur de Recommandation Content-Based Filtering
=============================================================================
 Algorithme :
   Pour un apprenant donné, on calcule un SCORE de pertinence pour chaque
   cours qu'il n'a PAS encore terminé/commencé.

   Score = (poids_tags × score_tags)
         + (poids_niveau × score_niveau)
         + (poids_rating × score_rating)
         + (poids_popularite × score_popularite)

   On retourne les 5 cours avec les meilleurs scores + explications.

 Ce fichier est importé par server.py. Il peut aussi être utilisé
 directement comme Lambda AWS (voir la fonction lambda_handler).
=============================================================================
"""

import json


# =============================================================================
# SECTION 1 : CONFIGURATION DES POIDS
# =============================================================================
# Ces poids déterminent l'importance de chaque critère dans le score final.
# La somme doit faire 1.0 (100%)

POIDS = {
    "tags": 0.45,          # 45% — Correspondance des tags (le plus important)
    "niveau": 0.25,        # 25% — Adéquation du niveau de difficulté
    "rating": 0.20,        # 20% — Note moyenne du cours
    "popularite": 0.10,    # 10% — Popularité (nombre d'inscrits)
}


# =============================================================================
# SECTION 2 : FONCTIONS DE CALCUL DES SCORES PARTIELS
# =============================================================================

def calculer_score_tags(tags_apprenant, tags_cours):
    """
    Calcule la similarité entre les tags de l'apprenant et ceux du cours.
    
    Utilise le coefficient de Jaccard simplifié :
        score = |intersection| / |union|
    
    Exemple :
        tags_apprenant = ["Python", "Data Science", "AI"]
        tags_cours     = ["Python", "Data Science", "Statistics"]
        intersection   = {"Python", "Data Science"} → 2 éléments
        union          = {"Python", "Data Science", "AI", "Statistics"} → 4
        score          = 2/4 = 0.5
    
    Paramètres :
        tags_apprenant (list) : tags d'intérêt de l'apprenant
        tags_cours (list)     : tags du cours
    Retourne : float entre 0.0 et 1.0
    """
    if not tags_apprenant or not tags_cours:
        return 0.0
    
    set_apprenant = set(tags_apprenant)
    set_cours = set(tags_cours)
    
    intersection = set_apprenant & set_cours    # Tags en commun
    union = set_apprenant | set_cours           # Tous les tags uniques
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def calculer_score_niveau(niveau_apprenant, niveau_cours):
    """
    Compare le niveau de l'apprenant avec celui du cours.
    
    Logique :
    - Même niveau         → score 1.0 (parfait)
    - Niveau juste au-dessus → score 0.7 (bon pour progresser)
    - Niveau en-dessous   → score 0.3 (trop facile)
    - 2 niveaux au-dessus → score 0.2 (trop difficile)
    
    Paramètres :
        niveau_apprenant (str) : "Beginner", "Intermediate" ou "Advanced"
        niveau_cours (str)     : idem
    Retourne : float entre 0.0 et 1.0
    """
    # Convertir les niveaux en nombres pour faciliter la comparaison
    niveaux = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    
    n_apprenant = niveaux.get(niveau_apprenant, 1)
    n_cours = niveaux.get(niveau_cours, 1)
    
    difference = n_cours - n_apprenant
    
    if difference == 0:
        return 1.0    # Même niveau → parfait
    elif difference == 1:
        return 0.7    # Cours un peu plus avancé → stimulant
    elif difference == -1:
        return 0.4    # Cours un peu plus facile → consolidation
    elif difference == 2:
        return 0.2    # Cours beaucoup plus avancé → difficile
    else:
        return 0.3    # Cours beaucoup plus facile


def calculer_score_rating(rating):
    """
    Normalise la note du cours entre 0 et 1.
    Les notes vont de 3.0 à 5.0 dans le dataset.
    
    Formule : (rating - 3.0) / (5.0 - 3.0)
    
    Paramètre : rating (float) — note entre 3.0 et 5.0
    Retourne  : float entre 0.0 et 1.0
    """
    return max(0.0, min(1.0, (rating - 3.0) / 2.0))


def calculer_score_popularite(nb_inscrits, max_inscrits):
    """
    Normalise la popularité du cours entre 0 et 1.
    Utilise une échelle logarithmique pour éviter que les cours
    très populaires dominent trop.
    
    Paramètres :
        nb_inscrits (int)  : nombre d'inscrits du cours
        max_inscrits (int) : nombre max d'inscrits dans le catalogue
    Retourne : float entre 0.0 et 1.0
    """
    if max_inscrits <= 0:
        return 0.0
    
    import math
    # Échelle logarithmique : log(inscrits) / log(max)
    if nb_inscrits <= 0:
        return 0.0
    
    return math.log(1 + nb_inscrits) / math.log(1 + max_inscrits)


# =============================================================================
# SECTION 3 : FONCTION PRINCIPALE DE RECOMMANDATION
# =============================================================================

def generer_recommandations(apprenant, tous_les_cours, interactions, top_n=5):
    """
    Génère les N meilleures recommandations pour un apprenant.
    
    Processus :
    1. Identifier les cours déjà vus/commencés/terminés par l'apprenant
    2. Filtrer les cours candidats (non encore suivis ou juste vus)
    3. Calculer un score de pertinence pour chaque candidat
    4. Trier et retourner les top N
    
    Paramètres :
        apprenant (dict)       : profil de l'apprenant
        tous_les_cours (list)  : catalogue complet des cours
        interactions (list)    : toutes les interactions
        top_n (int)            : nombre de recommandations à retourner
    
    Retourne : list[dict] — top N cours recommandés avec scores et explications
    """
    
    # ---- ÉTAPE 1 : Trouver les cours déjà suivis par l'apprenant ----
    # On considère qu'un cours est "déjà suivi" s'il a été COMMENCE ou TERMINE
    cours_suivis = set()
    for interaction in interactions:
        if interaction["apprenant_id"] == apprenant["apprenant_id"]:
            if interaction["type_interaction"] in ("COMMENCE", "TERMINE"):
                cours_suivis.add(interaction["cours_id"])
    
    # ---- ÉTAPE 2 : Préparer les cours candidats ----
    # On ne recommande que les cours que l'apprenant n'a pas encore suivis
    candidats = [c for c in tous_les_cours if c["cours_id"] not in cours_suivis]
    
    if not candidats:
        return []  # L'apprenant a suivi tous les cours !
    
    # ---- ÉTAPE 3 : Calculer le nombre max d'inscrits (pour la normalisation) ----
    max_inscrits = max(c["etudiants_inscrits"] for c in tous_les_cours)
    
    # ---- ÉTAPE 4 : Calculer le score pour chaque cours candidat ----
    resultats = []
    
    for cours in candidats:
        # Score de correspondance des tags
        s_tags = calculer_score_tags(
            apprenant["tags_interet"],
            cours["tags"]
        )
        
        # Score d'adéquation du niveau
        s_niveau = calculer_score_niveau(
            apprenant["niveau"],
            cours["niveau"]
        )
        
        # Score de la note moyenne
        s_rating = calculer_score_rating(cours["rating"])
        
        # Score de popularité
        s_popularite = calculer_score_popularite(
            cours["etudiants_inscrits"],
            max_inscrits
        )
        
        # ---- SCORE FINAL PONDÉRÉ ----
        score_final = (
            POIDS["tags"]       * s_tags +
            POIDS["niveau"]     * s_niveau +
            POIDS["rating"]     * s_rating +
            POIDS["popularite"] * s_popularite
        )
        
        # ---- GÉNÉRER L'EXPLICATION ----
        # L'explication aide l'apprenant à comprendre pourquoi ce cours
        # est recommandé
        explication = generer_explication(
            apprenant, cours, s_tags, s_niveau, s_rating
        )
        
        resultats.append({
            "cours_id": cours["cours_id"],
            "titre": cours["titre"],
            "categorie": cours["categorie"],
            "niveau": cours["niveau"],
            "organisation": cours["organisation"],
            "rating": cours["rating"],
            "duree_heures": cours["duree_heures"],
            "tags": cours["tags"],
            "score_pertinence": round(score_final, 4),
            "details_scores": {
                "tags": round(s_tags, 3),
                "niveau": round(s_niveau, 3),
                "rating": round(s_rating, 3),
                "popularite": round(s_popularite, 3),
            },
            "explication": explication,
        })
    
    # ---- ÉTAPE 5 : Trier par score décroissant et retourner le top N ----
    resultats.sort(key=lambda x: x["score_pertinence"], reverse=True)
    
    return resultats[:top_n]


# =============================================================================
# SECTION 4 : GÉNÉRATION DES EXPLICATIONS
# =============================================================================

def generer_explication(apprenant, cours, s_tags, s_niveau, s_rating):
    """
    Crée une explication en langage naturel de la recommandation.
    
    Exemples de sorties :
    - "Ce cours correspond à vos intérêts en Python et Data Science."
    - "Niveau adapté pour progresser depuis votre niveau Beginner."
    - "Très bien noté (4.8/5) par la communauté."
    
    Retourne : str — l'explication
    """
    raisons = []
    
    # Raison 1 : Tags en commun
    tags_communs = set(apprenant["tags_interet"]) & set(cours["tags"])
    if tags_communs:
        tags_str = ", ".join(sorted(tags_communs)[:3])
        raisons.append(f"Correspond à vos intérêts en {tags_str}")
    
    # Raison 2 : Niveau adapté
    if s_niveau >= 0.7:
        if apprenant["niveau"] == cours["niveau"]:
            raisons.append(f"Niveau {cours['niveau']} adapté à votre profil")
        else:
            raisons.append(f"Bon niveau pour progresser ({cours['niveau']})")
    
    # Raison 3 : Bonne note
    if cours["rating"] >= 4.7:
        raisons.append(f"Très bien noté ({cours['rating']}/5)")
    elif cours["rating"] >= 4.5:
        raisons.append(f"Bien noté ({cours['rating']}/5)")
    
    # Raison 4 : Organisme reconnu
    orgs_reconnues = ["Google", "IBM", "Amazon Web Services", "deeplearning.ai",
                      "Stanford University", "Johns Hopkins University"]
    for org in orgs_reconnues:
        if org.lower() in cours["organisation"].lower():
            raisons.append(f"Proposé par {cours['organisation']}")
            break
    
    # Combiner les raisons
    if raisons:
        return " | ".join(raisons[:3])  # Max 3 raisons
    else:
        return "Cours populaire dans votre domaine"


# =============================================================================
# SECTION 5 : FONCTION LAMBDA (pour AWS — sera utilisée plus tard)
# =============================================================================

def lambda_handler(event, context=None):
    """
    Point d'entrée pour AWS Lambda.
    
    Pour le moment, cette fonction est utilisée localement par server.py.
    Lors du déploiement AWS, elle sera le handler de la Lambda.
    
    Paramètre event (dict) :
        - apprenant_id (str) : ID de l'apprenant
    
    Retourne : dict avec les 5 recommandations
    """
    # Charger les données depuis les fichiers JSON
    # (sur AWS, on lirait depuis DynamoDB — voir commentaire ci-dessous)
    
    # --- VERSION LOCALE (fichiers JSON) ---
    with open("data/courses.json", "r", encoding="utf-8") as f:
        courses = json.load(f)
    with open("data/apprenants.json", "r", encoding="utf-8") as f:
        apprenants = json.load(f)
    with open("data/interactions.json", "r", encoding="utf-8") as f:
        interactions = json.load(f)
    
    # --- VERSION AWS (DynamoDB) — À UTILISER LORS DU DÉPLOIEMENT ---
    # import boto3
    # dynamodb = boto3.resource('dynamodb')
    # table_courses = dynamodb.Table('EduPath_Cours')
    # table_apprenants = dynamodb.Table('EduPath_Apprenants')
    # table_interactions = dynamodb.Table('EduPath_Interactions')
    # ... (scan ou query les tables)
    
    # Récupérer l'ID de l'apprenant depuis l'événement
    apprenant_id = event.get("apprenant_id", "")
    
    # Trouver le profil de l'apprenant
    apprenant = None
    for a in apprenants:
        if a["apprenant_id"] == apprenant_id:
            apprenant = a
            break
    
    if not apprenant:
        return {
            "statusCode": 404,
            "body": {"error": f"Apprenant {apprenant_id} non trouvé"}
        }
    
    # Générer les recommandations
    recommandations = generer_recommandations(
        apprenant, courses, interactions, top_n=5
    )
    
    return {
        "statusCode": 200,
        "body": {
            "apprenant": {
                "id": apprenant["apprenant_id"],
                "nom": apprenant["nom"],
                "niveau": apprenant["niveau"],
                "specialisation": apprenant["specialisation"],
                "pays": apprenant["pays"],
            },
            "recommandations": recommandations,
            "nombre_cours_catalogue": len(courses),
        }
    }


# =============================================================================
# SECTION 6 : TEST RAPIDE (si on exécute ce fichier directement)
# =============================================================================

if __name__ == "__main__":
    # Test avec le premier apprenant
    result = lambda_handler({"apprenant_id": "APP-001"})
    
    if result["statusCode"] == 200:
        body = result["body"]
        print(f"\n🎯 Recommandations pour {body['apprenant']['nom']}")
        print(f"   Niveau: {body['apprenant']['niveau']}")
        print(f"   Spécialisation: {body['apprenant']['specialisation']}")
        print(f"   Pays: {body['apprenant']['pays']}")
        print(f"\n{'='*70}")
        
        for i, reco in enumerate(body["recommandations"], 1):
            print(f"\n   #{i} — {reco['titre']}")
            print(f"       Score: {reco['score_pertinence']:.4f}")
            print(f"       Catégorie: {reco['categorie']} | Niveau: {reco['niveau']}")
            print(f"       Rating: {reco['rating']}/5 | Durée: {reco['duree_heures']}h")
            print(f"       💡 {reco['explication']}")
    else:
        print(f"❌ Erreur: {result['body']}")