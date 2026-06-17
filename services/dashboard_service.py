"""Construit les données affichées dans le dashboard de la page d'accueil.

Combine deux sources :
- l'API data.ameli.fr (via AmeliAPI) pour les chiffres (effectifs) ;
- la base locale (Departement, Region) pour traduire les codes département
  en libellés de région, et surtout pour savoir quels codes "departement"
  renvoyés par l'API correspondent à de vrais départements.

Pourquoi ce dernier point est important : les requêtes API groupées par
sexe/âge/profession (sans grouper aussi par département) remontent en plus
des lignes de niveau régional et national qui ont, elles aussi, une valeur
dans le champ "departement" (le simple filtre "departement is not null" ne
suffit donc pas à les exclure). En groupant systématiquement par département
ET en ne sommant que les codes présents dans notre table locale, on est sûr
de ne compter chaque professionnel qu'une seule fois.
"""

import time

from models.db import Session
from models.dimensions import Departement
from services.ameli_api import AmeliAPI

ameli = AmeliAPI()

# Profession et année utilisées comme référence pour la vue d'ensemble de
# la page d'accueil. "Ensemble des médecins" est une catégorie agrégée déjà
# présente dans le jeu de données (cf. table profession_sante).
PROFESSION_REFERENCE = "Ensemble des médecins"
ANNEE_REFERENCE = 2024

# Ordre chronologique des tranches d'âge, pour ne pas les trier par ordre
# alphabétique (qui n'a pas de sens ici).
ORDRE_TRANCHES_AGE = [
    "moins de 25 ans",
    "de 25 à 29 ans",
    "de 30 à 34 ans",
    "de 35 à 39 ans",
    "de 40 à 44 ans",
    "de 45 à 49 ans",
    "de 50 à 54 ans",
    "de 55 à 59 ans",
    "de 60 à 64 ans",
    "de 65 à 69 ans",
    "70 ans et plus",
    "âge inconnu",
]

# Le dashboard demande une cinquantaine d'appels à l'API publique d'Ameli
# (pagination comprise). On garde le résultat en mémoire un certain temps
# pour ne pas refaire tout ce travail à chaque chargement de la page
# d'accueil : les effectifs ne changent qu'une fois par an de toute façon.
DUREE_CACHE_SECONDES = 3600
_cache = {"contexte": None, "horodatage": 0}


def get_dashboard_context(forcer_actualisation=False):
    """Renvoie un dict prêt à être passé à render_template("accueil.html", **contexte).

    Le résultat est mis en cache en mémoire pendant DUREE_CACHE_SECONDES.
    Passe forcer_actualisation=True pour ignorer le cache (utile en debug).
    """

    maintenant = time.time()
    cache_valide = (
        _cache["contexte"] is not None
        and (maintenant - _cache["horodatage"]) < DUREE_CACHE_SECONDES
    )

    if cache_valide and not forcer_actualisation:
        return _cache["contexte"]

    contexte = _construire_dashboard_context()
    _cache["contexte"] = contexte
    _cache["horodatage"] = maintenant
    return contexte


def _construire_dashboard_context():
    session = Session()
    try:
        carte_dept_region = {d.code: d.region.libelle for d in session.query(Departement).all()}
    finally:
        session.close()

    codes_valides = set(carte_dept_region.keys())

    region_labels, region_values = _repartition_par_region(carte_dept_region)
    sexe_labels, sexe_values = _repartition_sexe(codes_valides)
    age_labels, age_values = _repartition_age(codes_valides)
    top_professions = _top_professions(codes_valides)

    return {
        "region_labels": region_labels,
        "region_values": region_values,
        "sexe_labels": sexe_labels,
        "sexe_values": sexe_values,
        "age_labels": age_labels,
        "age_values": age_values,
        "top_professions": top_professions,
    }


def _repartition_par_region(carte_dept_region):
    """Additionne les effectifs par département pour obtenir un total par région."""

    lignes = ameli.get_repartition_departements(PROFESSION_REFERENCE, ANNEE_REFERENCE)

    totaux_par_region = {}
    for ligne in lignes:
        nom_region = carte_dept_region.get(ligne.get("departement"))
        if nom_region is None:
            # Code renvoyé par l'API mais absent de notre table de référence
            continue

        effectif = ligne.get("effectif") or 0
        totaux_par_region[nom_region] = totaux_par_region.get(nom_region, 0) + effectif

    classement = sorted(totaux_par_region.items(), key=lambda item: item[1], reverse=True)

    labels = [nom for nom, _ in classement]
    valeurs = [valeur for _, valeur in classement]
    return labels, valeurs


def _repartition_sexe(codes_valides):
    lignes = ameli.get_repartition_sexe(PROFESSION_REFERENCE, ANNEE_REFERENCE)

    totaux = {}
    for ligne in lignes:
        if ligne.get("departement") not in codes_valides:
            continue

        sexe = ligne.get("libelle_sexe")
        effectif = ligne.get("effectif") or 0
        totaux[sexe] = totaux.get(sexe, 0) + effectif

    labels = [sexe.capitalize() for sexe in totaux.keys()]
    valeurs = list(totaux.values())
    return labels, valeurs


def _repartition_age(codes_valides):
    lignes = ameli.get_repartition_age(PROFESSION_REFERENCE, ANNEE_REFERENCE)

    totaux = {}
    for ligne in lignes:
        if ligne.get("departement") not in codes_valides:
            continue

        tranche = ligne.get("libelle_classe_age")
        effectif = ligne.get("effectif") or 0
        totaux[tranche] = totaux.get(tranche, 0) + effectif

    def position(tranche):
        return ORDRE_TRANCHES_AGE.index(tranche) if tranche in ORDRE_TRANCHES_AGE else len(ORDRE_TRANCHES_AGE)

    tranches_triees = sorted(totaux.keys(), key=position)

    labels = tranches_triees
    valeurs = [totaux[tranche] for tranche in tranches_triees]
    return labels, valeurs


def _top_professions(codes_valides, limite=5):
    lignes = ameli.get_repartition_professions(ANNEE_REFERENCE)

    totaux = {}
    for ligne in lignes:
        if ligne.get("departement") not in codes_valides:
            continue

        profession = ligne.get("profession_sante")
        if profession is None or profession.startswith("Ensemble"):
            # On exclut les catégories agrégées pour ne classer que des
            # professions individuelles.
            continue

        effectif = ligne.get("effectif") or 0
        totaux[profession] = totaux.get(profession, 0) + effectif

    classement = sorted(totaux.items(), key=lambda item: item[1], reverse=True)[:limite]

    return [{"libelle": nom, "valeur": valeur} for nom, valeur in classement]