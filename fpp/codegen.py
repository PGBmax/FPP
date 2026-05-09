"""
CodegenC — Générateur de code C pour F++.

Stratégie de types :
  - entier  → long long
  - decimal → double
  - texte   → char* (alloué sur le tas via fpp_str_*)
  - bool    → int (0/1)
  - liste   → FppListe* (tableau dynamique générique via void*)
  - dict    → FppDict* (table de hachage simple)
  - fonctions → double (retour), paramètres double par défaut

Le runtime F++ est inclus inline dans chaque .c généré.
"""

from .ast_noeuds import *
from typing import List, Dict, Optional


class ErreurCompilation(Exception):
    pass


# ── Runtime F++ (injecté dans chaque .c) ─────────────────────────────────────

RUNTIME = r"""
/* ═══════════════════════════════════════════════════════════════
   Runtime F++ — généré automatiquement, ne pas modifier
   ═══════════════════════════════════════════════════════════════ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <ctype.h>

/* ── Chaînes ──────────────────────────────────────────────────── */

static char* fpp_strdup(const char* s) {
    if (!s) return strdup("");
    return strdup(s);
}

static char* fpp_concat(const char* a, const char* b) {
    size_t la = strlen(a), lb = strlen(b);
    char* r = malloc(la + lb + 1);
    if (!r) { perror("malloc"); exit(1); }
    memcpy(r, a, la);
    memcpy(r + la, b, lb + 1);
    return r;
}

static char* fpp_entier_vers_texte(long long v) {
    char* s = malloc(32);
    if (!s) { perror("malloc"); exit(1); }
    snprintf(s, 32, "%lld", v);
    return s;
}

static char* fpp_decimal_vers_texte(double v) {
    char* s = malloc(64);
    if (!s) { perror("malloc"); exit(1); }
    snprintf(s, 64, "%g", v);
    return s;
}

static char* fpp_bool_vers_texte(int v) {
    return fpp_strdup(v ? "vrai" : "faux");
}

static char* fpp_trim(const char* s) {
    while (isspace((unsigned char)*s)) s++;
    if (*s == '\0') return fpp_strdup("");
    const char* end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) end--;
    size_t len = end - s + 1;
    char* r = malloc(len + 1);
    if (!r) { perror("malloc"); exit(1); }
    memcpy(r, s, len);
    r[len] = '\0';
    return r;
}

static char* fpp_majuscule(const char* s) {
    char* r = fpp_strdup(s);
    for (char* p = r; *p; p++) *p = (char)toupper((unsigned char)*p);
    return r;
}

static char* fpp_minuscule(const char* s) {
    char* r = fpp_strdup(s);
    for (char* p = r; *p; p++) *p = (char)tolower((unsigned char)*p);
    return r;
}

static char* fpp_remplacer(const char* s, const char* ancien, const char* nouveau) {
    if (!*ancien) return fpp_strdup(s);
    char* result = NULL;
    const char* p = s;
    size_t la = strlen(ancien), ln = strlen(nouveau);
    size_t cap = strlen(s) * 2 + 64;
    result = malloc(cap);
    if (!result) { perror("malloc"); exit(1); }
    size_t pos = 0;
    while (*p) {
        if (strncmp(p, ancien, la) == 0) {
            if (pos + ln + 1 >= cap) { cap = cap * 2 + ln; result = realloc(result, cap); }
            memcpy(result + pos, nouveau, ln);
            pos += ln;
            p += la;
        } else {
            if (pos + 2 >= cap) { cap *= 2; result = realloc(result, cap); }
            result[pos++] = *p++;
        }
    }
    result[pos] = '\0';
    return result;
}

static int fpp_commence_par(const char* s, const char* prefix) {
    return strncmp(s, prefix, strlen(prefix)) == 0;
}

static int fpp_finit_par(const char* s, const char* suffix) {
    size_t ls = strlen(s), lp = strlen(suffix);
    if (lp > ls) return 0;
    return strcmp(s + ls - lp, suffix) == 0;
}

/* ── Listes dynamiques ────────────────────────────────────────── */

typedef struct {
    void** elements;
    int    taille;
    int    capacite;
    int    type; /* 0=mixte,1=entier,2=decimal,3=texte */
} FppListe;

static FppListe* fpp_liste_creer(void) {
    FppListe* l = malloc(sizeof(FppListe));
    if (!l) { perror("malloc"); exit(1); }
    l->elements = malloc(8 * sizeof(void*));
    if (!l->elements) { perror("malloc"); exit(1); }
    l->taille = 0;
    l->capacite = 8;
    l->type = 0;
    return l;
}

static void fpp_liste_ajouter(FppListe* l, void* val) {
    if (l->taille >= l->capacite) {
        l->capacite *= 2;
        l->elements = realloc(l->elements, l->capacite * sizeof(void*));
        if (!l->elements) { perror("realloc"); exit(1); }
    }
    l->elements[l->taille++] = val;
}

static void* fpp_liste_obtenir(FppListe* l, long long idx) {
    if (idx < 0) idx = l->taille + idx;
    if (idx < 0 || idx >= l->taille) {
        fprintf(stderr, "F++: index %lld hors bornes (taille=%d)\n", idx, l->taille);
        exit(1);
    }
    return l->elements[idx];
}

static void fpp_liste_definir(FppListe* l, long long idx, void* val) {
    if (idx < 0) idx = l->taille + idx;
    if (idx < 0 || idx >= l->taille) {
        fprintf(stderr, "F++: index %lld hors bornes (taille=%d)\n", idx, l->taille);
        exit(1);
    }
    l->elements[idx] = val;
}

static void fpp_liste_supprimer_index(FppListe* l, long long idx) {
    if (idx < 0) idx = l->taille + idx;
    if (idx < 0 || idx >= l->taille) return;
    for (long long i = idx; i < l->taille - 1; i++)
        l->elements[i] = l->elements[i+1];
    l->taille--;
}

static void* fpp_liste_pop(FppListe* l) {
    if (l->taille == 0) { fprintf(stderr, "F++: pop sur liste vide\n"); exit(1); }
    return l->elements[--l->taille];
}

static int fpp_cmp_ll(const void* a, const void* b) {
    long long x = *(long long*)a, y = *(long long*)b;
    return (x > y) - (x < y);
}
static int fpp_cmp_dbl(const void* a, const void* b) {
    double x = *(double*)a, y = *(double*)b;
    return (x > y) - (x < y);
}
static int fpp_cmp_str(const void* a, const void* b) {
    return strcmp(*(const char**)a, *(const char**)b);
}

/* Affichage d'une liste (générique texte) */
static void fpp_liste_afficher(FppListe* l, int type_elem) {
    printf("[");
    for (int i = 0; i < l->taille; i++) {
        if (i) printf(", ");
        if (type_elem == 1)      printf("%lld", *(long long*)l->elements[i]);
        else if (type_elem == 2) printf("%g",   *(double*)l->elements[i]);
        else if (type_elem == 3) printf("%s",   (char*)l->elements[i]);
        else                     printf("?");
    }
    printf("]");
}

/* ── Entrée / sortie ──────────────────────────────────────────── */

static char* fpp_lire(const char* prompt) {
    if (prompt && *prompt) { printf("%s", prompt); fflush(stdout); }
    char* buf = malloc(4096);
    if (!buf) { perror("malloc"); exit(1); }
    if (!fgets(buf, 4096, stdin)) { buf[0] = '\0'; return buf; }
    size_t len = strlen(buf);
    if (len > 0 && buf[len-1] == '\n') buf[len-1] = '\0';
    return buf;
}

static long long fpp_lire_entier(const char* prompt) {
    char* s = fpp_lire(prompt);
    long long v = atoll(s);
    free(s);
    return v;
}

static double fpp_lire_decimal(const char* prompt) {
    char* s = fpp_lire(prompt);
    double v = atof(s);
    free(s);
    return v;
}

/* ── Maths / utilitaires ──────────────────────────────────────── */

static int fpp_rand_init = 0;
static long long fpp_hasard_entier(long long a, long long b) {
    if (!fpp_rand_init) { srand((unsigned int)time(NULL)); fpp_rand_init = 1; }
    if (b < a) { long long t = a; a = b; b = t; }
    return a + (long long)(rand() % (b - a + 1));
}
static double fpp_hasard(void) {
    if (!fpp_rand_init) { srand((unsigned int)time(NULL)); fpp_rand_init = 1; }
    return (double)rand() / (double)RAND_MAX;
}
static double fpp_hasard_intervalle(double a, double b) {
    return a + fpp_hasard() * (b - a);
}

static void fpp_liste_ajouter_dbl(FppListe* l, double val) {
    double* p = malloc(sizeof(double));
    if (!p) { perror("malloc"); exit(1); }
    *p = val;
    fpp_liste_ajouter(l, p);
}

static char* fpp_char_vers_texte(char c) {
    char* s = malloc(2);
    if (!s) { perror("malloc"); exit(1); }
    s[0] = c; s[1] = '\0';
    return s;
}

/* ════════════════════════════════════════════════════════════════
   Fin du runtime F++
   ════════════════════════════════════════════════════════════════ */
"""

