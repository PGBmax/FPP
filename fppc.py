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
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fpp.lexer import Lexer, ErreurLexicale
from fpp.parser import analyser, ErreurSyntaxique
from fpp.codegen import CodegenC, ErreurCompilation

VERSION = "1.0.0"

# Répertoire racine du projet FPP (là où se trouve fppc.py)
FPP_ROOT = os.path.dirname(os.path.abspath(__file__))

# ── Préprocesseur (inclure) ───────────────────────────────────────────────────

def _preprocesser(source: str, source_dir: str, deja_inclus: set = None) -> str:
    """Résout les directives `inclure "chemin"` récursivement."""
    if deja_inclus is None:
        deja_inclus = set()

    lignes_out = []
    for ligne in source.splitlines(keepends=True):
        stripped = ligne.strip()
        if stripped.startswith('inclure ') and ('"' in stripped or "'" in stripped):
            # Extraire le chemin entre guillemets
            debut = stripped.index('"') + 1 if '"' in stripped else stripped.index("'") + 1
            fin   = stripped.rindex('"')  if '"' in stripped else stripped.rindex("'")
            chemin_rel = stripped[debut:fin]

            # Résolution du chemin : d'abord relatif au fichier courant, puis include/ du projet
            candidats = [
                os.path.join(source_dir, chemin_rel),
                os.path.join(FPP_ROOT, chemin_rel),
                os.path.join(FPP_ROOT, "include", os.path.basename(chemin_rel)),
            ]
            chemin_abs = None
            for c in candidats:
                if os.path.isfile(c):
                    chemin_abs = os.path.realpath(c)
                    break

            if chemin_abs is None:
                raise FileNotFoundError(
                    f"inclure : fichier introuvable → {chemin_rel!r}\n"
                    f"  cherché dans : {source_dir}, {os.path.join(FPP_ROOT, 'include')}"
                )

            if chemin_abs in deja_inclus:
                # Déjà inclus (garde-fou contre les inclusions circulaires)
                continue

            deja_inclus.add(chemin_abs)
            with open(chemin_abs, "r", encoding="utf-8") as f:
                contenu = f.read()
            # Récursivement préprocesser le fichier inclus
            contenu = _preprocesser(contenu, os.path.dirname(chemin_abs), deja_inclus)
            lignes_out.append(contenu)
            if not contenu.endswith("\n"):
                lignes_out.append("\n")
        else:
            lignes_out.append(ligne)

    return "".join(lignes_out)

# ── Couleurs ANSI ──────────────────────────────────────────────────────────────

USE_COLOR = sys.stderr.isatty()

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text

def bold(t):    return _c("1",       t)
def dim(t):     return _c("2",       t)
def red(t):     return _c("1;31",    t)
def green(t):   return _c("1;32",    t)
def yellow(t):  return _c("1;33",    t)
def blue(t):    return _c("1;34",    t)
def cyan(t):    return _c("1;36",    t)
def magenta(t): return _c("1;35",    t)
def gray(t):    return _c("38;5;245",t)

# ── Spinner ────────────────────────────────────────────────────────────────────

SPINNER_FRAMES = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

class Spinner:
    def __init__(self, msg: str):
        self.msg     = msg
        self._stop   = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        i = 0
        while not self._stop.is_set():
            frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
            print(f"\r  {cyan(frame)} {self.msg}", end="", flush=True, file=sys.stderr)
            time.sleep(0.08)
            i += 1

    def __enter__(self):
        if USE_COLOR:
            self._thread.start()
        return self

    def __exit__(self, *_):
        if USE_COLOR:
            self._stop.set()
            self._thread.join()
            # Efface la ligne du spinner
            print(f"\r\033[2K", end="", file=sys.stderr)

# ── Affichage des étapes ───────────────────────────────────────────────────────

def _etape(icone: str, label: str, detail: str = ""):
    detail_str = f"  {gray(detail)}" if detail else ""
    print(f"  {icone} {label}{detail_str}", file=sys.stderr)

def _header(fichier: str):
    nom = os.path.basename(fichier)
    ligne = "─" * (len(nom) + 18)
    print(file=sys.stderr)
    print(f"  {bold(cyan('F++'))} {gray('►')} {bold(nom)}", file=sys.stderr)
    print(f"  {gray(ligne)}", file=sys.stderr)

def _footer_ok(sortie: str, duree: float):
    print(f"  {gray('─' * 38)}", file=sys.stderr)
    print(f"  {green('✔')} {bold('Compilation réussie')}  "
          f"{gray(f'→ {sortie}')}  {gray(f'({duree*1000:.0f} ms)')}", file=sys.stderr)
    print(file=sys.stderr)

