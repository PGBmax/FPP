# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque mathématique
#  inclure "include/math.fpp"
# ══════════════════════════════════════════════════════════════

# ── Arithmétique de base ─────────────────────────────────────

# Plus grand commun diviseur (algorithme d'Euclide)
fonction pgcd(a, b) faire
    tantque b != 0 faire
        decimal tmp = b
        b = a % b
        a = tmp
    fin
    retourner absolu(a)
fin

# Plus petit commun multiple
fonction ppcm(a, b) faire
    retourner absolu(a * b) / pgcd(a, b)
fin

# Signe d'un nombre : -1, 0 ou 1
fonction signe(n) faire
    si n > 0 alors
        retourner 1
    fin
    si n < 0 alors
        retourner -1
    fin
    retourner 0
fin

# Vérifie si un entier est pair
fonction est_pair(n) faire
    retourner n % 2 == 0
fin

# Vérifie si un entier est impair
fonction est_impair(n) faire
    retourner n % 2 != 0
fin

# Somme des chiffres d'un entier positif
fonction somme_chiffres(n) faire
    decimal s = 0
    tantque n > 0 faire
        s += n % 10
        n = plancher(n / 10)
    fin
    retourner s
fin

# Inverse les chiffres d'un entier (ex: 123 → 321)
fonction inverser_entier(n) faire
    decimal inv = 0
    tantque n > 0 faire
        inv = inv * 10 + n % 10
        n = plancher(n / 10)
    fin
    retourner inv
fin

# Vérifie si un entier est un palindrome (ex: 121, 1331)
fonction est_palindrome_entier(n) faire
    retourner n == inverser_entier(n)
fin

# ── Combinatoire ──────────────────────────────────────────────

# Factorielle de n (n >= 0)
fonction factorielle(n) faire
    si n <= 1 alors
        retourner 1
    fin
    retourner n * factorielle(n - 1)
fin

# Nombre de combinaisons C(n, k) = n! / (k! * (n-k)!)
fonction combinaisons(n, k) faire
    si k == 0 ou k == n alors
        retourner 1
    fin
    si k > n alors
        retourner 0
    fin
    retourner combinaisons(n - 1, k - 1) + combinaisons(n - 1, k)
fin

# Nombre de permutations P(n, k) = n! / (n-k)!
fonction permutations(n, k) faire
    retourner factorielle(n) / factorielle(n - k)
fin

# ── Nombres premiers ──────────────────────────────────────────

# Vérifie si un entier est premier
fonction est_premier(n) faire
    si n < 2 alors
        retourner 0
    fin
    si n == 2 alors
        retourner 1
    fin
    si n % 2 == 0 alors
        retourner 0
    fin
    pour i de 3 a racine(n) pas 2 faire
        si n % i == 0 alors
            retourner 0
        fin
    fin
    retourner 1
fin

# Prochain nombre premier supérieur ou égal à n
fonction prochain_premier(n) faire
    si n <= 2 alors
        retourner 2
    fin
    si est_pair(n) alors
        n += 1
    fin
    tantque est_premier(n) == 0 faire
        n += 2
    fin
    retourner n
fin

# ── Suite de Fibonacci ────────────────────────────────────────

# n-ième terme de la suite de Fibonacci (récursif)
fonction fibonacci(n) faire
    si n <= 1 alors
        retourner n
    fin
    retourner fibonacci(n - 1) + fibonacci(n - 2)
fin

# n-ième terme de Fibonacci (itératif, plus rapide)
fonction fibonacci_iter(n) faire
    si n <= 1 alors
        retourner n
    fin
    decimal a = 0
    decimal b = 1
    pour i de 2 a n faire
        decimal tmp = a + b
        a = b
        b = tmp
    fin
    retourner b
fin

# ── Puissances & logarithmes ──────────────────────────────────

# Puissance entière rapide (exponentiation rapide)
fonction puissance_rapide(base, exp) faire
    si exp == 0 alors
        retourner 1
    fin
    si est_pair(exp) alors
        decimal demi = puissance_rapide(base, exp / 2)
        retourner demi * demi
    fin
    retourner base * puissance_rapide(base, exp - 1)
fin

# Logarithme en base b de x
fonction log_base(x, b) faire
    retourner logarithme(x) / logarithme(b)
fin

# ── Interpolation & contrainte ────────────────────────────────

# Contraindre v entre mn et mx
fonction clamp(v, mn, mx) faire
    si v < mn alors
        retourner mn
    fin
    si v > mx alors
        retourner mx
    fin
    retourner v
fin

# Interpolation linéaire : a + t * (b - a), t dans [0, 1]
fonction interpoler(a, b, t) faire
    retourner a + (b - a) * t
fin

# Normaliser v depuis [mn, mx] vers [0, 1]
fonction normaliser(v, mn, mx) faire
    si mx == mn alors
        retourner 0
    fin
    retourner (v - mn) / (mx - mn)
fin

# Mapper v depuis [a1, b1] vers [a2, b2]
fonction remapper(v, a1, b1, a2, b2) faire
    retourner a2 + (v - a1) * (b2 - a2) / (b1 - a1)
fin

# ── Géométrie ─────────────────────────────────────────────────

# Distance euclidienne entre (x1,y1) et (x2,y2)
fonction distance(x1, y1, x2, y2) faire
    retourner racine((x2 - x1) ** 2 + (y2 - y1) ** 2)
fin

# Aire d'un cercle
fonction aire_cercle(r) faire
    retourner pi * r * r
fin

# Périmètre d'un cercle
fonction perimetre_cercle(r) faire
    retourner 2 * pi * r
fin

# Aire d'un triangle (formule de Héron)
fonction aire_triangle(a, b, c) faire
    decimal s = (a + b + c) / 2
    retourner racine(s * (s - a) * (s - b) * (s - c))
fin

# Hypoténuse (théorème de Pythagore)
fonction hypotenuse(a, b) faire
    retourner racine(a * a + b * b)
fin
