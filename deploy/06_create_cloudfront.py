"""
=============================================================================
 ÉTAPE 6 — Création de la distribution CloudFront (Tâche 49)
=============================================================================
 Configure CloudFront devant S3 avec :
   - Cache TTL 3600s pour les assets statiques
   - Cache TTL 300s pour les pages HTML
   - HTTPS activé
=============================================================================
"""

import boto3
import json
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

cf_client = boto3.client('cloudfront', region_name='us-east-1')  # CloudFront est global


def creer_distribution():
    """Crée une distribution CloudFront devant le bucket S3."""
    print(f"\n📌 Création de la distribution CloudFront...")

    # Origin : le bucket S3 en mode website hosting
    if REGION == "us-east-1":
        origin_domain = f"{S3_BUCKET_NAME}.s3-website-{REGION}.amazonaws.com"
    else:
        origin_domain = f"{S3_BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"

    # Identifiant unique pour l'origin
    origin_id = "S3-Website-" + S3_BUCKET_NAME

    try:
        response = cf_client.create_distribution(
            DistributionConfig={
                # ── Caller Reference (doit être unique à chaque création) ──
                'CallerReference': str(int(time.time())),

                # ── Comment ──
                'Comment': CLOUDFRONT_COMMENT,

                # ── Activée ──
                'Enabled': True,

                # ── Page par défaut ──
                'DefaultRootObject': 'index.html',

                # ── Origins (sources de contenu) ──
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': origin_id,
                            'DomainName': origin_domain,
                            'CustomOriginConfig': {
                                'HTTPPort': 80,
                                'HTTPSPort': 443,
                                'OriginProtocolPolicy': 'http-only',
                            }
                        }
                    ]
                },

                # ── Comportement de cache par défaut ──
                'DefaultCacheBehavior': {
                    'TargetOriginId': origin_id,
                    'ViewerProtocolPolicy': 'redirect-to-https',

                    # Méthodes autorisées
                    'AllowedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD'],
                        'CachedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD']
                        }
                    },

                    # Forwarding des headers/cookies
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'},
                    },

                    # TTL du cache
                    'MinTTL': 0,
                    'DefaultTTL': 3600,   # 1 heure pour les assets statiques
                    'MaxTTL': 86400,      # 24 heures maximum

                    'Compress': True,  # Compression gzip automatique
                },

                # ── Classe de prix ──
                # PriceClass_100 = USA + Europe (moins cher)
                # PriceClass_200 = + Asie, Afrique, Moyen-Orient
                # PriceClass_All = Toutes les régions
                'PriceClass': 'PriceClass_200',

                # ── Pages d'erreur personnalisées ──
                'CustomErrorResponses': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'ErrorCode': 404,
                            'ResponsePagePath': '/index.html',
                            'ResponseCode': '200',
                            'ErrorCachingMinTTL': 300
                        }
                    ]
                },
            }
        )

        distribution = response['Distribution']
        dist_id = distribution['Id']
        dist_domain = distribution['DomainName']

        print(f"   ✅ Distribution créée !")
        print(f"   📋 ID : {dist_id}")
        print(f"   🌐 URL : https://{dist_domain}")

        return dist_id, dist_domain

    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return None, None


def main():
    print("=" * 65)
    print("☁️  ÉTAPE 6 — Création de la distribution CloudFront")
    print("=" * 65)

    dist_id, dist_domain = creer_distribution()

    if dist_id:
        print("\n" + "=" * 65)
        print("✅ CLOUDFRONT CONFIGURÉ")
        print("=" * 65)
        print(f"\n   Distribution ID : {dist_id}")
        print(f"   URL HTTPS      : https://{dist_domain}")
        print(f"\n   ⏳ La distribution peut prendre 5-15 minutes pour se déployer.")
        print(f"   Pendant ce temps, le status sera 'InProgress'.")
        print(f"\n   Cache configuré :")
        print(f"     Assets statiques (CSS/JS) : TTL 3600s (1 heure)")
        print(f"     Compression gzip          : Activée")
        print(f"     HTTPS                     : Redirect HTTP → HTTPS")
        print("=" * 65)


if __name__ == "__main__":
    main()