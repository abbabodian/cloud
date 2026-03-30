"""
=============================================================================
 ÉTAPE 1 — Création des 3 rôles IAM (Tâche 51)
=============================================================================
 Crée :
   1. EduPath_LambdaRecoRole  → Lecture seule DynamoDB + Logs CloudWatch
   2. EduPath_LambdaAdminRole → Écriture DynamoDB (chargement initial)
   3. Bucket Policy S3        → Accès public en lecture (frontend)
=============================================================================
"""

import boto3
import json
import time
import sys
import os

# Ajouter le dossier deploy/ au path pour importer config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# Client IAM
iam = boto3.client('iam', region_name=REGION)


def creer_role(nom_role, description, policy_document):
    """
    Crée un rôle IAM avec une politique attachée.
    
    Paramètres :
        nom_role (str)        : Nom du rôle (ex: "EduPath_LambdaRecoRole")
        description (str)     : Description du rôle
        policy_document (dict): Document de politique JSON
    """
    # Document de confiance : qui peut assumer ce rôle ?
    # Ici, c'est le service Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        # Créer le rôle
        print(f"\n📌 Création du rôle : {nom_role}")
        response = iam.create_role(
            RoleName=nom_role,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description,
            MaxSessionDuration=3600
        )
        role_arn = response['Role']['Arn']
        print(f"   ✅ Rôle créé : {role_arn}")

        # Attacher la politique inline
        policy_name = nom_role + "_Policy"
        iam.put_role_policy(
            RoleName=nom_role,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"   ✅ Politique attachée : {policy_name}")

        return role_arn

    except iam.exceptions.EntityAlreadyExistsException:
        print(f"     Le rôle {nom_role} existe déjà")
        # Récupérer l'ARN existant
        response = iam.get_role(RoleName=nom_role)
        return response['Role']['Arn']

    except Exception as e:
        print(f"    Erreur : {e}")
        return None


def main():
    print("=" * 65)
    print("☁️  ÉTAPE 1 — Création des rôles IAM")
    print("=" * 65)

    # ─────────────────────────────────────────
    # RÔLE 1 : LambdaRecoRole (lecture seule)
    # ─────────────────────────────────────────
    # Ce rôle est utilisé par la Lambda de recommandation.
    # Il ne peut QUE lire les données DynamoDB (Query, GetItem).
    # Principe de moindre privilège : pas de PutItem, DeleteItem, etc.

    policy_reco = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DynamoDBReadOnly",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:Query",
                    "dynamodb:GetItem",
                    "dynamodb:Scan",
                    "dynamodb:BatchGetItem"
                ],
                "Resource": [
                    f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{TABLE_APPRENANTS}",
                    f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{TABLE_COURS}",
                    f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{TABLE_INTERACTIONS}",
                    f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{TABLE_INTERACTIONS}/index/*"
                ]
            },
            {
                "Sid": "CloudWatchLogs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": f"arn:aws:logs:{REGION}:{ACCOUNT_ID}:*"
            }
        ]
    }

    arn_reco = creer_role(
        ROLE_LAMBDA_RECO,
        "Rôle Lambda pour le moteur de recommandation EduPath (lecture seule DynamoDB)",
        policy_reco
    )

    # ─────────────────────────────────────────
    # RÔLE 2 : LambdaAdminRole (écriture)
    # ─────────────────────────────────────────
    # Ce rôle est utilisé UNIQUEMENT pour le chargement initial des données.
    # Il permet d'écrire dans DynamoDB (BatchWriteItem, PutItem).
    # À désactiver après la migration initiale pour plus de sécurité.

    policy_admin = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DynamoDBWrite",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:BatchWriteItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem"
                ],
                "Resource": [
                    f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{TABLE_APPRENANTS}",
                    f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{TABLE_COURS}",
                    f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{TABLE_INTERACTIONS}"
                ]
            },
            {
                "Sid": "CloudWatchLogs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": f"arn:aws:logs:{REGION}:{ACCOUNT_ID}:*"
            }
        ]
    }

    arn_admin = creer_role(
        ROLE_LAMBDA_ADMIN,
        "Rôle Lambda admin pour chargement initial des données EduPath (écriture DynamoDB)",
        policy_admin
    )

    # Attendre que les rôles soient propagés par IAM
    print("\n⏳ Attente de 10 secondes pour la propagation IAM...")
    time.sleep(10)

    # ─────────────────────────────────────────
    # RÉSUMÉ
    # ─────────────────────────────────────────
    print("\n" + "=" * 65)
    print("✅ RÔLES IAM CRÉÉS")
    print("=" * 65)
    print(f"   LambdaRecoRole  : {arn_reco}")
    print(f"   LambdaAdminRole : {arn_admin}")
    print(f"   S3 Bucket Policy: sera créée à l'étape 5 (deploy S3)")
    print()
    print("💡 Note : La Bucket Policy S3 (rôle 3) sera configurée")
    print("   automatiquement lors du déploiement du frontend S3.")
    print("=" * 65)


if __name__ == "__main__":
    main()