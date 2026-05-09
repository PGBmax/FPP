# bonjour.fpp — Premier programme F++

entier x = 10
entier y = 32
entier somme = x + y

afficher("Bonjour depuis F++ !")
afficher("x =", x)
afficher("y =", y)
afficher("x + y =", somme)
afficher("x * y =", x * y)
afficher("racine(144) =", racine(144))

si somme > 40 alors
    afficher("La somme est grande")
sinon
    afficher("La somme est petite")
fin

pour i de 1 a 5 faire
    afficher("i =", i)
fin

entier compteur = 0
tantque compteur < 3 faire
    afficher("compteur =", compteur)
    compteur += 1
fin
