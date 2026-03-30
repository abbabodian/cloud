"""
=============================================================================
 PREPARE_DATA.PY — Préparation des données EduPath Africa
=============================================================================
 Ce script :
   1. Charge les cours Coursera (intégrés directement depuis le CSV du PDF)
   2. Filtre les cours tech/IT pertinents (50+ cours)
   3. Enrichit chaque cours avec des tags et catégories
   4. Crée 20 profils d'apprenants fictifs africains
   5. Génère des interactions réalistes (VU/COMMENCE/TERMINE/NOTE)
   6. Sauvegarde tout en JSON dans le dossier data/

 Usage dans VS Code : clic droit sur le fichier > "Run Python File in Terminal"
 Ou dans le terminal : python prepare_data.py
=============================================================================
"""

import json       # Pour lire/écrire des fichiers JSON
import os         # Pour créer des dossiers
import random     # Pour générer des données aléatoires
import uuid       # Pour créer des identifiants uniques
from datetime import datetime, timedelta  # Pour les dates


# =============================================================================
# SECTION 1 : DONNÉES BRUTES DES COURS (extraites du PDF Coursera)
# =============================================================================
# Chaque cours est un dictionnaire avec les colonnes du CSV :
#   - id_original : l'index dans le dataset Coursera
#   - title : titre du cours
#   - organization : organisme qui propose le cours
#   - cert_type : COURSE, SPECIALIZATION ou PROFESSIONAL CERTIFICATE
#   - rating : note moyenne (sur 5)
#   - difficulty : Beginner, Intermediate, Advanced ou Mixed
#   - enrolled : nombre d'étudiants inscrits (chaîne comme "350k")

