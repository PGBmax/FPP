#!/usr/bin/env python3
"""
fppc — Compilateur F++ (Français++)

Usage:
    fppc <fichier.fpp>              Compile → a.out
    fppc <fichier.fpp> -o <nom>     Compile → <nom>
    fppc <fichier.fpp> -S           Affiche le C généré sans compiler
    fppc --version
    fppc --aide
"""

import sys
import os
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fpp.lexer import Lexer, ErreurLexicale
from fpp.parser import analyser, ErreurSyntaxique
from fpp.codegen import CodegenC, ErreurCompilation

VERSION = "1.0.0"


def compiler(source_fpp: str, source_chemin: str, sortie: str = "a.out",
             afficher_c: bool = False, garder_c: bool = False):
    # 1. Analyse
    try:
        ast = analyser(source_fpp)
    except ErreurLexicale as e:
        print(f"fppc: {e}", file=sys.stderr)
        return 1
    except ErreurSyntaxique as e:
        print(f"fppc: {e}", file=sys.stderr)
        return 1

    # 2. Génération C
    try:
        gen = CodegenC()
        code_c = gen.generer(ast)
    except ErreurCompilation as e:
        print(f"fppc: Erreur de compilation: {e}", file=sys.stderr)
        return 1

    if afficher_c:
        print(code_c)
        return 0

    # 3. Écriture du fichier C temporaire (ou permanent si -keep)
    base = os.path.splitext(source_chemin)[0]
    chemin_c = base + ".c"

    with open(chemin_c, "w", encoding="utf-8") as f:
        f.write(code_c)

    # 4. Compilation avec gcc
    gcc_commande = ["gcc", "-Wall", "-O2", "-o", sortie, chemin_c, "-lm"]
    try:
        resultat = subprocess.run(gcc_commande, capture_output=True, text=True)
    except FileNotFoundError:
        print("fppc: gcc introuvable. Installe gcc avec: sudo apt install gcc",
              file=sys.stderr)
        if not garder_c:
            os.remove(chemin_c)
        return 1

    if resultat.returncode != 0:
        print("fppc: Erreur de compilation C (gcc) :", file=sys.stderr)
        print(resultat.stderr, file=sys.stderr)
        if not garder_c:
            os.remove(chemin_c)
        return 1

    if not garder_c:
        os.remove(chemin_c)

    print(f"fppc: Compilation réussie → {sortie}")
    return 0


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--aide", "--help", "-h"):
        print(__doc__)
        return

    if args[0] in ("--version", "-v"):
        print(f"F++ compilateur version {VERSION}")
        return

    # Parser les arguments
    fichier_fpp = None
    sortie = "a.out"
    afficher_c = False
    garder_c = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "-o":
            i += 1
            if i >= len(args):
                print("fppc: -o nécessite un nom de fichier", file=sys.stderr)
                sys.exit(1)
            sortie = args[i]
        elif a == "-S":
            afficher_c = True
        elif a == "--keep-c":
            garder_c = True
        elif not a.startswith("-"):
            fichier_fpp = a
        else:
            print(f"fppc: option inconnue: {a}", file=sys.stderr)
            sys.exit(1)
        i += 1

    if not fichier_fpp:
        print("fppc: aucun fichier source fourni", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(fichier_fpp):
        print(f"fppc: fichier introuvable: '{fichier_fpp}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(fichier_fpp, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"fppc: impossible de lire '{fichier_fpp}': {e}", file=sys.stderr)
        sys.exit(1)

    code = compiler(source, fichier_fpp, sortie, afficher_c, garder_c)
    sys.exit(code)


if __name__ == "__main__":
    main()
