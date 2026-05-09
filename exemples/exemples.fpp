# ══════════════════════════════════════════════════════
#  exemples.fpp — Programme de démonstration F++
#  Couvre: variables, conditions, boucles, fonctions,
#          listes, dicts, entrée/sortie, maths, texte
# ══════════════════════════════════════════════════════

# ── 1. Variables et types ─────────────────────────────
entier age = 20
decimal taille = 1.75
texte prenom = "Marie"
bool etudiant = vrai
const LANGUE = "Français"

afficher("=== Variables ===")
afficher("Prénom :", prenom)
afficher("Âge :", age)
afficher("Taille :", taille, "m")
afficher("Étudiant :", etudiant)
afficher("Langue :", LANGUE)

# ── 2. Calculs ────────────────────────────────────────
afficher("")
afficher("=== Calculs ===")
entier a = 15
entier b = 4
afficher("a + b =", a + b)
afficher("a - b =", a - b)
afficher("a * b =", a * b)
afficher("a / b =", a / b)
afficher("a % b =", a % b)
afficher("a ** b =", a ** b)
afficher("racine(144) =", racine(144))
afficher("arrondir(3.14159, 2) =", arrondir(3.14159, 2))
afficher("absolu(-42) =", absolu(-42))

# ── 3. Conditions ─────────────────────────────────────
afficher("")
afficher("=== Conditions ===")
entier note = 14

si note >= 16 alors
    afficher("Mention : Très Bien")
sinonsi note >= 14 alors
    afficher("Mention : Bien")
sinonsi note >= 12 alors
    afficher("Mention : Assez Bien")
sinonsi note >= 10 alors
    afficher("Mention : Passable")
sinon
    afficher("Mention : Insuffisant")
fin

# ── 4. Boucle tantque ────────────────────────────────
afficher("")
afficher("=== Boucle TantQue ===")
entier compteur = 1
tantque compteur <= 5 faire
    afficher("Compteur :", compteur)
    compteur += 1
fin

# ── 5. Boucle pour (intervalle) ──────────────────────
afficher("")
afficher("=== Boucle Pour ===")
pour i de 1 a 5 faire
    afficher("i =", i)
fin

# ── 6. Boucle pour avec pas ──────────────────────────
afficher("")
afficher("=== Table de 3 ===")
pour n de 3 a 30 pas 3 faire
    afficher(n)
fin

# ── 7. Listes ─────────────────────────────────────────
afficher("")
afficher("=== Listes ===")
liste fruits = ["pomme", "banane", "cerise", "datte"]
afficher("Fruits :", fruits)
afficher("Longueur :", fruits.longueur())
fruits.ajouter("figue")
afficher("Après ajout :", fruits)
afficher("Premier :", fruits[0])
afficher("Dernier :", fruits[fruits.longueur() - 1])

# Parcourir une liste
afficher("Parcours :")
pour fruit dans fruits faire
    afficher(" -", fruit)
fin

fruits.trier()
afficher("Trié :", fruits)

# ── 8. Dictionnaires ──────────────────────────────────
afficher("")
afficher("=== Dictionnaires ===")
dict personne = {"nom": "Alice", "age": 25, "ville": "Paris"}
afficher("Nom :", personne["nom"])
afficher("Âge :", personne["age"])
personne["profession"] = "Développeuse"
afficher("Clés :", personne.cles())
afficher("Valeurs :", personne.valeurs())

# ── 9. Fonctions ──────────────────────────────────────
afficher("")
afficher("=== Fonctions ===")

fonction factorielle(n) faire
    si n <= 1 alors
        retourner 1
    fin
    retourner n * factorielle(n - 1)
fin

fonction est_pair(nombre) faire
    retourner nombre % 2 == 0
fin

fonction maximum_liste(lst) faire
    entier max = lst[0]
    pour val dans lst faire
        si val > max alors
            max = val
        fin
    fin
    retourner max
fin

afficher("5! =", factorielle(5))
afficher("10! =", factorielle(10))
afficher("8 est pair :", est_pair(8))
afficher("7 est pair :", est_pair(7))

liste nombres = [3, 1, 4, 1, 5, 9, 2, 6]
afficher("Max de", nombres, "=", maximum_liste(nombres))

# ── 10. Manipulation de texte ─────────────────────────
afficher("")
afficher("=== Texte ===")
texte phrase = "  Bonjour le Monde  "
afficher("Original :", phrase)
afficher("Majuscule :", phrase.majuscule())
afficher("Minuscule :", phrase.minuscule())
afficher("Sans espaces :", phrase.supprimer_espaces())
afficher("Longueur :", phrase.longueur())
afficher("Contient 'Monde' :", phrase.contient("Monde"))
texte nouveau = phrase.remplacer("Monde", "F++")
afficher("Remplacé :", nouveau.supprimer_espaces())

# ── 11. Mathématiques avancées ───────────────────────
afficher("")
afficher("=== Maths avancées ===")
afficher("pi =", pi)
afficher("sin(0) =", sinus(0))
afficher("cos(0) =", cosinus(0))
afficher("log(e) =", logarithme(e))
afficher("plancher(3.9) =", plancher(3.9))
afficher("plafond(3.1) =", plafond(3.1))

# ── 12. Génération aléatoire ─────────────────────────
afficher("")
afficher("=== Aléatoire ===")
entier resultat_de = hasard_entier(1, 6)
afficher("Résultat du dé (1-6) :", resultat_de)
decimal chance = arrondir(hasard(), 4)
afficher("Nombre aléatoire (0-1) :", chance)

# ── 13. Casser / Continuer ───────────────────────────
afficher("")
afficher("=== Casser / Continuer ===")
afficher("Nombres pairs de 1 à 10 :")
pour i de 1 a 10 faire
    si i % 2 != 0 alors
        continuer
    fin
    afficher(i)
fin

afficher("Cherche le premier multiple de 7 > 20 :")
entier x = 21
tantque vrai faire
    si x % 7 == 0 alors
        afficher("Trouvé :", x)
        casser
    fin
    x += 1
fin

afficher("")
afficher("=== Programme terminé ! ===")
