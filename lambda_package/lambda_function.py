"""
=============================================================================
 LAMBDA_FUNCTION.PY — Moteur de Recommandation AWS Lambda
=============================================================================
 Ce fichier est déployé sur AWS Lambda.
 Il remplace recommendation.py en lisant les données depuis DynamoDB
 au lieu des fichiers JSON locaux.

 Handler : lambda_function.lambda_handler

 Événement attendu (via Function URL) :
   GET /?apprenant_id=APP-001
   → Les query string parameters sont dans event['queryStringParameters']
=============================================================================
"""

import json
import math
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

REGION = "us-east-1"
TABLE_APPRENANTS = "EduPath_Apprenants"
TABLE_COURS = "EduPath_Cours"
TABLE_INTERACTIONS = "EduPath_Interactions"

# Client DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table_apprenants = dynamodb.Table(TABLE_APPRENANTS)
table_cours = dynamodb.Table(TABLE_COURS)
table_interactions = dynamodb.Table(TABLE_INTERACTIONS)


# ─────────────────────────────────────────────
# POIDS DE L'ALGORITHME
# ─────────────────────────────────────────────

POIDS = {
    "tags": 0.45,
    "niveau": 0.25,
    "rating": 0.20,
    "popularite": 0.10,
}


# ─────────────────────────────────────────────
# HELPER : Convertir Decimal → float/int
# ─────────────────────────────────────────────

class DecimalEncoder(json.JSONEncoder):
    """DynamoDB retourne des Decimal, JSON ne les accepte pas directement."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


def decimal_to_native(obj):
    """Convertit récursivement les Decimal en int/float natifs Python."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    return obj


# ─────────────────────────────────────────────
# FONCTIONS DE SCORE
# ─────────────────────────────────────────────

def score_tags(tags_apprenant, tags_cours):
    if not tags_apprenant or not tags_cours:
        return 0.0
    s_a = set(tags_apprenant)
    s_c = set(tags_cours)
    inter = s_a & s_c
    union = s_a | s_c
    if not union:
        return 0.0
    return len(inter) / len(union)


def score_niveau(niv_apprenant, niv_cours):
    niveaux = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    n_a = niveaux.get(niv_apprenant, 1)
    n_c = niveaux.get(niv_cours, 1)
    diff = n_c - n_a
    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.7
    elif diff == -1:
        return 0.4
    elif diff == 2:
        return 0.2
    return 0.3


def score_rating(rating):
    return max(0.0, min(1.0, (float(rating) - 3.0) / 2.0))


def score_popularite(nb, maximum):
    if maximum <= 0 or nb <= 0:
        return 0.0
    return math.log(1 + nb) / math.log(1 + maximum)


def generer_explication(apprenant, cours, s_t, s_n, s_r):
    raisons = []
    tags_communs = set(apprenant.get("tags_interet", [])) & set(cours.get("tags", []))
    if tags_communs:
        raisons.append("Correspond à vos intérêts en " + ", ".join(sorted(tags_communs)[:3]))
    if s_n >= 0.7:
        if apprenant.get("niveau") == cours.get("niveau"):
            raisons.append("Niveau " + cours.get("niveau", "") + " adapté à votre profil")
        else:
            raisons.append("Bon niveau pour progresser (" + cours.get("niveau", "") + ")")
    r = float(cours.get("rating", 0))
    if r >= 4.7:
        raisons.append("Très bien noté (" + str(r) + "/5)")
    elif r >= 4.5:
        raisons.append("Bien noté (" + str(r) + "/5)")
    orgs = ["Google", "IBM", "Amazon Web Services", "deeplearning.ai", "Stanford"]
    for o in orgs:
        if o.lower() in cours.get("organisation", "").lower():
            raisons.append("Proposé par " + cours.get("organisation", ""))
            break
    if raisons:
        return " | ".join(raisons[:3])
    return "Cours populaire dans votre domaine"


# ─────────────────────────────────────────────
# FONCTIONS D'ACCÈS DYNAMODB
# ─────────────────────────────────────────────

def get_apprenant(apprenant_id):
    """Récupère un apprenant par son ID depuis DynamoDB."""
    response = table_apprenants.get_item(Key={"apprenant_id": apprenant_id})
    item = response.get("Item")
    if item:
        return decimal_to_native(item)
    return None


def get_all_cours():
    """Récupère tous les cours depuis DynamoDB (scan complet)."""
    items = []
    response = table_cours.scan()
    items.extend(response.get("Items", []))
    # Gérer la pagination si > 1Mo de données
    while "LastEvaluatedKey" in response:
        response = table_cours.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return decimal_to_native(items)


def get_all_apprenants():
    """Récupère tous les apprenants depuis DynamoDB."""
    items = []
    response = table_apprenants.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table_apprenants.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return decimal_to_native(items)


def get_interactions_apprenant(apprenant_id):
    """Récupère toutes les interactions d'un apprenant (Query sur PK)."""
    response = table_interactions.query(
        KeyConditionExpression=Key("apprenant_id").eq(apprenant_id)
    )
    return decimal_to_native(response.get("Items", []))


# ─────────────────────────────────────────────
# FONCTION PRINCIPALE DE RECOMMANDATION
# ─────────────────────────────────────────────

