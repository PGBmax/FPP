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
│   ├── math.fpp            ← Bibliothèque mathématique
│   ├── stats.fpp           ← Bibliothèque statistique
│   ├── conversion.fpp      ← Conversions d'unités
│   ├── algo.fpp            ← Algorithmes (tri, recherche)
│   └── texte.fpp           ← Traitement de texte
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
