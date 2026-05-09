# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque de géométrie
#  inclure "include/geometrie.fpp"
#
#  Formes 2D, formes 3D, coordonnées, vecteurs, trigonométrie.
#  Les angles sont toujours en DEGRÉS sauf mention contraire.
# ══════════════════════════════════════════════════════════════

# ── Conversion d'angles ───────────────────────────────────────

fonction deg_vers_rad(deg) faire
    retourner deg * pi / 180
fin

fonction rad_vers_deg(rad) faire
    retourner rad * 180 / pi
fin

# Normaliser un angle dans [0, 360[
fonction normaliser_angle(deg) faire
    deg = deg % 360
    si deg < 0 alors
        deg += 360
    fin
    retourner deg
fin

# Différence angulaire signée minimale entre deux angles (résultat dans [-180, 180])
fonction diff_angle(a, b) faire
    decimal d = (b - a) % 360
    si d > 180 alors
        d -= 360
    fin
    si d < -180 alors
        d += 360
    fin
    retourner d
fin

# ── Trigonométrie en degrés ───────────────────────────────────

fonction sin_deg(deg) faire
    retourner sinus(deg_vers_rad(deg))
fin

fonction cos_deg(deg) faire
    retourner cosinus(deg_vers_rad(deg))
fin

fonction tan_deg(deg) faire
    retourner tangente(deg_vers_rad(deg))
fin

# ── Aires — formes 2D ─────────────────────────────────────────

fonction aire_carre(cote) faire
    retourner cote * cote
fin

fonction aire_rectangle(largeur, hauteur) faire
    retourner largeur * hauteur
fin

fonction aire_triangle_base(base, hauteur) faire
    retourner base * hauteur / 2
fin

# Triangle par les trois côtés (formule de Héron)
fonction aire_triangle_heron(a, b, c) faire
    decimal s = (a + b + c) / 2
    retourner racine(s * (s - a) * (s - b) * (s - c))
fin

fonction aire_cercle(r) faire
    retourner pi * r * r
fin

# Secteur circulaire (angle en degrés)
fonction aire_secteur(r, angle_deg) faire
    retourner pi * r * r * angle_deg / 360
fin

# Couronne circulaire (anneau)
fonction aire_anneau(r_ext, r_int) faire
    retourner pi * (r_ext * r_ext - r_int * r_int)
fin

fonction aire_ellipse(demi_a, demi_b) faire
    retourner pi * demi_a * demi_b
fin

fonction aire_trapeze(b1, b2, hauteur) faire
    retourner (b1 + b2) * hauteur / 2
fin

fonction aire_losange(d1, d2) faire
    retourner d1 * d2 / 2
fin

# Polygone régulier de n côtés et de côté c
fonction aire_polygone_regulier(n_cotes, cote) faire
    retourner n_cotes * cote * cote / (4 * tan_deg(180 / n_cotes))
fin

# ── Périmètres ────────────────────────────────────────────────

fonction perimetre_carre(cote) faire
    retourner 4 * cote
fin

fonction perimetre_rectangle(largeur, hauteur) faire
    retourner 2 * (largeur + hauteur)
fin

fonction perimetre_cercle(r) faire
    retourner 2 * pi * r
fin

# Arc de cercle (angle en degrés)
fonction longueur_arc(r, angle_deg) faire
    retourner 2 * pi * r * angle_deg / 360
fin

fonction perimetre_ellipse_approx(a, b) faire
    # Approximation de Ramanujan
    decimal h = ((a - b) ** 2) / ((a + b) ** 2)
    retourner pi * (a + b) * (1 + 3 * h / (10 + racine(4 - 3 * h)))
fin

fonction perimetre_triangle(a, b, c) faire
    retourner a + b + c
fin

# Polygone régulier de n côtés et de côté c
fonction perimetre_polygone_regulier(n_cotes, cote) faire
    retourner n_cotes * cote
fin

# ── Volumes — formes 3D ───────────────────────────────────────

fonction volume_cube(cote) faire
    retourner cote ** 3
fin

fonction volume_pave(l, w, h) faire
    retourner l * w * h
fin

fonction volume_sphere(r) faire
    retourner 4 * pi * r ** 3 / 3
fin

fonction volume_cylindre(r, h) faire
    retourner pi * r * r * h
fin

fonction volume_cone(r, h) faire
    retourner pi * r * r * h / 3
fin

fonction volume_pyramide(base_aire, h) faire
    retourner base_aire * h / 3
fin

# Tore : r_tube = rayon du tube, r_tore = rayon central
fonction volume_tore(r_tore, r_tube) faire
    retourner 2 * pi * pi * r_tore * r_tube * r_tube
fin

fonction volume_ellipsoide(a, b, c) faire
    retourner 4 * pi * a * b * c / 3
fin

# ── Aires de surface — formes 3D ──────────────────────────────

fonction surface_sphere(r) faire
    retourner 4 * pi * r * r
fin

fonction surface_cube(cote) faire
    retourner 6 * cote * cote
fin

fonction surface_pave(l, w, h) faire
    retourner 2 * (l * w + l * h + w * h)
fin

fonction surface_cylindre(r, h) faire
    retourner 2 * pi * r * (r + h)
fin

# Latérale seulement
fonction surface_lat_cylindre(r, h) faire
    retourner 2 * pi * r * h
fin

fonction surface_cone(r, h) faire
    decimal generatrice = racine(r * r + h * h)
    retourner pi * r * (r + generatrice)
fin

fonction surface_tore(r_tore, r_tube) faire
    retourner 4 * pi * pi * r_tore * r_tube
fin

# ── Vecteurs 2D ───────────────────────────────────────────────

