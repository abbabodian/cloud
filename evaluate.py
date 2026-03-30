"""
=============================================================================
 EVALUATE.PY — Évaluation de la qualité des recommandations
=============================================================================
 Pour 5 apprenants test, compare les recommandations du système avec
 ce qu'un expert jugerait pertinent (évaluation subjective).
 
 Calcule un "taux de pertinence" : pourcentage des recommandations
 que l'expert juge effectivement utiles pour l'apprenant.
 
 Usage : python evaluate.py
=============================================================================
"""

import json
from recommendation import lambda_handler


def evaluate():
    """
    Évalue les recommandations pour 5 apprenants de test.
    """
    print("=" * 70)
    print("📊 ÉVALUATION DE LA QUALITÉ DES RECOMMANDATIONS")
    print("=" * 70)
    
    # Les 5 apprenants à évaluer
    test_apprenants = ["APP-001", "APP-002", "APP-004", "APP-009", "APP-015"]
    
    # Critères d'évaluation subjective :
    # Pour chaque apprenant, on définit ce qu'on considère comme des
    # catégories/tags PERTINENTS pour leur profil
    evaluation_criteria = {
        "APP-001": {
            # Aminata Diallo — Beginner Data Science (Sénégal)
            "description": "Débutante en Data Science, intéressée par Python et Stats",
            "categories_pertinentes": ["Data Science", "Python", "Statistics"],
            "tags_pertinents": ["Data Science", "Python", "Statistics", "Analytics",
                               "Data Analysis", "Programming", "SQL"],
        },
        "APP-002": {
            # Kwame Asante — Intermediate Machine Learning (Ghana)
            "description": "Intermédiaire en ML, connaît Python et veut du Deep Learning",
            "categories_pertinentes": ["Machine Learning", "AI", "Data Science", "Mathematics"],
            "tags_pertinents": ["Machine Learning", "Deep Learning", "TensorFlow",
                               "AI", "Neural Networks", "Python", "Computer Vision", "NLP"],
        },
        "APP-004": {
            # Chidi Okonkwo — Advanced Deep Learning (Nigeria)
            "description": "Avancé en Deep Learning, cherche des cours spécialisés",
            "categories_pertinentes": ["Machine Learning", "AI"],
            "tags_pertinents": ["Deep Learning", "Neural Networks", "Computer Vision",
                               "NLP", "TensorFlow", "AI", "Reinforcement Learning"],
        },
        "APP-009": {
            # Zainab Adeyemi — Advanced Machine Learning (Nigeria)
            "description": "Avancée en ML, intéressée par Big Data aussi",
            "categories_pertinentes": ["Machine Learning", "AI", "Big Data", "Data Science"],
            "tags_pertinents": ["Machine Learning", "AI", "Deep Learning", "Big Data",
                               "Data Engineering", "TensorFlow", "NLP"],
        },
        "APP-015": {
            # Fatoumata Keita — Advanced Cloud AWS (Mali)
            "description": "Avancée en Cloud AWS, intéressée par Serverless et DevOps",
            "categories_pertinentes": ["Cloud AWS", "Cloud Computing", "DevOps", "Cybersecurity"],
            "tags_pertinents": ["Cloud AWS", "Cloud Computing", "Serverless", "DevOps",
                               "Security", "Cybersecurity", "CI/CD"],
        },
    }
    
    total_pertinent = 0
    total_recommandations = 0
    
    for apprenant_id in test_apprenants:
        criteria = evaluation_criteria[apprenant_id]
        
        # Obtenir les recommandations du système
        result = lambda_handler({"apprenant_id": apprenant_id})
        
        if result["statusCode"] != 200:
            print(f"❌ Erreur pour {apprenant_id}")
            continue
        
        body = result["body"]
        recos = body["recommandations"]
        
        print(f"\n{'─'*70}")
        print(f"👤 {body['apprenant']['nom']} ({apprenant_id})")
        print(f"   {criteria['description']}")
        print(f"   Niveau: {body['apprenant']['niveau']}")
        print()
        
        nb_pertinent = 0
        
        for i, reco in enumerate(recos, 1):
            # Évaluer la pertinence :
            # Un cours est "pertinent" si sa catégorie OU au moins 2 de ses tags
            # correspondent aux critères de l'évaluateur
            
            cat_match = reco["categorie"] in criteria["categories_pertinentes"]
            tags_match = len(set(reco["tags"]) & set(criteria["tags_pertinents"]))
            
            est_pertinent = cat_match or tags_match >= 2
            
            status = "✅ Pertinent" if est_pertinent else "⚠️ Discutable"
            
            if est_pertinent:
                nb_pertinent += 1
            
            print(f"   #{i} {reco['titre'][:55]:55s} Score:{reco['score_pertinence']:.3f} → {status}")
        
        taux = (nb_pertinent / len(recos)) * 100 if recos else 0
        total_pertinent += nb_pertinent
        total_recommandations += len(recos)
        
        print(f"\n   📈 Taux de pertinence : {nb_pertinent}/{len(recos)} = {taux:.0f}%")
    
    # Résumé global
    taux_global = (total_pertinent / total_recommandations * 100) if total_recommandations else 0
    
    print(f"\n{'='*70}")
    print(f"📊 RÉSUMÉ GLOBAL")
    print(f"   Recommandations pertinentes : {total_pertinent}/{total_recommandations}")
    print(f"   Taux de pertinence global   : {taux_global:.1f}%")
    print(f"{'='*70}")
    
    # Limites de l'approche
    print(f"""
📝 LIMITES DE L'APPROCHE :

1. COLD START : Pour un nouvel apprenant sans historique, le système 
   se base uniquement sur les tags d'intérêt déclarés. La qualité 
   dépend de la précision de ces déclarations initiales.

2. BIAIS DE POPULARITÉ : Les cours très populaires (comme "Machine 
   Learning" de Stanford avec 3.2M inscrits) ont un léger avantage 
   dans le score. Cela peut masquer des cours de niche plus pertinents.

3. TAGS AUTOMATIQUES : L'extraction de tags basée sur les mots-clés 
   du titre n'est pas parfaite. Un cours sur "Mathematics for Machine 
   Learning" sera tagué "Mathematics" ET "Machine Learning", ce qui est 
   correct, mais certaines nuances peuvent être manquées.

4. PAS DE FILTRAGE COLLABORATIF : Le système ne prend pas en compte 
   les préférences d'apprenants similaires. Un apprenant avec le même 
   profil que 100 autres pourrait bénéficier de leurs choix de cours.

5. ABSENCE DE SÉQUENÇAGE : Le système ne recommande pas un parcours 
   ordonné (d'abord les bases, puis les cours avancés). Il recommande 
   les 5 cours les plus pertinents indépendamment de l'ordre.

6. ÉVALUATION SUBJECTIVE : Le taux de pertinence est calculé par 
   l'évaluateur humain, ce qui introduit un biais subjectif. Une 
   évaluation A/B avec de vrais apprenants serait plus fiable.
""")


if __name__ == "__main__":
    evaluate()