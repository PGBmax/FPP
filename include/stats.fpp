# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque statistique
#  inclure "include/stats.fpp"
#
#  Toutes les fonctions prennent une liste numérique en entrée.
#  Pré-requis : la liste doit être non vide.
# ══════════════════════════════════════════════════════════════

# ── Agrégats de base ──────────────────────────────────────────

# Somme de tous les éléments
fonction somme(lst) faire
    decimal s = 0
    pour v dans lst faire
        s += v
    fin
    retourner s
fin

# Produit de tous les éléments
fonction produit(lst) faire
    decimal p = 1
    pour v dans lst faire
        p *= v
    fin
    retourner p
fin

# Valeur minimale
fonction min_liste(lst) faire
    decimal m = lst[0]
    pour i de 1 a lst.longueur() - 1 faire
        si lst[i] < m alors
            m = lst[i]
        fin
    fin
    retourner m
fin

# Valeur maximale
fonction max_liste(lst) faire
    decimal m = lst[0]
    pour i de 1 a lst.longueur() - 1 faire
        si lst[i] > m alors
            m = lst[i]
        fin
    fin
    retourner m
fin

# Index du minimum
fonction index_min(lst) faire
    decimal m = lst[0]
    decimal idx = 0
    pour i de 1 a lst.longueur() - 1 faire
        si lst[i] < m alors
            m = lst[i]
            idx = i
        fin
    fin
    retourner idx
fin

# Index du maximum
fonction index_max(lst) faire
    decimal m = lst[0]
    decimal idx = 0
    pour i de 1 a lst.longueur() - 1 faire
        si lst[i] > m alors
            m = lst[i]
            idx = i
        fin
    fin
    retourner idx
fin

# Étendue (max - min)
fonction etendue(lst) faire
    retourner max_liste(lst) - min_liste(lst)
fin

# ── Tendance centrale ─────────────────────────────────────────

# Moyenne arithmétique
fonction moyenne(lst) faire
    retourner somme(lst) / lst.longueur()
fin

# Médiane (trie la liste en place, retourne la valeur centrale)
fonction mediane(lst) faire
    lst.trier()
    decimal n = lst.longueur()
    decimal milieu = plancher(n / 2)
    si n % 2 == 1 alors
        retourner lst[milieu]
    fin
    retourner (lst[milieu - 1] + lst[milieu]) / 2
fin

# Moyenne harmonique : n / Σ(1/xi)
fonction moyenne_harmonique(lst) faire
    decimal s = 0
    pour v dans lst faire
        si v == 0 alors
            retourner 0
        fin
        s += 1 / v
    fin
    retourner lst.longueur() / s
fin

# Moyenne géométrique : (x1 * x2 * ... * xn)^(1/n)
fonction moyenne_geometrique(lst) faire
    retourner produit(lst) ** (1 / lst.longueur())
fin

# ── Dispersion ────────────────────────────────────────────────

# Variance de la population (diviseur n)
fonction variance(lst) faire
    decimal mu = moyenne(lst)
    decimal s = 0
    pour v dans lst faire
        s += (v - mu) ** 2
    fin
    retourner s / lst.longueur()
fin

# Variance de l'échantillon (diviseur n-1, non biaisée)
fonction variance_echantillon(lst) faire
    si lst.longueur() <= 1 alors
        retourner 0
    fin
    decimal mu = moyenne(lst)
    decimal s = 0
    pour v dans lst faire
        s += (v - mu) ** 2
    fin
    retourner s / (lst.longueur() - 1)
fin

# Écart-type de la population
fonction ecart_type(lst) faire
    retourner racine(variance(lst))
fin

# Écart-type de l'échantillon
fonction ecart_type_echantillon(lst) faire
    retourner racine(variance_echantillon(lst))
fin

# Écart absolu moyen
fonction ecart_absolu_moyen(lst) faire
    decimal mu = moyenne(lst)
    decimal s = 0
    pour v dans lst faire
        s += absolu(v - mu)
    fin
    retourner s / lst.longueur()
fin

# ── Percentiles & quantiles ───────────────────────────────────

# Percentile p (0–100) : interpolation linéaire
fonction percentile(lst, p) faire
    lst.trier()
    decimal n = lst.longueur()
    decimal rang = p * (n - 1) / 100
    decimal i = plancher(rang)
    decimal f = rang - i
    si i + 1 >= n alors
        retourner lst[n - 1]
    fin
    retourner lst[i] + f * (lst[i + 1] - lst[i])
fin

# Premier quartile Q1
fonction q1(lst) faire
    retourner percentile(lst, 25)
fin

# Troisième quartile Q3
fonction q3(lst) faire
    retourner percentile(lst, 75)
fin

# Intervalle interquartile IQR = Q3 - Q1
fonction iqr(lst) faire
    retourner q3(lst) - q1(lst)
fin

# ── Forme de la distribution ──────────────────────────────────

# Coefficient de variation (en %) = écart-type / moyenne * 100
fonction coef_variation(lst) faire
    decimal mu = moyenne(lst)
    si mu == 0 alors
        retourner 0
    fin
    retourner ecart_type(lst) / absolu(mu) * 100
fin

# Nombre de valeurs supérieures à un seuil
fonction compter_sup(lst, seuil) faire
    decimal n = 0
    pour v dans lst faire
        si v > seuil alors
            n += 1
        fin
    fin
    retourner n
fin

# Nombre de valeurs inférieures à un seuil
fonction compter_inf(lst, seuil) faire
    decimal n = 0
    pour v dans lst faire
        si v < seuil alors
            n += 1
        fin
    fin
    retourner n
fin

# Nombre de valeurs dans l'intervalle [a, b]
fonction compter_entre(lst, a, b) faire
    decimal n = 0
    pour v dans lst faire
        si v >= a et v <= b alors
            n += 1
        fin
    fin
    retourner n
fin

# ── Normalisation ─────────────────────────────────────────────

# Normaliser tous les éléments vers [0, 1] (min-max, en place)
fonction normaliser_liste(lst) faire
    decimal mn = min_liste(lst)
    decimal mx = max_liste(lst)
    decimal d = mx - mn
    si d == 0 alors
        retourner 0
    fin
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] = (lst[i] - mn) / d
    fin
    retourner 0
fin

# Centrer-réduire (z-score) tous les éléments (en place)
fonction centrer_reduire(lst) faire
    decimal mu = moyenne(lst)
    decimal sigma = ecart_type(lst)
    si sigma == 0 alors
        retourner 0
    fin
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] = (lst[i] - mu) / sigma
    fin
    retourner 0
fin
