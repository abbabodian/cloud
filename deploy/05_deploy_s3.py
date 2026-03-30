"""
=============================================================================
 ÉTAPE 5 — Déploiement du frontend sur S3 (Tâche 48)
=============================================================================
 Ce script :
   1. Crée un bucket S3
   2. Active le Static Website Hosting
   3. Configure la Bucket Policy (accès public en lecture)
   4. Modifie app.js pour pointer vers la Lambda Function URL
   5. Upload tous les fichiers du frontend
=============================================================================
"""

import boto3
import json
import os
import sys
import mimetypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

s3_client = boto3.client('s3', region_name=REGION)


def creer_bucket():
    """Crée le bucket S3."""
    print(f"\n📌 Création du bucket : {S3_BUCKET_NAME}")
    try:
        if REGION == "us-east-1":
            s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
        else:
            s3_client.create_bucket(
                Bucket=S3_BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": REGION}
            )
        print(f"   ✅ Bucket créé")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"     Bucket existe déjà (vous en êtes le propriétaire)")
    except Exception as e:
        print(f"    Erreur : {e}")
        return False
    return True


def configurer_website_hosting():
    """Active le Static Website Hosting sur le bucket."""
    print(f"\n📌 Activation du Static Website Hosting...")

    # Désactiver le blocage d'accès public
    s3_client.put_public_access_block(
        Bucket=S3_BUCKET_NAME,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )

    # Configurer le website hosting
    s3_client.put_bucket_website(
        Bucket=S3_BUCKET_NAME,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'index.html'}
        }
    )
    print(f"   ✅ Website Hosting activé")


def configurer_bucket_policy():
    """Configure la Bucket Policy pour accès public en lecture (Rôle 3 IAM)."""
    print(f"\n📌 Configuration de la Bucket Policy (accès public lecture)...")

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
            }
        ]
    }

    s3_client.put_bucket_policy(
        Bucket=S3_BUCKET_NAME,
        Policy=json.dumps(policy)
    )
    print(f"   ✅ Bucket Policy configurée (s3:GetObject public)")


def modifier_api_base(lambda_url):
    """
    Modifie le fichier app.js pour remplacer API_BASE par l'URL Lambda.
    Crée une copie modifiée dans un dossier temporaire.
    """
    print(f"\n📌 Configuration de l'URL API dans app.js...")

    source = os.path.join(FRONTEND_DIR, "app.js")
    with open(source, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Remplacer la ligne API_BASE
    # On cherche : var API_BASE = '';
    # On remplace par : var API_BASE = 'https://xxxxx.lambda-url.us-east-1.on.aws';
    ancien = "var API_BASE = '';"
    nouveau = f"var API_BASE = '{lambda_url.rstrip('/')}';"

    if ancien in contenu:
        contenu = contenu.replace(ancien, nouveau)
        print(f"   ✅ API_BASE remplacé par : {lambda_url}")
    else:
        print(f"   ⚠️  Pattern 'var API_BASE = '';' non trouvé dans app.js")
        print(f"   💡 Modifiez manuellement API_BASE dans app.js")

    return contenu


def upload_fichiers(lambda_url):
    """Upload tous les fichiers du dossier frontend/ vers S3."""
    print(f"\n📌 Upload des fichiers frontend...")

    # Obtenir le contenu modifié de app.js
    app_js_modifie = modifier_api_base(lambda_url)

    compteur = 0
    for nom_fichier in os.listdir(FRONTEND_DIR):
        chemin = os.path.join(FRONTEND_DIR, nom_fichier)

        if not os.path.isfile(chemin):
            continue

        # Déterminer le Content-Type
        content_type, _ = mimetypes.guess_type(nom_fichier)
        if not content_type:
            content_type = 'application/octet-stream'

        # Pour les fichiers HTML/CSS/JS, forcer UTF-8
        if content_type.startswith('text/') or content_type == 'application/javascript':
            content_type += '; charset=utf-8'

        # Lire le contenu
        if nom_fichier == 'app.js':
            # Utiliser la version modifiée avec l'URL Lambda
            contenu = app_js_modifie.encode('utf-8')
        else:
            with open(chemin, 'rb') as f:
                contenu = f.read()

        # Upload vers S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=nom_fichier,
            Body=contenu,
            ContentType=content_type
        )
        print(f"   📄 {nom_fichier} ({content_type})")
        compteur += 1

    print(f"\n   ✅ {compteur} fichiers uploadés")


def main():
    print("=" * 65)
    print("☁️  ÉTAPE 5 — Déploiement du frontend sur S3")
    print("=" * 65)

    # Demander l'URL Lambda
    print("\n📝 Entrez l'URL de votre Lambda Function URL")
    print("   (obtenue à l'étape 4, ex: https://xxx.lambda-url.us-east-1.on.aws/)")
    lambda_url = input("\n   Lambda URL : ").strip()

    if not lambda_url:
        print("❌ URL Lambda requise. Exécutez d'abord l'étape 4.")
        return

    # Vérifier que le dossier frontend existe
    if not os.path.exists(FRONTEND_DIR):
        print(f"❌ Dossier introuvable : {FRONTEND_DIR}")
        return

    # Déployer
    if not creer_bucket():
        return

    configurer_website_hosting()
    configurer_bucket_policy()
    upload_fichiers(lambda_url)

    # URL du site
    if REGION == "us-east-1":
        site_url = f"http://{S3_BUCKET_NAME}.s3-website-{REGION}.amazonaws.com"
    else:
        site_url = f"http://{S3_BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"

    print("\n" + "=" * 65)
    print("✅ FRONTEND DÉPLOYÉ SUR S3")
    print("=" * 65)
    print(f"\n   🌐 URL du site : {site_url}")
    print(f"\n   Ouvrez cette URL dans votre navigateur !")
    print("=" * 65)


if __name__ == "__main__":
    main()