# ── Générateur de code ────────────────────────────────────────────────────────

class Scope:
    """Table des variables avec leurs types C."""
    def __init__(self, parent: Optional["Scope"] = None):
        self.vars: Dict[str, str] = {}   # nom → type_c ("ll","dbl","str","int","lst")
        self.parent = parent

    def definir(self, nom: str, type_c: str):
        self.vars[nom] = type_c

    def type_de(self, nom: str) -> Optional[str]:
        if nom in self.vars:
            return self.vars[nom]
        if self.parent:
            return self.parent.type_de(nom)
        return None

    def enfant(self) -> "Scope":
        return Scope(parent=self)


FPP_TYPES = {
    "entier":  "ll",
    "decimal": "dbl",
    "texte":   "str",
    "bool":    "int",
    "liste":   "lst",
    "dict":    "dct",
    "const":   "ll",  # sera affiné
}

C_DECL = {
    "ll":  "long long",
    "dbl": "double",
    "str": "char*",
    "int": "int",
    "lst": "FppListe*",
    "dct": "FppDict*",
}


class CodegenC:
    def __init__(self):
        self.lignes: List[str] = []
        self.indent_n = 0
        self._tmp_cpt = 0

    # ── Sortie ────────────────────────────────────────────────────────────────

    def _w(self, ligne=""):
        self.lignes.append("    " * self.indent_n + ligne)

    def _ouvrir(self, ligne=""):
        if ligne:
            self._w(ligne + " {")
        else:
            self._w("{")
        self.indent_n += 1

    def _fermer(self, suf=""):
        self.indent_n -= 1
        self._w("}" + suf)

    def _tmp(self) -> str:
        self._tmp_cpt += 1
        return f"_fpp_t{self._tmp_cpt}"

    # ── Point d'entrée ────────────────────────────────────────────────────────

    def generer(self, programme: Programme) -> str:
        self.lignes = [RUNTIME]
        scope_global = Scope()

        # Forward declarations + fonctions
        fonctions = [n for n in programme.instructions if isinstance(n, DefFonction)]
        principal = [n for n in programme.instructions if not isinstance(n, DefFonction)]

        # Prototypes
        for fn in fonctions:
            params = ", ".join("double " + p for p in fn.parametres) if fn.parametres else "void"
            self._w(f"double {fn.nom}({params});")
        if fonctions:
            self._w()

        # Corps des fonctions
        for fn in fonctions:
            self._gen_fonction(fn, scope_global)
            self._w()

        # main
        self._ouvrir("int main(void)")
        scope_main = scope_global.enfant()
        for instr in principal:
            self._gen_instr(instr, scope_main)
        self._w("return 0;")
        self._fermer()

        return "\n".join(self.lignes)

    # ── Fonctions ─────────────────────────────────────────────────────────────

    def _gen_fonction(self, n: DefFonction, scope_parent: Scope):
        params_str = ", ".join(f"double {p}" for p in n.parametres) if n.parametres else "void"
        self._ouvrir(f"double {n.nom}({params_str})")
        scope = scope_parent.enfant()
        for p in n.parametres:
            scope.definir(p, "dbl")
        for instr in n.corps:
            self._gen_instr(instr, scope)
        self._w("return 0.0;")
        self._fermer()

    # ── Instructions ─────────────────────────────────────────────────────────

    def _gen_instr(self, noeud: Noeud, scope: Scope):
        t = type(noeud).__name__
        m = getattr(self, f"_instr_{t}", None)
        if m:
            m(noeud, scope)
        else:
            self._w(f"/* TODO instr: {t} */")

    def _instr_Declaration(self, n: Declaration, scope: Scope):
        type_fpp = n.type_var
        tc = FPP_TYPES.get(type_fpp, "dbl")

        # Affiner le type const en fonction de la valeur
        if type_fpp == "const" and n.valeur:
            tc = self._inferer_tc(n.valeur, scope)

        val_expr, val_tc = self._eval_expr(n.valeur, scope) if n.valeur else (self._defaut_c(tc), tc)
        val_expr = self._coercer(val_expr, val_tc, tc, n.ligne)

        scope.definir(n.nom, tc)
        type_c = C_DECL.get(tc, "double")

        if type_fpp == "const":
            self._w(f"const {type_c} {n.nom} = {val_expr};")
        elif tc == "lst":
            self._w(f"FppListe* {n.nom} = {val_expr};")
        else:
            self._w(f"{type_c} {n.nom} = {val_expr};")

    def _instr_Assignation(self, n: Assignation, scope: Scope):
        val_expr, val_tc = self._eval_expr(n.valeur, scope)

        if isinstance(n.cible, Identifiant):
            nom = n.cible.nom
            cible_tc = scope.type_de(nom) or val_tc
            val_expr = self._coercer(val_expr, val_tc, cible_tc, n.ligne)
            op = n.operateur
            if op == "=" and cible_tc == "str":
                self._w(f"{nom} = {val_expr};")
            elif op in ("+=", "-=", "*=", "/=") and cible_tc == "str" and op == "+=":
                self._w(f"{nom} = fpp_concat({nom}, {val_expr});")
            else:
                self._w(f"{nom} {op} {val_expr};")

        elif isinstance(n.cible, AccesIndex):
            obj_expr, obj_tc = self._eval_expr(n.cible.objet, scope)
            idx_expr, _ = self._eval_expr(n.cible.index, scope)
            if obj_tc == "lst":
                # On stocke un pointeur vers la valeur
                elem_tc = "dbl"  # hypothèse par défaut
                tmp = self._tmp()
                self._w(f"double* {tmp} = malloc(sizeof(double));")
                self._w(f"*{tmp} = {self._coercer(val_expr, val_tc, 'dbl', n.ligne)};")
                self._w(f"fpp_liste_definir({obj_expr}, {idx_expr}, {tmp});")
            else:
                # Tableau C natif
                self._w(f"{obj_expr}[{idx_expr}] = {val_expr};")
        else:
            self._w("/* assignation complexe */")

    def _instr_Afficher(self, n: Afficher, scope: Scope):
        if not n.arguments:
            self._w('printf("\\n");')
            return
        for i, arg in enumerate(n.arguments):
            if i > 0:
                self._w('printf(" ");')
            expr, tc = self._eval_expr(arg, scope)
            self._gen_printf(expr, tc)
        self._w('printf("\\n");')

    def _gen_printf(self, expr: str, tc: str):
        if tc == "ll":
            self._w(f'printf("%lld", (long long)({expr}));')
        elif tc == "dbl":
            self._w(f'printf("%g", (double)({expr}));')
        elif tc == "str":
            self._w(f'printf("%s", {expr} ? {expr} : "nul");')
        elif tc == "int":
            self._w(f'printf("%s", ({expr}) ? "vrai" : "faux");')
        elif tc == "lst":
            # On ne connaît pas le type des éléments — on affiche les pointeurs
            # Par simplification, on génère un helper
            self._w(f'printf("[liste]"); /* affichage liste simplifié */;')
        else:
            self._w(f'printf("%g", (double)({expr}));')

    def _instr_ExprInstruction(self, n: ExprInstruction, scope: Scope):
        expr, _ = self._eval_expr(n.expression, scope)
        self._w(f"{expr};")

    def _instr_Si(self, n: Si, scope: Scope):
        cond, _ = self._eval_expr(n.condition, scope)
        self._ouvrir(f"if ({cond})")
        for instr in n.alors:
            self._gen_instr(instr, scope.enfant())
        self._fermer()
        for cond_si, bloc in n.sinon_si:
            c, _ = self._eval_expr(cond_si, scope)
            self._ouvrir(f"else if ({c})")
            for instr in bloc:
                self._gen_instr(instr, scope.enfant())
            self._fermer()
        if n.sinon is not None:
            self._ouvrir("else")
            for instr in n.sinon:
                self._gen_instr(instr, scope.enfant())
            self._fermer()

    def _instr_TantQue(self, n: TantQue, scope: Scope):
        cond, _ = self._eval_expr(n.condition, scope)
        self._ouvrir(f"while ({cond})")
        for instr in n.corps:
            self._gen_instr(instr, scope.enfant())
        self._fermer()

    def _instr_Pour(self, n: Pour, scope: Scope):
        debut, _ = self._eval_expr(n.debut, scope)
        fin, _   = self._eval_expr(n.fin, scope)
        pas, _   = (self._eval_expr(n.pas, scope) if n.pas else ("1", "ll"))
        sous = scope.enfant()
        sous.definir(n.variable, "ll")
        self._ouvrir(
            f"for (long long {n.variable} = {debut}; "
            f"{n.variable} <= (long long)({fin}); "
            f"{n.variable} += (long long)({pas}))"
        )
        for instr in n.corps:
            self._gen_instr(instr, sous)
        self._fermer()

    def _instr_PourDans(self, n: PourDans, scope: Scope):
        obj_expr, obj_tc = self._eval_expr(n.iterable, scope)
        idx = self._tmp()
        sous = scope.enfant()
        if obj_tc == "lst":
            sous.definir(n.variable, "dbl")
            self._ouvrir(f"for (int {idx} = 0; {idx} < ({obj_expr})->taille; {idx}++)")
            self._w(f"double {n.variable} = *(double*)fpp_liste_obtenir({obj_expr}, {idx});")
            for instr in n.corps:
                self._gen_instr(instr, sous)
            self._fermer()
        else:
            self._w(f"/* pour-dans: type non supporté pour '{obj_expr}' */")

    def _instr_Retourner(self, n: Retourner, scope: Scope):
        if n.valeur:
            expr, tc = self._eval_expr(n.valeur, scope)
            self._w(f"return (double)({expr});")
        else:
            self._w("return 0.0;")

    def _instr_Casser(self, n, scope):
        self._w("break;")

    def _instr_Continuer(self, n, scope):
        self._w("continue;")

    def _instr_DefFonction(self, n, scope):
        pass  # déjà généré avant main

    # ── Expressions ──────────────────────────────────────────────────────────
    # Retourne (expression_C: str, type_C: str)

    def _eval_expr(self, noeud: Noeud, scope: Scope):
        t = type(noeud).__name__
        m = getattr(self, f"_expr_{t}", None)
        if m:
            return m(noeud, scope)
        return (f"/* expr:{t} */", "dbl")

    def _expr_NombreLitteral(self, n: NombreLitteral, scope):
        if isinstance(n.valeur, float):
            return (repr(n.valeur), "dbl")
        return (str(n.valeur) + "LL", "ll")

    def _expr_TexteLitteral(self, n: TexteLitteral, scope):
        s = (n.valeur
             .replace("\\", "\\\\")
             .replace('"', '\\"')
             .replace("\n", "\\n")
             .replace("\t", "\\t"))
        return (f'"{s}"', "str")

    def _expr_BoolLitteral(self, n: BoolLitteral, scope):
        return ("1" if n.valeur else "0", "int")

    def _expr_NulLitteral(self, n: NulLitteral, scope):
        return ("NULL", "str")

    def _expr_Identifiant(self, n: Identifiant, scope):
        builtins = {
            "pi": ("M_PI", "dbl"),
            "e":  ("M_E",  "dbl"),
            "infini": ("INFINITY", "dbl"),
            "vrai": ("1", "int"),
            "faux": ("0", "int"),
            "nul":  ("NULL", "str"),
        }
        if n.nom in builtins:
            return builtins[n.nom]
        tc = scope.type_de(n.nom) or "dbl"
        return (n.nom, tc)

    def _expr_OpBinaire(self, n: OpBinaire, scope):
        # Court-circuit logique → juste C standard
        g, gtc = self._eval_expr(n.gauche, scope)
        d, dtc = self._eval_expr(n.droite, scope)
        op = n.operateur

        if op in ("et", "ou"):
            cop = "&&" if op == "et" else "||"
            return (f"({g} {cop} {d})", "int")

        if op == "**":
            return (f"pow((double)({g}), (double)({d}))", "dbl")

        # Concaténation texte + texte
        if op == "+" and (gtc == "str" or dtc == "str"):
            sg = g if gtc == "str" else (
                f"fpp_entier_vers_texte({g})" if gtc == "ll" else f"fpp_decimal_vers_texte({g})")
            sd = d if dtc == "str" else (
                f"fpp_entier_vers_texte({d})" if dtc == "ll" else f"fpp_decimal_vers_texte({d})")
            return (f"fpp_concat({sg}, {sd})", "str")

        # Comparaisons sur texte
        if op in ("==", "!=") and (gtc == "str" or dtc == "str"):
            cmp = f"strcmp({g}, {d})"
            return (f"({cmp} == 0)" if op == "==" else f"({cmp} != 0)", "int")

        cops = {"+":"+", "-":"-", "*":"*", "/":"/", "%":"%",
                "==":"==", "!=":"!=", "<":"<", ">":">", "<=":"<=", ">=":">="}
        cop = cops.get(op, op)

        # Résultat entier vs décimal
        if op in ("==", "!=", "<", ">", "<=", ">="):
            return (f"({g} {cop} {d})", "int")
        if op == "/" or gtc == "dbl" or dtc == "dbl":
            return (f"((double)({g}) {cop} (double)({d}))", "dbl")
        return (f"({g} {cop} {d})", "ll")

    def _expr_OpUnaire(self, n: OpUnaire, scope):
        val, tc = self._eval_expr(n.operande, scope)
        if n.operateur == "-":
            return (f"(-({val}))", tc)
        if n.operateur == "non":
            return (f"(!({val}))", "int")
        return (val, tc)

    def _expr_AppelFonction(self, n: AppelFonction, scope):
        if n.nom == "__methode__":
            return self._expr_methode(n, scope)
        return self._expr_builtin_ou_user(n, scope)

    def _expr_builtin_ou_user(self, n: AppelFonction, scope):
        nom = n.nom
        args = [(self._eval_expr(a, scope)) for a in n.arguments]
        exprs = [e for e, _ in args]
        tcs   = [t for _, t in args]

        def a(i): return exprs[i] if i < len(exprs) else "0"

        builtins = {
            "racine":        lambda: (f"sqrt((double)({a(0)}))", "dbl"),
            "absolu":        lambda: (f"fabs((double)({a(0)}))", "dbl"),
            "arrondir":      lambda: (
                (f"round((double)({a(0)}))", "dbl") if len(exprs) < 2 else
                (f"(round((double)({a(0)}) * pow(10.0, {a(1)})) / pow(10.0, {a(1)}))", "dbl")
            ),
            "sinus":         lambda: (f"sin((double)({a(0)}))", "dbl"),
            "cosinus":       lambda: (f"cos((double)({a(0)}))", "dbl"),
            "tangente":      lambda: (f"tan((double)({a(0)}))", "dbl"),
            "logarithme":    lambda: (
                (f"log((double)({a(0)}))", "dbl") if len(exprs) < 2 else
                (f"(log((double)({a(0)}))/log((double)({a(1)})))", "dbl")
            ),
            "plancher":      lambda: (f"((long long)floor((double)({a(0)})))", "ll"),
            "plafond":       lambda: (f"((long long)ceil((double)({a(0)})))", "ll"),
            "minimum":       lambda: (f"fmin((double)({a(0)}), (double)({a(1)}))", "dbl"),
            "maximum":       lambda: (f"fmax((double)({a(0)}), (double)({a(1)}))", "dbl"),
            "hasard_entier": lambda: (f"fpp_hasard_entier({a(0)}, {a(1)})", "ll"),
            "hasard":        lambda: (
                ("fpp_hasard()", "dbl") if len(exprs) < 2 else
                (f"fpp_hasard_intervalle({a(0)}, {a(1)})", "dbl")
            ),
            "entier":  lambda: (f"((long long)({a(0)}))", "ll"),
            "decimal": lambda: (f"((double)({a(0)}))", "dbl"),
            "bool":    lambda: (f"(({a(0)}) != 0)", "int"),
            "texte":   lambda: (
                (f"fpp_entier_vers_texte({a(0)})" if tcs[0]=="ll" else
                 f"fpp_decimal_vers_texte({a(0)})" if tcs[0]=="dbl" else
                 f"fpp_bool_vers_texte({a(0)})" if tcs[0]=="int" else
                 a(0)),
                "str"
            ),
            "longueur": lambda: (f"((long long)strlen({a(0)}))", "ll") if tcs and tcs[0]=="str" else
                                 (f"((long long)({a(0)})->taille)", "ll"),
            "lire":         lambda: (f"fpp_lire({a(0) if exprs else 'NULL'})", "str"),
            "lire_entier":  lambda: (f"fpp_lire_entier({a(0) if exprs else 'NULL'})", "ll"),
            "lire_decimal": lambda: (f"fpp_lire_decimal({a(0) if exprs else 'NULL'})", "dbl"),
            "somme":        lambda: (f"/* somme TODO */0.0", "dbl"),
            "type":         lambda: (f'"/* type */"', "str"),
            "effacer":      lambda: ('(system("clear"), 0)', "int"),
            "lire_fichier": lambda: self._builtin_lire_fichier(a(0)),
            "ecrire_fichier": lambda: self._builtin_ecrire_fichier(a(0), a(1)),
        }

        if nom in builtins:
            return builtins[nom]()

        # Fonction utilisateur (retourne double)
        args_str = ", ".join(f"(double)({e})" for e in exprs)
        return (f"{nom}({args_str})", "dbl")

    def _expr_methode(self, n: AppelFonction, scope):
        obj_expr, obj_tc = self._eval_expr(n.arguments[0], scope)
        methode = n.arguments[1].valeur  # TexteLitteral
        extra_args = [(self._eval_expr(a, scope)) for a in n.arguments[2:]]
        eargs = [e for e, _ in extra_args]
        etcs  = [t for _, t in extra_args]

        def a(i): return eargs[i] if i < len(eargs) else ""

        # Méthodes sur texte
        if obj_tc == "str":
            m = {
                "longueur":         lambda: (f"((long long)strlen({obj_expr}))", "ll"),
                "majuscule":        lambda: (f"fpp_majuscule({obj_expr})", "str"),
                "minuscule":        lambda: (f"fpp_minuscule({obj_expr})", "str"),
                "capitaliser":      lambda: (f"fpp_majuscule({obj_expr})", "str"),  # simplifié
                "supprimer_espaces":lambda: (f"fpp_trim({obj_expr})", "str"),
                "contient":         lambda: (f"(strstr({obj_expr}, {a(0)}) != NULL)", "int"),
                "remplacer":        lambda: (f"fpp_remplacer({obj_expr}, {a(0)}, {a(1)})", "str"),
                "commencer_par":    lambda: (f"fpp_commence_par({obj_expr}, {a(0)})", "int"),
                "finir_par":        lambda: (f"fpp_finit_par({obj_expr}, {a(0)})", "int"),
                "vide":             lambda: (f"(strlen(fpp_trim({obj_expr})) == 0)", "int"),
            }
            fn = m.get(methode)
            if fn:
                return fn()
            raise ErreurCompilation(f"Méthode texte inconnue: '{methode}'")

        # Méthodes sur liste
        if obj_tc == "lst":
            m = {
                "longueur":  lambda: (f"((long long)({obj_expr})->taille)", "ll"),
                "vide":      lambda: (f"(({obj_expr})->taille == 0)", "int"),
                "contient":  lambda: (f"/* contient TODO */0", "int"),
                "pop":       lambda: (f"(*(double*)fpp_liste_pop({obj_expr}))", "dbl"),
                "ajouter":   lambda: self._methode_liste_ajouter(obj_expr, a(0), etcs[0] if etcs else "dbl"),
                "trier":     lambda: (f"/* trier TODO */(void)0", "int"),
                "inverser":  lambda: (f"/* inverser TODO */(void)0", "int"),
            }
            fn = m.get(methode)
            if fn:
                return fn()
            raise ErreurCompilation(f"Méthode liste inconnue: '{methode}'")

        raise ErreurCompilation(
            f"Méthode '.{methode}()' non supportée sur ce type ({obj_tc})"
        )

    def _methode_liste_ajouter(self, lst_expr, val_expr, val_tc):
        # On génère du code inline comme instruction (pas expression pure)
        # Mais on est dans _eval_expr... on écrit du code inline avec virgule-operator
        tmp = self._tmp()
        # On ne peut pas écrire plusieurs lignes ici facilement
        # → on retourne une expression qui appelle fpp_liste_ajouter
        # et on pré-génère un tmp dans le scope courant via un truc C
        # La vraie solution : on génère l'instruction dans _instr_ExprInstruction
        # Pour simplifier : retourner l'expression d'ajout en une seule ligne C
        # en utilisant une fonction helper inline
        return (
            f"(fpp_liste_ajouter_dbl({lst_expr}, {val_expr}), 0)",
            "int"
        )

    def _expr_AccesIndex(self, n: AccesIndex, scope):
        obj_expr, obj_tc = self._eval_expr(n.objet, scope)
        idx_expr, idx_tc = self._eval_expr(n.index, scope)
        if obj_tc == "lst":
            return (f"(*(double*)fpp_liste_obtenir({obj_expr}, {idx_expr}))", "dbl")
        if obj_tc == "str":
            # Accès à un caractère : retourne char* d'un seul char
            tmp = self._tmp()
            # On ne peut pas allouer ici dans une expression...
            # On retourne une expression qui extrait le char (char → char* via helper)
            return (f"fpp_char_vers_texte(({obj_expr})[{idx_expr}])", "str")
        return (f"{obj_expr}[{idx_expr}]", "dbl")

    def _expr_ListeLitterale(self, n: ListeLitterale, scope):
        # On ne peut pas créer une liste dans une expression pure en C
        # On génère le code de construction et on retourne le nom de la variable
        tmp = self._tmp()
        self._w(f"FppListe* {tmp} = fpp_liste_creer();")
        for elem in n.elements:
            e_expr, e_tc = self._eval_expr(elem, scope)
            etmp = self._tmp()
            self._w(f"double* {etmp} = malloc(sizeof(double));")
            self._w(f"*{etmp} = (double)({e_expr});")
            self._w(f"fpp_liste_ajouter({tmp}, {etmp});")
        return (tmp, "lst")

    def _expr_DictLitteral(self, n: DictLitteral, scope):
        return ("NULL /* dict */", "dct")

    def _expr_Lire(self, n: Lire, scope):
        prompt = self._eval_expr(n.prompt, scope)[0] if n.prompt else '""'
        if n.mode == "entier":
            return (f"fpp_lire_entier({prompt})", "ll")
        if n.mode == "decimal":
            return (f"fpp_lire_decimal({prompt})", "dbl")
        return (f"fpp_lire({prompt})", "str")

    # ── Utilitaires de type ───────────────────────────────────────────────────

    def _inferer_tc(self, noeud, scope: Scope = None) -> str:
        if isinstance(noeud, NombreLitteral):
            return "dbl" if isinstance(noeud.valeur, float) else "ll"
        if isinstance(noeud, TexteLitteral):
            return "str"
        if isinstance(noeud, BoolLitteral):
            return "int"
        if isinstance(noeud, ListeLitterale):
            return "lst"
        if isinstance(noeud, Identifiant) and scope:
            return scope.type_de(noeud.nom) or "dbl"
        return "dbl"

    def _coercer(self, expr: str, src: str, dst: str, ligne: int = 0) -> str:
        if src == dst:
            return expr
        if dst == "dbl":
            return f"(double)({expr})"
        if dst == "ll":
            return f"(long long)({expr})"
        if dst == "int":
            return f"(int)(({expr}) != 0)"
        if dst == "str":
            if src == "ll":
                return f"fpp_entier_vers_texte({expr})"
            if src == "dbl":
                return f"fpp_decimal_vers_texte({expr})"
            if src == "int":
                return f"fpp_bool_vers_texte({expr})"
        return expr

    def _defaut_c(self, tc: str) -> str:
        return {"ll": "0LL", "dbl": "0.0", "str": '""', "int": "0", "lst": "fpp_liste_creer()", "dct": "NULL"}.get(tc, "0")

    def _builtin_lire_fichier(self, chemin_expr):
        return (
            f"/* lire_fichier: voir man fopen */ NULL",
            "str"
        )

    def _builtin_ecrire_fichier(self, chemin_expr, contenu_expr):
        return (
            f"(fprintf(fopen({chemin_expr},\"w\"), \"%s\", {contenu_expr}), 0)",
            "int"
        )
