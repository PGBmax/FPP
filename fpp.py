#!/usr/bin/env python3
"""
fpp — Interpréteur en ligne de commande pour le langage F++ (Français++)

Usage:
    fpp <fichier.fpp>          Exécuter un fichier F++
    fpp                        Lancer le mode interactif (REPL)
    fpp --version              Afficher la version
    fpp --aide                 Afficher l'aide
"""

import sys
import os
import readline  # historique dans le REPL

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fpp.lexer import Lexer, ErreurLexicale
from fpp.parser import analyser, ErreurSyntaxique
from fpp.interpreteur import Interpreteur, ErreurExecution

VERSION = "1.0.0"

BANNIERE = r"""
  _____ _     _     
 |  ___| |   | |    
 | |__ | |_  | |    
 |  __|| ' \ | |    
 | |   | (_) || |__ 
 |_|    \___/ |____|
   F++ v{version} — Français++
   Tape 'aide()' pour de l'aide, 'quitter()' pour quitter.
""".format(version=VERSION)

AIDE_REPL = """
══════════════════════════════════════════════
  Aide F++ — Commandes disponibles dans le REPL
══════════════════════════════════════════════
  aide()          → Affiche cette aide
  quitter()       → Quitte le REPL
  effacer()       → Efface l'écran
══════════════════════════════════════════════
  Types :   entier, decimal, texte, bool, liste, dict, const
  Blocs :   si/alors/sinonsi/sinon/fin
            tantque/faire/fin
            pour/de/a/faire/fin
            pour x dans liste faire/fin
  Fonctions: fonction nom(param) faire ... fin
             retourner valeur
  I/O :     afficher(...)   lire(prompt)
            lire_entier()   lire_decimal()
══════════════════════════════════════════════
"""


def executer_fichier(chemin: str):
    """Lit et exécute un fichier .fpp."""
    if not os.path.isfile(chemin):
        print(f"[Erreur] Fichier introuvable : '{chemin}'", file=sys.stderr)
        sys.exit(1)
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"[Erreur] Impossible de lire le fichier : {e}", file=sys.stderr)
        sys.exit(1)

    try:
        ast = analyser(source)
        interp = Interpreteur()
        interp.executer(ast)
    except ErreurLexicale as e:
        print(f"[Erreur Lexicale] {e}", file=sys.stderr)
        sys.exit(1)
    except ErreurSyntaxique as e:
        print(f"[Erreur Syntaxique] {e}", file=sys.stderr)
        sys.exit(1)
    except ErreurExecution as e:
        print(f"[Erreur d'Exécution] {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[Interrompu]", file=sys.stderr)
        sys.exit(130)


def repl():
    """Mode interactif (Read-Eval-Print Loop)."""
    print(BANNIERE)
    interp = Interpreteur()

    # Enregistrer quelques commandes REPL
    def builtin_quitter(args, l, c):
        print("Au revoir !")
        sys.exit(0)

    def builtin_aide(args, l, c):
        print(AIDE_REPL)
        return None

    interp.global_env.definir("quitter", type("_Fn", (), {
        "__class__": type,
    }))

    # Override _obtenir_builtin pour quitter/aide dans le REPL
    _orig_builtin = interp._obtenir_builtin

    def _builtin_repl(nom):
        if nom == "quitter":
            return builtin_quitter
        if nom == "aide":
            return builtin_aide
        return _orig_builtin(nom)

    interp._obtenir_builtin = _builtin_repl

    tampon = []
    profondeur = 0  # pour les blocs multi-lignes

    OUVERTURES = {"si", "tantque", "pour", "fonction"}
    FERMETURES = {"fin"}

    while True:
        try:
            invite = ">>> " if profondeur == 0 else "... " * profondeur + " "
            ligne = input(invite)
        except EOFError:
            print("\nAu revoir !")
            break
        except KeyboardInterrupt:
            print()
            tampon = []
            profondeur = 0
            continue

        tampon.append(ligne)

        # Compter la profondeur de bloc
        mots = ligne.strip().lower().split()
        for mot in mots:
            mot_clean = mot.rstrip("(")
            if mot_clean in OUVERTURES:
                profondeur += 1
            elif mot_clean in FERMETURES:
                profondeur = max(0, profondeur - 1)

        if profondeur > 0:
            continue

        source = "\n".join(tampon).strip()
        tampon = []

        if not source:
            continue

        try:
            ast = analyser(source)
            interp.executer(ast)
        except ErreurLexicale as e:
            print(f"[Erreur Lexicale] {e}")
        except ErreurSyntaxique as e:
            print(f"[Erreur Syntaxique] {e}")
        except ErreurExecution as e:
            print(f"[Erreur d'Exécution] {e}")
        except KeyboardInterrupt:
            print("[Interrompu]")
            tampon = []
            profondeur = 0


def main():
    args = sys.argv[1:]

    if not args:
        repl()
        return

    if args[0] in ("--version", "-v"):
        print(f"F++ version {VERSION}")
        return

    if args[0] in ("--aide", "--help", "-h"):
        print(__doc__)
        return

    executer_fichier(args[0])


if __name__ == "__main__":
    main()
