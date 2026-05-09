# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque financière
#  inclure "include/finance.fpp"
#
#  Calculs d'intérêts, d'emprunts, d'investissements,
#  de rentabilité, de fiscalité et de gestion de portefeuille.
# ══════════════════════════════════════════════════════════════

# ── Intérêts simples ──────────────────────────────────────────

# Intérêt simple : I = C * t * n  (t en % annuel, n en années)
fonction interet_simple(capital, taux_pct, duree_ans) faire
    retourner capital * (taux_pct / 100) * duree_ans
fin

# Capital acquis avec intérêt simple
fonction capital_acquis_simple(capital, taux_pct, duree_ans) faire
    retourner capital + interet_simple(capital, taux_pct, duree_ans)
fin

# Durée nécessaire pour atteindre un capital cible (intérêt simple)
fonction duree_interet_simple(capital, taux_pct, capital_cible) faire
    si taux_pct == 0 alors
        retourner 0
    fin
    retourner (capital_cible - capital) / (capital * taux_pct / 100)
fin

# ── Intérêts composés ─────────────────────────────────────────

# Capital avec intérêts composés : C * (1 + t)^n
fonction capital_compose(capital, taux_pct, duree_ans) faire
    retourner capital * (1 + taux_pct / 100) ** duree_ans
fin

# Intérêt total composé
fonction interet_compose(capital, taux_pct, duree_ans) faire
    retourner capital_compose(capital, taux_pct, duree_ans) - capital
fin

# Taux annuel équivalent (TAE) d'un taux mensuel
fonction taux_annuel_depuis_mensuel(taux_mensuel_pct) faire
    retourner ((1 + taux_mensuel_pct / 100) ** 12 - 1) * 100
fin

# Taux mensuel depuis taux annuel
fonction taux_mensuel_depuis_annuel(taux_annuel_pct) faire
    retourner ((1 + taux_annuel_pct / 100) ** (1 / 12) - 1) * 100
fin

# Nombre d'années pour doubler un capital (règle des 72)
fonction regle_72(taux_pct) faire
    si taux_pct == 0 alors
        retourner 0
    fin
    retourner 72 / taux_pct
fin

# ── Capitalisation avec versements périodiques ────────────────

# Valeur future d'une rente (versements en fin de période)
# VF = v * ((1+t)^n - 1) / t     (t = taux par période)
fonction rente_valeur_future(versement, taux_pct, n_periodes) faire
    decimal t = taux_pct / 100
    si t == 0 alors
        retourner versement * n_periodes
    fin
    retourner versement * ((1 + t) ** n_periodes - 1) / t
fin

# Valeur actuelle d'une rente
# VA = v * (1 - (1+t)^(-n)) / t
fonction rente_valeur_actuelle(versement, taux_pct, n_periodes) faire
    decimal t = taux_pct / 100
    si t == 0 alors
        retourner versement * n_periodes
    fin
    retourner versement * (1 - (1 + t) ** (-n_periodes)) / t
fin

# Versement nécessaire pour atteindre un capital cible
fonction versement_pour_capital(capital_cible, taux_pct, n_periodes) faire
    decimal t = taux_pct / 100
    si t == 0 alors
        retourner capital_cible / n_periodes
    fin
    retourner capital_cible * t / ((1 + t) ** n_periodes - 1)
fin

# ── Emprunts & remboursements ────────────────────────────────

# Mensualité d'un emprunt (méthode amortissement constant)
# M = C * t / (1 - (1+t)^(-n))    (t = taux mensuel)
fonction mensualite(capital, taux_annuel_pct, duree_mois) faire
    decimal t = taux_annuel_pct / 100 / 12
    si t == 0 alors
        retourner capital / duree_mois
    fin
    retourner capital * t / (1 - (1 + t) ** (-duree_mois))
fin

