# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque de matrices
#  inclure "include/matrice.fpp"
#
#  Une matrice NxM est représentée comme une liste plate de N*M
#  éléments, rangée ligne par ligne.
#  Accès à (i, j) : indice = i * nb_colonnes + j  (i, j base 0)
# ══════════════════════════════════════════════════════════════

# ── Accès aux éléments ────────────────────────────────────────

# Calcule l'indice linéaire de l'élément (i, j) dans une matrice de ncols colonnes
fonction mat_idx(i, j, ncols) faire
    retourner i * ncols + j
fin

# Lire l'élément (i, j) d'une matrice
fonction mat_get(mat, i, j, ncols) faire
    retourner mat[i * ncols + j]
fin

# ── Création ──────────────────────────────────────────────────

# Créer une liste remplie de zeros de taille n
fonction vec_zeros(n) faire
    liste resultat = []
    pour i de 0 a n - 1 faire
        ajouter(resultat, 0)
    fin
    retourner resultat
fin

# Créer une matrice nulle (nlignes x ncols)
fonction mat_zeros(nlignes, ncols) faire
    retourner vec_zeros(nlignes * ncols)
fin

# Créer une matrice identité (n x n)
fonction mat_identite(n) faire
    liste m = mat_zeros(n, n)
    pour i de 0 a n - 1 faire
        m[i * n + i] = 1
    fin
    retourner m
fin

# Créer une matrice remplie d'une valeur donnée
fonction mat_remplir(nlignes, ncols, valeur) faire
    liste m = []
    pour i de 0 a nlignes * ncols - 1 faire
        ajouter(m, valeur)
    fin
    retourner m
fin

# ── Informations ──────────────────────────────────────────────

# Trace d'une matrice carrée (somme des éléments diagonaux)
fonction mat_trace(mat, n) faire
    decimal s = 0
    pour i de 0 a n - 1 faire
        s += mat[i * n + i]
    fin
    retourner s
fin

# Somme de tous les éléments
fonction mat_somme(mat) faire
    decimal s = 0
    pour v dans mat faire
        s += v
    fin
    retourner s
fin

# Valeur maximale de la matrice
fonction mat_max(mat) faire
    decimal m = mat[0]
    pour v dans mat faire
        si v > m alors
            m = v
        fin
    fin
    retourner m
fin

# Valeur minimale de la matrice
fonction mat_min(mat) faire
    decimal m = mat[0]
    pour v dans mat faire
        si v < m alors
            m = v
        fin
    fin
    retourner m
fin

# Déterminant 2x2
fonction mat_det2(a00, a01, a10, a11) faire
    retourner a00 * a11 - a01 * a10
fin

# Déterminant d'une matrice 2x2 stockée en liste plate
fonction mat_det2_liste(mat) faire
    retourner mat[0] * mat[3] - mat[1] * mat[2]
fin

# Déterminant 3x3 (développement par la première ligne)
fonction mat_det3(mat) faire
    decimal a = mat[0] * mat_det2(mat[4], mat[5], mat[7], mat[8])
    decimal b = mat[1] * mat_det2(mat[3], mat[5], mat[6], mat[8])
    decimal c = mat[2] * mat_det2(mat[3], mat[4], mat[6], mat[7])
    retourner a - b + c
fin

# ── Opérations élémentaires ───────────────────────────────────

# Addition de deux matrices (même dimensions)
fonction mat_additionner(a, b) faire
    liste r = []
    pour i de 0 a taille(a) - 1 faire
        ajouter(r, a[i] + b[i])
    fin
    retourner r
fin

# Soustraction de deux matrices
fonction mat_soustraire(a, b) faire
    liste r = []
    pour i de 0 a taille(a) - 1 faire
        ajouter(r, a[i] - b[i])
    fin
    retourner r
fin

# Multiplication par un scalaire
fonction mat_scalaire(mat, k) faire
    liste r = []
    pour v dans mat faire
        ajouter(r, v * k)
    fin
    retourner r
fin

