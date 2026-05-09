# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque de traitement de texte
#  inclure "include/texte.fpp"
#
#  Fonctions d'analyse et de génération de texte.
#  Note : les fonctions retournent des valeurs numériques ;
#  pour la manipulation de chaînes, utiliser les méthodes
#  intégrées (t.majuscule(), t.remplacer(), etc.)
# ══════════════════════════════════════════════════════════════

# ── Analyse numérique d'un texte ──────────────────────────────

# Nombre de mots dans une phrase (séparés par des espaces)
fonction compter_mots(t) faire
    liste parties = t.diviser(" ")
    retourner parties.longueur()
fin

# Vérifie si un texte est vide ou ne contient que des espaces
fonction est_vide_ou_espace(t) faire
    texte nettoye = t.supprimer_espaces()
    retourner nettoye.longueur() == 0
fin

# ── Validation de format ──────────────────────────────────────

# Vérifie si un texte représente un entier valide
# (uniquement chiffres, avec possible signe - initial)
fonction est_entier_valide(t) faire
    si t.longueur() == 0 alors
        retourner 0
    fin
    # Retourner 1 si conversion aller-retour est cohérente
    decimal valeur = entier(t)
    retourner valeur != 0 ou t == "0" ou t == "-0"
fin

# Vérifie si un texte commence par un chiffre
fonction commence_par_chiffre(t) faire
    si t.longueur() == 0 alors
        retourner 0
    fin
    texte c = t.diviser("")[0]
    retourner c == "0" ou c == "1" ou c == "2" ou c == "3" ou c == "4"
        ou c == "5" ou c == "6" ou c == "7" ou c == "8" ou c == "9"
fin

# Compte le nombre d'occurrences d'un sous-texte dans un texte
fonction compter_sous_texte(t, sous) faire
    si sous.longueur() == 0 alors
        retourner 0
    fin
    liste parties = t.diviser(sous)
    retourner parties.longueur() - 1
fin

# ── Génération de séparateurs & affichage ────────────────────

# Affiche un titre encadré par des tirets
fonction afficher_titre(titre) faire
    decimal n = titre.longueur() + 4
    texte ligne = ""
    pour i de 0 a n - 1 faire
        ligne = ligne + "─"
    fin
    afficher(ligne)
    afficher("│ " + titre + " │")
    afficher(ligne)
    retourner 0
fin

# Affiche un séparateur de n caractères
fonction afficher_separateur(n, c) faire
    texte ligne = ""
    pour i de 0 a n - 1 faire
        ligne = ligne + c
    fin
    afficher(ligne)
    retourner 0
fin

# Affiche un tableau simple à deux colonnes (clé/valeur)
fonction afficher_paire(cle, valeur) faire
    afficher(cle + " : " + texte(valeur))
    retourner 0
fin

# ── Répétition ────────────────────────────────────────────────

# Répète un texte n fois (retourne le résultat via afficher)
fonction repeter_afficher(t, n) faire
    pour i de 0 a n - 1 faire
        afficher(t)
    fin
    retourner 0
fin

# Longueur d'un texte (alias lisible)
fonction longueur_texte(t) faire
    retourner t.longueur()
fin

# ── Statistiques sur du texte ────────────────────────────────

# Compte les voyelles dans un texte (a, e, i, o, u, y)
fonction compter_voyelles(t) faire
    texte tmin = t.minuscule()
    liste chars = tmin.diviser("")
    decimal n = 0
    pour c dans chars faire
        si c == "a" ou c == "e" ou c == "i" ou c == "o" ou c == "u" ou c == "y" alors
            n += 1
        fin
    fin
    retourner n
fin

# Compte les consonnes dans un texte
fonction compter_consonnes(t) faire
    texte tmin = t.minuscule()
    liste chars = tmin.diviser("")
    decimal n = 0
    pour c dans chars faire
        si c != " " et c != "a" et c != "e" et c != "i"
            et c != "o" et c != "u" et c != "y" alors
            si c.longueur() == 1 alors
                n += 1
            fin
        fin
    fin
    retourner n
fin

# Retourne la longueur du mot le plus long dans une phrase
fonction longueur_mot_max(phrase) faire
    liste mots = phrase.diviser(" ")
    decimal max_len = 0
    pour mot dans mots faire
        si mot.longueur() > max_len alors
            max_len = mot.longueur()
        fin
    fin
    retourner max_len
fin

# Retourne la longueur du mot le plus court dans une phrase
fonction longueur_mot_min(phrase) faire
    liste mots = phrase.diviser(" ")
    si mots.longueur() == 0 alors
        retourner 0
    fin
    decimal min_len = mots[0].longueur()
    pour i de 1 a mots.longueur() - 1 faire
        si mots[i].longueur() < min_len alors
            min_len = mots[i].longueur()
        fin
    fin
    retourner min_len
fin

# Longueur moyenne des mots d'une phrase
fonction longueur_mots_moyenne(phrase) faire
    liste mots = phrase.diviser(" ")
    si mots.longueur() == 0 alors
        retourner 0
    fin
    decimal total = 0
    pour mot dans mots faire
        total += mot.longueur()
    fin
    retourner total / mots.longueur()
fin
