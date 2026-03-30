"""
=============================================================================
 ÉTAPE 3 — Chargement des données dans DynamoDB (Tâche 46)
=============================================================================
 Lit les fichiers JSON générés par prepare_data.py et les insère
 dans les 3 tables DynamoDB (75 cours, 20 apprenants, ~100 interactions).
=============================================================================
"""

import boto3
import json
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# Ressource DynamoDB (pas client — plus simple pour PutItem)
dynamodb = boto3.resource('dynamodb', region_name=REGION)


def convertir_float_en_decimal(obj):
    """
    DynamoDB n'accepte pas les float Python, seulement les Decimal.
    Cette fonction convertit récursivement tous les float en Decimal.
    
    Paramètre : obj — n'importe quel type Python
    Retourne  : le même objet avec les float convertis en Decimal
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convertir_float_en_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_float_en_decimal(i) for i in obj]
    return obj


def charger_table(nom_table, fichier_json, cle_nom):
    """
    Charge un fichier JSON dans une table DynamoDB.
    
    Utilise batch_writer() pour des insertions par lots
    (plus rapide et moins coûteux que des PutItem individuels).
    
    Paramètres :
        nom_table (str)   : Nom de la table DynamoDB
        fichier_json (str): Chemin du fichier JSON source
        cle_nom (str)     : Nom de la clé primaire (pour le log)
    """
    print(f"\n📌 Chargement dans {nom_table}...")

    # Vérifier que le fichier existe
    chemin = os.path.join(DATA_DIR, fichier_json)
    if not os.path.exists(chemin):
        print(f"   ❌ Fichier introuvable : {chemin}")
        print(f"   💡 Exécutez d'abord : python prepare_data.py")
        return 0

    # Lire le fichier JSON
    with open(chemin, 'r', encoding='utf-8') as f:
        donnees = json.load(f)

    # Convertir les float en Decimal (exigence DynamoDB)
    donnees = convertir_float_en_decimal(donnees)

    # Ouvrir la table
    table = dynamodb.Table(nom_table)

    # Insérer par lots avec batch_writer
    compteur = 0
    with table.batch_writer() as batch:
        for item in donnees:
            # Supprimer les champs None (DynamoDB ne les accepte pas)
            item_propre = {k: v for k, v in item.items() if v is not None}
            batch.put_item(Item=item_propre)
            compteur += 1

    print(f"   ✅ {compteur} éléments insérés dans {nom_table}")
    return compteur


def main():
    print("=" * 65)
    print("☁️  ÉTAPE 3 — Chargement des données dans DynamoDB")
    print("=" * 65)

    # Vérifier que le dossier data/ existe
    if not os.path.exists(DATA_DIR):
        print("\n❌ Le dossier data/ n'existe pas !")
        print("   Exécutez d'abord : python prepare_data.py")
        return

    # Charger les 3 tables
    n1 = charger_table(TABLE_COURS, "courses.json", "cours_id")
    n2 = charger_table(TABLE_APPRENANTS, "apprenants.json", "apprenant_id")
    n3 = charger_table(TABLE_INTERACTIONS, "interactions.json", "apprenant_id")

    print("\n" + "=" * 65)
    print("✅ DONNÉES CHARGÉES DANS DYNAMODB")
    print("=" * 65)
    print(f"   {TABLE_COURS}         : {n1} cours")
    print(f"   {TABLE_APPRENANTS}    : {n2} apprenants")
    print(f"   {TABLE_INTERACTIONS}  : {n3} interactions")
    print("=" * 65)


if __name__ == "__main__":
    main()