# Transposée d'une matrice nlignes x ncols
fonction mat_transposee(mat, nlignes, ncols) faire
    liste r = mat_zeros(ncols, nlignes)
    pour i de 0 a nlignes - 1 faire
        pour j de 0 a ncols - 1 faire
            r[j * nlignes + i] = mat[i * ncols + j]
        fin
    fin
    retourner r
fin

# Multiplication de matrices : A (nla x nca) * B (nca x ncb) → C (nla x ncb)
fonction mat_multiplier(a, b, nla, nca, ncb) faire
    liste r = mat_zeros(nla, ncb)
    pour i de 0 a nla - 1 faire
        pour j de 0 a ncb - 1 faire
            decimal s = 0
            pour k de 0 a nca - 1 faire
                s += a[i * nca + k] * b[k * ncb + j]
            fin
            r[i * ncb + j] = s
        fin
    fin
    retourner r
fin

# ── Opérations sur les lignes et colonnes ─────────────────────

# Extraire une ligne (retourne une liste)
fonction mat_ligne(mat, i, ncols) faire
    liste r = []
    pour j de 0 a ncols - 1 faire
        ajouter(r, mat[i * ncols + j])
    fin
    retourner r
fin

# Extraire une colonne (retourne une liste)
fonction mat_colonne(mat, j, nlignes, ncols) faire
    liste r = []
    pour i de 0 a nlignes - 1 faire
        ajouter(r, mat[i * ncols + j])
    fin
    retourner r
fin

# Somme d'une ligne
fonction mat_somme_ligne(mat, i, ncols) faire
    decimal s = 0
    pour j de 0 a ncols - 1 faire
        s += mat[i * ncols + j]
    fin
    retourner s
fin

# Somme d'une colonne
fonction mat_somme_colonne(mat, j, nlignes, ncols) faire
    decimal s = 0
    pour i de 0 a nlignes - 1 faire
        s += mat[i * ncols + j]
    fin
    retourner s
fin

# ── Résolution de système 2x2 ─────────────────────────────────

# Résoudre ax + by = e, cx + dy = f  (retourne x)
fonction systeme2x2_x(a, b, c, d, e, f) faire
    decimal det = mat_det2(a, b, c, d)
    si det == 0 alors
        retourner 0
    fin
    retourner mat_det2(e, b, f, d) / det
fin

# Résoudre ax + by = e, cx + dy = f  (retourne y)
fonction systeme2x2_y(a, b, c, d, e, f) faire
    decimal det = mat_det2(a, b, c, d)
    si det == 0 alors
        retourner 0
    fin
    retourner mat_det2(a, e, c, f) / det
fin

# ── Vecteurs (matrices 1D) ────────────────────────────────────

# Produit scalaire de deux vecteurs
fonction vec_scalaire(u, v) faire
    decimal s = 0
    pour i de 0 a taille(u) - 1 faire
        s += u[i] * v[i]
    fin
    retourner s
fin

# Norme euclidienne d'un vecteur
fonction vec_norme(u) faire
    retourner racine(vec_scalaire(u, u))
fin

# Normaliser un vecteur
fonction vec_normaliser(u) faire
    decimal n = vec_norme(u)
    si n == 0 alors
        retourner u
    fin
    liste r = []
    pour v dans u faire
        ajouter(r, v / n)
    fin
    retourner r
fin

# Additionner deux vecteurs
fonction vec_additionner(u, v) faire
    liste r = []
    pour i de 0 a taille(u) - 1 faire
        ajouter(r, u[i] + v[i])
    fin
    retourner r
fin

# Soustraire deux vecteurs
fonction vec_soustraire(u, v) faire
    liste r = []
    pour i de 0 a taille(u) - 1 faire
        ajouter(r, u[i] - v[i])
    fin
    retourner r
fin

# Multiplier un vecteur par un scalaire
fonction vec_scalaire_mult(u, k) faire
    liste r = []
    pour v dans u faire
        ajouter(r, v * k)
    fin
    retourner r
fin

# Distance entre deux vecteurs
fonction vec_distance(u, v) faire
    decimal s = 0
    pour i de 0 a taille(u) - 1 faire
        s += (u[i] - v[i]) ** 2
    fin
    retourner racine(s)
fin
