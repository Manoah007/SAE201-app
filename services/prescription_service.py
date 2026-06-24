class PrescriptionService:
    """Service gérant la logique métier des pages prescriptions."""

    def __init__(self, ameli_api):
        self.api = ameli_api

    # ==========================================================
    # DISPARITÉS GÉOGRAPHIQUES
    # ==========================================================

    def get_prescription_toutes_zones(self, toutes_regions=True, tous_depart=False, annee="2024", limite_ligne=100):
        """Retourne les prescriptions par région ou par département."""

        if toutes_regions and tous_depart:
            return self.api._requete(
                "prescriptions",
                {
                    "select": (
                        "departement, libelle_departement, "
                        "sum(montant_total_prescription_integer) as cout_total, "
                        "avg(montant_moyen_prescription_integer) as cout_moyen"
                    ),
                    "where": f"year(annee)={annee} AND departement is not null",
                    "group_by": "departement, libelle_departement",
                    "order_by": "cout_total DESC",
                    "limit": limite_ligne
                }
            )

        if toutes_regions:
            return self.api._requete(
                "prescriptions",
                {
                    "select": (
                        "region, libelle_region, "
                        "sum(montant_total_prescription_integer) as cout_total, "
                        "avg(montant_moyen_prescription_integer) as cout_moyen"
                    ),
                    "where": f"year(annee)={annee} AND region is not null",
                    "group_by": "region, libelle_region",
                    "order_by": "cout_total DESC",
                    "limit": limite_ligne
                }
            )

        return []

    def get_region_prescription(self, region_list_id=None, annee="2024", limite_ligne=100):
        """Filtre les prescriptions selon une ou plusieurs régions."""

        where_clauses = [
            f"year(annee)={annee}",
            "region is not null"
        ]

        if region_list_id:
            ids_reg = ",".join([f"'{r_id}'" for r_id in region_list_id])
            where_clauses.append(f"region IN ({ids_reg})")

        where = " AND ".join(where_clauses)

        return self.api._requete(
            "prescriptions",
            {
                "select": (
                    "region, libelle_region, "
                    "sum(montant_total_prescription_integer) as cout_total, "
                    "avg(montant_moyen_prescription_integer) as cout_moyen"
                ),
                "where": where,
                "group_by": "region, libelle_region",
                "order_by": "cout_total DESC",
                "limit": limite_ligne
            }
        )

    def get_departement_prescriptions(self, region_list_id=None, departement_list_id=None, annee="2024", limite_ligne=100):
        """Filtre les prescriptions selon une ou plusieurs régions/départements."""

        where_clauses = [
            f"year(annee)={annee}",
            "departement is not null"
        ]

        if departement_list_id:
            ids_dep = ",".join([f"'{d_id}'" for d_id in departement_list_id])
            where_clauses.append(f"departement IN ({ids_dep})")

        elif region_list_id:
            ids_reg = ",".join([f"'{r_id}'" for r_id in region_list_id])
            where_clauses.append(f"region IN ({ids_reg})")

        where = " AND ".join(where_clauses)

        return self.api._requete(
            "prescriptions",
            {
                "select": (
                    "departement, libelle_departement, "
                    "sum(montant_total_prescription_integer) as cout_total, "
                    "avg(montant_moyen_prescription_integer) as cout_moyen"
                ),
                "where": where,
                "group_by": "departement, libelle_departement",
                "order_by": "cout_total DESC",
                "limit": limite_ligne
            }
        )

    # ==========================================================
    # CORRÉLATION DÉMOGRAPHIE / PRESCRIPTIONS
    # ==========================================================

    def get_donnees_pyramide_ages(self, profession, departement_code=None, annee="2024", limit_ligne=5000):
        where_clauses = [
            f"year(annee)={annee}",
            f'profession_sante="{profession}"',
            'libelle_sexe!="tout sexe"',
            'libelle_classe_age!="Tout âge"'
        ]

        if departement_code:
            where_clauses.append(f'departement="{departement_code}"')
        else:
            where_clauses.append("departement is not null")

        where = " AND ".join(where_clauses)

        donnees_brutes = self.api._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "libelle_sexe, libelle_classe_age, sum(effectif) as total",
                "where": where,
                "group_by": "libelle_sexe, libelle_classe_age",
                "limit": 100
            },
            limite_max=limit_ligne
        )

        pyramide = {}

        for ligne in donnees_brutes:
            age = ligne.get("libelle_classe_age") or "Inconnu"
            sexe = (ligne.get("libelle_sexe") or "").lower()
            total = ligne.get("total") or 0

            if age not in pyramide:
                pyramide[age] = {
                    "age": age,
                    "hommes": 0,
                    "femmes": 0,
                    "total_tranche": 0
                }

            if "homme" in sexe:
                pyramide[age]["hommes"] += total
            elif "femme" in sexe:
                pyramide[age]["femmes"] += total

            pyramide[age]["total_tranche"] += total

        resultats = list(pyramide.values())
        resultats.sort(key=lambda x: x["age"])

        return resultats

    def get_graphique_top_deserts_medicaux(self, profession, annee="2024", limite=15):
        where = " AND ".join([
            f"year(annee)={annee}",
            f'profession_sante="{profession}"',
            'libelle_sexe="tout sexe"',
            'libelle_classe_age!="Tout âge"',
            "departement is not null"
        ])

        donnees_brutes = self.api._requete_paginee(
            "demographie-effectifs-et-les-densites",
            {
                "select": "departement, libelle_departement, libelle_classe_age, sum(effectif) as effectif",
                "where": where,
                "group_by": "departement, libelle_departement, libelle_classe_age",
                "limit": 100
            },
            limite_max=5000
        )

        mots_seniors = ["de 60 à 64", "de 65 à 69", "70 ans et plus"]
        stats = {}

        for ligne in donnees_brutes:
            code = ligne.get("departement")
            nom = ligne.get("libelle_departement") or code
            age = ligne.get("libelle_classe_age") or ""
            effectif = ligne.get("effectif") or 0

            if not code:
                continue

            if code not in stats:
                stats[code] = {
                    "code_dept": code,
                    "nom_dept": nom,
                    "total": 0,
                    "seniors": 0
                }

            stats[code]["total"] += effectif

            if any(mot in age for mot in mots_seniors):
                stats[code]["seniors"] += effectif

        resultats = []

        for code, ligne in stats.items():
            total = ligne["total"]
            seniors = ligne["seniors"]
            pourcentage = round((seniors / total) * 100, 2) if total else 0

            resultats.append({
                "departement_code": code,
                "code_dept": code,
                "nom_dept": ligne["nom_dept"],
                "total_praticiens": total,
                "total": total,
                "praticiens_seniors": seniors,
                "seniors": seniors,
                "pourcentage_seniors": pourcentage
            })

        resultats.sort(key=lambda x: x["pourcentage_seniors"], reverse=True)

        if limite:
            return resultats[:limite]

        return resultats

    def get_tableau_top_deserts_medicaux(self, profession, annee="2024"):
        resultats = self.get_graphique_top_deserts_medicaux(
            profession=profession,
            annee=annee,
            limite=None
        )

        resultats.sort(key=lambda x: x["code_dept"])
        return resultats

    def get_correlation_age_depense(self, profession, annee="2024"):
        donnees_demo = self.get_graphique_top_deserts_medicaux(
            profession=profession,
            annee=annee,
            limite=None
        )

        if not donnees_demo:
            return []

        donnees_finance = self.get_prescription_toutes_zones(
            toutes_regions=True,
            tous_depart=True,
            annee=annee,
            limite_ligne=5000
        )

        finance_par_dept = {}

        for ligne in donnees_finance:
            code = ligne.get("departement")
            if not code:
                continue

            finance_par_dept[code] = {
                "cout_total": ligne.get("cout_total") or 0,
                "cout_moyen": ligne.get("cout_moyen") or 0
            }

        resultats = []

        for ligne in donnees_demo:
            code = ligne.get("departement_code")
            finance = finance_par_dept.get(code, {})

            resultats.append({
                "departement_code": code,
                "nom_dept": ligne.get("nom_dept"),
                "total_medecins": ligne.get("total_praticiens", 0),
                "praticiens_seniors": ligne.get("praticiens_seniors", 0),
                "pourcentage_seniors": ligne.get("pourcentage_seniors", 0),
                "cout_total": finance.get("cout_total", 0),
                "cout_moyen": round(finance.get("cout_moyen", 0), 2)
            })

        return resultats