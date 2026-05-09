# fonctions.fpp — Test des fonctions et de la récursivité

fonction factorielle(n) faire
    si n <= 1 alors
        retourner 1
    fin
    retourner n * factorielle(n - 1)
fin

fonction fibonacci(n) faire
    si n <= 1 alors
        retourner n
    fin
    retourner fibonacci(n - 1) + fibonacci(n - 2)
fin

fonction puissance_entiere(base, exp) faire
    decimal resultat = 1
    pour i de 1 a exp faire
        resultat = resultat * base
    fin
    retourner resultat
fin

afficher("=== Factorielles ===")
pour i de 1 a 10 faire
    afficher(i, "! =", factorielle(i))
fin

afficher("")
afficher("=== Fibonacci ===")
pour i de 0 a 10 faire
    afficher("fib(", i, ") =", fibonacci(i))
fin

afficher("")
afficher("=== Puissances ===")
afficher("2^10 =", puissance_entiere(2, 10))
afficher("3^5  =", puissance_entiere(3, 5))
