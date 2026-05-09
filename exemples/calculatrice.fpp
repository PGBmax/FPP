# calculatrice.fpp — Calculatrice interactive en F++

afficher("╔═════════════════════════╗")
afficher("║     Calculatrice F++    ║")
afficher("╚═════════════════════════╝")
afficher("Opérations : +  -  *  /  %  **")
afficher("Tapez 'quitter' pour sortir.")
afficher("")

fonction calculer(a, op, b) faire
    si op == "+" alors
        retourner a + b
    fin
    si op == "-" alors
        retourner a - b
    fin
    si op == "*" alors
        retourner a * b
    fin
    si op == "/" alors
        si b == 0 alors
            afficher("Erreur : division par zéro !")
            retourner nul
        fin
        retourner a / b
    fin
    si op == "%" alors
        retourner a % b
    fin
    si op == "**" alors
        retourner a ** b
    fin
    afficher("Opérateur inconnu :", op)
    retourner nul
fin

tantque vrai faire
    afficher("──────────────────────────")
    texte saisie = lire("Expression (ex: 5 + 3) : ")
    
    si saisie == "quitter" alors
        afficher("Au revoir !")
        casser
    fin

    liste parties = saisie.diviser(" ")
    
    si longueur(parties) != 3 alors
        afficher("Format invalide. Exemple : 12.5 * 3")
        continuer
    fin

    decimal nb1 = decimal(parties[0])
    texte operateur = parties[1]
    decimal nb2 = decimal(parties[2])

    decimal resultat = calculer(nb1, operateur, nb2)

    si resultat != nul alors
        afficher("Résultat :", arrondir(resultat, 6))
    fin
fin