def _footer_err(etape: str, duree: float):
    print(f"  {gray('─' * 38)}", file=sys.stderr)
    print(f"  {red('✘')} {bold('Échec')} {gray(f'({etape})')}  "
          f"{gray(f'({duree*1000:.0f} ms)')}", file=sys.stderr)
    print(file=sys.stderr)

def _err_msg(msg: str):
    for ligne in str(msg).strip().splitlines():
        print(f"    {red('│')} {ligne}", file=sys.stderr)

# ── Compilateur ───────────────────────────────────────────────────────────────

def compiler(source_fpp: str, source_chemin: str, sortie: str = "a.out",
             afficher_c: bool = False, garder_c: bool = False):

    debut = time.time()
    nom_fpp = os.path.basename(source_chemin)

    if not afficher_c:
        _header(source_chemin)

    # ── 1. Analyse lexicale + syntaxique ──────────────────────────────────────
    with Spinner("Analyse…") as sp:
        try:
            ast = analyser(source_fpp)
        except ErreurLexicale as e:
            sp.__exit__(None, None, None)
            _etape(red("✘"), bold("Erreur lexicale"), nom_fpp)
            _err_msg(e)
            _footer_err("analyse", time.time() - debut)
            return 1
        except ErreurSyntaxique as e:
            sp.__exit__(None, None, None)
            _etape(red("✘"), bold("Erreur syntaxique"), nom_fpp)
            _err_msg(e)
            _footer_err("analyse", time.time() - debut)
            return 1

    if not afficher_c:
        _etape(green("✔"), "Analyse", nom_fpp)

    # ── 2. Génération C ───────────────────────────────────────────────────────
    with Spinner("Génération C…") as sp:
        try:
            gen = CodegenC()
            code_c = gen.generer(ast)
        except ErreurCompilation as e:
            sp.__exit__(None, None, None)
            _etape(red("✘"), bold("Erreur de génération"), "")
            _err_msg(e)
            _footer_err("génération C", time.time() - debut)
            return 1

    if afficher_c:
        print(code_c)
        return 0

    if not afficher_c:
        _etape(green("✔"), "Génération C", "")

    # ── 3. Écriture du .c ─────────────────────────────────────────────────────
    base = os.path.splitext(source_chemin)[0]
    chemin_c = base + ".c"
    with open(chemin_c, "w", encoding="utf-8") as f:
        f.write(code_c)

    # ── 4. Compilation GCC ────────────────────────────────────────────────────
    gcc_cmd = ["gcc", "-Wall", "-Werror", "-Wextra", "-g3", "-O3", "-o", sortie, chemin_c, "-lm"]
    nom_sortie = os.path.basename(sortie)

    with Spinner(f"GCC  {gray(nom_sortie)}…") as sp:
        try:
            resultat = subprocess.run(gcc_cmd, capture_output=True, text=True)
        except FileNotFoundError:
            sp.__exit__(None, None, None)
            _etape(red("✘"), bold("gcc introuvable"),
                   "sudo apt install gcc")
            if not garder_c:
                os.remove(chemin_c)
            _footer_err("gcc", time.time() - debut)
            return 1

    if resultat.returncode != 0:
        _etape(red("✘"), bold("Erreur de compilation C"), "")
        _err_msg(resultat.stderr)
        if not garder_c:
            os.remove(chemin_c)
        _footer_err("gcc", time.time() - debut)
        return 1

    if not garder_c:
        os.remove(chemin_c)

    _etape(green("✔"), f"GCC  {gray('-Wall -Wextra -Werror -O3')}", nom_sortie)
    _footer_ok(sortie, time.time() - debut)
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
                print(f"  {red('✘')} -o nécessite un nom de fichier", file=sys.stderr)
                sys.exit(1)
            sortie = args[i]
        elif a == "-S":
            afficher_c = True
        elif a == "--keep-c":
            garder_c = True
        elif not a.startswith("-"):
            fichier_fpp = a
        else:
            print(f"  {red('✘')} option inconnue: {yellow(a)}", file=sys.stderr)
            sys.exit(1)
        i += 1

    if not fichier_fpp:
        print(f"  {red('✘')} aucun fichier source fourni", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(fichier_fpp):
        print(f"  {red('✘')} fichier introuvable: {yellow(repr(fichier_fpp))}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(fichier_fpp, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"  {red('✘')} impossible de lire {yellow(repr(fichier_fpp))}: {e}",
              file=sys.stderr)
        sys.exit(1)

    # Préprocesseur : résoudre les inclure "..."
    try:
        source_dir = os.path.dirname(os.path.abspath(fichier_fpp))
        source = _preprocesser(source, source_dir)
    except FileNotFoundError as e:
        print(f"  {red('✘')} {e}", file=sys.stderr)
        sys.exit(1)

    code = compiler(source, fichier_fpp, sortie, afficher_c, garder_c)
    sys.exit(code)


if __name__ == "__main__":
    main()
