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