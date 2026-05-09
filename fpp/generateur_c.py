"""
Générateur de code C à partir de l'AST F++.
Produit du C99 standard compilable avec gcc.
"""

from .ast_noeuds import *
from typing import List


class GenerateurC:
    def __init__(self):
        self.indent = 0
        self.lignes: List[str] = []
        self.fonctions_definies: set = set()
        self._en_tete()

    # ── En-tête C standard ───────────────────────────────────────────────────

    def _en_tete(self):
        self.lignes += [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <math.h>",
            "#include <time.h>",
            "#include <ctype.h>",
            "",
            "/* ── Runtime F++ ─────────────────────────────────────── */",
            "",
            "/* Lecture d'une ligne depuis stdin */",
            "static char* fpp_lire(const char* prompt) {",
            "    if (prompt) printf(\"%s\", prompt);",
            "    fflush(stdout);",
            "    char* buf = malloc(4096);",
            "    if (!buf) { perror(\"malloc\"); exit(1); }",
            "    if (!fgets(buf, 4096, stdin)) { buf[0] = '\\0'; return buf; }",
            "    size_t len = strlen(buf);",
            "    if (len > 0 && buf[len-1] == '\\n') buf[len-1] = '\\0';",
            "    return buf;",
            "}",
            "",
            "static long long fpp_lire_entier(const char* prompt) {",
            "    char* s = fpp_lire(prompt);",
            "    long long v = atoll(s);",
            "    free(s);",
            "    return v;",
            "}",
            "",
            "static double fpp_lire_decimal(const char* prompt) {",
            "    char* s = fpp_lire(prompt);",
            "    double v = atof(s);",
            "    free(s);",
            "    return v;",
            "}",
            "",
            "/* Concaténation de chaînes (alloue) */",
            "static char* fpp_concat(const char* a, const char* b) {",
            "    size_t la = strlen(a), lb = strlen(b);",
            "    char* r = malloc(la + lb + 1);",
            "    if (!r) { perror(\"malloc\"); exit(1); }",
            "    memcpy(r, a, la);",
            "    memcpy(r + la, b, lb + 1);",
            "    return r;",
            "}",
            "",
            "/* Conversion numérique -> texte */",
            "static char* fpp_entier_texte(long long v) {",
            "    char* s = malloc(32);",
            "    snprintf(s, 32, \"%lld\", v);",
            "    return s;",
            "}",
            "static char* fpp_decimal_texte(double v) {",
            "    char* s = malloc(64);",
            "    snprintf(s, 64, \"%g\", v);",
            "    return s;",
            "}",
            "static char* fpp_bool_texte(int v) {",
            "    return strdup(v ? \"vrai\" : \"faux\");",
            "}",
            "",
            "/* Hasard */",
            "static int fpp_rand_init = 0;",
            "static long long fpp_hasard_entier(long long a, long long b) {",
            "    if (!fpp_rand_init) { srand((unsigned)time(NULL)); fpp_rand_init=1; }",
            "    return a + rand() % (b - a + 1);",
            "}",
            "static double fpp_hasard(void) {",
            "    if (!fpp_rand_init) { srand((unsigned)time(NULL)); fpp_rand_init=1; }",
            "    return (double)rand() / RAND_MAX;",
            "}",
            "",
            "/* ── Fin runtime ──────────────────────────────────────── */",
            "",
        ]

    # ── Utilitaires d'écriture ───────────────────────────────────────────────

    def _ecrire(self, ligne=""):
        self.lignes.append("    " * self.indent + ligne)

    def _ouvrir_bloc(self, ligne=""):
        if ligne:
            self._ecrire(ligne + " {")
        else:
            self._ecrire("{")
        self.indent += 1

    def _fermer_bloc(self, suffixe=""):
        self.indent -= 1
        self._ecrire("}" + suffixe)

    # ── Point d'entrée ───────────────────────────────────────────────────────

    def generer(self, programme: Programme) -> str:
        # Séparer déclarations de fonctions du reste (main)
        fonctions = [n for n in programme.instructions if isinstance(n, DefFonction)]
        principal = [n for n in programme.instructions if not isinstance(n, DefFonction)]

        # Générer les fonctions en premier
        for fn in fonctions:
            self._gen_fonction(fn)
            self._ecrire()

        # Main
        self._ecrire("int main(void) {")
        self.indent += 1
        for instr in principal:
            self._gen_instr(instr)
        self._ecrire("return 0;")
        self.indent -= 1
        self._ecrire("}")

        return "\n".join(self.lignes)

    # ── Instructions ─────────────────────────────────────────────────────────

    def _gen_instr(self, noeud: Noeud):
        t = type(noeud).__name__
        methode = getattr(self, f"_gen_{t}", None)
        if methode:
            methode(noeud)
        else:
            self._ecrire(f"/* TODO: {t} */")

    def _gen_Declaration(self, n: Declaration):
        if n.valeur is not None:
            valeur = self._gen_expr(n.valeur)
        else:
            valeur = self._valeur_defaut_c(n.type_var)

        type_c = self._type_c(n.type_var, n.valeur)
        if n.type_var == "const":
            type_c = self._inferer_type_const(n.valeur)
            self._ecrire(f"const {type_c} {n.nom} = {valeur};")
        elif n.type_var == "texte":
            self._ecrire(f"char* {n.nom} = {valeur};")
        else:
            self._ecrire(f"{type_c} {n.nom} = {valeur};")

    def _gen_Assignation(self, n: Assignation):
        cible = self._gen_expr(n.cible)
        valeur = self._gen_expr(n.valeur)
        op = n.operateur
        self._ecrire(f"{cible} {op} {valeur};")

    def _gen_Afficher(self, n: Afficher):
        # Construire un printf avec les bons formats
        if not n.arguments:
            self._ecrire('printf("\\n");')
            return
        parties = []
        for i, arg in enumerate(n.arguments):
            if i > 0:
                parties.append('" "')
            parties.append(self._gen_printf_arg(arg))
        # On utilise plusieurs printf pour simplifier
        self._ecrire("/* afficher */")
        for i, arg in enumerate(n.arguments):
            if i > 0:
                self._ecrire('printf(" ");')
            fmt, val = self._format_printf(arg)
            if val:
                self._ecrire(f'printf("{fmt}", {val});')
            else:
                self._ecrire(f'printf("{fmt}");')
        self._ecrire('printf("\\n");')

    def _gen_ExprInstruction(self, n: ExprInstruction):
        expr = self._gen_expr(n.expression)
        self._ecrire(f"{expr};")

    def _gen_Si(self, n: Si):
        cond = self._gen_expr(n.condition)
        self._ouvrir_bloc(f"if ({cond})")
        for instr in n.alors:
            self._gen_instr(instr)
        self._fermer_bloc()
        for cond_si, bloc_si in n.sinon_si:
            c = self._gen_expr(cond_si)
            self._ouvrir_bloc(f"else if ({c})")
            for instr in bloc_si:
                self._gen_instr(instr)
            self._fermer_bloc()
        if n.sinon is not None:
            self._ouvrir_bloc("else")
            for instr in n.sinon:
                self._gen_instr(instr)
            self._fermer_bloc()

    def _gen_TantQue(self, n: TantQue):
        cond = self._gen_expr(n.condition)
        self._ouvrir_bloc(f"while ({cond})")
        for instr in n.corps:
            self._gen_instr(instr)
        self._fermer_bloc()

    def _gen_Pour(self, n: Pour):
        debut = self._gen_expr(n.debut)
        fin = self._gen_expr(n.fin)
        pas = self._gen_expr(n.pas) if n.pas else "1"
        v = n.variable
        self._ouvrir_bloc(
            f"for (long long {v} = {debut}; {v} <= {fin}; {v} += {pas})"
        )
        for instr in n.corps:
            self._gen_instr(instr)
        self._fermer_bloc()

    def _gen_PourDans(self, n: PourDans):
        # Limité aux tableaux statiques — on génère une boucle for générique
        # Pour les chaînes et listes dynamiques ce serait complexe en C pur.
        # On génère un commentaire explicatif + boucle basique sur tableau.
        self._ecrire(f"/* pour {n.variable} dans — boucle générée */")
        obj = self._gen_expr(n.iterable)
        v = n.variable
        idx = f"_fpp_i_{v}"
        self._ecrire(f"for (int {idx} = 0; {idx} < (int)(sizeof({obj})/sizeof({obj}[0])); {idx}++) {{")
        self.indent += 1
        self._ecrire(f"__typeof__({obj}[0]) {v} = {obj}[{idx}];")
        for instr in n.corps:
            self._gen_instr(instr)
        self.indent -= 1
        self._ecrire("}")

    def _gen_DefFonction(self, n: DefFonction):
        # déjà généré en dehors de main
        pass

    def _gen_fonction(self, n: DefFonction):
        params = ", ".join(f"double {p}" for p in n.parametres)
        self._ecrire(f"double {n.nom}({params}) {{")
        self.indent += 1
        for instr in n.corps:
            self._gen_instr(instr)
        self._ecrire("return 0;")
        self.indent -= 1
        self._ecrire("}")

    def _gen_Retourner(self, n: Retourner):
        if n.valeur:
            val = self._gen_expr(n.valeur)
            self._ecrire(f"return {val};")
        else:
            self._ecrire("return 0;")

    def _gen_Casser(self, n):
        self._ecrire("break;")

    def _gen_Continuer(self, n):
        self._ecrire("continue;")

    # ── Expressions ──────────────────────────────────────────────────────────

    def _gen_expr(self, noeud: Noeud) -> str:
        t = type(noeud).__name__
        methode = getattr(self, f"_expr_{t}", None)
        if methode:
            return methode(noeud)
        return f"/* expr:{t} */"

    def _expr_NombreLitteral(self, n: NombreLitteral) -> str:
        if isinstance(n.valeur, float):
            return repr(n.valeur)
        return str(n.valeur)

    def _expr_TexteLitteral(self, n: TexteLitteral) -> str:
        # Échapper les caractères spéciaux pour C
        s = n.valeur.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
        return f'"{s}"'

    def _expr_BoolLitteral(self, n: BoolLitteral) -> str:
        return "1" if n.valeur else "0"

    def _expr_NulLitteral(self, n: NulLitteral) -> str:
        return "NULL"

    def _expr_Identifiant(self, n: Identifiant) -> str:
        # Constantes intégrées
        builtins_c = {
            "pi": "M_PI",
            "e": "M_E",
            "infini": "INFINITY",
            "vrai": "1",
            "faux": "0",
        }
        return builtins_c.get(n.nom, n.nom)

    def _expr_OpBinaire(self, n: OpBinaire) -> str:
        g = self._gen_expr(n.gauche)
        d = self._gen_expr(n.droite)
        ops = {
            "et": "&&", "ou": "||",
            "+": "+", "-": "-", "*": "*", "/": "/", "%": "%",
            "==": "==", "!=": "!=", "<": "<", ">": ">", "<=": "<=", ">=": ">=",
        }
        if n.operateur == "**":
            return f"pow({g}, {d})"
        op_c = ops.get(n.operateur, n.operateur)
        return f"({g} {op_c} {d})"

    def _expr_OpUnaire(self, n: OpUnaire) -> str:
        val = self._gen_expr(n.operande)
        if n.operateur == "-": return f"(-{val})"
        if n.operateur == "non": return f"(!{val})"
        return val

    def _expr_AppelFonction(self, n: AppelFonction) -> str:
        args_c = [self._gen_expr(a) for a in n.arguments]

        # Fonctions builtin → fonctions C
        map_builtins = {
            "racine": lambda a: f"sqrt({a[0]})",
            "absolu": lambda a: f"fabs({a[0]})",
            "arrondir": lambda a: (f"round({a[0]})" if len(a)==1 else
                                   f"(round({a[0]} * pow(10,{a[1]})) / pow(10,{a[1]}))"),
            "sinus": lambda a: f"sin({a[0]})",
            "cosinus": lambda a: f"cos({a[0]})",
            "tangente": lambda a: f"tan({a[0]})",
            "logarithme": lambda a: f"log({a[0]})" if len(a)==1 else f"(log({a[0]})/log({a[1]}))",
            "plancher": lambda a: f"floor({a[0]})",
            "plafond": lambda a: f"ceil({a[0]})",
            "minimum": lambda a: f"fmin({a[0]}, {a[1]})" if len(a)==2 else f"fmin({a[0]},fmin({a[1]},{a[2]}))",
            "maximum": lambda a: f"fmax({a[0]}, {a[1]})" if len(a)==2 else f"fmax({a[0]},fmax({a[1]},{a[2]}))",
            "hasard_entier": lambda a: f"fpp_hasard_entier({a[0]}, {a[1]})",
            "hasard": lambda a: "fpp_hasard()",
            "entier": lambda a: f"((long long)({a[0]}))",
            "decimal": lambda a: f"((double)({a[0]}))",
            "texte": lambda a: f"fpp_entier_texte({a[0]})",
            "afficher": lambda a: f'printf("%s\\n", {a[0]})',
            "lire": lambda a: f"fpp_lire({a[0] if a else 'NULL'})",
            "lire_entier": lambda a: f"fpp_lire_entier({a[0] if a else 'NULL'})",
            "lire_decimal": lambda a: f"fpp_lire_decimal({a[0] if a else 'NULL'})",
            "longueur": lambda a: f"strlen({a[0]})",
        }
        if n.nom in map_builtins:
            return map_builtins[n.nom](args_c)

        # Méthode d'objet
        if n.nom == "__methode__":
            return self._expr_methode(n, args_c)

        # Fonction utilisateur
        return f"{n.nom}({', '.join(args_c)})"

    def _expr_methode(self, n: AppelFonction, args_c: list) -> str:
        # args_c[0] = objet, n.arguments[1] = TexteLitteral(nom méthode)
        obj = args_c[0]
        methode = n.arguments[1].valeur
        margs = args_c[2:]

        methodes_str = {
            "longueur": lambda: f"strlen({obj})",
            "majuscule": lambda: f"/* majuscule non supporté nativement en C */ {obj}",
            "minuscule": lambda: f"/* minuscule non supporté nativement en C */ {obj}",
            "contient": lambda: f"(strstr({obj}, {margs[0]}) != NULL)",
            "supprimer_espaces": lambda: f"/* trim: */ {obj}",
        }
        fn = methodes_str.get(methode)
        if fn:
            return fn()
        return f"/* méthode .{methode}() */"

    def _expr_AccesIndex(self, n: AccesIndex) -> str:
        obj = self._gen_expr(n.objet)
        idx = self._gen_expr(n.index)
        return f"{obj}[{idx}]"

    def _expr_Lire(self, n: Lire) -> str:
        prompt = self._gen_expr(n.prompt) if n.prompt else "NULL"
        if n.mode == "entier":
            return f"fpp_lire_entier({prompt})"
        if n.mode == "decimal":
            return f"fpp_lire_decimal({prompt})"
        return f"fpp_lire({prompt})"

    def _expr_ListeLitterale(self, n: ListeLitterale) -> str:
        elems = ", ".join(self._gen_expr(e) for e in n.elements)
        return "{" + elems + "}"

    def _expr_DictLitteral(self, n: DictLitteral) -> str:
        return "/* dict non supporté comme expression C simple */"

    # ── Helpers printf ───────────────────────────────────────────────────────

    def _format_printf(self, noeud: Noeud) -> tuple:
        """Retourne (format_string, expression_C) pour printf."""
        if isinstance(noeud, NombreLitteral):
            if isinstance(noeud.valeur, float):
                return ("%g", self._gen_expr(noeud))
            return ("%lld", self._gen_expr(noeud))
        if isinstance(noeud, TexteLitteral):
            s = noeud.valeur.replace("\\", "\\\\").replace('"', '\\"').replace("\n","\\n").replace("\t","\\t")
            return (s, None)
        if isinstance(noeud, BoolLitteral):
            return ("%s", '"vrai"' if noeud.valeur else '"faux"')
        if isinstance(noeud, Identifiant):
            # On ne connaît pas le type — utiliser %g par défaut pour les nombres
            # L'utilisateur doit avoir déclaré le type
            return ("%g", self._gen_expr(noeud))
        if isinstance(noeud, OpBinaire):
            return ("%g", self._gen_expr(noeud))
        if isinstance(noeud, AppelFonction):
            return ("%g", self._gen_expr(noeud))
        return ("%s", self._gen_expr(noeud))

    def _gen_printf_arg(self, noeud: Noeud) -> str:
        return self._gen_expr(noeud)

    # ── Types C ──────────────────────────────────────────────────────────────

    def _type_c(self, type_fpp: str, valeur_noeud=None) -> str:
        return {
            "entier": "long long",
            "decimal": "double",
            "texte": "char*",
            "bool": "int",
            "liste": "/* liste */",
            "dict": "/* dict */",
            "const": "const double",
        }.get(type_fpp, "double")

    def _valeur_defaut_c(self, type_fpp: str) -> str:
        return {
            "entier": "0",
            "decimal": "0.0",
            "texte": '""',
            "bool": "0",
            "const": "0",
        }.get(type_fpp, "0")

    def _inferer_type_const(self, noeud) -> str:
        if isinstance(noeud, NombreLitteral):
            return "long long" if isinstance(noeud.valeur, int) else "double"
        if isinstance(noeud, TexteLitteral):
            return "const char*"
        return "double"
