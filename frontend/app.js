/**
 * =============================================================================
 *  APP.JS — EduPath Africa — Interface Premium
 * =============================================================================
 */


/* ─────────────────────────────────────────────────────────────────────────────
   CONFIGURATION
   ───────────────────────────────────────────────────────────────────────────── */

// URL de ta Lambda Function URL sur AWS
var API_BASE = '';


/* ─────────────────────────────────────────────────────────────────────────────
   1. CHARGEMENT DES APPRENANTS
   ───────────────────────────────────────────────────────────────────────────── */

async function loadApprenants() {
    try {
        var url = API_BASE + '/api/apprenants';
        console.log('📡 Appel API apprenants:', url);

        var response = await fetch(url);

        if (!response.ok) {
            throw new Error('Erreur serveur: ' + response.status);
        }

        var apprenants = await response.json();

        var select = document.getElementById('apprenant-select');

        for (var i = 0; i < apprenants.length; i++) {
            var a = apprenants[i];

            var option = document.createElement('option');
            option.value = a.apprenant_id;

            var drapeau = getFlag(a.pays);
            option.textContent = drapeau + ' ' + a.nom + ' — ' + a.specialisation + ' (' + a.niveau + ')';

            option.setAttribute('data-nom', a.nom);
            option.setAttribute('data-pays', a.pays);
            option.setAttribute('data-niveau', a.niveau);
            option.setAttribute('data-spec', a.specialisation);
            option.setAttribute('data-date', a.date_inscription);
            option.setAttribute('data-tags', JSON.stringify(a.tags_interet));

            select.appendChild(option);
        }

        console.log('✅ ' + apprenants.length + ' apprenants chargés avec succès');

    } catch (erreur) {
        console.error(' Erreur chargement apprenants:', erreur);
    }
}


function getFlag(pays) {
    var drapeaux = {
        'Sénégal': '🇸🇳',
        'Ghana': '🇬🇭',
        'Nigeria': '🇳🇬',
        'Kenya': '🇰🇪',
        'Mali': '🇲🇱',
        "Côte d'Ivoire": '🇨🇮',
        'Rwanda': '🇷🇼',
        'Guinée': '🇬🇳',
        'Gambie': '🇬🇲',
        'Éthiopie': '🇪🇹',
        'Maroc': '🇲🇦'
    };

    if (drapeaux[pays]) {
        return drapeaux[pays];
    }
    return '🌍';
}


/* ─────────────────────────────────────────────────────────────────────────────
   2. CHARGEMENT DES STATISTIQUES
   ───────────────────────────────────────────────────────────────────────────── */

async function loadStats() {
    try {
        var url = API_BASE + '/api/stats';
        console.log('📡 Appel API stats:', url);

        var response = await fetch(url);

        if (!response.ok) {
            console.warn('Stats non disponibles');
            return;
        }

        var stats = await response.json();

        animateCounter('stat-cours', stats.total_cours);
        animateCounter('stat-apprenants', stats.total_apprenants);
        animateCounter('stat-interactions', stats.total_interactions);

        var categories = stats.cours_par_categorie || {};
        var nbCategories = Object.keys(categories).length;
        animateCounter('stat-categories', nbCategories);

        console.log('✅ Stats chargées');

    } catch (erreur) {
        console.error('Erreur chargement stats:', erreur);
    }
}


function animateCounter(elementId, cible) {
    var element = document.getElementById(elementId);

    if (!element || !cible) {
        if (element) {
            element.textContent = cible || '0';
        }
        return;
    }

    var duree = 900;
    var debut = performance.now();

    function mettreAJour(maintenant) {
        var elapsed = maintenant - debut;
        var progression = Math.min(elapsed / duree, 1);

        var eased = 1 - Math.pow(1 - progression, 3);

        var valeurActuelle = Math.round(cible * eased);

        element.textContent = valeurActuelle;

        if (progression < 1) {
            requestAnimationFrame(mettreAJour);
        }
    }

    requestAnimationFrame(mettreAJour);
}


/* ─────────────────────────────────────────────────────────────────────────────
   3. OBTENIR LES RECOMMANDATIONS
   ───────────────────────────────────────────────────────────────────────────── */

