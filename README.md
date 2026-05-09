<div align="center">

# F++ — *Français++*

**Un langage de programmation compilé dont la syntaxe est entièrement en français.**

```
fichier.fpp  →  fppc  →  fichier.c  →  gcc  →  exécutable natif
```

[![Langage](https://img.shields.io/badge/syntaxe-français-blue)](#)
[![Cible](https://img.shields.io/badge/cible-C99-lightgrey)](#)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](#)

</div>

---

## Démarrage rapide

```bash
git clone https://github.com/votre-pseudo/fpp.git
cd fpp
python3 fppc.py exemples/bonjour.fpp -o bonjour
./bonjour
```

**Prérequis :** Python 3.8+, gcc

---

## Utilisation du compilateur

```bash
# Compiler → a.out
python3 fppc.py monprogramme.fpp

# Compiler avec un nom de sortie
python3 fppc.py monprogramme.fpp -o monprogramme

# Afficher le code C généré (sans compiler)
python3 fppc.py monprogramme.fpp -S

# Aide / version
python3 fppc.py --aide
python3 fppc.py --version
```

### Compilation avec make

```bash
make all              # compile tous les exemples → build/
make run-bonjour      # compile + exécute exemples/bonjour.fpp
make voir-c-bonjour   # affiche le C généré de bonjour.fpp
make re               # recompile tout depuis zéro
make fclean           # supprime binaires et fichiers .c
make liste            # liste les exemples disponibles
```

---

## Syntaxe

### Variables et types

```fpp
entier   age     = 25
decimal  taille  = 1.80
texte    prenom  = "Alice"
bool     actif   = vrai
liste    notes   = [12, 15, 18, 9]
dict     infos   = {"ville": "Paris", "pays": "France"}
const    PI      = 3.14159
```

### Affichage et saisie

```fpp
afficher("Bonjour", prenom)
texte   nom   = lire("Ton nom : ")
entier  nb    = lire_entier("Nombre : ")
decimal prix  = lire_decimal("Prix : ")
```

### Conditions

```fpp
si age >= 18 alors
    afficher("Majeur")
sinonsi age >= 13 alors
    afficher("Adolescent")
sinon
    afficher("Enfant")
fin
```

### Boucles

```fpp
# Boucle tant que
tantque compteur < 10 faire
    afficher(compteur)
    compteur += 1
fin

# Boucle pour (intervalle, avec pas optionnel)
pour i de 1 a 10 faire
    afficher(i)
fin

pour i de 0 a 100 pas 5 faire
    afficher(i)
fin

# Parcourir une liste
pour fruit dans fruits faire
    afficher(fruit)
fin
```

### Fonctions

```fpp
fonction factorielle(n) faire
    si n <= 1 alors
        retourner 1
    fin
    retourner n * factorielle(n - 1)
fin

afficher(factorielle(10))
```

### Opérateurs

| Opérateur | Description |
|-----------|-------------|
| `+` `-` `*` `/` | Arithmétique de base (+ concaténation texte) |
| `%` | Modulo (entier) |
| `**` | Puissance |
| `==` `!=` `<` `>` `<=` `>=` | Comparaisons |
| `et` `ou` `non` | Logique booléenne |
| `+=` `-=` `*=` `/=` | Assignation composée |

### Méthodes intégrées

**Listes**
```fpp
l.ajouter(v)        # ajoute en fin
l.pop()             # retire et retourne le dernier élément
l.trier()           # tri sur place
l.longueur()        # nombre d'éléments
l[i]                # accès par index (lecture/écriture)
```

**Textes**
```fpp
t.longueur()
t.majuscule()   /  t.minuscule()
t.supprimer_espaces()
t.contient("sous-texte")
t.remplacer("ancien", "nouveau")
t.diviser(" ")          # retourne une liste de textes
t.commence_par("pré")
t.finit_par("suf")
```

**Dictionnaires**
```fpp
d.cles()        # liste des clés
d.valeurs()     # liste des valeurs
d.longueur()
d["cle"]        # lecture
d["cle"] = v    # écriture
```

### Fonctions intégrées

| Catégorie | Fonctions |
|-----------|-----------|
| **Conversion** | `entier(x)` `decimal(x)` `texte(x)` `bool(x)` |
| **Math** | `absolu(x)` `racine(x)` `arrondir(x,n)` `plancher(x)` `plafond(x)` |
| **Trigo** | `sinus(x)` `cosinus(x)` `tangente(x)` |
| **Logarithme** | `logarithme(x)` `logarithme(x, base)` |
| **Listes** | `longueur(x)` `trier(l)` `inverser(l)` `somme(l)` `minimum(a,b)` `maximum(a,b)` |
| **Aléatoire** | `hasard()` `hasard(a,b)` `hasard_entier(a,b)` `melanger(l)` |
| **Fichiers** | `lire_fichier(chemin)` `ecrire_fichier(chemin, texte)` |
| **Divers** | `effacer()` `type(x)` |

### Constantes

```fpp
pi      # 3.141592653589793
e       # 2.718281828459045
infini  # +∞
```

### Contrôle de flux

```fpp
casser      # break (sortir d'une boucle)
continuer   # continue (itération suivante)
retourner   # return (sortir d'une fonction)
```

### Commentaires

```fpp
# Ceci est un commentaire
```

---

## Bibliothèques (`include/`)

F++ fournit des bibliothèques prêtes à l'emploi dans le dossier `include/`.
Pour les utiliser, ajoutez une directive `inclure` en tête de fichier :

```fpp
inclure "include/math.fpp"
inclure "include/stats.fpp"

afficher(pgcd(48, 18))           # → 6
afficher(est_premier(97))        # → 1
afficher(fibonacci_iter(30))     # → 832040
```

Les inclusions sont **récursives** (un fichier inclus peut lui-même inclure d'autres fichiers)
et **sans doublon** (chaque fichier n'est inclus qu'une seule fois même s'il est référencé plusieurs fois).

### `include/math.fpp` — Mathématiques avancées

| Fonction | Description |
|----------|-------------|
| `pgcd(a, b)` | Plus grand commun diviseur |
| `ppcm(a, b)` | Plus petit commun multiple |
| `signe(n)` | -1, 0 ou 1 |
| `est_pair(n)` / `est_impair(n)` | Parité |
| `factorielle(n)` | n! (récursif) |
| `combinaisons(n, k)` | C(n, k) |
| `permutations(n, k)` | P(n, k) |
| `est_premier(n)` | Test de primalité |
| `prochain_premier(n)` | Premier ≥ n |
| `fibonacci(n)` | Fibonacci (récursif) |
| `fibonacci_iter(n)` | Fibonacci (itératif, rapide) |
| `puissance_rapide(b, e)` | Exponentiation rapide |
| `log_base(x, b)` | Logarithme en base b |
| `clamp(v, mn, mx)` | Contraindre v dans [mn, mx] |
| `interpoler(a, b, t)` | Interpolation linéaire |
| `normaliser(v, mn, mx)` | Normaliser vers [0, 1] |
| `remapper(v, a1, b1, a2, b2)` | Remapper d'un intervalle à un autre |
| `distance(x1, y1, x2, y2)` | Distance euclidienne 2D |
| `aire_cercle(r)` | πr² |
| `aire_triangle(a, b, c)` | Formule de Héron |
| `hypotenuse(a, b)` | √(a²+b²) |
| `deg_vers_rad(d)` / `rad_vers_deg(r)` | Conversion d'angles |

### `include/stats.fpp` — Statistiques

| Fonction | Description |
|----------|-------------|
| `somme(lst)` | Σxi |
| `produit(lst)` | Πxi |
| `min_liste(lst)` / `max_liste(lst)` | Extrêmes |
| `index_min(lst)` / `index_max(lst)` | Index des extrêmes |
| `etendue(lst)` | max − min |
| `moyenne(lst)` | Moyenne arithmétique |
| `mediane(lst)` | Médiane (trie en place) |
| `moyenne_harmonique(lst)` | Moyenne harmonique |
| `moyenne_geometrique(lst)` | Moyenne géométrique |
| `variance(lst)` | Variance population |
| `variance_echantillon(lst)` | Variance échantillon (n−1) |
| `ecart_type(lst)` | Écart-type population |
| `ecart_type_echantillon(lst)` | Écart-type échantillon |
| `ecart_absolu_moyen(lst)` | Écart absolu moyen |
| `percentile(lst, p)` | p-ième percentile |
| `q1(lst)` / `q3(lst)` / `iqr(lst)` | Quartiles et IQR |
| `coef_variation(lst)` | CV en % |
| `compter_sup(lst, s)` | Valeurs > seuil |
| `compter_inf(lst, s)` | Valeurs < seuil |
| `compter_entre(lst, a, b)` | Valeurs dans [a, b] |
| `normaliser_liste(lst)` | Normalisation min-max (en place) |
| `centrer_reduire(lst)` | Z-score (en place) |

### `include/conversion.fpp` — Conversions d'unités

Températures, distances, masses, volumes, surfaces, vitesses, énergie, pression, temps, données, angles — plus de 50 fonctions de conversion.

```fpp
inclure "include/conversion.fpp"

afficher(celsius_vers_fahrenheit(100))   # → 212
afficher(km_vers_miles(42.195))          # → 26.218...
afficher(kg_vers_livres(70))             # → 154.32...
```

### `include/algo.fpp` — Algorithmes

| Fonction | Description |
|----------|-------------|
| `recherche(lst, v)` | Recherche linéaire → index ou -1 |
| `recherche_binaire(lst, v)` | Recherche binaire (liste triée) → index ou -1 |
| `contient_valeur(lst, v)` | Présence d'une valeur |
| `compter_occurrences(lst, v)` | Nombre d'occurrences |
| `tri_bulles(lst)` | Tri à bulles (en place) |
| `tri_insertion(lst)` | Tri par insertion (en place) |
| `tri_selection(lst)` | Tri par sélection (en place) |
| `est_triee(lst)` | Vérifie l'ordre croissant |
| `decaler(lst, delta)` | Ajouter delta à chaque élément |
| `echelonner(lst, f)` | Multiplier par f |
| `absolus(lst)` | Valeur absolue de chaque élément |
| `puissances(lst, p)` | Élever chaque élément à la puissance p |
| `fenetre_somme(lst, i, w)` | Somme d'une fenêtre glissante |
| `fenetre_moyenne(lst, i, w)` | Moyenne d'une fenêtre glissante |
| `remplir_arithmetique(lst, d, p)` | Suite arithmétique en place |
| `remplir_geometrique(lst, d, r)` | Suite géométrique en place |
| `rotation_gauche(lst, k)` | Rotation circulaire à gauche |
| `rotation_droite(lst, k)` | Rotation circulaire à droite |

### `include/texte.fpp` — Traitement de texte

| Fonction | Description |
|----------|-------------|
| `compter_mots(t)` | Nombre de mots (séparés par espaces) |
| `est_vide_ou_espace(t)` | Texte vide ou blanc |
| `compter_sous_texte(t, s)` | Occurrences d'un sous-texte |
| `afficher_titre(titre)` | Affiche un titre encadré |
| `afficher_separateur(n, c)` | Affiche n fois le caractère c |
| `compter_voyelles(t)` | Nombre de voyelles |
| `compter_consonnes(t)` | Nombre de consonnes |
| `longueur_mot_max(phrase)` | Longueur du mot le plus long |
| `longueur_mot_min(phrase)` | Longueur du mot le plus court |
| `longueur_mots_moyenne(phrase)` | Longueur moyenne des mots |

### `include/finance.fpp` — Finance & mathématiques financières

| Fonction | Description |
|----------|-------------|
| `interet_simple(C, t, d)` | Intérêt simple |
| `capital_compose(C, t, n)` | Capital avec intérêts composés |
| `mensualite(C, t_mensuel, n)` | Mensualité d'un emprunt |
| `cout_total_emprunt(C, t, n)` | Coût total du crédit |
| `capital_restant(C, t, n, k)` | Capital restant dû après k mois |
| `van(taux, flux)` | Valeur actuelle nette (VAN) |
| `roi(gain, cout)` | Retour sur investissement (ROI %) |
| `cagr(debut, fin, annees)` | Taux de croissance annuel composé |
| `payback(investissement, flux_annuel)` | Durée de retour sur investissement |
| `seuil_rentabilite(fixes, prix_u, var_u)` | Seuil de rentabilité (unités) |
| `per(prix_action, bna)` | Price-Earning Ratio |
| `sharpe(rendement, taux_sans_risque, volatilite)` | Ratio de Sharpe |
| `impot_4_tranches(revenu, s1, t1, s2, t2, s3, t3, t4)` | Impôt à 4 tranches |
| `ht_vers_ttc(ht, tva_pct)` / `ttc_vers_ht(ttc, tva_pct)` | Conversion HT ↔ TTC |
| `variation_pct(ancienne, nouvelle)` | Variation en % |
| *+ 25 autres fonctions* | Rentes, levier, volatilité, rendement… |

### `include/geometrie.fpp` — Géométrie

| Fonction | Description |
|----------|-------------|
| `aire_rectangle(l, h)` / `perimetre_rectangle(l, h)` | Rectangle |
| `aire_triangle_heron(a, b, c)` | Triangle par les 3 côtés (Héron) |
| `aire_ellipse(a, b)` / `perimetre_ellipse_approx(a, b)` | Ellipse (Ramanujan) |
| `aire_trapeze(b1, b2, h)` / `aire_losange(d1, d2)` | Trapèze, losange |
| `aire_polygone_regulier(n, c)` / `perimetre_polygone_regulier(n, c)` | Polygone régulier |
| `volume_sphere(r)` / `surface_sphere(r)` | Sphère |
| `volume_cylindre(r, h)` / `surface_cylindre(r, h)` | Cylindre |
| `volume_cone(r, h)` / `surface_cone(r, h)` | Cône |
| `volume_tore(R, r)` / `surface_tore(R, r)` | Tore |
| `volume_ellipsoide(a, b, c)` | Ellipsoïde |
| `norme2d(x, y)` / `norme3d(x, y, z)` | Norme de vecteur |
| `scalaire2d(...)` / `scalaire3d(...)` | Produit scalaire |
| `distance2d(x1, y1, x2, y2)` / `distance3d(...)` | Distance euclidienne |
| `cart_vers_pol_r(x, y)` / `cart_vers_pol_deg(x, y)` | Coordonnées polaires |
| `pente(x1, y1, x2, y2)` | Pente d'une droite |
| `dist_point_droite(px, py, a, b, c)` | Distance point-droite |
| `angle_triangle(a, b, c)` | Angle via loi des cosinus |
| `rayon_inscrit(a, b, c)` / `rayon_circonscrit(a, b, c)` | Cercles inscrit/circonscrit |
| `sin_deg(d)` / `cos_deg(d)` / `tan_deg(d)` | Trigonométrie en degrés |
| `deg_vers_rad(d)` / `rad_vers_deg(r)` | Conversion d'angles |
| *+ 15 autres fonctions* | Apothème, diagonales, secteurs, rotations… |

### `include/jeux.fpp` — Jeux & aléatoire

| Fonction | Description |
|----------|-------------|
| `lancer_de(n)` | Dé à n faces |
| `lancer_des(n, f)` | Somme de n dés à f faces |
| `lancer_des_drop_low(n, f)` | n dés, retire le plus bas (DnD) |
| `prob_de_sup_egal(n, k)` | Probabilité d'obtenir ≥ k |
| `esperance_de(n)` | Espérance d'un dé |
| `valeur_blackjack(carte)` | Valeur d'une carte au blackjack |
| `binomiale(n, k, p)` | Probabilité de la loi binomiale |
| `esperance_binomiale(n, p)` / `variance_binomiale(n, p)` | Loi binomiale |
| `xp_vers_niveau(xp, base)` / `niveau_vers_xp(niv, base)` | Système XP/niveau |
| `score_normalise(v, min, max)` | Score en % |
| `terrain_aleatoire(p_eau, p_plaine, p_foret)` | Génération de terrain |
| `position_y(y0, vy0, g, t)` / `vitesse_y(vy0, g, t)` | Physique de saut |
| `calculer_degats(min, max, armure_pct)` | Dégâts avec armure |
| `est_critique(prob_crit_pct)` | Coup critique ? |
| `appliquer_soin(hp, hp_max, soin)` / `appliquer_degats(hp, dmg)` | Points de vie |
| `cooldown_restant(tour, tour_util, duree)` | Cooldown en tours |

### `include/bits.fpp` — Manipulation de bits

| Fonction | Description |
|----------|-------------|
| `bit_et(a, b)` / `bit_ou(a, b)` / `bit_xor(a, b)` | AND / OR / XOR |
| `bit_non(a, n_bits)` | NOT sur n bits |
| `bit_shl(a, k)` / `bit_shr(a, k)` | Décalages gauche / droite |
| `bit_valeur(n, k)` | Valeur du bit k |
| `bit_set(n, k)` / `bit_clear(n, k)` / `bit_toggle(n, k)` | Set / Clear / Toggle |
| `compter_bits_1(n)` | Poids de Hamming (popcount) |
| `est_puissance_de_2(n)` | Vérification puissance de 2 |
| `prochain_puissance_2(n)` | Prochaine puissance de 2 ≥ n |
| `bit_longueur(n)` | ⌊log₂(n)⌋ |
| `distance_hamming(a, b)` | Distance de Hamming |
| `rotate_left(v, k, n)` / `rotate_right(v, k, n)` | Rotation circulaire |
| `masque_bits(k, n)` | Masque de n bits à partir du bit k |
| `extraire_bits(v, k, n)` / `inserer_bits(v, k, n, val)` | Champs de bits |
| `checksum_xor(lst)` / `checksum_somme(lst)` | Checksums |
| `est_mersenne(n)` | Nombre de Mersenne ? |
| `parite(n)` / `bit_parite_paire(n)` | Parité |

### `include/matrice.fpp` — Matrices & vecteurs

Une matrice N×M est représentée comme une liste plate de N×M éléments, rangée ligne par ligne.
Accès à l'élément (i, j) : `mat_get(mat, i, j, ncols)` ou indice `i * ncols + j`.

| Fonction | Description |
|----------|-------------|
| `mat_zeros(nl, nc)` | Matrice nulle |
| `mat_identite(n)` | Matrice identité n×n |
| `mat_remplir(nl, nc, v)` | Matrice remplie d'une valeur |
| `mat_get(mat, i, j, nc)` | Lecture d'un élément |
| `mat_trace(mat, n)` | Trace d'une matrice carrée |
| `mat_det2_liste(mat)` | Déterminant 2×2 |
| `mat_det3(mat)` | Déterminant 3×3 |
| `mat_additionner(a, b)` / `mat_soustraire(a, b)` | Addition / Soustraction |
| `mat_scalaire(mat, k)` | Multiplication par un scalaire |
| `mat_transposee(mat, nl, nc)` | Transposée |
| `mat_multiplier(a, b, nla, nca, ncb)` | Multiplication matricielle |
| `mat_ligne(mat, i, nc)` / `mat_colonne(mat, j, nl, nc)` | Extraction ligne/colonne |
| `systeme2x2_x(...)` / `systeme2x2_y(...)` | Résolution système 2×2 (Cramer) |
| `vec_scalaire(u, v)` | Produit scalaire |
| `vec_norme(u)` / `vec_normaliser(u)` | Norme et normalisation |
| `vec_additionner(u, v)` / `vec_soustraire(u, v)` | Opérations vectorielles |
| `vec_distance(u, v)` | Distance euclidienne |

### `include/date.fpp` — Calculs de dates

Les dates sont au format `AAAAMMJJ` (ex : `20240315` = 15 mars 2024).

| Fonction | Description |
|----------|-------------|
| `date_annee(d)` / `date_mois(d)` / `date_jour(d)` | Extraction des composantes |
| `creer_date(a, m, j)` | Construire une date |
| `est_bissextile(annee)` | Année bissextile ? |
| `jours_dans_mois(mois, annee)` | Jours dans un mois |
| `jour_de_annee(date)` | Numéro du jour dans l'année (1-366) |
| `diff_jours(d1, d2)` | Différence en jours |
| `diff_semaines(d1, d2)` / `diff_mois(d1, d2)` / `diff_annees(d1, d2)` | Différences |
| `jour_semaine(date)` | Jour (0=Dim … 6=Sam), algorithme de Zeller |
| `est_weekend(date)` / `est_ouvrable(date)` | Fin de semaine ? |
| `numero_semaine(date)` | Numéro de semaine dans l'année |
| `ajouter_jours(date, n)` | Ajouter n jours (n peut être négatif) |
| `ajouter_mois(date, n)` / `ajouter_annees(date, n)` | Ajout de mois/années |
| `date_avant(d1, d2)` / `date_apres(d1, d2)` / `date_egale(d1, d2)` | Comparaison |
| `date_valide(date)` | Validation d'une date |
| `trimestre(date)` / `semestre(date)` | Période |
| `age_annees(date_naissance, date_ref)` | Âge en années révolues |
| `afficher_date(date)` | Affiche au format JJ/MM/AAAA |

---

## Exemples inclus

| Fichier | Description |
|---------|-------------|
| `exemples/bonjour.fpp` | Hello World, variables, affichage |
| `exemples/fonctions.fpp` | Fonctions, récursivité, factorielle, Fibonacci |
| `exemples/exemples.fpp` | Tour complet : listes, dict, boucles, texte |
| `exemples/jeu_devinette.fpp` | Jeu interactif de devinette |
| `exemples/calculatrice.fpp` | Calculatrice interactive (+, -, *, /, %, **) |

---

## Utiliser F++ dans votre propre projet

### Makefile minimal

```makefile
FPPC = python3 /chemin/vers/F++/fppc.py

all: monprog

monprog: main.fpp
	$(FPPC) main.fpp -o monprog

run: monprog
	./monprog

clean:
	rm -f monprog

.PHONY: all run clean
```

### Exemple complet utilisant les bibliothèques

```fpp
inclure "include/math.fpp"
inclure "include/stats.fpp"
inclure "include/conversion.fpp"

# Mathématiques
afficher("pgcd(48, 18) =", pgcd(48, 18))
afficher("est_premier(97) =", est_premier(97))
afficher("fibonacci(10) =", fibonacci_iter(10))

# Statistiques
liste notes = [12, 15, 8, 18, 10, 14, 16]
afficher("Moyenne :", moyenne(notes))
afficher("Ecart-type :", ecart_type(notes))
afficher("Mediane :", mediane(notes))

# Conversions
afficher("100 C en F :", celsius_vers_fahrenheit(100))
afficher("Marathon en miles :", km_vers_miles(42.195))
```

---

## Architecture du projet

```
F++/
├── fppc.py                 ← Compilateur F++ (fppc)
├── fpp.py                  ← Interpréteur / REPL
├── Makefile                ← Makefile du projet
├── fpp/
│   ├── __init__.py
│   ├── lexer.py            ← Tokeniseur
│   ├── ast_noeuds.py       ← Nœuds de l'AST
│   ├── parser.py           ← Analyseur syntaxique
│   ├── codegen.py          ← Générateur de code C + runtime embarqué
│   └── interpreteur.py     ← Évaluateur (mode REPL)
├── include/
│   ├── math.fpp            ← Mathématiques avancées
│   ├── stats.fpp           ← Statistiques descriptives
│   ├── conversion.fpp      ← Conversions d'unités (50+ fonctions)
│   ├── algo.fpp            ← Algorithmes (tri, recherche, fenêtres)
│   ├── texte.fpp           ← Traitement de texte
│   ├── finance.fpp         ← Finance & mathématiques financières
│   ├── geometrie.fpp       ← Géométrie 2D/3D & vecteurs
│   ├── jeux.fpp            ← Jeux, aléatoire & physique
│   ├── bits.fpp            ← Manipulation de bits & bases
│   ├── matrice.fpp         ← Matrices & vecteurs
│   └── date.fpp            ← Calculs sur les dates (AAAAMMJJ)
└── exemples/
    ├── bonjour.fpp
    ├── fonctions.fpp
    ├── exemples.fpp
    ├── jeu_devinette.fpp
    ├── calculatrice.fpp
    └── Makefile.exemple    ← Modèle de Makefile pour un projet F++
```

---

## Mode interactif (REPL)

```bash
python3 fpp.py              # REPL interactif
python3 fpp.py script.fpp   # Interprétation directe d'un fichier
```

---

## Contribuer

Les contributions sont les bienvenues !

- Nouvelles fonctions dans les bibliothèques `include/`
- Nouveaux exemples dans `exemples/`
- Amélioration du compilateur (`fpp/codegen.py`, `fpp/parser.py`)
- Support de nouveaux types (matrices, ensembles…)
- Optimisations du code C généré

---

<div align="center">
<i>Fait avec ❤️ pour apprendre la programmation en français.</i>
</div>
