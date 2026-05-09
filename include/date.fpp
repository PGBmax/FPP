# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque de calcul sur les dates
#  inclure "include/date.fpp"
#
#  Les dates sont représentées en format AAAAMMJJ (ex: 20240315).
#  Toutes les fonctions supposent le calendrier grégorien.
# ══════════════════════════════════════════════════════════════

# ── Extraction des composantes ────────────────────────────────

# Extraire l'année d'une date AAAAMMJJ
fonction date_annee(date) faire
    retourner plancher(date / 10000)
fin

# Extraire le mois (1-12) d'une date AAAAMMJJ
fonction date_mois(date) faire
    retourner plancher(date / 100) % 100
fin

# Extraire le jour (1-31) d'une date AAAAMMJJ
fonction date_jour(date) faire
    retourner date % 100
fin

# Reconstruire une date depuis ses composantes
fonction creer_date(annee, mois, jour) faire
    retourner annee * 10000 + mois * 100 + jour
fin

# ── Années bissextiles ────────────────────────────────────────

# Vérifie si une année est bissextile
fonction est_bissextile(annee) faire
    si annee % 400 == 0 alors
        retourner 1
    fin
    si annee % 100 == 0 alors
        retourner 0
    fin
    si annee % 4 == 0 alors
        retourner 1
    fin
    retourner 0
fin

# ── Durée des mois ────────────────────────────────────────────

# Nombre de jours dans un mois (mois 1-12, annee pour le mois de février)
fonction jours_dans_mois(mois, annee) faire
    si mois == 2 alors
        si est_bissextile(annee) alors
            retourner 29
        sinon
            retourner 28
        fin
    fin
    si mois == 4 ou mois == 6 ou mois == 9 ou mois == 11 alors
        retourner 30
    fin
    retourner 31
fin

# Nombre de jours dans une année
fonction jours_dans_annee(annee) faire
    si est_bissextile(annee) alors
        retourner 366
    fin
    retourner 365
fin

# ── Jour de l'année ───────────────────────────────────────────

# Numéro du jour dans l'année (1 = 1er janvier)
fonction jour_de_annee(date) faire
    decimal a = date_annee(date)
    decimal m = date_mois(date)
    decimal j = date_jour(date)
    decimal total = 0
    pour mois de 1 a m - 1 faire
        total += jours_dans_mois(mois, a)
    fin
    retourner total + j
fin

# ── Conversion en jours juliens simplifiés ────────────────────

# Nombre de jours depuis une époque de référence (2000-01-01 = 0)
# Algorithme basé sur le Jour Julien
fonction date_vers_jours(date) faire
    decimal a = date_annee(date)
    decimal m = date_mois(date)
    decimal j = date_jour(date)
    # Nombre de jours depuis le 1er janvier 2000
    decimal annees_depuis = a - 2000
    decimal jours = annees_depuis * 365 + plancher(annees_depuis / 4) - plancher(annees_depuis / 100) + plancher(annees_depuis / 400)
    # Ajouter les jours des mois précédents
    pour mi de 1 a m - 1 faire
        jours += jours_dans_mois(mi, a)
    fin
    retourner jours + j - 1
fin

# Différence en jours entre deux dates (date2 - date1)
fonction diff_jours(date1, date2) faire
    retourner date_vers_jours(date2) - date_vers_jours(date1)
fin

# Différence en semaines (arrondie à l'entier inférieur)
fonction diff_semaines(date1, date2) faire
    retourner plancher(diff_jours(date1, date2) / 7)
fin

# Différence en mois approximative
fonction diff_mois(date1, date2) faire
    decimal a1 = date_annee(date1)
    decimal m1 = date_mois(date1)
    decimal a2 = date_annee(date2)
    decimal m2 = date_mois(date2)
    retourner (a2 - a1) * 12 + (m2 - m1)
fin

# Différence en années approximative
fonction diff_annees(date1, date2) faire
    retourner date_annee(date2) - date_annee(date1)
fin

# ── Jour de la semaine ────────────────────────────────────────

# Algorithme de Zeller (résultat : 0=Dimanche, 1=Lundi, ..., 6=Samedi)
fonction jour_semaine(date) faire
    decimal j = date_jour(date)
    decimal m = date_mois(date)
    decimal a = date_annee(date)
    # En janvier et février, traiter comme mois 13 et 14 de l'année précédente
    si m < 3 alors
        m += 12
        a -= 1
    fin
    decimal k = a % 100
    decimal siecle = plancher(a / 100)
    decimal h = (j + plancher(13 * (m + 1) / 5) + k + plancher(k / 4) + plancher(siecle / 4) - 2 * siecle) % 7
    # Zeller donne : 0=Sam, 1=Dim, 2=Lun, ..., 6=Ven
    # Convertir en 0=Dim, 1=Lun, ..., 6=Sam
    retourner (h + 6) % 7
fin

# Nom du jour (0=Dimanche, ..., 6=Samedi) — retourne un code numérique
# 0=Dim, 1=Lun, 2=Mar, 3=Mer, 4=Jeu, 5=Ven, 6=Sam
fonction nom_jour_index(date) faire
    retourner jour_semaine(date)
fin

