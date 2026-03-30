"""
=============================================================================
 ÉTAPE 2 — Création des 3 tables DynamoDB (Tâche 45)
=============================================================================
 Crée les tables :
   1. EduPath_Apprenants    (PK: apprenant_id)
   2. EduPath_Cours         (PK: cours_id)
   3. EduPath_Interactions  (PK: apprenant_id, SK: cours_id_timestamp)
=============================================================================
"""

import boto3
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# Client DynamoDB
dynamodb = boto3.client('dynamodb', region_name=REGION)


def creer_table(nom_table, cle_partition, cle_tri=None):
    """
    Crée une table DynamoDB.
    
    Paramètres :
        nom_table (str)      : Nom de la table
        cle_partition (str)  : Nom de la clé de partition (PK)
        cle_tri (str ou None): Nom de la clé de tri (SK), optionnelle
    """
    print(f"\n📌 Création de la table : {nom_table}")

    # Définir le schéma de clé
    key_schema = [
        {
            'AttributeName': cle_partition,
            'KeyType': 'HASH'  # HASH = Partition Key
        }
    ]
    attribute_definitions = [
        {
            'AttributeName': cle_partition,
            'AttributeType': 'S'  # S = String
        }
    ]

    # Ajouter la clé de tri si elle est définie
    if cle_tri:
        key_schema.append({
            'AttributeName': cle_tri,
            'KeyType': 'RANGE'  # RANGE = Sort Key
        })
        attribute_definitions.append({
            'AttributeName': cle_tri,
            'AttributeType': 'S'
        })

    try:
        dynamodb.create_table(
            TableName=nom_table,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode='PAY_PER_REQUEST'  # Mode à la demande (pas de provisionnement)
        )
        print(f"    Table créée : {nom_table}")

        # Attendre que la table soit active
        print(f"    Attente de l'activation...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=nom_table)
        print(f"    Table active !")

    except dynamodb.exceptions.ResourceInUseException:
        print(f"     La table {nom_table} existe déjà")
    except Exception as e:
        print(f"    Erreur : {e}")


def main():
    print("=" * 65)
    print("☁️  ÉTAPE 2 — Création des tables DynamoDB")
    print("=" * 65)

    # Table 1 : Apprenants
    # PK = apprenant_id (ex: "APP-001")
    creer_table(TABLE_APPRENANTS, "apprenant_id")

    # Table 2 : Cours
    # PK = cours_id (ex: "COURS-001")
    creer_table(TABLE_COURS, "cours_id")

    # Table 3 : Interactions
    # PK = apprenant_id, SK = cours_id_timestamp
    # Le SK combine le cours_id et le timestamp pour permettre
    # plusieurs interactions par apprenant sur le même cours
    creer_table(TABLE_INTERACTIONS, "apprenant_id", "cours_id_timestamp")

    print("\n" + "=" * 65)
    print("✅ TOUTES LES TABLES SONT CRÉÉES")
    print("=" * 65)
    print(f"   {TABLE_APPRENANTS}")
    print(f"   {TABLE_COURS}")
    print(f"   {TABLE_INTERACTIONS}")
    print("=" * 65)


if __name__ == "__main__":
    main()