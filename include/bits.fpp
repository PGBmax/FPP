# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque de manipulation de bits & bases numériques
#  inclure "include/bits.fpp"
#
#  Opérations bit-à-bit, conversion de bases, encodage.
#  Toutes les valeurs sont des entiers (lonng long).
# ══════════════════════════════════════════════════════════════

# ── Opérations bit-à-bit basiques ────────────────────────────

# ET bit-à-bit
fonction bit_et(a, b) faire
    decimal r = 0
    decimal bit = 1
    pour i de 0 a 62 faire
        decimal ba = plancher(a / bit) % 2
        decimal bb = plancher(b / bit) % 2
        si ba == 1 et bb == 1 alors
            r += bit
        fin
        bit *= 2
    fin
    retourner r
fin

# OU bit-à-bit
fonction bit_ou(a, b) faire
    decimal r = 0
    decimal bit = 1
    pour i de 0 a 62 faire
        decimal ba = plancher(a / bit) % 2
        decimal bb = plancher(b / bit) % 2
        si ba == 1 ou bb == 1 alors
            r += bit
        fin
        bit *= 2
    fin
    retourner r
fin

# OU exclusif bit-à-bit (XOR)
fonction bit_xor(a, b) faire
    decimal r = 0
    decimal bit = 1
    pour i de 0 a 62 faire
        decimal ba = plancher(a / bit) % 2
        decimal bb = plancher(b / bit) % 2
        si ba != bb alors
            r += bit
        fin
        bit *= 2
    fin
    retourner r
fin

# NON bit-à-bit sur n bits (complément à 2, n bits)
fonction bit_non(a, n_bits) faire
    decimal max_val = (2 ** n_bits) - 1
    retourner max_val - a
fin

# Décalage à gauche de k bits (équivalent à * 2^k)
fonction bit_shl(a, k) faire
    retourner a * (2 ** k)
fin

# Décalage à droite de k bits (équivalent à plancher(a / 2^k))
fonction bit_shr(a, k) faire
    retourner plancher(a / (2 ** k))
fin

# ── Inspection des bits ───────────────────────────────────────

# Valeur du bit numéro k (0 = bit de poids faible)
fonction bit_valeur(n, k) faire
    retourner plancher(n / (2 ** k)) % 2
fin

# Mettre le bit k à 1
fonction bit_set(n, k) faire
    retourner bit_ou(n, 2 ** k)
fin

# Mettre le bit k à 0
fonction bit_clear(n, k) faire
    decimal masque = bit_non(2 ** k, 64)
    retourner bit_et(n, masque)
fin

# Inverser le bit k
fonction bit_toggle(n, k) faire
    retourner bit_xor(n, 2 ** k)
fin

# Compter le nombre de bits à 1 (poids de Hamming)
fonction compter_bits_1(n) faire
    decimal count = 0
    decimal v = n
    tantque v > 0 faire
        si v % 2 == 1 alors
            count += 1
        fin
        v = plancher(v / 2)
    fin
    retourner count
fin

# Vérifier si n est une puissance de 2
fonction est_puissance_de_2(n) faire
    si n <= 0 alors
        retourner 0
    fin
    retourner bit_et(n, n - 1) == 0
fin

# Prochaine puissance de 2 >= n
fonction prochain_puissance_2(n) faire
    si n <= 1 alors
        retourner 1
    fin
    decimal p = 1
    tantque p < n faire
        p *= 2
    fin
    retourner p
fin

# Indice du bit de poids fort (floor(log2(n)))
fonction bit_longueur(n) faire
    si n <= 0 alors
        retourner 0
    fin
    decimal count = 0
    decimal v = n
    tantque v > 1 faire
        v = plancher(v / 2)
        count += 1
    fin
    retourner count
fin

# Distance de Hamming entre deux entiers
fonction distance_hamming(a, b) faire
    retourner compter_bits_1(bit_xor(a, b))
fin

# ── Conversion de bases ───────────────────────────────────────

# Inverser un nombre en base b (ex: 123 base 10 → 321 base 10)
fonction inverser_base(n, base) faire
    decimal r = 0
    tantque n > 0 faire
        r = r * base + n % base
        n = plancher(n / base)
    fin
    retourner r
fin

# Somme des chiffres en base b
fonction somme_chiffres_base(n, base) faire
    decimal s = 0
    tantque n > 0 faire
        s += n % base
        n = plancher(n / base)
    fin
    retourner s
fin

# Nombre de chiffres en base b
fonction nb_chiffres_base(n, base) faire
    si n == 0 alors
        retourner 1
    fin
    decimal count = 0
    decimal v = n
    tantque v > 0 faire
        count += 1
        v = plancher(v / base)
    fin
    retourner count
fin

# k-ième chiffre de n en base b (0 = chiffre des unités)
fonction chiffre_en_base(n, base, k) faire
    retourner plancher(n / (base ** k)) % base
fin

# ── Encodage & hachage simples ────────────────────────────────

# XOR simple de deux valeurs (chiffrement symétrique minimal)
fonction xor_chiffrer(valeur, cle) faire
    retourner bit_xor(valeur, cle)
fin

# Parité d'un entier (0 = pair, 1 = impair)
fonction parite(n) faire
    retourner compter_bits_1(n) % 2
fin

# Bit de parité paire (valeur à ajouter pour que le nb de 1 soit pair)
fonction bit_parite_paire(n) faire
    retourner parite(n)
fin

# Rotation circulaire à gauche sur n_bits bits
fonction rotate_left(val, k, n_bits) faire
    decimal masque = (2 ** n_bits) - 1
    k = k % n_bits
    decimal gauche = bit_et(bit_shl(val, k), masque)
    decimal droite = bit_shr(val, n_bits - k)
    retourner bit_ou(gauche, droite)
fin

# Rotation circulaire à droite sur n_bits bits
fonction rotate_right(val, k, n_bits) faire
    retourner rotate_left(val, n_bits - k % n_bits, n_bits)
fin

# ── Codes de correction d'erreur (simplifié) ──────────────────

# Checksum XOR d'une liste d'entiers
fonction checksum_xor(liste_vals) faire
    decimal cs = 0
    pour v dans liste_vals faire
        cs = bit_xor(cs, v)
    fin
    retourner cs
fin

# Checksum somme modulo 256
fonction checksum_somme(liste_vals) faire
    decimal s = 0
    pour v dans liste_vals faire
        s += v
    fin
    retourner s % 256
fin

# ── Masques ───────────────────────────────────────────────────

# Masque de n bits à partir du bit k
fonction masque_bits(k, n) faire
    retourner ((2 ** n) - 1) * (2 ** k)
fin

# Extraire n bits à partir du bit k dans val
fonction extraire_bits(val, k, n) faire
    retourner plancher(val / (2 ** k)) % (2 ** n)
fin

# Insérer une valeur de n bits à la position k dans val
fonction inserer_bits(val, k, n, valeur_a_inserer) faire
    decimal masque = masque_bits(k, n)
    decimal efface = bit_et(val, bit_non(masque, 64))
    retourner bit_ou(efface, bit_shl(valeur_a_inserer % (2 ** n), k))
fin

# ── Nombres remarquables ──────────────────────────────────────

# Vérifie si n est un nombre de Mersenne (2^k - 1)
fonction est_mersenne(n) faire
    si n <= 0 alors
        retourner 0
    fin
    retourner est_puissance_de_2(n + 1)
fin

# Complément à 2 sur n_bits (entier négatif en représentation binaire)
fonction complement_a_2(n, n_bits) faire
    retourner (2 ** n_bits) - n
fin
