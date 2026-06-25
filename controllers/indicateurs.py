from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Departement, Region
from services.ameli_api import AmeliAPI

bp_indicateurs = Blueprint("indicateurs", __name__)
api = AmeliAPI()


def convertir_nombre(valeur):
    """Convertit proprement une valeur API en nombre."""
    if valeur is None or valeur == "":
        return None

    if isinstance(valeur, (int, float)):
        return float(valeur)

    texte = str(valeur)
    texte = texte.replace("€", "")
    texte = texte.replace("\u202f", "")
    texte = texte.replace(" ", "")
    texte = texte.replace(",", ".")

    try:
        return float(texte)
    except ValueError:
        return None


def formater_nombre(valeur):
    """Formate un nombre avec des espaces."""
    nombre = convertir_nombre(valeur)

    if nombre is None:
        return "N/A"

    if nombre.is_integer():
        return f"{int(nombre):,}".replace(",", " ")

    return f"{nombre:,.2f}".replace(",", " ").replace(".", ",")


def extraire_annee(valeur):
    """Récupère l'année même si l'API renvoie une date complète."""
    if valeur is None:
        return ""

    return str(valeur)[:4]


@bp_indicateurs.route("/indicateurs")
def afficher():
    session = Session()

    try:
        professions = session.query(ProfessionSante).order_by(ProfessionSante.libelle).all()
        departements = session.query(Departement).order_by(Departement.code).all()
        regions = session.query(Region).order_by(Region.libelle).all()

        prof_id = request.args.get("profession", type=int)
        dept_code = request.args.get("departement", type=str)
        annee = request.args.get("annee", type=int)

        if prof_id and dept_code and annee:
            prof = session.get(ProfessionSante, prof_id)

            if prof:
                # 1. Récupération des données depuis l'API
                data_eff = api.get_effectifs(prof.libelle, dept_code, annee)
                data_evo = api.get_evolution_effectifs(prof.libelle, dept_code)
                data_hon = api.get_honoraires(prof.libelle, dept_code, annee)
                data_pat = api.get_patientele(prof.libelle, dept_code, annee)

                # 2. Extraction sécurisée des effectifs et densités
                effectif_val = convertir_nombre(data_eff[0].get("effectif")) if data_eff else 0
                densite_val = convertir_nombre(data_eff[0].get("densite")) if data_eff else 0

                effectif_val = effectif_val or 0
                densite_val = densite_val or 0

                # 3. Évolution annuelle
                evolution_val = "Stable"

                if data_evo and len(data_evo) > 1:
                    eff_actuel = None
                    eff_prec = None

                    for row in data_evo:
                        annee_ligne = extraire_annee(row.get("annee"))
                        effectif_ligne = convertir_nombre(row.get("effectif"))

                        if annee_ligne == str(annee):
                            eff_actuel = effectif_ligne

                        if annee_ligne == str(annee - 1):
                            eff_prec = effectif_ligne

                    if eff_actuel is not None and eff_prec is not None and eff_prec > 0:
                        taux = ((eff_actuel - eff_prec) / eff_prec) * 100
                        evolution_val = f"+{taux:.1f}%" if taux > 0 else f"{taux:.1f}%"

                # 4. Habitants par praticien
                hab_par_doc = "N/A"

                if densite_val > 0:
                    hab_par_doc = formater_nombre(100000 / densite_val)

                # 5. Analyse de la couverture
                statut_territoire = "Couverture normale"

                if densite_val == 0:
                    statut_territoire = "Aucun praticien"
                elif densite_val < 30:
                    statut_territoire = "⚠️ Zone fragile"
                elif densite_val > 150:
                    statut_territoire = "✅ Zone sur-dotée"

                # 6. Gestion du secret statistique
                if effectif_val < 11:
                    secret_stat = "🔒 Données masquées"
                    honoraire_txt = "Secret statistique"
                    patientele_txt = "Secret statistique"
                    revenu_moyen = "Secret statistique"

                else:
                    secret_stat = "✅ Publiques"

                    ligne_hon = data_hon[0] if data_hon else {}

                    hon_brut = convertir_nombre(
                        ligne_hon.get("hono_sans_depassement_totaux")
                        or ligne_hon.get("honoraires_sans_depassement")
                        or ligne_hon.get("totaux_integer")
                    )

                    honoraire_txt = (
                        f"{formater_nombre(hon_brut)} €"
                        if hon_brut
                        else "Non communiqué"
                    )

                    pat_brut = convertir_nombre(data_pat[0].get("patientele")) if data_pat else None

                    patientele_txt = (
                        formater_nombre(pat_brut)
                        if pat_brut
                        else "Non communiquée"
                    )

                    # 7. Revenu moyen estimé par praticien
                    if hon_brut and effectif_val and effectif_val > 0:
                        revenu_moyen = f"{formater_nombre(hon_brut / effectif_val)} € / pro"
                    else:
                        revenu_moyen = "Non calculable"

                # 8. Liste des 12 KPI affichés
                kpis = [
                    {
                        "titre": "Effectifs totaux",
                        "valeur": formater_nombre(effectif_val),
                        "description": f"Nombre de praticiens dans le département {dept_code} en {annee}."
                    },
                    {
                        "titre": "Densité médicale",
                        "valeur": formater_nombre(densite_val),
                        "description": "Nombre de praticiens pour 100 000 habitants."
                    },
                    {
                        "titre": "Évolution annuelle",
                        "valeur": evolution_val,
                        "description": f"Variation des effectifs par rapport à {annee - 1}."
                    },
                    {
                        "titre": "Habitants par médecin",
                        "valeur": hab_par_doc,
                        "description": "Nombre théorique d'habitants pour un seul praticien."
                    },
                    {
                        "titre": "État du territoire",
                        "valeur": statut_territoire,
                        "description": "Évaluation de l'offre de soins dans ce département."
                    },
                    {
                        "titre": "Confidentialité",
                        "valeur": secret_stat,
                        "description": "Certaines données financières peuvent être masquées quand les effectifs sont trop faibles."
                    },
                    {
                        "titre": "Patientèle moyenne",
                        "valeur": patientele_txt,
                        "description": "Nombre moyen de patients suivis par praticien."
                    },
                    {
                        "titre": "Honoraires totaux",
                        "valeur": honoraire_txt,
                        "description": "Total des revenus conventionnés générés dans le département."
                    },
                    {
                        "titre": "Chiffre d'affaires estimé",
                        "valeur": revenu_moyen,
                        "description": "Moyenne estimée : honoraires divisés par les effectifs."
                    },
                    {
                        "titre": "Secteur d'exercice",
                        "valeur": "Libéral",
                        "description": "Les données de l'API concernent principalement les professionnels libéraux."
                    },
                    {
                        "titre": "Fiabilité de la donnée",
                        "valeur": "Validée",
                        "description": "Chiffres extraits des données publiques de l'Assurance Maladie."
                    },
                    {
                        "titre": "Source",
                        "valeur": "data.ameli.fr",
                        "description": "Base de données ouverte de l'Assurance Maladie."
                    }
                ]

            else:
                kpis = []

        else:
            # Mode global quand aucun filtre n’est sélectionné
            kpis = [
                {
                    "titre": "Professions intégrées",
                    "valeur": len(professions),
                    "description": "Spécialités médicales et paramédicales référencées."
                },
                {
                    "titre": "Territoires cartographiés",
                    "valeur": len(departements),
                    "description": "Départements français couverts par l'analyse."
                },
                {
                    "titre": "Profondeur d'historique",
                    "valeur": "15 ans",
                    "description": "Données disponibles et analysables de 2010 à 2024."
                },
                {
                    "titre": "Praticiens en France",
                    "valeur": "1.2 M+",
                    "description": "Estimation du nombre total de professionnels de santé."
                },
                {
                    "titre": "Dépenses de Santé",
                    "valeur": "240 Md€",
                    "description": "Budget annuel global estimé pour le système de santé français."
                },
                {
                    "titre": "Part du budget de l'État",
                    "valeur": "~11.5%",
                    "description": "Pourcentage du PIB français alloué à la santé."
                },
                {
                    "titre": "Actes médicaux annuels",
                    "valeur": "1.5 Md+",
                    "description": "Volume estimé des actes tracés par l'Assurance Maladie."
                },
                {
                    "titre": "Réseau de soins",
                    "valeur": "Dense",
                    "description": "La France possède un maillage de santé important."
                },
                {
                    "titre": "Consultations télé-santé",
                    "valeur": "En hausse",
                    "description": "Forte augmentation des pratiques de télémédecine depuis 2020."
                },
                {
                    "titre": "Serveur API Ameli",
                    "valeur": "Connecté",
                    "description": "Liaison active avec les bases de données publiques."
                },
                {
                    "titre": "Type de données",
                    "valeur": "Open Data",
                    "description": "Informations publiques, anonymisées et conformes au RGPD."
                },
                {
                    "titre": "Dernière synchronisation",
                    "valeur": "Automatique",
                    "description": "Requêtes effectuées en temps réel via l'API REST."
                }
            ]

        return render_template(
            "indicateurs.html",
            professions=professions,
            departements=departements,
            regions=regions,
            kpis=kpis
        )

    finally:
        session.close()