def recommander(apprenant_id):
    """Génère les 5 meilleures recommandations pour un apprenant."""

    # 1. Récupérer l'apprenant
    apprenant = get_apprenant(apprenant_id)
    if not apprenant:
        return {"statusCode": 404, "body": {"error": "Apprenant non trouvé: " + apprenant_id}}

    # 2. Récupérer tous les cours
    cours = get_all_cours()

    # 3. Récupérer les interactions de l'apprenant
    interactions = get_interactions_apprenant(apprenant_id)

    # 4. Cours déjà suivis (COMMENCE ou TERMINE)
    cours_suivis = set()
    for inter in interactions:
        if inter.get("type_interaction") in ("COMMENCE", "TERMINE"):
            cours_suivis.add(inter.get("cours_id"))

    # 5. Filtrer les candidats
    candidats = [c for c in cours if c.get("cours_id") not in cours_suivis]
    if not candidats:
        return {
            "statusCode": 200,
            "body": {
                "apprenant": {
                    "id": apprenant["apprenant_id"],
                    "nom": apprenant["nom"],
                    "niveau": apprenant.get("niveau", ""),
                    "specialisation": apprenant.get("specialisation", ""),
                    "pays": apprenant.get("pays", ""),
                },
                "recommandations": [],
                "nombre_cours_catalogue": len(cours),
            }
        }

    # 6. Max inscrits pour normalisation
    max_inscrits = max(c.get("etudiants_inscrits", 0) for c in cours)

    # 7. Calculer les scores
    resultats = []
    for c in candidats:
        s_t = score_tags(apprenant.get("tags_interet", []), c.get("tags", []))
        s_n = score_niveau(apprenant.get("niveau", "Beginner"), c.get("niveau", "Beginner"))
        s_r = score_rating(c.get("rating", 4.0))
        s_p = score_popularite(c.get("etudiants_inscrits", 0), max_inscrits)

        total = (
            POIDS["tags"] * s_t +
            POIDS["niveau"] * s_n +
            POIDS["rating"] * s_r +
            POIDS["popularite"] * s_p
        )

        explication = generer_explication(apprenant, c, s_t, s_n, s_r)

        resultats.append({
            "cours_id": c.get("cours_id"),
            "titre": c.get("titre"),
            "categorie": c.get("categorie"),
            "niveau": c.get("niveau"),
            "organisation": c.get("organisation"),
            "rating": float(c.get("rating", 0)),
            "duree_heures": int(c.get("duree_heures", 0)),
            "tags": c.get("tags", []),
            "score_pertinence": round(total, 4),
            "details_scores": {
                "tags": round(s_t, 3),
                "niveau": round(s_n, 3),
                "rating": round(s_r, 3),
                "popularite": round(s_p, 3),
            },
            "explication": explication,
        })

    # 8. Trier et retourner top 5
    resultats.sort(key=lambda x: x["score_pertinence"], reverse=True)

    return {
        "statusCode": 200,
        "body": {
            "apprenant": {
                "id": apprenant["apprenant_id"],
                "nom": apprenant["nom"],
                "niveau": apprenant.get("niveau", ""),
                "specialisation": apprenant.get("specialisation", ""),
                "pays": apprenant.get("pays", ""),
            },
            "recommandations": resultats[:5],
            "nombre_cours_catalogue": len(cours),
        }
    }


# ─────────────────────────────────────────────
# HANDLER LAMBDA (point d'entrée AWS)
# ─────────────────────────────────────────────

def lambda_handler(event, context):
    """
    Point d'entrée de la Lambda AWS.
    
    Gère 3 routes selon le path :
      /api/recommend    → recommandations
      /api/apprenants   → liste des apprenants
      /api/stats        → statistiques
      /api/courses      → catalogue complet
    """
    print("EVENT:", json.dumps(event, default=str))

    # Récupérer le chemin et les paramètres
    # Lambda Function URL met le path dans rawPath
    # et les query params dans queryStringParameters
    path = event.get("rawPath", event.get("path", "/"))
    params = event.get("queryStringParameters") or {}

    # Headers CORS pour autoriser les requêtes depuis CloudFront
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    try:
        # ── Route : Recommandations ──
        if "/api/recommend" in path:
            apprenant_id = params.get("apprenant_id", "")
            if not apprenant_id:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"error": "Paramètre apprenant_id manquant"})
                }

            result = recommander(apprenant_id)
            return {
                "statusCode": result["statusCode"],
                "headers": headers,
                "body": json.dumps(result["body"], ensure_ascii=False, cls=DecimalEncoder)
            }

        # ── Route : Liste des apprenants ──
        elif "/api/apprenants" in path:
            apprenants = get_all_apprenants()
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(apprenants, ensure_ascii=False, cls=DecimalEncoder)
            }

        # ── Route : Statistiques ──
        elif "/api/stats" in path:
            cours = get_all_cours()
            apprenants = get_all_apprenants()

            categories = {}
            for c in cours:
                cat = c.get("categorie", "Autre")
                categories[cat] = categories.get(cat, 0) + 1

            # Compter les interactions (scan léger)
            resp = table_interactions.scan(Select="COUNT")
            total_interactions = resp.get("Count", 0)

            stats = {
                "total_cours": len(cours),
                "total_apprenants": len(apprenants),
                "total_interactions": total_interactions,
                "cours_par_categorie": categories,
            }
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(stats, ensure_ascii=False)
            }

        # ── Route : Catalogue de cours ──
        elif "/api/courses" in path:
            cours = get_all_cours()
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(cours, ensure_ascii=False, cls=DecimalEncoder)
            }

        # ── Route par défaut ──
        else:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "EduPath Africa API",
                    "routes": [
                        "/api/apprenants",
                        "/api/recommend?apprenant_id=APP-001",
                        "/api/courses",
                        "/api/stats"
                    ]
                })
            }

    except Exception as e:
        print("ERREUR:", str(e))
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }