"""
=============================================================================
 ÉTAPE 4 — Déploiement de la Lambda + Function URL (Tâches 47, 50)
=============================================================================
 Ce script :
   1. Crée un fichier ZIP contenant lambda_function.py
   2. Crée la fonction Lambda sur AWS (ou la met à jour)
   3. Active la Function URL avec la configuration CORS corrigée
=============================================================================
"""

import boto3
import json
import zipfile
import os
import sys
import time

# Permet d'importer le fichier de configuration depuis le dossier parent
try:
    from config import *
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import *


# Initialisation des clients AWS
lambda_client = boto3.client('lambda', region_name=REGION)
iam_client = boto3.client('iam', region_name=REGION)


def creer_zip():
    """
    Crée un fichier ZIP contenant le code de la fonction Lambda.
    Le fichier ZIP est nécessaire pour le déploiement sur AWS.
    
    Retourne:
        str or None: Chemin du fichier ZIP créé, ou None en cas d'erreur.
    """
    # Définir les chemins source et destination
    zip_path = os.path.join(PROJECT_ROOT, "lambda_package", "lambda_deploy.zip")
    source_path = os.path.join(PROJECT_ROOT, "lambda_package", "lambda_function.py")

    # Vérifier que le fichier source existe
    if not os.path.exists(source_path):
        print(f"❌ Fichier source Lambda introuvable : {source_path}")
        return None

    print(f"📦 Création du fichier ZIP : {os.path.basename(zip_path)}")
    try:
        # Ouvrir un fichier ZIP en mode écriture
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Ajouter le fichier source au ZIP avec un nom simple
            zf.write(source_path, "lambda_function.py")

        taille = os.path.getsize(zip_path) / 1024
        print(f"   ✅ ZIP créé avec succès ({taille:.1f} Ko)")
        return zip_path
    except Exception as e:
        print(f"   ❌ Erreur lors de la création du ZIP : {e}")
        return None


def deployer_lambda():
    """
    Crée une nouvelle fonction Lambda ou met à jour le code d'une fonction existante.
    
    Retourne:
        bool: True si le déploiement a réussi, False sinon.
    """
    # Étape 1 : Créer l'archive ZIP
    zip_path = creer_zip()
    if not zip_path:
        return False

    # Étape 2 : Récupérer l'ARN du rôle IAM
    try:
        role_response = iam_client.get_role(RoleName=ROLE_LAMBDA_RECO)
        role_arn = role_response['Role']['Arn']
        print(f"   🔑 Utilisation du rôle IAM : {role_arn}")
    except Exception as e:
        print(f"   ❌ Rôle IAM '{ROLE_LAMBDA_RECO}' introuvable.")
        print(f"   💡 Exécutez d'abord le script '01_create_iam_roles.py'.")
        return False

    # Étape 3 : Lire le contenu du fichier ZIP
    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()

    # Étape 4 : Tenter de créer ou de mettre à jour la fonction Lambda
    try:
        print(f"\n📌 Tentative de création de la Lambda : {LAMBDA_FUNCTION_NAME}")
        lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime=LAMBDA_RUNTIME,
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": zip_bytes},
            Description="EduPath Africa - Moteur de recommandation IA",
            Timeout=LAMBDA_TIMEOUT,
            MemorySize=LAMBDA_MEMORY,
            Environment={
                "Variables": {
                    "REGION": REGION,
                    "TABLE_APPRENANTS": TABLE_APPRENANTS,
                    "TABLE_COURS": TABLE_COURS,
                    "TABLE_INTERACTIONS": TABLE_INTERACTIONS,
                }
            }
        )
        print(f"   ✅ Lambda créée avec succès.")

        # Attendre que la Lambda soit pleinement active avant de continuer
        print(f"   ⏳ Attente de l'activation de la Lambda...")
        waiter = lambda_client.get_waiter('function_active_v2')
        waiter.wait(FunctionName=LAMBDA_FUNCTION_NAME)
        print("   ✅ Lambda active.")

    except lambda_client.exceptions.ResourceConflictException:
        print(f"   ⚠️  La Lambda '{LAMBDA_FUNCTION_NAME}' existe déjà. Mise à jour du code en cours...")
        lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_bytes
        )
        print(f"   ✅ Code de la Lambda mis à jour.")
        # Attendre que la mise à jour soit terminée
        waiter = lambda_client.get_waiter('function_updated_v2')
        waiter.wait(FunctionName=LAMBDA_FUNCTION_NAME)
        print("   ✅ Mise à jour terminée.")
    
    except Exception as e:
        print(f"   ❌ Erreur inattendue lors du déploiement de la Lambda : {e}")
        return False
        
    return True


