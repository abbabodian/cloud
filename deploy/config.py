"""
=============================================================================
 CONFIG.PY — Configuration centrale pour le déploiement AWS
=============================================================================
 Modifiez les valeurs ci-dessous selon votre compte AWS.
 Toutes les autres scripts de déploiement importent ce fichier.
=============================================================================
"""

# ─────────────────────────────────────────────
# RÉGION AWS
# ─────────────────────────────────────────────
# Choisissez la région la plus proche de vos utilisateurs
# us-east-1 = Virginie du Nord (la plus courante)
# eu-west-1 = Irlande (proche de l'Afrique de l'Ouest)
REGION = "us-east-1"

# ─────────────────────────────────────────────
# VOTRE ID DE COMPTE AWS (12 chiffres)
# ─────────────────────────────────────────────
# Pour le trouver : Console AWS > coin supérieur droit > votre nom > Account ID
# Ou : aws sts get-caller-identity --query Account --output text
ACCOUNT_ID = "123456789012"  # ← REMPLACEZ PAR VOTRE ID

# ─────────────────────────────────────────────
# NOMS DES RESSOURCES
# ─────────────────────────────────────────────

# DynamoDB
TABLE_APPRENANTS = "EduPath_Apprenants"
TABLE_COURS = "EduPath_Cours"
TABLE_INTERACTIONS = "EduPath_Interactions"

# Lambda
LAMBDA_FUNCTION_NAME = "EduPath_Recommandation"
LAMBDA_RUNTIME = "python3.12"
LAMBDA_TIMEOUT = 30        # secondes
LAMBDA_MEMORY = 256        # Mo

# S3
S3_BUCKET_NAME = "edupath-africa-frontend-" + ACCOUNT_ID  # Doit être unique mondialement

# IAM
ROLE_LAMBDA_RECO = "EduPath_LambdaRecoRole"
ROLE_LAMBDA_ADMIN = "EduPath_LambdaAdminRole"

# CloudFront
CLOUDFRONT_COMMENT = "EduPath Africa Frontend Distribution"

# CloudWatch
ALARM_NAME = "EduPath_Lambda_Errors"

# ─────────────────────────────────────────────
# CHEMINS LOCAUX
# ─────────────────────────────────────────────
import os

# Dossier racine du projet (un niveau au-dessus de deploy/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
LAMBDA_DIR = os.path.join(PROJECT_ROOT, "lambda_package")