# Coût total d'un emprunt
fonction cout_total_emprunt(capital, taux_annuel_pct, duree_mois) faire
    retourner mensualite(capital, taux_annuel_pct, duree_mois) * duree_mois
fin

# Intérêt total payé sur un emprunt
fonction interet_total_emprunt(capital, taux_annuel_pct, duree_mois) faire
    retourner cout_total_emprunt(capital, taux_annuel_pct, duree_mois) - capital
fin

# Capital restant dû après k mensualités
fonction capital_restant(capital, taux_annuel_pct, duree_mois, k_mois) faire
    decimal t = taux_annuel_pct / 100 / 12
    decimal m = mensualite(capital, taux_annuel_pct, duree_mois)
    si t == 0 alors
        retourner capital - m * k_mois
    fin
    retourner capital * (1 + t) ** k_mois - m * ((1 + t) ** k_mois - 1) / t
fin

# Part d'intérêt dans la k-ième mensualité
fonction interet_mensualite(capital, taux_annuel_pct, duree_mois, k_mois) faire
    decimal restant = capital_restant(capital, taux_annuel_pct, duree_mois, k_mois - 1)
    retourner restant * taux_annuel_pct / 100 / 12
fin

# Part d'amortissement dans la k-ième mensualité
fonction amortissement_mensualite(capital, taux_annuel_pct, duree_mois, k_mois) faire
    decimal m = mensualite(capital, taux_annuel_pct, duree_mois)
    decimal i = interet_mensualite(capital, taux_annuel_pct, duree_mois, k_mois)
    retourner m - i
fin

# ── Valorisation & rendement ──────────────────────────────────

# Valeur actuelle nette (VAN)
# VAN = -investissement + Σ CF_k / (1+t)^k
# Prend une liste de flux de trésorerie (CF0 est l'investissement initial négatif)
fonction van(liste_flux, taux_pct) faire
    decimal t = taux_pct / 100
    decimal total = 0
    pour k de 0 a liste_flux.longueur() - 1 faire
        total += liste_flux[k] / (1 + t) ** k
    fin
    retourner total
fin

# Retour sur investissement (ROI) en %
fonction roi(gain_net, cout) faire
    si cout == 0 alors
        retourner 0
    fin
    retourner gain_net / cout * 100
fin

# CAGR — Taux de croissance annuel composé
fonction cagr(valeur_debut, valeur_fin, duree_ans) faire
    si valeur_debut == 0 ou duree_ans == 0 alors
        retourner 0
    fin
    retourner ((valeur_fin / valeur_debut) ** (1 / duree_ans) - 1) * 100
fin

# Délai de récupération (payback period) simple
# liste_flux : flux annuels (sans investissement initial)
fonction payback(investissement, liste_flux) faire
    decimal cumul = 0
    pour k de 0 a liste_flux.longueur() - 1 faire
        cumul += liste_flux[k]
        si cumul >= investissement alors
            retourner k + 1
        fin
    fin
    retourner -1
fin

# Valeur future d'un investissement avec rendement variable
# liste_taux : taux annuels en % pour chaque année
fonction valeur_future_variable(capital, liste_taux) faire
    decimal v = capital
    pour t dans liste_taux faire
        v = v * (1 + t / 100)
    fin
    retourner v
fin

# ── Prix & marges ─────────────────────────────────────────────

# Prix de vente HT depuis prix de revient et marge en %
fonction prix_vente_ht(prix_revient, marge_pct) faire
    retourner prix_revient * (1 + marge_pct / 100)
fin

# Marge brute en %
fonction marge_brute_pct(prix_vente, cout) faire
    si prix_vente == 0 alors
        retourner 0
    fin
    retourner (prix_vente - cout) / prix_vente * 100
fin

# Prix TTC depuis prix HT et taux de TVA
fonction ht_vers_ttc(prix_ht, tva_pct) faire
    retourner prix_ht * (1 + tva_pct / 100)
fin

