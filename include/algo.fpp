# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque d'algorithmes
#  inclure "include/algo.fpp"
#
#  Recherche, tri, manipulation de listes numériques.
# ══════════════════════════════════════════════════════════════

# ── Recherche ─────────────────────────────────────────────────

# Recherche linéaire : retourne l'index ou -1
fonction recherche(lst, cible) faire
    pour i de 0 a lst.longueur() - 1 faire
        si lst[i] == cible alors
            retourner i
        fin
    fin
    retourner -1
fin

# Recherche binaire (la liste DOIT être triée) : retourne l'index ou -1
fonction recherche_binaire(lst, cible) faire
    decimal gauche = 0
    decimal droite = lst.longueur() - 1
    tantque gauche <= droite faire
        decimal milieu = plancher((gauche + droite) / 2)
        si lst[milieu] == cible alors
            retourner milieu
        fin
        si lst[milieu] < cible alors
            gauche = milieu + 1
        sinon
            droite = milieu - 1
        fin
    fin
    retourner -1
fin

# Vérifie si une valeur est présente dans la liste
fonction contient_valeur(lst, v) faire
    retourner recherche(lst, v) != -1
fin

# Compte le nombre d'occurrences d'une valeur
fonction compter_occurrences(lst, v) faire
    decimal n = 0
    pour x dans lst faire
        si x == v alors
            n += 1
        fin
    fin
    retourner n
fin

# ── Tri ───────────────────────────────────────────────────────

# Tri à bulles (en place, retourne le nombre d'échanges)
fonction tri_bulles(lst) faire
    decimal n = lst.longueur()
    decimal echanges = 0
    pour i de 0 a n - 2 faire
        pour j de 0 a n - 2 - i faire
            si lst[j] > lst[j + 1] alors
                decimal tmp = lst[j]
                lst[j] = lst[j + 1]
                lst[j + 1] = tmp
                echanges += 1
            fin
        fin
    fin
    retourner echanges
fin

# Tri par insertion (en place)
fonction tri_insertion(lst) faire
    decimal n = lst.longueur()
    pour i de 1 a n - 1 faire
        decimal cle = lst[i]
        decimal j = i - 1
        tantque j >= 0 et lst[j] > cle faire
            lst[j + 1] = lst[j]
            j -= 1
        fin
        lst[j + 1] = cle
    fin
    retourner 0
fin

# Tri par sélection (en place)
fonction tri_selection(lst) faire
    decimal n = lst.longueur()
    pour i de 0 a n - 2 faire
        decimal idx_min = i
        pour j de i + 1 a n - 1 faire
            si lst[j] < lst[idx_min] alors
                idx_min = j
            fin
        fin
        si idx_min != i alors
            decimal tmp = lst[i]
            lst[i] = lst[idx_min]
            lst[idx_min] = tmp
        fin
    fin
    retourner 0
fin

# Vérifie si une liste est triée (ordre croissant)
fonction est_triee(lst) faire
    pour i de 0 a lst.longueur() - 2 faire
        si lst[i] > lst[i + 1] alors
            retourner 0
        fin
    fin
    retourner 1
fin

# ── Transformation ────────────────────────────────────────────

# Décaler tous les éléments de delta (en place)
fonction decaler(lst, delta) faire
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] += delta
    fin
    retourner 0
fin

# Multiplier tous les éléments par facteur (en place)
fonction echelonner(lst, facteur) faire
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] *= facteur
    fin
    retourner 0
fin

# Appliquer une valeur absolue à tous les éléments (en place)
fonction absolus(lst) faire
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] = absolu(lst[i])
    fin
    retourner 0
fin

# Élever tous les éléments à la puissance p (en place)
fonction puissances(lst, p) faire
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] = lst[i] ** p
    fin
    retourner 0
fin

# ── Fenêtrage & sous-listes ───────────────────────────────────

# Somme d'une fenêtre glissante de largeur w à la position i
fonction fenetre_somme(lst, i, w) faire
    decimal s = 0
    decimal fin_w = minimum(i + w - 1, lst.longueur() - 1)
    pour j de i a fin_w faire
        s += lst[j]
    fin
    retourner s
fin

# Moyenne d'une fenêtre glissante de largeur w à la position i
fonction fenetre_moyenne(lst, i, w) faire
    decimal fin_w = minimum(i + w - 1, lst.longueur() - 1)
    decimal taille = fin_w - i + 1
    si taille == 0 alors
        retourner 0
    fin
    retourner fenetre_somme(lst, i, w) / taille
fin

# ── Suites & séquences ────────────────────────────────────────

# Remplir une liste avec une progression arithmétique (en place)
# lst[i] = debut + i * pas
fonction remplir_arithmetique(lst, debut, pas) faire
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] = debut + i * pas
    fin
    retourner 0
fin

# Remplir une liste avec une progression géométrique (en place)
# lst[i] = debut * raison^i
fonction remplir_geometrique(lst, debut, raison) faire
    decimal val = debut
    pour i de 0 a lst.longueur() - 1 faire
        lst[i] = val
        val *= raison
    fin
    retourner 0
fin

# ── Manipulation avancée ──────────────────────────────────────

# Rotation à gauche de k positions (en place)
fonction rotation_gauche(lst, k) faire
    decimal n = lst.longueur()
    si n == 0 alors
        retourner 0
    fin
    k = k % n
    pour _ de 0 a k - 1 faire
        decimal premier = lst[0]
        pour i de 0 a n - 2 faire
            lst[i] = lst[i + 1]
        fin
        lst[n - 1] = premier
    fin
    retourner 0
fin

# Rotation à droite de k positions (en place)
fonction rotation_droite(lst, k) faire
    decimal n = lst.longueur()
    si n == 0 alors
        retourner 0
    fin
    k = k % n
    pour _ de 0 a k - 1 faire
        decimal dernier = lst[n - 1]
        pour i de n - 2 a 0 pas -1 faire
            lst[i + 1] = lst[i]
        fin
        lst[0] = dernier
    fin
    retourner 0
fin

# Dupliquer chaque élément n fois (en place, la liste doit avoir la capacité)
fonction dupliquer_elements(lst, n_fois) faire
    decimal taille = lst.longueur()
    pour i de 0 a taille - 1 faire
        pour _ de 1 a n_fois - 1 faire
            lst.ajouter(lst[i])
        fin
    fin
    retourner 0
fin
