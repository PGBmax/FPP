# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque pour jeux & aléatoire
#  inclure "include/jeux.fpp"
#
#  Dés, cartes, probabilités, génération de niveaux, IA simple.
# ══════════════════════════════════════════════════════════════

# ── Dés ───────────────────────────────────────────────────────

# Lancer un dé à n faces (résultat entre 1 et n)
fonction lancer_de(n_faces) faire
    retourner hasard_entier(1, n_faces)
fin

# Lancer n dés à f faces et retourner la somme
fonction lancer_des(n_des, n_faces) faire
    decimal total = 0
    pour i de 1 a n_des faire
        total += lancer_de(n_faces)
    fin
    retourner total
fin

# Lancer n dés à f faces, retirer le plus bas, retourner la somme (DnD 4d6 drop lowest)
fonction lancer_des_drop_low(n_des, n_faces) faire
    decimal total = 0
    decimal min_val = n_faces + 1
    pour i de 1 a n_des faire
        decimal r = lancer_de(n_faces)
        total += r
        si r < min_val alors
            min_val = r
        fin
    fin
    retourner total - min_val
fin

# Probabilité d'obtenir exactement k avec un dé à n faces
fonction prob_de_exact(n_faces, k) faire
    si k < 1 ou k > n_faces alors
        retourner 0
    fin
    retourner 1.0 / n_faces
fin

# Probabilité d'obtenir >= k avec un dé à n faces
fonction prob_de_sup_egal(n_faces, k) faire
    si k <= 1 alors
        retourner 1
    fin
    si k > n_faces alors
        retourner 0
    fin
    retourner (n_faces - k + 1.0) / n_faces
fin

# Espérance d'un dé à n faces
fonction esperance_de(n_faces) faire
    retourner (n_faces + 1.0) / 2
fin

# ── Cartes ────────────────────────────────────────────────────

# Valeur numérique d'une carte (1 = As, 11 = Valet, 12 = Dame, 13 = Roi)
# Retourne la valeur blackjack (As = 11, figures = 10)
fonction valeur_blackjack(carte) faire
    si carte == 1 alors
        retourner 11
    fin
    si carte >= 11 alors
        retourner 10
    fin
    retourner carte
fin

# Probabilité de piocher une carte de valeur blackjack donnée dans un jeu de 52
fonction prob_carte_bj(valeur_bj) faire
    si valeur_bj == 10 alors
        # 10, Valet, Dame, Roi = 16 cartes sur 52
        retourner 16.0 / 52
    fin
    si valeur_bj == 11 alors
        # As = 4 sur 52
        retourner 4.0 / 52
    fin
    # Autres (2-9) = 4 par valeur
    retourner 4.0 / 52
fin

# Tirage d'une carte (1-13)
fonction piocher_carte() faire
    retourner hasard_entier(1, 13)
fin

# Tirage d'une couleur (1=Pique, 2=Coeur, 3=Carreau, 4=Trèfle)
fonction piocher_couleur() faire
    retourner hasard_entier(1, 4)
fin

# ── Probabilités combinées ────────────────────────────────────

# Probabilité que l'événement A et B se produisent (indépendants)
fonction prob_et(pa, pb) faire
    retourner pa * pb
fin

# Probabilité que A ou B se produise (mutuellement exclusifs)
fonction prob_ou_excl(pa, pb) faire
    retourner pa + pb
fin

# Probabilité que A ou B (quelconques)
fonction prob_ou(pa, pb) faire
    retourner pa + pb - pa * pb
fin

# Probabilité complémentaire
fonction prob_non(pa) faire
    retourner 1 - pa
fin

# Probabilité d'avoir exactement k succès en n essais (loi binomiale)
# Nécessite include/math.fpp pour combinaisons
fonction binomiale(n, k, p) faire
    decimal c = 1
    # Calcul de C(n, k) en itératif pour éviter les overflows
    pour i de 0 a k - 1 faire
        c = c * (n - i) / (i + 1)
    fin
    retourner c * p ** k * (1 - p) ** (n - k)
fin

# Espérance de la loi binomiale
fonction esperance_binomiale(n, p) faire
    retourner n * p
fin

# Variance de la loi binomiale
fonction variance_binomiale(n, p) faire
    retourner n * p * (1 - p)
fin

# ── Scores & niveaux ──────────────────────────────────────────

# Niveau depuis une expérience (croissance quadratique)
# Niveau l = plancher(racine(xp / base))
fonction xp_vers_niveau(xp, base) faire
    si base == 0 alors
        retourner 1
    fin
    retourner plancher(racine(xp / base)) + 1
fin

# XP nécessaire pour atteindre le niveau l (croissance quadratique)
fonction niveau_vers_xp(niveau, base) faire
    retourner base * (niveau - 1) ** 2
