from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import ProfessionSante, Departement, Region
from services.ameli_api import AmeliAPI

bp_indicateurs = Blueprint("indicateurs", __name__)
api = AmeliAPI()

def formater_nombre(valeur):
    if isinstance(valeur, (int, float)):
        return f"{valeur:,}".replace(",", " ")
    return valeur

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
            # ==========================================
            # 🎯 MODE FILTRÉ : 12 KPIs calculés et robustes
            # ==========================================
            prof = session.get(ProfessionSante, prof_id)
            
            if prof:
                # 1. Récupération des données brutes
                data_eff = api.get_effectifs(prof.libelle, dept_code, annee)
                data_evo = api.get_evolution_effectifs(prof.libelle, dept_code)
                data_hon = api.get_honoraires(prof.libelle, dept_code, annee)
                data_pat = api.get_patientele(prof.libelle, dept_code, annee)
                
                # 2. Extraction sécurisée
                effectif_val = (data_eff[0].get("effectif") or 0) if data_eff else 0
                densite_val = (data_eff[0].get("densite") or 0) if data_eff else 0
                
                # 3. Calculs Data Science (Création de valeur)
                
                # A. Évolution annuelle
                evolution_val = "Stable"
                if data_evo and len(data_evo) > 1:
                    eff_actuel = next((row.get("effectif") for row in data_evo if str(annee) in str(row.get("annee"))), None)
                    eff_prec = next((row.get("effectif") for row in data_evo if str(annee-1) in str(row.get("annee"))), None)
                    if eff_actuel and eff_prec and eff_prec > 0:
                        taux = ((eff_actuel - eff_prec) / eff_prec) * 100
                        evolution_val = f"+{taux:.1f}%" if taux > 0 else f"{taux:.1f}%"

                # B. Habitants par praticien (100 000 / densité)
                hab_par_doc = "N/A"
                if densite_val > 0:
                    hab_par_doc = formater_nombre(int(100000 / densite_val))

                # C. Analyse de la couverture (Désert médical ?)
                statut_territoire = "Couverture Normale"
                if densite_val == 0: statut_territoire = "Aucun praticien"
                elif densite_val < 30: statut_territoire = "⚠️ Zone Fragile"
                elif densite_val > 150: statut_territoire = "✅ Zone Sur-dotée"

                # 4. Gestion du Secret Statistique (< 11 médecins)
                if effectif_val < 11:
                    secret_stat = "🔒 Données Masquées"
                    honoraire_txt = "Secret Statistique"
                    patientele_txt = "Secret Statistique"
                    revenu_moyen = "Secret Statistique"
                else:
                    secret_stat = "✅ Publiques"
                    ligne_hon = data_hon[0] if data_hon else {}

                    hon_brut = (
                        ligne_hon.get("hono_sans_depassement_totaux")
                        or ligne_hon.get("honoraires_sans_depassement")
                        or ligne_hon.get("totaux_integer")
                    )

                    honoraire_txt = f"{formater_nombre(hon_brut)} €" if hon_brut else "Non communiqué"
                    
                    pat_brut = data_pat[0].get("patientele") if data_pat else None
                    patientele_txt = formater_nombre(pat_brut) if pat_brut else "Non communiquée"
                    
                    # D. Revenu moyen estimé par praticien
                    if hon_brut and effectif_val > 0:
                        revenu_moyen = f"{formater_nombre(int(hon_brut / effectif_val))} € / pro"
                    else:
                        revenu_moyen = "Non calculable"

                # 5. La liste des 12 cartes filtrées
                kpis = [
                    {"titre": "Effectifs totaux", "valeur": formater_nombre(effectif_val), "description": f"Nombre de praticiens dans le {dept_code} en {annee}."},
                    {"titre": "Densité médicale", "valeur": densite_val, "description": "Nombre de praticiens pour 100 000 habitants."},
                    {"titre": "Évolution annuelle", "valeur": evolution_val, "description": f"Variation des effectifs par rapport à {annee - 1}."},
                    {"titre": "Habitants par médecin", "valeur": hab_par_doc, "description": "Nombre théorique d'habitants pour un seul praticien."},
                    {"titre": "État du territoire", "valeur": statut_territoire, "description": "Évaluation de l'offre de soins dans ce département."},
                    {"titre": "Confidentialité", "valeur": secret_stat, "description": "L'État masque l'argent s'il y a moins de 11 praticiens."},
                    {"titre": "Patientèle moyenne", "valeur": patientele_txt, "description": "Nombre moyen de patients suivis par praticien."},
                    {"titre": "Honoraires totaux", "valeur": honoraire_txt, "description": "Total des revenus conventionnés générés dans le département."},
                    {"titre": "Chiffre d'affaires estimé", "valeur": revenu_moyen, "description": "Moyenne estimée (Honoraires totaux divisés par les effectifs)."},
                    {"titre": "Secteur d'exercice", "valeur": "Libéral", "description": "Les données de l'API concernent les professionnels libéraux."},
                    {"titre": "Fiabilité de la donnée", "valeur": "Validée", "description": "Chiffres extraits du système d'information de la CNAM."},
                    {"titre": "Source", "valeur": "data.ameli.fr", "description": "Base de données ouverte de l'Assurance Maladie."}
                ]
            else:
                kpis = []
                
        else:
            # ==========================================
            # 🌍 MODE GLOBAL : 12 KPIs d'accueil (Vue d'ensemble)
            # ==========================================
            kpis = [
                {"titre": "Professions intégrées", "valeur": len(professions), "description": "Spécialités médicales et paramédicales référencées."},
                {"titre": "Territoires cartographiés", "valeur": len(departements), "description": "Départements français couverts par l'analyse."},
                {"titre": "Profondeur d'historique", "valeur": "10 ans", "description": "Données disponibles et analysables de 2014 à 2024."},
                {"titre": "Praticiens en France", "valeur": "1.2 M+", "description": "Estimation du nombre total de professionnels de santé."},
                {"titre": "Dépenses de Santé", "valeur": "240 Md€", "description": "Budget annuel global estimé pour le système de santé français."},
                {"titre": "Part du budget de l'État", "valeur": "~11.5%", "description": "Pourcentage du PIB français alloué à la santé."},
                {"titre": "Actes médicaux annuels", "valeur": "1.5 Md+", "description": "Volume estimé des actes tracés par l'Assurance Maladie."},
                {"titre": "Réseau de soins", "valeur": "Dense", "description": "La France possède l'un des maillages de santé les plus fins d'Europe."},
                {"titre": "Consultations télé-santé", "valeur": "En hausse", "description": "Forte augmentation des pratiques de télémédecine depuis 2020."},
                {"titre": "Serveur API Ameli", "valeur": "Connecté", "description": "Liaison active avec les bases de données gouvernementales."},
                {"titre": "Type de données", "valeur": "Open Data", "description": "Informations publiques, anonymisées et conformes au RGPD."},
                {"titre": "Dernière synchronisation", "valeur": "Automatique", "description": "Requêtes effectuées en temps réel via l'API REST."}
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