async function getRecommendations() {
    var select = document.getElementById('apprenant-select');
    var apprenantId = select.value;

    if (!apprenantId) {
        alert('Veuillez sélectionner un apprenant dans la liste.');
        return;
    }

    afficher('loading');
    cacher('results-section');
    cacher('profile-section');

    await attendre(450);

    try {
        var url = API_BASE + '/api/recommend?apprenant_id=' + apprenantId;
        console.log('📡 Appel API recommandations:', url);

        var response = await fetch(url);

        if (!response.ok) {
            throw new Error('Erreur API: ' + response.status);
        }

        var data = await response.json();

        cacher('loading');

        var optionSelectionnee = select.options[select.selectedIndex];

        var profilComplet = {
            id: data.apprenant.id,
            nom: data.apprenant.nom,
            niveau: data.apprenant.niveau,
            specialisation: data.apprenant.specialisation,
            pays: data.apprenant.pays,
            date_inscription: optionSelectionnee.getAttribute('data-date') || '—',
            tags_interet: JSON.parse(optionSelectionnee.getAttribute('data-tags') || '[]')
        };

        afficherProfil(profilComplet);

        afficherRecommandations(data.recommandations);

        var prenom = data.apprenant.nom.split(' ')[0];
        var eyebrow = document.querySelector('.hero-eyebrow');
        if (eyebrow) {
            eyebrow.innerHTML = '<span class="eyebrow-dot"></span> Recommandations pour ' + prenom;
        }

        var initiales = data.apprenant.nom.split(' ').map(function(n) {
            return n[0];
        }).join('').slice(0, 2).toUpperCase();

        var navAvatar = document.querySelector('#nav-avatar span');
        if (navAvatar) {
            navAvatar.textContent = initiales;
        }

        console.log('✅ Recommandations affichées pour ' + data.apprenant.nom);

    } catch (erreur) {
        cacher('loading');
        console.error('❌ Erreur recommandations:', erreur);
        alert('Erreur lors du calcul des recommandations. Vérifiez que le serveur est actif.');
    }
}


/* ─────────────────────────────────────────────────────────────────────────────
   4. AFFICHAGE DU PROFIL APPRENANT
   ───────────────────────────────────────────────────────────────────────────── */

function afficherProfil(apprenant) {
    var parties = apprenant.nom.split(' ');
    var initiales = '';
    for (var i = 0; i < parties.length && i < 2; i++) {
        initiales += parties[i][0];
    }
    initiales = initiales.toUpperCase();

    document.getElementById('profile-initials').textContent = initiales;
    document.getElementById('profile-name').textContent = apprenant.nom;
    document.getElementById('profile-country').textContent = apprenant.pays;
    document.getElementById('profile-spec').textContent = apprenant.specialisation;
    document.getElementById('profile-date').textContent = apprenant.date_inscription;

    var badge = document.getElementById('profile-level');
    badge.textContent = apprenant.niveau;

    badge.className = 'profile-badge';

    if (apprenant.niveau === 'Beginner') {
        badge.className = 'profile-badge badge-beg';
    } else if (apprenant.niveau === 'Intermediate') {
        badge.className = 'profile-badge badge-int';
    } else if (apprenant.niveau === 'Advanced') {
        badge.className = 'profile-badge badge-adv';
    }

    var conteneurTags = document.getElementById('profile-tags');
    conteneurTags.innerHTML = '';

    var tags = apprenant.tags_interet || [];
    for (var j = 0; j < tags.length; j++) {
        var span = document.createElement('span');
        span.className = 'interest-tag';
        span.textContent = tags[j];
        conteneurTags.appendChild(span);
    }

    afficher('profile-section');
}


/* ─────────────────────────────────────────────────────────────────────────────
   5. AFFICHAGE DES RECOMMANDATIONS
   ───────────────────────────────────────────────────────────────────────────── */