# Prix HT depuis prix TTC et taux de TVA
fonction ttc_vers_ht(prix_ttc, tva_pct) faire
    si tva_pct == -100 alors
        retourner 0
    fin
    retourner prix_ttc / (1 + tva_pct / 100)
fin

# Montant de la TVA
fonction montant_tva(prix_ht, tva_pct) faire
    retourner prix_ht * tva_pct / 100
fin

# Point mort (seuil de rentabilité) en unités
fonction seuil_rentabilite(charges_fixes, prix_unitaire, cout_variable_unitaire) faire
    decimal marge_unit = prix_unitaire - cout_variable_unitaire
    si marge_unit == 0 alors
        retourner 0
    fin
    retourner charges_fixes / marge_unit
fin

# Bénéfice net depuis CA, charges fixes et variables totales
fonction benefice(chiffre_affaires, charges_fixes, charges_variables) faire
    retourner chiffre_affaires - charges_fixes - charges_variables
fin

# ── Indicateurs boursiers ─────────────────────────────────────

# Price-Earnings Ratio
fonction per(prix_action, benefice_par_action) faire
    si benefice_par_action == 0 alors
        retourner 0
    fin
    retourner prix_action / benefice_par_action
fin

# Rendement d'une action (dividende yield)
fonction rendement_action(dividende, prix_action) faire
    si prix_action == 0 alors
        retourner 0
    fin
    retourner dividende / prix_action * 100
fin

# Plus ou moins-value en %
fonction variation_pct(valeur_initiale, valeur_finale) faire
    si valeur_initiale == 0 alors
        retourner 0
    fin
    retourner (valeur_finale - valeur_initiale) / valeur_initiale * 100
fin

# Valeur d'une position avec levier
fonction valeur_avec_levier(capital, levier, variation_pct_marche) faire
    retourner capital + capital * levier * variation_pct_marche / 100
fin

# Volatilité (écart-type des rendements, liste de rendements en %)
# Nécessite include/stats.fpp pour ecart_type
fonction volatilite(liste_rendements) faire
    decimal mu = 0
    pour r dans liste_rendements faire
        mu += r
    fin
    mu = mu / liste_rendements.longueur()
    decimal s = 0
    pour r dans liste_rendements faire
        s += (r - mu) ** 2
    fin
    retourner racine(s / liste_rendements.longueur())
fin

# Ratio de Sharpe (rendement ajusté au risque)
# (rendement_moyen - taux_sans_risque) / volatilite
fonction sharpe(rendement_moyen_pct, taux_sans_risque_pct, vol_pct) faire
    si vol_pct == 0 alors
        retourner 0
    fin
    retourner (rendement_moyen_pct - taux_sans_risque_pct) / vol_pct
fin

# ── Fiscalité ────────────────────────────────────────────────

# Impôt progressif — 4 tranches (ex : barème simplifié)
# Limites : [0, t1, t2, t3, infini]   Taux : [r0, r1, r2, r3]
fonction impot_4_tranches(revenu, t1, t2, t3, r0, r1, r2, r3) faire
    si revenu <= 0 alors
        retourner 0
    fin
    decimal impot = 0
    si revenu > t1 alors
        impot += (minimum(revenu, t2) - t1) * r1 / 100
    fin
    si revenu > t2 alors
        impot += (minimum(revenu, t3) - t2) * r2 / 100
    fin
    si revenu > t3 alors
        impot += (revenu - t3) * r3 / 100
    fin
    impot += minimum(revenu, t1) * r0 / 100
    retourner impot
fin

# Taux moyen d'imposition
fonction taux_moyen_imposition(impot, revenu) faire
    si revenu == 0 alors
        retourner 0
    fin
    retourner impot / revenu * 100
fin

# Revenu net après impôt
fonction revenu_net(revenu_brut, taux_impot_pct) faire
    retourner revenu_brut * (1 - taux_impot_pct / 100)
fin