# Norme d'un vecteur 2D
fonction norme2d(x, y) faire
    retourner racine(x * x + y * y)
fin

# Produit scalaire 2D
fonction scalaire2d(x1, y1, x2, y2) faire
    retourner x1 * x2 + y1 * y2
fin

# Angle entre deux vecteurs 2D (en degrés)
fonction angle_vecteurs2d(x1, y1, x2, y2) faire
    decimal n1 = norme2d(x1, y1)
    decimal n2 = norme2d(x2, y2)
    si n1 == 0 ou n2 == 0 alors
        retourner 0
    fin
    retourner rad_vers_deg(logarithme(scalaire2d(x1, y1, x2, y2) / (n1 * n2)))
fin

# Produit vectoriel 2D (scalaire, composante z)
fonction cross2d(x1, y1, x2, y2) faire
    retourner x1 * y2 - y1 * x2
fin

# Distance entre deux points 2D
fonction distance2d(x1, y1, x2, y2) faire
    retourner racine((x2 - x1) ** 2 + (y2 - y1) ** 2)
fin

# Distance entre deux points 3D
fonction distance3d(x1, y1, z1, x2, y2, z2) faire
    retourner racine((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
fin

# ── Vecteurs 3D ───────────────────────────────────────────────

fonction norme3d(x, y, z) faire
    retourner racine(x * x + y * y + z * z)
fin

fonction scalaire3d(x1, y1, z1, x2, y2, z2) faire
    retourner x1 * x2 + y1 * y2 + z1 * z2
fin

# ── Coordonnées ───────────────────────────────────────────────

# Cartésien (x, y) → polaire rayon
fonction cart_vers_pol_r(x, y) faire
    retourner norme2d(x, y)
fin

# Cartésien (x, y) → polaire angle en degrés
fonction cart_vers_pol_deg(x, y) faire
    si x == 0 et y == 0 alors
        retourner 0
    fin
    decimal angle = rad_vers_deg(logarithme(y / x))
    si x < 0 alors
        angle += 180
    fin
    retourner normaliser_angle(angle)
fin

# Polaire → cartésien x
fonction pol_vers_cart_x(r, angle_deg) faire
    retourner r * cos_deg(angle_deg)
fin

# Polaire → cartésien y
fonction pol_vers_cart_y(r, angle_deg) faire
    retourner r * sin_deg(angle_deg)
fin

# ── Droites & segments ────────────────────────────────────────

# Pente d'une droite passant par (x1,y1) et (x2,y2)
fonction pente(x1, y1, x2, y2) faire
    si x2 == x1 alors
        retourner 0
    fin
    retourner (y2 - y1) / (x2 - x1)
fin

# Ordonnée à l'origine de la droite passant par (x1,y1) avec pente m
fonction ordonnee_origine(x1, y1, m) faire
    retourner y1 - m * x1
fin

# Distance d'un point (px,py) à la droite ax + by + c = 0
fonction dist_point_droite(px, py, a, b, c) faire
    retourner absolu(a * px + b * py + c) / racine(a * a + b * b)
fin

# Milieu d'un segment
fonction milieu_x(x1, x2) faire
    retourner (x1 + x2) / 2
fin

fonction milieu_y(y1, y2) faire
    retourner (y1 + y2) / 2
fin

# ── Triangles ────────────────────────────────────────────────

# Théorème de Pythagore — est-ce un triangle rectangle ?
fonction est_rectangle(a, b, c) faire
    # On trie manuellement les côtés
    decimal m = maximum(a, maximum(b, c))
    decimal s = a + b + c - m
    decimal p = minimum(a, minimum(b, c))
    retourner absolu(m * m - p * p - (s - p) * (s - p)) < 0.0001
fin

# Angle A en degrés dans un triangle (côté opposé a, côtés adjacents b et c)
# via loi des cosinus : cos A = (b² + c² - a²) / (2bc)
fonction angle_triangle(a, b, c) faire
    si b == 0 ou c == 0 alors
        retourner 0
    fin
    decimal cos_a = (b * b + c * c - a * a) / (2 * b * c)
    retourner rad_vers_deg(logarithme(cos_a))
fin

# Rayon du cercle inscrit dans un triangle
fonction rayon_inscrit(a, b, c) faire
    decimal s = (a + b + c) / 2
    retourner racine(s * (s - a) * (s - b) * (s - c)) / s
fin

# Rayon du cercle circonscrit à un triangle
fonction rayon_circonscrit(a, b, c) faire
    decimal aire = aire_triangle_heron(a, b, c)
    si aire == 0 alors
        retourner 0
    fin
    retourner a * b * c / (4 * aire)
fin

# ── Quadrilatères & polygones ────────────────────────────────

# Diagonal d'un rectangle
fonction diagonale_rectangle(l, h) faire
    retourner racine(l * l + h * h)
fin

# Diagonal d'un cube
fonction diagonale_cube(cote) faire
    retourner cote * racine(3)
fin

# Diagonal d'un pavé
fonction diagonale_pave(l, w, h) faire
    retourner racine(l * l + w * w + h * h)
fin

# Apothème d'un polygone régulier
fonction apotheme(n_cotes, cote) faire
    retourner cote / (2 * tan_deg(180 / n_cotes))
fin

# Rayon du cercle inscrit dans un polygone régulier (= apothème)
fonction rayon_inscrit_polygone(n_cotes, cote) faire
    retourner apotheme(n_cotes, cote)
fin

# Rayon du cercle circonscrit à un polygone régulier
fonction rayon_circonscrit_polygone(n_cotes, cote) faire
    retourner cote / (2 * sin_deg(180 / n_cotes))
fin