# Est-ce un jour de week-end ?
fonction est_weekend(date) faire
    decimal js = jour_semaine(date)
    retourner js == 0 ou js == 6
fin

# Est-ce un jour ouvrable ?
fonction est_ouvrable(date) faire
    retourner est_weekend(date) == 0
fin

# ── Numéro de semaine ISO 8601 ────────────────────────────────

# Numéro de semaine approximatif dans l'année (1-53)
fonction numero_semaine(date) faire
    decimal jda = jour_de_annee(date)
    decimal js = jour_semaine(creer_date(date_annee(date), 1, 1))
    # Décalage pour que le premier lundi soit le début de la semaine 1
    retourner plancher((jda + js - 2) / 7) + 1
fin

# ── Ajout/soustraction de jours ───────────────────────────────

# Ajouter n jours à une date (n peut être négatif)
fonction ajouter_jours(date, n) faire
    decimal a = date_annee(date)
    decimal m = date_mois(date)
    decimal j = date_jour(date) + n
    # Avancer si j > jours dans le mois
    tantque j > jours_dans_mois(m, a) faire
        j -= jours_dans_mois(m, a)
        m += 1
        si m > 12 alors
            m = 1
            a += 1
        fin
    fin
    # Reculer si j < 1
    tantque j < 1 faire
        m -= 1
        si m < 1 alors
            m = 12
            a -= 1
        fin
        j += jours_dans_mois(m, a)
    fin
    retourner creer_date(a, m, j)
fin

# Ajouter n mois à une date
fonction ajouter_mois(date, n) faire
    decimal a = date_annee(date)
    decimal m = date_mois(date) + n
    decimal j = date_jour(date)
    tantque m > 12 faire
        m -= 12
        a += 1
    fin
    tantque m < 1 faire
        m += 12
        a -= 1
    fin
    # Corriger si le jour dépasse la fin du mois
    decimal jmax = jours_dans_mois(m, a)
    si j > jmax alors
        j = jmax
    fin
    retourner creer_date(a, m, j)
fin

# Ajouter n années à une date
fonction ajouter_annees(date, n) faire
    decimal a = date_annee(date) + n
    decimal m = date_mois(date)
    decimal j = date_jour(date)
    decimal jmax = jours_dans_mois(m, a)
    si j > jmax alors
        j = jmax
    fin
    retourner creer_date(a, m, j)
fin

# ── Comparaison ───────────────────────────────────────────────

# Vérifier si date1 est avant date2
fonction date_avant(date1, date2) faire
    retourner date1 < date2
fin

# Vérifier si date1 est après date2
fonction date_apres(date1, date2) faire
    retourner date1 > date2
fin

# Vérifier si deux dates sont égales
fonction date_egale(date1, date2) faire
    retourner date1 == date2
fin

# Date la plus récente parmi deux
fonction date_max(date1, date2) faire
    si date1 > date2 alors
        retourner date1
    fin
    retourner date2
fin

# Date la plus ancienne parmi deux
fonction date_min(date1, date2) faire
    si date1 < date2 alors
        retourner date1
    fin
    retourner date2
fin

# ── Validité ──────────────────────────────────────────────────

# Vérifier si une date est valide
fonction date_valide(date) faire
    decimal a = date_annee(date)
    decimal m = date_mois(date)
    decimal j = date_jour(date)
    si m < 1 ou m > 12 alors
        retourner 0
    fin
    si j < 1 ou j > jours_dans_mois(m, a) alors
        retourner 0
    fin
    si a < 1 alors
        retourner 0
    fin
    retourner 1
fin

# ── Trimestres & périodes ─────────────────────────────────────

# Numéro du trimestre (1-4) d'une date
fonction trimestre(date) faire
    retourner plancher((date_mois(date) - 1) / 3) + 1
fin

# Premier mois du trimestre
fonction debut_trimestre(date) faire
    retourner (trimestre(date) - 1) * 3 + 1
fin

# Dernier mois du trimestre
fonction fin_trimestre(date) faire
    retourner trimestre(date) * 3
fin

# Numéro du semestre (1 ou 2)
fonction semestre(date) faire
    si date_mois(date) <= 6 alors
        retourner 1
    fin
    retourner 2
fin

# ── Âge ──────────────────────────────────────────────────────

# Âge en années révolues entre une date de naissance et une date de référence
fonction age_annees(date_naissance, date_reference) faire
    decimal annees = date_annee(date_reference) - date_annee(date_naissance)
    # Si l'anniversaire n'est pas encore passé cette année
    decimal mois_n = date_mois(date_naissance)
    decimal jour_n = date_jour(date_naissance)
    decimal mois_r = date_mois(date_reference)
    decimal jour_r = date_jour(date_reference)
    si mois_r < mois_n alors
        annees -= 1
    fin
    si mois_r == mois_n et jour_r < jour_n alors
        annees -= 1
    fin
    retourner annees
fin

# ── Affichage ────────────────────────────────────────────────

# Afficher une date en format JJ/MM/AAAA
fonction afficher_date(date) faire
    decimal j = date_jour(date)
    decimal m = date_mois(date)
    decimal a = date_annee(date)
    afficher(j & "/" & m & "/" & a)
fin
