# F++ — Le langage de programmation en Français

**F++** (Français++) est un langage de programmation compilé dont la syntaxe est entièrement en français.  
Le compilateur transpile le code F++ en C, puis invoque `gcc` pour produire un **exécutable natif**.

```
fichier.fpp  →  fppc  →  fichier.c  →  gcc  →  a.out
```

**Prérequis :** Python 3.8+, gcc

---

## Compilation

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

## Utilisation avec make

Un `Makefile` est fourni à la racine du projet :

```bash
make bonjour          # compile exemples/bonjour.fpp → ./bonjour
make run-bonjour      # compile et exécute
make voir-c-bonjour   # affiche le C généré
make clean            # supprime les binaires
```

### Makefile pour ton propre projet

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

## Mode interactif (REPL)

Un interpréteur est aussi disponible pour tester rapidement :

```bash
python3 fpp.py              # REPL interactif
python3 fpp.py script.fpp   # Interprétation directe
```

---

## Syntaxe complète

### Variables

```fpp
entier   age     = 25
decimal  taille  = 1.80
texte    prenom  = "Luc"
bool     actif   = vrai
liste    notes   = [12, 15, 18, 9]
dict     infos   = {"ville": "Paris", "pays": "France"}
const    PI      = 3.14159
```

### Affichage et saisie

```fpp
afficher("Bonjour", prenom)         # affiche plusieurs valeurs séparées par des espaces
texte    nom   = lire("Ton nom : ") # saisie texte
entier   nb    = lire_entier("Nombre : ")
decimal  prix  = lire_decimal("Prix : ")
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
# TantQue
tantque compteur < 10 faire
    afficher(compteur)
    compteur += 1
fin

# Pour (intervalle)
pour i de 1 a 10 faire
    afficher(i)
fin

# Pour avec pas
pour i de 0 a 100 pas 10 faire
    afficher(i)
fin

# Pour dans une liste
pour fruit dans fruits faire
    afficher(fruit)
fin
```

### Fonctions

```fpp
fonction saluer(prenom) faire
    retourner "Bonjour " + prenom + " !"
fin

afficher(saluer("Marie"))
```

### Opérateurs

| Opérateur | Description         |
|-----------|---------------------|
| `+`       | Addition / concat   |
| `-`       | Soustraction        |
| `*`       | Multiplication      |
| `/`       | Division            |
| `%`       | Modulo              |
| `**`      | Puissance           |
| `==`      | Égalité             |
| `!=`      | Différent           |
| `<` `>`   | Comparaisons        |
| `<=` `>=` | Comparaisons        |
| `et`      | ET logique          |
| `ou`      | OU logique          |
| `non`     | NON logique         |
| `+=` `-=` `*=` `/=` | Assignation composée |

### Méthodes des listes

```fpp
liste l = [3, 1, 2]
l.ajouter(4)          # [3, 1, 2, 4]
l.supprimer(1)        # supprime la valeur 1
l.trier()             # [2, 3, 4]
l.inverser()          # [4, 3, 2]
l.longueur()          # 3
l.contient(3)         # vrai
l.pop()               # retire et retourne le dernier
l.inserer(0, 99)      # insère 99 à l'index 0
l.compter(3)          # nombre d'occurrences de 3
l.vide()              # vrai/faux
```

### Méthodes des textes

```fpp
texte t = "  Bonjour Monde  "
t.longueur()
t.majuscule()
t.minuscule()
t.capitaliser()
t.supprimer_espaces()
t.contient("Monde")
t.remplacer("Monde", "F++")
t.diviser(" ")           # retourne une liste
t.commencer_par("Bon")
t.finir_par("de")
t.vide()
```

### Méthodes des dictionnaires

```fpp
dict d = {"a": 1, "b": 2}
d.cles()               # ["a", "b"]
d.valeurs()            # [1, 2]
d.contient("a")        # vrai
d.supprimer("a")
d.longueur()
d.vide()
```

### Fonctions intégrées

| Fonction               | Description                        |
|------------------------|------------------------------------|
| `entier(x)`            | Convertir en entier                |
| `decimal(x)`           | Convertir en décimal               |
| `texte(x)`             | Convertir en texte                 |
| `bool(x)`              | Convertir en booléen               |
| `longueur(x)`          | Taille d'une liste/texte           |
| `arrondir(x, n)`       | Arrondir à n décimales             |
| `absolu(x)`            | Valeur absolue                     |
| `minimum(a, b, ...)`   | Valeur minimale                    |
| `maximum(a, b, ...)`   | Valeur maximale                    |
| `racine(x)`            | Racine carrée                      |
| `sinus(x)`             | Sinus (radians)                    |
| `cosinus(x)`           | Cosinus (radians)                  |
| `tangente(x)`          | Tangente (radians)                 |
| `logarithme(x)`        | Logarithme naturel                 |
| `logarithme(x, base)`  | Logarithme en base donnée          |
| `plancher(x)`          | Arrondi vers le bas                |
| `plafond(x)`           | Arrondi vers le haut               |
| `intervalle(n)`        | Liste de 0 à n-1                   |
| `intervalle(a, b)`     | Liste de a à b-1                   |
| `intervalle(a, b, p)`  | Liste avec pas p                   |
| `trier(liste)`         | Retourne une liste triée           |
| `inverser(liste)`      | Retourne une liste inversée        |
| `somme(liste)`         | Somme des éléments                 |
| `type(x)`              | Retourne le type sous forme texte  |
| `hasard()`             | Décimal aléatoire entre 0 et 1     |
| `hasard(a, b)`         | Décimal aléatoire entre a et b     |
| `hasard_entier(a, b)`  | Entier aléatoire entre a et b      |
| `melanger(liste)`      | Mélange une liste                  |
| `lire_fichier(chemin)` | Lire le contenu d'un fichier texte |
| `ecrire_fichier(c, t)` | Écrire dans un fichier texte       |
| `effacer()`            | Effacer l'écran                    |

### Constantes intégrées

```fpp
pi      # 3.141592...
e       # 2.718281...
infini  # +∞
```

### Contrôle de flux

```fpp
casser      # sortir d'une boucle (break)
continuer   # passer à l'itération suivante (continue)
retourner   # retourner d'une fonction (return)
```

### Commentaires

```fpp
# Ceci est un commentaire
```

---

## Exemples

| Fichier                           | Compilation                              |
|-----------------------------------|------------------------------------------|
| `exemples/bonjour.fpp`            | `python3 fppc.py exemples/bonjour.fpp -o bonjour` |
| `exemples/fonctions.fpp`          | `python3 fppc.py exemples/fonctions.fpp -o fonctions` |
| `exemples/exemples.fpp`           | Tour complet (interpréteur recommandé)   |
| `exemples/jeu_devinette.fpp`      | Jeu interactif de devinette              |
| `exemples/calculatrice.fpp`       | Calculatrice interactive                 |

---

## Structure du projet

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
└── exemples/
    ├── bonjour.fpp
    ├── fonctions.fpp
    ├── exemples.fpp
    ├── jeu_devinette.fpp
    ├── calculatrice.fpp
    └── Makefile.exemple    ← Modèle de Makefile pour un projet F++
```

## Mots-clés réservés

Les mots suivants ne peuvent pas être utilisés comme noms de variables :

`si` `alors` `sinonsi` `sinon` `fin` `tantque` `pour` `de` `faire` `fonction`
`retourner` `casser` `continuer` `afficher` `lire` `lire_entier` `lire_decimal`
`et` `ou` `non` `vrai` `faux` `nul` `entier` `decimal` `texte` `bool` `liste`
`dict` `const`
```