function afficherRecommandations(recommandations) {
    var conteneur = document.getElementById('recommendations-list');

    conteneur.innerHTML = '';

    for (var i = 0; i < recommandations.length; i++) {
        var reco = recommandations[i];

        var pourcentage = (reco.score_pertinence * 100).toFixed(1);

        var iconeSvg = getIconeCategorie(reco.categorie);
        var couleurCat = getCouleurCategorie(reco.categorie);

        var tagsHtml = '';
        for (var t = 0; t < reco.tags.length; t++) {
            tagsHtml += '<span class="tag">' + echapper(reco.tags[t]) + '</span>';
        }

        var carte = document.createElement('div');
        carte.className = 'reco-card';

        carte.innerHTML =
            '<div class="reco-body">' +
                '<div class="reco-row-1">' +
                    '<div class="reco-rank">' + (i + 1) + '</div>' +
                    '<div class="reco-title-area">' +
                        '<div class="reco-title">' + echapper(reco.titre) + '</div>' +
                        '<div class="reco-org">' + echapper(reco.organisation) + '</div>' +
                    '</div>' +
                    '<div class="reco-score">' +
                        '<span class="score-val">' + pourcentage + '%</span>' +
                        '<span class="score-lbl">pertinence</span>' +
                    '</div>' +
                '</div>' +
                '<div class="reco-metas">' +
                    '<span class="rmeta">' +
                        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="' + couleurCat + '" stroke-width="2">' + iconeSvg + '</svg>' +
                        ' ' + echapper(reco.categorie) +
                    '</span>' +
                    '<span class="rmeta">' +
                        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#A0AEC0" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>' +
                        ' ' + reco.niveau +
                    '</span>' +
                    '<span class="rmeta">' +
                        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>' +
                        ' ' + reco.rating + '/5' +
                    '</span>' +
                    '<span class="rmeta">' +
                        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#A0AEC0" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' +
                        ' ' + reco.duree_heures + 'h' +
                    '</span>' +
                '</div>' +
                '<div class="reco-tags">' + tagsHtml + '</div>' +
                '<div class="prog-wrap">' +
                    '<div class="prog-bg">' +
                        '<div class="prog-fill" data-w="' + pourcentage + '"></div>' +
                    '</div>' +
                '</div>' +
                '<div class="reco-explain">' +
                    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6EE7B7" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>' +
                    '<span>' + echapper(reco.explication) + '</span>' +
                '</div>' +
            '</div>';

        conteneur.appendChild(carte);
    }

    afficher('results-section');

    setTimeout(function() {
        var barres = document.querySelectorAll('.prog-fill');
        for (var b = 0; b < barres.length; b++) {
            (function(barre, index) {
                setTimeout(function() {
                    barre.style.width = barre.getAttribute('data-w') + '%';
                }, index * 100);
            })(barres[b], b);
        }
    }, 150);

    var resultatsSection = document.getElementById('results-section');
    if (resultatsSection) {
        resultatsSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}


/* ─────────────────────────────────────────────────────────────────────────────
   6. FONCTIONS UTILITAIRES
   ───────────────────────────────────────────────────────────────────────────── */

function afficher(id) {
    var element = document.getElementById(id);
    if (element) {
        element.style.display = 'block';
    }
}

function cacher(id) {
    var element = document.getElementById(id);
    if (element) {
        element.style.display = 'none';
    }
}

function attendre(ms) {
    return new Promise(function(resolve) {
        setTimeout(resolve, ms);
    });
}

function echapper(texte) {
    if (!texte) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(texte));
    return div.innerHTML;
}


function getCouleurCategorie(categorie) {
    var couleurs = {
        'Cloud AWS': '#F59E0B',
        'Cloud Computing': '#F59E0B',
        'Python': '#3B82F6',
        'Data Science': '#0EA5E9',
        'Machine Learning': '#8B5CF6',
        'AI': '#7C3AED',
        'Cybersecurity': '#EF4444',
        'Web Development': '#10B981',
        'DevOps': '#06B6D4',
        'Mobile Development': '#EC4899',
        'Big Data': '#F97316',
        'Database': '#14B8A6',
        'Blockchain': '#6366F1',
        'Statistics': '#0EA5E9',
        'IT Support': '#64748B',
        'Mathematics': '#A855F7',
        'Project Management': '#84CC16'
    };

    return couleurs[categorie] || '#A0AEC0';
}


function getIconeCategorie(categorie) {
    var icones = {
        'Cloud AWS':
            '<path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>',
        'Cloud Computing':
            '<path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>',
        'Python':
            '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
        'Data Science':
            '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        'Machine Learning':
            '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/>',
        'AI':
            '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>',
        'Cybersecurity':
            '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
        'Web Development':
            '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
        'DevOps':
            '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33"/>',
        'Mobile Development':
            '<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
        'Big Data':
            '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
        'Database':
            '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
        'Blockchain':
            '<rect x="1" y="1" width="9" height="9"/><rect x="14" y="1" width="9" height="9"/><rect x="1" y="14" width="9" height="9"/><rect x="14" y="14" width="9" height="9"/>',
        'Statistics':
            '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        'IT Support':
            '<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
        'Mathematics':
            '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
        'Project Management':
            '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/>'
    };

    return icones[categorie] || '<circle cx="12" cy="12" r="10"/>';
}


/* ─────────────────────────────────────────────────────────────────────────────
   7. EFFET NAVBAR AU SCROLL
   ───────────────────────────────────────────────────────────────────────────── */

function gererScrollNavbar() {
    var navbar = document.getElementById('navbar');
    if (!navbar) return;

    if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
}


/* ─────────────────────────────────────────────────────────────────────────────
   8. INITIALISATION
   ───────────────────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🌍 EduPath Africa — Interface Premium chargée');
    console.log('📍 API_BASE = "' + API_BASE + '"');

    loadApprenants();

    loadStats();

    window.addEventListener('scroll', gererScrollNavbar, { passive: true });
});