fin

# XP restant pour passer au niveau suivant
fonction xp_restant(xp_actuel, base) faire
    decimal niv = xp_vers_niveau(xp_actuel, base)
    retourner niveau_vers_xp(niv + 1, base) - xp_actuel
fin

# Score normalisé entre 0 et 100
fonction score_normalise(valeur, minimum_val, maximum_val) faire
    si maximum_val == minimum_val alors
        retourner 0
    fin
    retourner (valeur - minimum_val) / (maximum_val - minimum_val) * 100
fin

# Rang centile dans une liste (sans include/stats.fpp)
fonction rang_centile(position, total) faire
    si total == 0 alors
        retourner 0
    fin
    retourner (total - position) / total * 100
fin

# ── Génération de terrain ─────────────────────────────────────

# Valeur de terrain aléatoire avec biais (0=eau, 1=plaine, 2=forêt, 3=montagne)
# prob_eau + prob_plaine + prob_foret + prob_montagne doivent faire 100
fonction terrain_aleatoire(prob_eau, prob_plaine, prob_foret) faire
    decimal r = hasard_entier(1, 100)
    si r <= prob_eau alors
        retourner 0
    fin
    si r <= prob_eau + prob_plaine alors
        retourner 1
    fin
    si r <= prob_eau + prob_plaine + prob_foret alors
        retourner 2
    fin
    retourner 3
fin

# ── Physique de jeu ───────────────────────────────────────────

# Position après t secondes avec vitesse initiale et gravité
fonction position_y(y0, vy0, gravite, t) faire
    retourner y0 + vy0 * t - 0.5 * gravite * t * t
fin

# Vitesse verticale après t secondes
fonction vitesse_y(vy0, gravite, t) faire
    retourner vy0 - gravite * t
fin

# Temps d'atteinte du sol (y0 > 0, vy0 >= 0, retourne -1 si impossible)
fonction temps_chute(y0, vy0, gravite) faire
    si gravite == 0 alors
        retourner -1
    fin
    # y0 + vy0*t - 0.5*g*t^2 = 0  →  résoudre avec discriminant
    decimal disc = vy0 * vy0 + 2 * gravite * y0
    si disc < 0 alors
        retourner -1
    fin
    retourner (vy0 + racine(disc)) / gravite
fin

# Hauteur maximale atteinte
fonction hauteur_max(y0, vy0, gravite) faire
    si gravite == 0 alors
        retourner y0
    fin
    retourner y0 + vy0 * vy0 / (2 * gravite)
fin

# ── IA simple : décisions ────────────────────────────────────

# Décision IA simple : attaquer si hp_ennemi < seuil, sinon défendre
fonction ia_decision(hp_joueur, hp_ennemi, seuil_attaque) faire
    si hp_ennemi <= seuil_attaque alors
        retourner 1
    fin
    si hp_joueur < 20 alors
        retourner 2
    fin
    retourner 1
fin

# Damage avec variabilité (min_dmg à max_dmg, réduit par armure en %)
fonction calculer_degats(min_dmg, max_dmg, armure_pct) faire
    decimal brut = hasard_entier(min_dmg, max_dmg)
    retourner brut * (1 - armure_pct / 100)
fin

# Est-ce un coup critique ? (prob_crit en %)
fonction est_critique(prob_crit_pct) faire
    retourner hasard_entier(1, 100) <= prob_crit_pct
fin

# HP après soin (ne dépasse pas hp_max)
fonction appliquer_soin(hp_actuel, hp_max, soin) faire
    decimal nouveaux_hp = hp_actuel + soin
    si nouveaux_hp > hp_max alors
        retourner hp_max
    fin
    retourner nouveaux_hp
fin

# HP après dégâts (ne passe pas sous 0)
fonction appliquer_degats(hp_actuel, degats) faire
    decimal nouveaux_hp = hp_actuel - degats
    si nouveaux_hp < 0 alors
        retourner 0
    fin
    retourner nouveaux_hp
fin

# Est-ce que le personnage est mort ?
fonction est_mort(hp) faire
    retourner hp <= 0
fin

# ── Timers & tours ────────────────────────────────────────────

# Nombre de tours restants depuis un cooldown (cooldown en tours)
fonction cooldown_restant(tour_actuel, tour_utilisation, duree_cooldown) faire
    decimal ecoule = tour_actuel - tour_utilisation
    si ecoule >= duree_cooldown alors
        retourner 0
    fin
    retourner duree_cooldown - ecoule
fin

# Est-ce que la capacité est disponible ?
fonction capacite_disponible(tour_actuel, tour_utilisation, duree_cooldown) faire
    retourner cooldown_restant(tour_actuel, tour_utilisation, duree_cooldown) == 0
fin
