"""
=============================================================================
 ÉTAPE 7 — Configuration CloudWatch (M10)
=============================================================================
 Configure :
   1. Une alarme sur les erreurs Lambda (> 5 erreurs en 5 minutes)
   2. Un dashboard avec les métriques Lambda
=============================================================================
"""

import boto3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

cw_client = boto3.client('cloudwatch', region_name=REGION)
logs_client = boto3.client('logs', region_name=REGION)


def creer_alarme():
    """Crée une alarme CloudWatch sur les erreurs Lambda."""
    print(f"\n📌 Création de l'alarme CloudWatch...")

    cw_client.put_metric_alarm(
        AlarmName=ALARM_NAME,
        AlarmDescription="Alerte si la Lambda EduPath a plus de 5 erreurs en 5 minutes",
        Namespace="AWS/Lambda",
        MetricName="Errors",
        Dimensions=[
            {
                "Name": "FunctionName",
                "Value": LAMBDA_FUNCTION_NAME
            }
        ],
        Statistic="Sum",
        Period=300,            # 5 minutes
        EvaluationPeriods=1,   # 1 période d'évaluation
        Threshold=5,           # Seuil : 5 erreurs
        ComparisonOperator="GreaterThanThreshold",
        TreatMissingData="notBreaching",
    )
    print(f"   ✅ Alarme créée : {ALARM_NAME}")
    print(f"   📊 Seuil : > 5 erreurs en 5 minutes")


def creer_dashboard():
    """Crée un dashboard CloudWatch avec les métriques Lambda."""
    print(f"\n📌 Création du dashboard CloudWatch...")

    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "title": "Lambda - Invocations",
                    "metrics": [
                        ["AWS/Lambda", "Invocations", "FunctionName", LAMBDA_FUNCTION_NAME]
                    ],
                    "period": 300,
                    "region": REGION,
                    "stat": "Sum"
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "title": "Lambda - Durée (ms)",
                    "metrics": [
                        ["AWS/Lambda", "Duration", "FunctionName", LAMBDA_FUNCTION_NAME]
                    ],
                    "period": 300,
                    "region": REGION,
                    "stat": "Average"
                }
            },
            {
                "type": "metric",
                "x": 0, "y": 6,
                "width": 12, "height": 6,
                "properties": {
                    "title": "Lambda - Erreurs",
                    "metrics": [
                        ["AWS/Lambda", "Errors", "FunctionName", LAMBDA_FUNCTION_NAME]
                    ],
                    "period": 300,
                    "region": REGION,
                    "stat": "Sum"
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 6,
                "width": 12, "height": 6,
                "properties": {
                    "title": "Lambda - Exécutions concurrentes",
                    "metrics": [
                        ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", LAMBDA_FUNCTION_NAME]
                    ],
                    "period": 300,
                    "region": REGION,
                    "stat": "Maximum"
                }
            }
        ]
    }

    cw_client.put_dashboard(
        DashboardName="EduPath_Africa_Dashboard",
        DashboardBody=json.dumps(dashboard_body)
    )
    print(f"   ✅ Dashboard créé : EduPath_Africa_Dashboard")


def main():
    print("=" * 65)
    print("☁️  ÉTAPE 7 — Configuration CloudWatch")
    print("=" * 65)

    creer_alarme()
    creer_dashboard()

    console_url = f"https://{REGION}.console.aws.amazon.com/cloudwatch/home?region={REGION}#dashboards:name=EduPath_Africa_Dashboard"

    print("\n" + "=" * 65)
    print("✅ CLOUDWATCH CONFIGURÉ")
    print("=" * 65)
    print(f"\n   📊 Dashboard : EduPath_Africa_Dashboard")
    print(f"   🔔 Alarme    : {ALARM_NAME}")
    print(f"\n   🔗 Console CloudWatch :")
    print(f"   {console_url}")
    print("=" * 65)


if __name__ == "__main__":
    main()