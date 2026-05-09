# jeu_devinette.fpp — Jeu de devinette en F++

afficher("╔══════════════════════════════╗")
afficher("║   Jeu : Devine le nombre !   ║")
afficher("╚══════════════════════════════╝")
afficher("")

const entier MINIMUM = 1
const entier MAXIMUM = 100

entier secret = hasard_entier(MINIMUM, MAXIMUM)
entier essais = 0
bool gagne = faux

afficher("J'ai choisi un nombre entre", MINIMUM, "et", MAXIMUM)
afficher("À toi de deviner !")
afficher("")

tantque non gagne faire
    entier proposition = lire_entier("Ta proposition : ")
    essais += 1

    si proposition < secret alors
        afficher("📈 Trop petit ! Essaie plus grand.")
    sinonsi proposition > secret alors
        afficher("📉 Trop grand ! Essaie plus petit.")
    sinon
        gagne = vrai
        afficher("")
        afficher("🎉 Bravo ! Tu as trouvé", secret, "en", essais, "essai(s) !")
    fin
fin

si essais == 1 alors
    afficher("Incroyable, tu l'as trouvé du premier coup !")
sinonsi essais <= 5 alors
    afficher("Excellent score !")
sinonsi essais <= 10 alors
    afficher("Bon score !")
sinon
    afficher("Continue de t'entraîner !")
fin