RAW_COURSES = [
    # ---- CLOUD AWS ----
    {"id_original": 43, "title": "AWS Fundamentals", "organization": "Amazon Web Services", "cert_type": "SPECIALIZATION", "rating": 4.6, "difficulty": "Beginner", "enrolled": "130k"},
    {"id_original": 631, "title": "AWS Fundamentals: Addressing Security Risk", "organization": "Amazon Web Services", "cert_type": "COURSE", "rating": 4.3, "difficulty": "Beginner", "enrolled": "11k"},
    {"id_original": 861, "title": "AWS Fundamentals: Building Serverless Applications", "organization": "Amazon Web Services", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "27k"},
    {"id_original": 281, "title": "AWS Fundamentals: Going Cloud-Native", "organization": "Amazon Web Services", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "110k"},
    {"id_original": 828, "title": "AWS Fundamentals: Migrating to the Cloud", "organization": "Amazon Web Services", "cert_type": "COURSE", "rating": 4.5, "difficulty": "Intermediate", "enrolled": "13k"},
    {"id_original": 568, "title": "Getting Started with AWS Machine Learning", "organization": "Amazon Web Services", "cert_type": "COURSE", "rating": 4.5, "difficulty": "Intermediate", "enrolled": "73k"},

    # ---- CLOUD COMPUTING (autres) ----
    {"id_original": 349, "title": "Cloud Computing", "organization": "University of Illinois at Urbana-Champaign", "cert_type": "SPECIALIZATION", "rating": 4.4, "difficulty": "Intermediate", "enrolled": "110k"},
    {"id_original": 777, "title": "Cloud Computing Basics (Cloud 101)", "organization": "LearnQuest", "cert_type": "COURSE", "rating": 4.5, "difficulty": "Beginner", "enrolled": "37k"},
    {"id_original": 594, "title": "Introduction to Cloud Computing", "organization": "IBM", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "2.6k"},

    # ---- PYTHON ----
    {"id_original": 179, "title": "Crash Course on Python", "organization": "Google", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Beginner", "enrolled": "81k"},
    {"id_original": 47, "title": "Programming for Everybody (Getting Started with Python)", "organization": "University of Michigan", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Mixed", "enrolled": "1.3m"},
    {"id_original": 3, "title": "Python for Everybody", "organization": "University of Michigan", "cert_type": "SPECIALIZATION", "rating": 4.8, "difficulty": "Beginner", "enrolled": "1.5m"},
    {"id_original": 279, "title": "Python Basics", "organization": "University of Michigan", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Beginner", "enrolled": "110k"},
    {"id_original": 111, "title": "Python Data Structures", "organization": "University of Michigan", "cert_type": "COURSE", "rating": 4.9, "difficulty": "Mixed", "enrolled": "420k"},
    {"id_original": 152, "title": "Python for Data Science and AI", "organization": "IBM", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "170k"},
    {"id_original": 25, "title": "Google IT Automation with Python", "organization": "Google", "cert_type": "PROFESSIONAL CERTIFICATE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "93k"},

    # ---- DATA SCIENCE ----
    {"id_original": 0, "title": "IBM Data Science", "organization": "IBM", "cert_type": "PROFESSIONAL CERTIFICATE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "480k"},
    {"id_original": 1, "title": "Introduction to Data Science", "organization": "IBM", "cert_type": "SPECIALIZATION", "rating": 4.6, "difficulty": "Beginner", "enrolled": "310k"},
    {"id_original": 13, "title": "Data Science", "organization": "Johns Hopkins University", "cert_type": "SPECIALIZATION", "rating": 4.5, "difficulty": "Beginner", "enrolled": "830k"},
    {"id_original": 88, "title": "What is Data Science?", "organization": "IBM", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "260k"},
    {"id_original": 198, "title": "Data Science Methodology", "organization": "IBM", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "89k"},
    {"id_original": 146, "title": "Tools for Data Science", "organization": "IBM", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "120k"},
    {"id_original": 399, "title": "Data Science Math Skills", "organization": "Duke University", "cert_type": "COURSE", "rating": 4.5, "difficulty": "Beginner", "enrolled": "140k"},
    {"id_original": 8, "title": "Applied Data Science", "organization": "IBM", "cert_type": "SPECIALIZATION", "rating": 4.6, "difficulty": "Beginner", "enrolled": "220k"},
    {"id_original": 26, "title": "Applied Data Science with Python", "organization": "University of Michigan", "cert_type": "SPECIALIZATION", "rating": 4.5, "difficulty": "Intermediate", "enrolled": "480k"},
    {"id_original": 277, "title": "Data Analysis with Python", "organization": "IBM", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "110k"},
    {"id_original": 157, "title": "Advanced Data Science with IBM", "organization": "IBM", "cert_type": "SPECIALIZATION", "rating": 4.4, "difficulty": "Advanced", "enrolled": "320k"},
    {"id_original": 187, "title": "Introduction to Data Science in Python", "organization": "University of Michigan", "cert_type": "COURSE", "rating": 4.5, "difficulty": "Intermediate", "enrolled": "390k"},

    # ---- DATA VISUALIZATION ----
    {"id_original": 420, "title": "Data Visualization with Python", "organization": "IBM", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Intermediate", "enrolled": "66k"},
    {"id_original": 686, "title": "Data Visualization and Communication with Tableau", "organization": "Duke University", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Mixed", "enrolled": "130k"},

    # ---- MACHINE LEARNING ----
    {"id_original": 6, "title": "Machine Learning", "organization": "Stanford University", "cert_type": "COURSE", "rating": 4.9, "difficulty": "Mixed", "enrolled": "3.2m"},
    {"id_original": 321, "title": "Machine Learning with Python", "organization": "IBM", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Intermediate", "enrolled": "120k"},
    {"id_original": 630, "title": "Applied Machine Learning in Python", "organization": "University of Michigan", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Intermediate", "enrolled": "150k"},
    {"id_original": 585, "title": "Machine Learning for All", "organization": "University of London", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "19k"},
    {"id_original": 189, "title": "Structuring Machine Learning Projects", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Beginner", "enrolled": "220k"},
    {"id_original": 125, "title": "Machine Learning with TensorFlow on Google Cloud Platform", "organization": "Google Cloud", "cert_type": "SPECIALIZATION", "rating": 4.5, "difficulty": "Intermediate", "enrolled": "72k"},

    # ---- DEEP LEARNING / AI ----
    {"id_original": 5, "title": "Deep Learning", "organization": "deeplearning.ai", "cert_type": "SPECIALIZATION", "rating": 4.8, "difficulty": "Intermediate", "enrolled": "690k"},
    {"id_original": 62, "title": "Neural Networks and Deep Learning", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.9, "difficulty": "Intermediate", "enrolled": "630k"},
    {"id_original": 207, "title": "Convolutional Neural Networks", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.9, "difficulty": "Intermediate", "enrolled": "240k"},
    {"id_original": 285, "title": "Sequence Models", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Intermediate", "enrolled": "14k"},
    {"id_original": 123, "title": "Improving Deep Neural Networks: Hyperparameter Tuning, Regularization and Optimization", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.9, "difficulty": "Beginner", "enrolled": "270k"},
    {"id_original": 54, "title": "AI For Everyone", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Beginner", "enrolled": "350k"},
    {"id_original": 58, "title": "AI Foundations for Everyone", "organization": "IBM", "cert_type": "SPECIALIZATION", "rating": 4.7, "difficulty": "Beginner", "enrolled": "61k"},
    {"id_original": 427, "title": "Introduction to Artificial Intelligence (AI)", "organization": "IBM", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "44k"},
    {"id_original": 230, "title": "Introduction to TensorFlow for Artificial Intelligence, Machine Learning, and Deep Learning", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Intermediate", "enrolled": "150k"},
    {"id_original": 27, "title": "TensorFlow in Practice", "organization": "deeplearning.ai", "cert_type": "SPECIALIZATION", "rating": 4.7, "difficulty": "Intermediate", "enrolled": "170k"},
    {"id_original": 431, "title": "Natural Language Processing in TensorFlow", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Intermediate", "enrolled": "40k"},
    {"id_original": 358, "title": "Convolutional Neural Networks in TensorFlow", "organization": "deeplearning.ai", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Intermediate", "enrolled": "46k"},

    # ---- CYBERSÉCURITÉ ----
    {"id_original": 134, "title": "(ISC)2 Systems Security Certified Practitioner (SSCP)", "organization": "(ISC)2", "cert_type": "SPECIALIZATION", "rating": 4.7, "difficulty": "Beginner", "enrolled": "5.3k"},
    {"id_original": 372, "title": "Cybersecurity", "organization": "University of Maryland, College Park", "cert_type": "SPECIALIZATION", "rating": 4.5, "difficulty": "Intermediate", "enrolled": "99k"},
    {"id_original": 183, "title": "Introduction to Cyber Security", "organization": "New York University", "cert_type": "SPECIALIZATION", "rating": 4.7, "difficulty": "Beginner", "enrolled": "32k"},
    {"id_original": 469, "title": "Introduction to Cybersecurity Tools and Cyber Attacks", "organization": "IBM", "cert_type": "COURSE", "rating": 4.5, "difficulty": "Beginner", "enrolled": "30k"},
    {"id_original": 497, "title": "Cybersecurity for Business", "organization": "University of Colorado System", "cert_type": "SPECIALIZATION", "rating": 4.6, "difficulty": "Beginner", "enrolled": "23k"},
    {"id_original": 526, "title": "Palo Alto Networks Cybersecurity", "organization": "Palo Alto Networks", "cert_type": "SPECIALIZATION", "rating": 4.6, "difficulty": "Beginner", "enrolled": "9.1k"},
    {"id_original": 612, "title": "Access Controls", "organization": "(ISC)2", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "2.9k"},

    # ---- WEB DEVELOPMENT ----
    {"id_original": 329, "title": "HTML, CSS, and Javascript for Web Developers", "organization": "Johns Hopkins University", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Mixed", "enrolled": "240k"},
    {"id_original": 307, "title": "Introduction to HTML5", "organization": "University of Michigan", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Mixed", "enrolled": "220k"},
    {"id_original": 664, "title": "Introduction to CSS3", "organization": "University of Michigan", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Mixed", "enrolled": "84k"},
    {"id_original": 89, "title": "Full-Stack Web Development with React", "organization": "The Hong Kong University of Science and Technology", "cert_type": "SPECIALIZATION", "rating": 4.7, "difficulty": "Intermediate", "enrolled": "150k"},
    {"id_original": 625, "title": "Introduction to Web Development", "organization": "University of California, Davis", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "76k"},

    # ---- DATABASE / SQL ----
    {"id_original": 263, "title": "Databases and SQL for Data Science", "organization": "IBM", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "110k"},
    {"id_original": 332, "title": "SQL for Data Science", "organization": "University of California, Davis", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "160k"},

    # ---- DEVOPS / AGILE ----
    {"id_original": 448, "title": "Continuous Delivery and DevOps", "organization": "University of Virginia", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "26k"},
    {"id_original": 75, "title": "Agile Development", "organization": "University of Virginia", "cert_type": "SPECIALIZATION", "rating": 4.7, "difficulty": "Beginner", "enrolled": "94k"},
    {"id_original": 482, "title": "Agile Meets Design Thinking", "organization": "University of Virginia", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "69k"},
    {"id_original": 589, "title": "Version Control with Git", "organization": "Atlassian", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Mixed", "enrolled": "40k"},

    # ---- MOBILE DEVELOPMENT ----
    {"id_original": 390, "title": "Android App Development", "organization": "Vanderbilt University", "cert_type": "SPECIALIZATION", "rating": 4.5, "difficulty": "Beginner", "enrolled": "120k"},
    {"id_original": 387, "title": "Swift 5 iOS Application Developer", "organization": "LearnQuest", "cert_type": "SPECIALIZATION", "rating": 4.5, "difficulty": "Beginner", "enrolled": "3.9k"},

    # ---- BIG DATA ----
    {"id_original": 862, "title": "Introduction to Big Data", "organization": "University of California San Diego", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Mixed", "enrolled": "160k"},
    {"id_original": 227, "title": "Google Cloud Platform Big Data and Machine Learning Fundamentals", "organization": "Google Cloud", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Intermediate", "enrolled": "120k"},

    # ---- BLOCKCHAIN ----
    {"id_original": 251, "title": "Blockchain", "organization": "University at Buffalo", "cert_type": "SPECIALIZATION", "rating": 4.6, "difficulty": "Intermediate", "enrolled": "68k"},
    {"id_original": 719, "title": "Blockchain: Foundations and Use Cases", "organization": "ConsenSys Academy", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "31k"},

    # ---- GESTION DE PROJET ----
    {"id_original": 30, "title": "Project Management Principles and Practices", "organization": "University of California, Irvine", "cert_type": "SPECIALIZATION", "rating": 4.7, "difficulty": "Beginner", "enrolled": "230k"},

    # ---- IT SUPPORT ----
    {"id_original": 4, "title": "Google IT Support", "organization": "Google", "cert_type": "PROFESSIONAL CERTIFICATE", "rating": 4.8, "difficulty": "Beginner", "enrolled": "350k"},
    {"id_original": 41, "title": "Technical Support Fundamentals", "organization": "Google", "cert_type": "COURSE", "rating": 4.8, "difficulty": "Beginner", "enrolled": "280k"},

    # ---- STATISTICS / R ----
    {"id_original": 317, "title": "R Programming", "organization": "Johns Hopkins University", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Intermediate", "enrolled": "480k"},
    {"id_original": 642, "title": "Basic Statistics", "organization": "University of Amsterdam", "cert_type": "COURSE", "rating": 4.6, "difficulty": "Beginner", "enrolled": "180k"},

    # ---- MATHEMATICS FOR ML ----
    {"id_original": 55, "title": "Mathematics for Machine Learning", "organization": "Imperial College London", "cert_type": "SPECIALIZATION", "rating": 4.6, "difficulty": "Beginner", "enrolled": "150k"},
    {"id_original": 223, "title": "Mathematics for Machine Learning: Linear Algebra", "organization": "Imperial College London", "cert_type": "COURSE", "rating": 4.7, "difficulty": "Beginner", "enrolled": "140k"},
]

# Au total : 75 cours tech couvrant 8+ domaines ✓


# =============================================================================
# SECTION 2 : MAPPINGS MOTS-CLÉS → TAGS
# =============================================================================
# Ce dictionnaire associe des mots-clés (trouvés dans le titre) à des tags.
# Le moteur de recommandation utilisera ces tags pour comparer les cours
# avec les préférences des apprenants.

TAG_KEYWORDS = {
    "python":           ["Python", "Programming"],
    "machine learning": ["Machine Learning", "AI"],
    "deep learning":    ["Deep Learning", "AI", "Machine Learning"],
    "neural network":   ["Deep Learning", "Neural Networks", "AI"],
    "tensorflow":       ["TensorFlow", "Deep Learning", "Machine Learning"],
    "aws":              ["Cloud AWS", "Cloud Computing"],
    "cloud":            ["Cloud Computing"],
    "serverless":       ["Cloud AWS", "Serverless", "Cloud Computing"],
    "cybersecurity":    ["Cybersecurity", "Security"],
    "cyber security":   ["Cybersecurity", "Security"],
    "cyber attack":     ["Cybersecurity", "Security"],
    "security":         ["Security"],
    "sql":              ["SQL", "Database"],
    "database":         ["Database", "SQL"],
    "html":             ["Web Development", "HTML/CSS"],
    "css":              ["Web Development", "HTML/CSS"],
    "javascript":       ["Web Development", "JavaScript"],
    "react":            ["Web Development", "React", "JavaScript"],
    "full-stack":       ["Web Development", "Full-Stack"],
    "full stack":       ["Web Development", "Full-Stack"],
    "web development":  ["Web Development"],
    "android":          ["Mobile Development", "Android"],
    "ios":              ["Mobile Development", "iOS"],
    "swift":            ["Mobile Development", "iOS", "Swift"],
    "mobile":           ["Mobile Development"],
    "agile":            ["DevOps", "Agile", "Project Management"],
    "devops":           ["DevOps"],
    "continuous delivery": ["DevOps", "CI/CD"],
    "git":              ["Git", "DevOps"],
    "version control":  ["Git", "DevOps"],
    "blockchain":       ["Blockchain"],
    "big data":         ["Big Data", "Data Engineering"],
    "data science":     ["Data Science", "Analytics"],
    "data analysis":    ["Data Analysis", "Data Science"],
    "data visualization": ["Data Visualization", "Analytics"],
    "artificial intelligence": ["AI"],
    "ai for":           ["AI"],
    "ai foundation":    ["AI"],
    "statistics":       ["Statistics", "Data Science"],
    "r programming":    ["R", "Statistics", "Data Science"],
    "project management": ["Project Management"],
    "it support":       ["IT Support"],
    "it automation":    ["IT Support", "Automation", "DevOps"],
    "nlp":              ["NLP", "AI"],
    "natural language":  ["NLP", "AI"],
    "tableau":          ["Tableau", "Data Visualization"],
    "data engineer":    ["Data Engineering", "Big Data"],
    "reinforcement":    ["Reinforcement Learning", "AI"],
    "convolutional":    ["Computer Vision", "Deep Learning"],
    "sequence model":   ["NLP", "Deep Learning"],
    "linear algebra":   ["Mathematics", "Machine Learning"],
    "math":             ["Mathematics"],
    "hyperparameter":   ["Deep Learning", "Machine Learning"],
}


# =============================================================================
# SECTION 3 : MAPPING VERS LES CATÉGORIES PRINCIPALES
# =============================================================================
# Chaque cours sera assigné à UNE catégorie principale pour l'affichage.
# L'ordre dans ce dictionnaire définit la priorité (première correspondance gagne).

CATEGORY_PRIORITY = [
    ("Cloud AWS",           ["aws"]),
    ("Cloud Computing",     ["cloud"]),
    ("Python",              ["python"]),
    ("Data Science",        ["data science", "data analysis", "data visualization"]),
    ("Machine Learning",    ["machine learning", "deep learning", "neural", "tensorflow"]),
    ("AI",                  ["artificial intelligence", "ai for", "ai foundation"]),
    ("DevOps",              ["devops", "agile", "continuous delivery", "git", "version control"]),
    ("Cybersecurity",       ["cybersecurity", "cyber security", "security", "cyber attack"]),
    ("Web Development",     ["html", "css", "javascript", "react", "web", "full-stack", "full stack"]),
    ("Mobile Development",  ["android", "ios", "swift", "mobile"]),
    ("Big Data",            ["big data"]),
    ("Database",            ["sql", "database"]),
    ("Blockchain",          ["blockchain"]),
    ("Project Management",  ["project management"]),
    ("Statistics",          ["statistics", "r programming"]),
    ("IT Support",          ["it support", "technical support"]),
    ("Mathematics",         ["math", "linear algebra"]),
]


# =============================================================================
# SECTION 4 : FONCTIONS UTILITAIRES
# =============================================================================

def parse_enrolled(value_str):
    """
    Convertit une chaîne comme '5.3k', '130k', '1.3m', '3.2m'
    en un nombre entier (5300, 130000, 1300000, 3200000).
    
    Paramètre : value_str (str) — ex: "130k"
    Retourne  : int — ex: 130000
    """
    value_str = str(value_str).strip().lower()
    
    if 'm' in value_str:
        # Cas millions : "3.2m" → 3200000
        return int(float(value_str.replace('m', '')) * 1_000_000)
    elif 'k' in value_str:
        # Cas milliers : "130k" → 130000
        return int(float(value_str.replace('k', '')) * 1_000)
    else:
        # Cas normal : "500" → 500
        return int(float(value_str))


def extract_tags(title):
    """
    Extrait automatiquement les tags d'un cours à partir de son titre.
    
    Parcourt le dictionnaire TAG_KEYWORDS et vérifie si chaque mot-clé
    apparaît dans le titre du cours (insensible à la casse).
    
    Paramètre : title (str) — ex: "Machine Learning with Python"
    Retourne  : list[str] — ex: ["Machine Learning", "AI", "Python", "Programming"]
    """
    title_lower = title.lower()
    tags = set()  # set pour éviter les doublons
    
    for keyword, tag_list in TAG_KEYWORDS.items():
        if keyword in title_lower:
            for tag in tag_list:
                tags.add(tag)
    
    # Si aucun tag trouvé, on ajoute un tag générique
    if not tags:
        tags.add("General Tech")
    
    return sorted(list(tags))  # Trier pour cohérence


def assign_category(title):
    """
    Assigne UNE catégorie principale à un cours basé sur son titre.
    Utilise CATEGORY_PRIORITY — la première correspondance est choisie.
    
    Paramètre : title (str) — ex: "AWS Fundamentals: Building Serverless Applications"
    Retourne  : str — ex: "Cloud AWS"
    """
    title_lower = title.lower()
    
    for category_name, keywords in CATEGORY_PRIORITY:
        for kw in keywords:
            if kw in title_lower:
                return category_name
    
    return "General Tech"  # Catégorie par défaut


def estimate_duration(cert_type, difficulty):
    """
    Estime la durée en heures d'un cours selon son type et sa difficulté.
    
    Paramètres :
        cert_type (str) — "COURSE", "SPECIALIZATION" ou "PROFESSIONAL CERTIFICATE"
        difficulty (str) — "Beginner", "Intermediate", "Advanced" ou "Mixed"
    Retourne : int — durée estimée en heures
    """
    # Durées de base selon le type
    base_hours = {
        "COURSE": 20,
        "SPECIALIZATION": 80,
        "PROFESSIONAL CERTIFICATE": 120,
    }
    hours = base_hours.get(cert_type, 30)
    
    # Ajustement selon la difficulté
    if difficulty == "Advanced":
        hours = int(hours * 1.3)
    elif difficulty == "Intermediate":
        hours = int(hours * 1.1)
    elif difficulty == "Beginner":
        hours = int(hours * 0.9)
    
    return hours


def generate_prerequisites(tags, difficulty):
    """
    Génère une liste de prérequis logiques basés sur les tags et le niveau.
    
    Un cours avancé en ML aura des prérequis comme "Python", "Statistics" etc.
    Un cours débutant n'aura pas de prérequis.
    
    Paramètres :
        tags (list) — tags du cours
        difficulty (str) — niveau de difficulté
    Retourne : list[str] — liste des prérequis
    """
    if difficulty == "Beginner":
        return []  # Pas de prérequis pour les débutants
    
    prereqs = []
    
    # Règles de prérequis basées sur les tags
    prereq_rules = {
        "Machine Learning": ["Python", "Basic Statistics"],
        "Deep Learning": ["Python", "Machine Learning basics"],
        "TensorFlow": ["Python", "Machine Learning basics"],
        "Data Science": ["Python basics", "Basic Statistics"],
        "Data Analysis": ["Python basics or Excel"],
        "Cloud AWS": ["Basic IT knowledge"],
        "Cloud Computing": ["Basic IT knowledge"],
        "Cybersecurity": ["Basic networking"],
        "Web Development": ["HTML/CSS basics"],
        "React": ["JavaScript basics"],
        "Full-Stack": ["HTML/CSS", "JavaScript"],
        "DevOps": ["Basic programming"],
        "Big Data": ["SQL basics", "Python basics"],
        "NLP": ["Python", "Machine Learning basics"],
        "Computer Vision": ["Python", "Deep Learning basics"],
        "Database": ["Basic programming"],
        "Data Visualization": ["Basic data analysis"],
        "Statistics": ["Basic mathematics"],
        "R": ["Basic statistics"],
        "Data Engineering": ["Python", "SQL"],
    }
    
    for tag in tags:
        if tag in prereq_rules:
            for prereq in prereq_rules[tag]:
                if prereq not in prereqs:
                    prereqs.append(prereq)
    
    return prereqs[:3]  # Maximum 3 prérequis


# =============================================================================
# SECTION 5 : CRÉATION DU CATALOGUE DE COURS
# =============================================================================

def create_course_catalog():
    """
    Transforme les données brutes (RAW_COURSES) en un catalogue enrichi
    au format compatible DynamoDB.
    
    Chaque cours reçoit :
    - Un cours_id unique (format "COURS-001")
    - Des tags automatiques
    - Une catégorie
    - Une durée estimée
    - Des prérequis
    
    Retourne : list[dict] — liste des cours enrichis
    """
    catalog = []
    
    for i, raw_course in enumerate(RAW_COURSES):
        # Générer un ID unique pour le cours
        cours_id = f"COURS-{i+1:03d}"  # COURS-001, COURS-002, etc.
        
        # Extraire les tags automatiquement depuis le titre
        tags = extract_tags(raw_course["title"])
        
        # Assigner une catégorie principale
        categorie = assign_category(raw_course["title"])
        
        # Estimer la durée
        duree = estimate_duration(raw_course["cert_type"], raw_course["difficulty"])
        
        # Générer les prérequis
        prereqs = generate_prerequisites(tags, raw_course["difficulty"])
        
        # Convertir le nombre d'inscrits
        enrolled_count = parse_enrolled(raw_course["enrolled"])
        
        # Mapper la difficulté : "Mixed" → "Intermediate" pour simplifier
        niveau = raw_course["difficulty"]
        if niveau == "Mixed":
            niveau = "Intermediate"
        
        # Construire l'objet cours (format DynamoDB)
        course = {
            "cours_id": cours_id,
            "id_original_coursera": raw_course["id_original"],
            "titre": raw_course["title"],
            "organisation": raw_course["organization"],
            "type_certificat": raw_course["cert_type"],
            "categorie": categorie,
            "niveau": niveau,
            "rating": raw_course["rating"],
            "duree_heures": duree,
            "etudiants_inscrits": enrolled_count,
            "prerequis": prereqs,
            "tags": tags,
        }
        
        catalog.append(course)
    
    print(f"✅ Catalogue créé : {len(catalog)} cours")
    return catalog


# =============================================================================
# SECTION 6 : CRÉATION DES PROFILS APPRENANTS
# =============================================================================

def create_learner_profiles():
    """
    Crée 20 profils d'apprenants fictifs avec des contextes africains.
    
    Chaque apprenant a :
    - Un ID unique
    - Un nom réaliste (diversité africaine)
    - Un pays africain
    - Un niveau (Beginner/Intermediate/Advanced)
    - Une spécialisation (domaine d'intérêt)
    - Des tags d'intérêt (pour le moteur de recommandation)
    - Une date d'inscription
    
    Retourne : list[dict] — liste des 20 profils
    """
    # Données des apprenants fictifs
    learners_data = [
        # (nom, pays, niveau, spécialisation, tags_interet)
        ("Aminata Diallo", "Sénégal", "Beginner", "Data Science",
         ["Data Science", "Python", "Statistics"]),
        
        ("Kwame Asante", "Ghana", "Intermediate", "Machine Learning",
         ["Machine Learning", "Deep Learning", "Python", "TensorFlow"]),
        
        ("Fatou Ndiaye", "Sénégal", "Beginner", "Cloud AWS",
         ["Cloud AWS", "Cloud Computing", "Security"]),
        
        ("Chidi Okonkwo", "Nigeria", "Advanced", "Deep Learning",
         ["Deep Learning", "Neural Networks", "Computer Vision", "NLP"]),
        
        ("Amina Yusuf", "Kenya", "Beginner", "Web Development",
         ["Web Development", "HTML/CSS", "JavaScript"]),
        
        ("Moussa Traoré", "Mali", "Intermediate", "Cybersecurity",
         ["Cybersecurity", "Security", "Cloud Computing"]),
        
        ("Grace Mwangi", "Kenya", "Intermediate", "Data Science",
         ["Data Science", "Data Analysis", "Python", "SQL"]),
        
        ("Ibrahim Coulibaly", "Côte d'Ivoire", "Beginner", "Python",
         ["Python", "Programming", "Data Science"]),
        
        ("Zainab Adeyemi", "Nigeria", "Advanced", "Machine Learning",
         ["Machine Learning", "AI", "Deep Learning", "Big Data"]),
        
        ("Jean-Pierre Habimana", "Rwanda", "Beginner", "Cloud AWS",
         ["Cloud AWS", "Cloud Computing", "DevOps"]),
        
        ("Aissatou Barry", "Guinée", "Intermediate", "Data Science",
         ["Data Science", "Data Visualization", "Python", "Tableau"]),
        
        ("David Mensah", "Ghana", "Beginner", "DevOps",
         ["DevOps", "Git", "Cloud Computing", "Agile"]),
        
        ("Mariama Bah", "Gambie", "Intermediate", "AI",
         ["AI", "Machine Learning", "Python"]),
        
        ("Oluwaseun Adeleke", "Nigeria", "Beginner", "Mobile Development",
         ["Mobile Development", "Android", "Programming"]),
        
        ("Fatoumata Keita", "Mali", "Advanced", "Cloud AWS",
         ["Cloud AWS", "Cloud Computing", "Serverless", "DevOps", "Security"]),
        
        ("Samuel Tesfaye", "Éthiopie", "Intermediate", "Big Data",
         ["Big Data", "Data Engineering", "SQL", "Python"]),
        
        ("Nadia Benali", "Maroc", "Beginner", "Data Science",
         ["Data Science", "Statistics", "Python", "Analytics"]),
        
        ("Kofi Boateng", "Ghana", "Intermediate", "Web Development",
         ["Web Development", "React", "JavaScript", "Full-Stack"]),
        
        ("Blessing Okafor", "Nigeria", "Beginner", "Cybersecurity",
         ["Cybersecurity", "Security", "IT Support"]),
        
        ("Abdoulaye Sow", "Sénégal", "Intermediate", "Machine Learning",
         ["Machine Learning", "Python", "Data Science", "Mathematics"]),
    ]
    
    apprenants = []
    base_date = datetime(2024, 1, 1)
    
    for i, (nom, pays, niveau, specialisation, tags) in enumerate(learners_data):
        # Générer un ID unique
        apprenant_id = f"APP-{i+1:03d}"
        
        # Date d'inscription aléatoire dans les 12 derniers mois
        jours_offset = random.randint(0, 365)
        date_inscription = (base_date + timedelta(days=jours_offset)).strftime("%Y-%m-%d")
        
        apprenant = {
            "apprenant_id": apprenant_id,
            "nom": nom,
            "pays": pays,
            "niveau": niveau,
            "specialisation": specialisation,
            "tags_interet": tags,
            "date_inscription": date_inscription,
        }
        
        apprenants.append(apprenant)
    
    print(f"✅ Profils créés : {len(apprenants)} apprenants")
    return apprenants


# =============================================================================
# SECTION 7 : CRÉATION DES INTERACTIONS
# =============================================================================

def create_interactions(apprenants, courses):
    """
    Génère des interactions réalistes entre apprenants et cours.
    
    Types d'interaction :
    - VU       : l'apprenant a vu la fiche du cours
    - COMMENCE : l'apprenant a commencé le cours
    - TERMINE  : l'apprenant a terminé le cours
    - NOTE     : l'apprenant a noté le cours
    
    La logique : les interactions sont basées sur la correspondance
    entre les tags d'intérêt de l'apprenant et les tags du cours.
    
    Retourne : list[dict] — liste des interactions
    """
    interactions = []
    base_date = datetime(2024, 3, 1)
    
    for apprenant in apprenants:
        # Trouver les cours qui correspondent aux intérêts de l'apprenant
        matching_courses = []
        for course in courses:
            # Compter le nombre de tags en commun
            common_tags = set(apprenant["tags_interet"]) & set(course["tags"])
            if common_tags:
                matching_courses.append((course, len(common_tags)))
        
        # Trier par pertinence (plus de tags en commun = plus pertinent)
        matching_courses.sort(key=lambda x: x[1], reverse=True)
        
        # Chaque apprenant interagit avec 3 à 8 cours
        nb_interactions = random.randint(3, min(8, len(matching_courses)))
        selected_courses = matching_courses[:nb_interactions]
        
        for course, match_score in selected_courses:
            # Générer un timestamp aléatoire
            jours_offset = random.randint(0, 180)
            timestamp = (base_date + timedelta(
                days=jours_offset,
                hours=random.randint(8, 22),
                minutes=random.randint(0, 59)
            )).strftime("%Y-%m-%dT%H:%M:%S")
            
            # Déterminer le type d'interaction selon le match score
            # Plus le score est élevé, plus l'apprenant avance dans le cours
            if match_score >= 3:
                # Fort intérêt → probablement terminé
                type_interaction = random.choice(["TERMINE", "TERMINE", "COMMENCE"])
                progression = random.randint(70, 100) if type_interaction == "TERMINE" else random.randint(30, 70)
                note = round(random.uniform(3.5, 5.0), 1) if type_interaction == "TERMINE" else None
            elif match_score >= 2:
                # Intérêt moyen → commencé ou vu
                type_interaction = random.choice(["COMMENCE", "COMMENCE", "VU"])
                progression = random.randint(10, 60) if type_interaction == "COMMENCE" else 0
                note = None
            else:
                # Faible intérêt → juste vu
                type_interaction = "VU"
                progression = 0
                note = None
            
            interaction = {
                "apprenant_id": apprenant["apprenant_id"],
                "cours_id_timestamp": f"{course['cours_id']}#{timestamp}",
                "cours_id": course["cours_id"],
                "type_interaction": type_interaction,
                "note": note,
                "progression_pct": progression,
                "timestamp": timestamp,
            }
            
            interactions.append(interaction)
    
    print(f"✅ Interactions créées : {len(interactions)} interactions")
    return interactions


# =============================================================================
# SECTION 8 : PROGRAMME PRINCIPAL
# =============================================================================

def main():
    """
    Fonction principale qui orchestre toute la préparation des données.
    Crée le dossier 'data/' et y sauvegarde les 3 fichiers JSON.
    """
    print("=" * 60)
    print("🚀 EduPath Africa — Préparation des données")
    print("=" * 60)
    
    # Créer le dossier data/ s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Étape 1 : Créer le catalogue de cours
    print("\n📚 Étape 1 : Création du catalogue de cours...")
    courses = create_course_catalog()
    
    # Étape 2 : Créer les profils apprenants
    print("\n👥 Étape 2 : Création des profils apprenants...")
    apprenants = create_learner_profiles()
    
    # Étape 3 : Créer les interactions
    print("\n🔄 Étape 3 : Génération des interactions...")
    interactions = create_interactions(apprenants, courses)
    
    # Étape 4 : Sauvegarder en JSON
    print("\n💾 Étape 4 : Sauvegarde des fichiers JSON...")
    
    # Sauvegarde courses.json
    with open("data/courses.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)
    print(f"   → data/courses.json ({len(courses)} cours)")
    
    # Sauvegarde apprenants.json
    with open("data/apprenants.json", "w", encoding="utf-8") as f:
        json.dump(apprenants, f, ensure_ascii=False, indent=2)
    print(f"   → data/apprenants.json ({len(apprenants)} apprenants)")
    
    # Sauvegarde interactions.json
    with open("data/interactions.json", "w", encoding="utf-8") as f:
        json.dump(interactions, f, ensure_ascii=False, indent=2)
    print(f"   → data/interactions.json ({len(interactions)} interactions)")
    
    # Résumé
    print("\n" + "=" * 60)
    print("✅ TERMINÉ ! Fichiers générés dans le dossier data/")
    print("=" * 60)
    
    # Afficher quelques statistiques
    categories = {}
    for c in courses:
        cat = c["categorie"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Répartition des cours par catégorie :")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat:25s} : {count} cours")


# Point d'entrée du script
if __name__ == "__main__":
    main()