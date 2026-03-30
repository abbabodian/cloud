# 🌍 EduPath Africa — Système de Recommandation de Parcours de Formation

> **Projet P-06** — AWS Academy Cloud Foundations
> Responsable pédagogique : M. LAM Sabarane | Année 2025–2026

---

## 📋 Table des matières

1. [Présentation du projet](#-présentation-du-projet)
2. [Architecture du système](#-architecture-du-système)
3. [Technologies utilisées](#-technologies-utilisées)
4. [Structure du projet](#-structure-du-projet)
5. [Prérequis](#-prérequis)
6. [Installation pas à pas](#-installation-pas-à-pas)
7. [Lancement du projet en local](#-lancement-du-projet-en-local)
8. [Utilisation de l'interface web](#-utilisation-de-linterface-web)
9. [API Endpoints](#-api-endpoints)
10. [Algorithme de recommandation](#-algorithme-de-recommandation)
11. [Modèle de données DynamoDB](#-modèle-de-données-dynamodb)
12. [Déploiement sur AWS](#-déploiement-sur-aws)
13. [Rôles IAM](#-rôles-iam)
14. [Configuration CloudFront](#-configuration-cloudfront)
15. [Monitoring CloudWatch](#-monitoring-cloudwatch)
16. [Évaluation de la qualité](#-évaluation-de-la-qualité)
17. [Dataset source](#-dataset-source)
18. [Correspondance avec les tâches](#-correspondance-avec-les-tâches)
19. [Limites et améliorations futures](#-limites-et-améliorations-futures)
20. [Auteur](#-auteur)

---

## 🎯 Présentation du projet

### Contexte

Le continent africain possède la population la plus jeune du monde : **60 % des habitants ont moins de 25 ans**. Le déficit de compétences numériques est estimé à plusieurs millions de professionnels d'ici 2030 (World Economic Forum).

**EduPath Africa** est une plateforme EdTech fictive proposant **500+ cours en ligne** couvrant la programmation Python, le Cloud AWS, le Big Data, la Cybersécurité, le Machine Learning et bien d'autres domaines.

### Objectif

Construire un **moteur de recommandation personnalisé** capable de suggérer les **5 prochains cours les plus pertinents** pour chaque apprenant, basé sur :

- Son **profil** (niveau, spécialisation, pays)
- Son **historique** d'interactions (cours vus, commencés, terminés, notés)
- La **correspondance des tags** entre ses intérêts et le contenu des cours

Le système utilise une architecture **serverless AWS** avec une interface web accessible depuis un navigateur.

### Services AWS mobilisés

| Module du cours | Service AWS | Rôle dans le projet |
|-----------------|-------------|---------------------|
| M6 — Calcul | **Lambda Python** | Moteur de recommandation, API |
| M7 — Stockage | **S3** | Interface web statique, exports |
| M8 — Bases de données | **DynamoDB** | Profils apprenants, catalogue cours, interactions |
| M5 — Réseau | **CloudFront** | Distribution mondiale du frontend avec cache |
| M4 — Sécurité | **IAM** | Roles, S3 Bucket Policy, Lambda execution role |
| M10 — Monitoring | **CloudWatch** | Logs, métriques Lambda, alarmes |

---

## 🏗 Architecture du système

### Architecture AWS (production)


---

## 🛠 Technologies utilisées

| Catégorie | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| Backend | Python | 3.10+ | Logique métier, algorithme |
| Framework web | Flask | 2.3+ | API REST locale |
| Frontend | HTML5 / CSS3 / JavaScript ES6 | — | Interface utilisateur |
| Données | JSON | — | Stockage local (simule DynamoDB) |
| Typographie | Google Fonts (Inter, Poppins) | — | Police de l'interface |
| Cloud | AWS Lambda, S3, DynamoDB, CloudFront, IAM, CloudWatch | — | Déploiement production |
| Dataset source | Coursera Courses Dataset | 2020 | Catalogue de cours réels |
| Déploiement | boto3, AWS CLI | — | Scripts d'automatisation |

---

## 📁 Structure du projet


---

## ⚙ Prérequis

### Pour le développement local

| Outil | Version minimale | Vérification |
|-------|-----------------|--------------|
| **Python** | 3.10 ou supérieur | `python --version` |
| **pip** | 21.0 ou supérieur | `pip --version` |
| **VS Code** | Dernière version | [Télécharger](https://code.visualstudio.com/) |
| **Navigateur web** | Chrome, Firefox, Edge | N'importe lequel |

### Pour le déploiement AWS (optionnel)

| Outil | Installation | Vérification |
|-------|-------------|--------------|
| **AWS CLI** | [Guide officiel](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) | `aws --version` |
| **boto3** | `pip install boto3` | `python -c "import boto3; print(boto3.__version__)"` |
| **Compte AWS** | Via AWS Academy | `aws sts get-caller-identity` |

### Extensions VS Code recommandées

- **Python** (Microsoft) — Coloration syntaxique, IntelliSense
- **Prettier** — Formatage HTML/CSS/JS

---

## 📥 Installation pas à pas

### Étape 1 — Créer le projet

```bash
# Créer le dossier
mkdir edupath-africa
cd edupath-africa

# Créer les sous-dossiers
mkdir frontend data lambda_package deploy


---

## ⚙ Prérequis

### Pour le développement local

| Outil | Version minimale | Vérification |
|-------|-----------------|--------------|
| **Python** | 3.10 ou supérieur | `python --version` |
| **pip** | 21.0 ou supérieur | `pip --version` |
| **VS Code** | Dernière version | [Télécharger](https://code.visualstudio.com/) |
| **Navigateur web** | Chrome, Firefox, Edge | N'importe lequel |

### Pour le déploiement AWS (optionnel)

| Outil | Installation | Vérification |
|-------|-------------|--------------|
| **AWS CLI** | [Guide officiel](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) | `aws --version` |
| **boto3** | `pip install boto3` | `python -c "import boto3; print(boto3.__version__)"` |
| **Compte AWS** | Via AWS Academy | `aws sts get-caller-identity` |

### Extensions VS Code recommandées

- **Python** (Microsoft) — Coloration syntaxique, IntelliSense
- **Prettier** — Formatage HTML/CSS/JS

---

## 📥 Installation pas à pas

### Étape 1 — Créer le projet

```bash
# Créer le dossier
mkdir edupath-africa
cd edupath-africa

# Créer les sous-dossiers
mkdir frontend data lambda_package deploy

pip install flask
flask>=2.3.0

flask>=2.3.0

python prepare_data.py
============================================================
🚀 EduPath Africa — Préparation des données
============================================================

📚 Étape 1 : Création du catalogue de cours...
✅ Catalogue créé : 75 cours

👥 Étape 2 : Création des profils apprenants...
✅ Profils créés : 20 apprenants

🔄 Étape 3 : Génération des interactions...
✅ Interactions créées : 108 interactions

💾 Étape 4 : Sauvegarde des fichiers JSON...
   → data/courses.json (75 cours)
   → data/apprenants.json (20 apprenants)
   → data/interactions.json (108 interactions)

============================================================
✅ TERMINÉ ! Fichiers générés dans le dossier data/
============================================================

📊 Répartition des cours par catégorie :
   Machine Learning           : 12 cours
   Data Science               : 11 cours
   AI                         : 8 cours
   Python                     : 7 cours
   Cybersecurity              : 7 cours
   Cloud AWS                  : 6 cours
   Web Development            : 5 cours
   ...

   python recommendation.py
   🎯 Recommandations pour Aminata Diallo
   Niveau: Beginner
   Spécialisation: Data Science
   Pays: Sénégal

======================================================================

   #1 — What is Data Science?
       Score: 0.7842
       Catégorie: Data Science | Niveau: Beginner
       Rating: 4.7/5 | Durée: 18h
       💡 Correspond à vos intérêts en Data Science | Proposé par IBM
   ...

   python server.py
   ============================================================
🌍 EduPath Africa — Serveur Local
============================================================
📍 Interface web : http://localhost:5000
📡 API apprenants : http://localhost:5000/api/apprenants
📡 API recommandations : http://localhost:5000/api/recommend?apprenant_id=APP-001
📡 API cours : http://localhost:5000/api/courses
📡 API stats : http://localhost:5000/api/stats
============================================================
Appuyez sur Ctrl+C pour arrêter le serveur