def creer_function_url():
    """
    Crée ou met à jour une Function URL pour la Lambda.
    C'est le point d'accès public (endpoint HTTPS) de notre API.
    
    Retourne:
        str or None: L'URL de la fonction, ou None en cas d'erreur.
    """
    print(f"\n📌 Configuration de la Function URL (endpoint public)...")

    try:
        print(f"   Tentative de création de la Function URL...")
        response = lambda_client.create_function_url_config(
            FunctionName=LAMBDA_FUNCTION_NAME,
            AuthType="NONE",  # Accès public, pas d'authentification IAM
            Cors={
                "AllowOrigins": ["*"],  # Autorise les requêtes de n'importe quel site
                
                # ==============================================================
                # CORRECTION : Ne spécifier que "GET". AWS gère implicitement la
                # méthode OPTIONS pour les pré-vols CORS (preflight requests).
                # Inclure "OPTIONS" ici cause une erreur de validation.
                # ==============================================================
                "AllowMethods": ["GET"],
                
                "AllowHeaders": ["Content-Type"],
                "MaxAge": 86400  # Le navigateur peut mettre en cache la réponse CORS pendant 24h
            }
        )
        function_url = response["FunctionUrl"]
        print(f"   ✅ Function URL créée avec succès : {function_url}")

    except lambda_client.exceptions.ResourceConflictException:
        print(f"   ⚠️  Une Function URL existe déjà. Récupération de l'URL existante...")
        response = lambda_client.get_function_url_config(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        function_url = response["FunctionUrl"]
        print(f"   ✅ URL existante récupérée : {function_url}")

    # Ajouter la permission pour que tout le monde puisse invoquer l'URL
    try:
        lambda_client.add_permission(
            FunctionName=LAMBDA_FUNCTION_NAME,
            StatementId="FunctionURLAllowPublicAccess",
            Action="lambda:InvokeFunctionUrl",
            Principal="*",
            FunctionUrlAuthType="NONE"
        )
        print(f"   ✅ Permission publique (lambda:InvokeFunctionUrl) ajoutée.")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"   ⚠️  La permission publique existe déjà.")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de l'ajout de la permission : {e}")
        return None

    return function_url


def main():
    """
    Fonction principale qui orchestre le déploiement de la Lambda.
    """
    print("=" * 65)
    print("☁️  ÉTAPE 4 — Déploiement Lambda + Function URL")
    print("=" * 65)

    # Déployer la Lambda
    deployment_success = deployer_lambda()
    if not deployment_success:
        print("\n❌ Le déploiement de la Lambda a échoué. Arrêt du script.")
        return

    # Créer la Function URL
    function_url = creer_function_url()
    if not function_url:
        print("\n❌ La création de la Function URL a échoué. Arrêt du script.")
        return

    # Afficher le résumé
    print("\n" + "=" * 65)
    print("✅ LAMBDA DÉPLOYÉE AVEC SUCCÈS")
    print("=" * 65)
    print(f"\n   🔗 Function URL (endpoint public) : {function_url}")
    print(f"\n   💡 Testez ces liens directement dans votre navigateur :")
    print(f"      - {function_url}api/apprenants")
    print(f"      - {function_url}api/recommend?apprenant_id=APP-001")
    print(f"\n   ⚠️  IMPORTANT : Copiez et conservez cette URL !")
    print(f"      Vous en aurez besoin pour l'étape 5 (déploiement du frontend).")
    print("=" * 65)


if __name__ == "__main__":
    main()