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

/* Supprime "-Wunused-function" pour les helpers du runtime qui ne sont
   pas tous appelés selon le programme compilé.                          */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#pragma GCC diagnostic ignored "-Wunused-variable"

/* ── Gestionnaire mémoire automatique ────────────────────────── */

static void**  _fpp_ptrs      = NULL;
static size_t  _fpp_nptrs     = 0;
static size_t  _fpp_ptrs_cap  = 0;

static void _fpp_track(void* p) {
    if (!p) return;
    if (_fpp_nptrs >= _fpp_ptrs_cap) {
        size_t nc = _fpp_ptrs_cap ? _fpp_ptrs_cap * 2 : 256;
        void** t = realloc(_fpp_ptrs, nc * sizeof(void*));
        if (!t) return; /* best effort */
        _fpp_ptrs     = t;
        _fpp_ptrs_cap = nc;
    }
    _fpp_ptrs[_fpp_nptrs++] = p;
}

/* ── Chaînes ──────────────────────────────────────────────────── */

static char* fpp_strdup(const char* s) {
    char* r = strdup(s ? s : "");
    _fpp_track(r);
    return r;
}

static char* fpp_concat(const char* a, const char* b) {
    size_t la = strlen(a), lb = strlen(b);
    char* r = malloc(la + lb + 1);
    if (!r) { perror("malloc"); exit(1); }
    memcpy(r, a, la);
    memcpy(r + la, b, lb + 1);
    _fpp_track(r);
    return r;
}

static char* fpp_entier_vers_texte(long long v) {
    char* s = malloc(32);
    if (!s) { perror("malloc"); exit(1); }
    snprintf(s, 32, "%lld", v);
    _fpp_track(s);
    return s;
}

static char* fpp_decimal_vers_texte(double v) {
    char* s = malloc(64);
    if (!s) { perror("malloc"); exit(1); }
    snprintf(s, 64, "%g", v);
    _fpp_track(s);
    return s;
}

static char* fpp_bool_vers_texte(int v) {
    return fpp_strdup(v ? "vrai" : "faux"); /* tracké via fpp_strdup */
}

static char* fpp_trim(const char* s) {
    while (isspace((unsigned char)*s)) s++;
    if (*s == '\0') return fpp_strdup("");
    const char* end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) end--;
    size_t len = (size_t)(end - s + 1);
    char* r = malloc(len + 1);
    if (!r) { perror("malloc"); exit(1); }
    memcpy(r, s, len);
    r[len] = '\0';
    _fpp_track(r);
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
    size_t la = strlen(ancien), ln = strlen(nouveau), ls = strlen(s);
    /* Compter les occurrences pour allouer exactement la bonne taille */
    size_t count = 0;
    const char* p = s;
    while ((p = strstr(p, ancien)) != NULL) { count++; p += la; }
    size_t new_len = ls + count * ln - count * la;
    char* result = malloc(new_len + 1);
    if (!result) { perror("malloc"); exit(1); }
    char* out = result;
    p = s;
    while (*p) {
        if (strncmp(p, ancien, la) == 0) {
            memcpy(out, nouveau, ln);
            out += ln;
            p   += la;
        } else {
            *out++ = *p++;
        }
    }
    *out = '\0';
    _fpp_track(result);
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

static char* fpp_char_vers_texte(char c) {
    char* s = malloc(2);
    if (!s) { perror("malloc"); exit(1); }
    s[0] = c; s[1] = '\0';
    _fpp_track(s);
    return s;
}

/* ── Listes dynamiques ────────────────────────────────────────── */

typedef struct {
    void** elements;
    int    taille;
    int    capacite;
    int    type; /* 0=mixte,1=entier,2=decimal,3=texte */
} FppListe;

static FppListe** _fpp_listes     = NULL;
static size_t     _fpp_nlistes    = 0;
static size_t     _fpp_listes_cap = 0;

static void _fpp_track_liste(FppListe* l) {
    if (!l) return;
    if (_fpp_nlistes >= _fpp_listes_cap) {
        size_t nc = _fpp_listes_cap ? _fpp_listes_cap * 2 : 64;
        FppListe** t = realloc(_fpp_listes, nc * sizeof(FppListe*));
        if (!t) return;
        _fpp_listes     = t;
        _fpp_listes_cap = nc;
    }
    _fpp_listes[_fpp_nlistes++] = l;
}

static void fpp_liste_detruire(FppListe* l) {
    if (!l) return;
    for (int i = 0; i < l->taille; i++) {
        /* type=3 → char*, type=2 ou 0 → double*, type=1 → long long* */
        free(l->elements[i]);
    }
    free(l->elements);
    free(l);
}

static FppListe* fpp_liste_creer(void) {
    FppListe* l = malloc(sizeof(FppListe));
    if (!l) { perror("malloc"); exit(1); }
    l->elements = malloc(8 * sizeof(void*));
    if (!l->elements) { perror("malloc"); exit(1); }
    l->taille   = 0;
    l->capacite = 8;
    l->type     = 0;
    _fpp_track_liste(l);
    return l;
}

static void fpp_liste_ajouter(FppListe* l, void* val) {
    if (l->taille >= l->capacite) {
        l->capacite *= 2;
        void** tmp = realloc(l->elements, (size_t)l->capacite * sizeof(void*));
        if (!tmp) { perror("realloc"); exit(1); }
        l->elements = tmp;
    }
    l->elements[l->taille++] = val;
}

static void* fpp_liste_obtenir(FppListe* l, long long idx) {
    if (idx < 0) idx = (long long)l->taille + idx;
    if (idx < 0 || idx >= (long long)l->taille) {
        fprintf(stderr, "F++: index %lld hors bornes (taille=%d)\n", idx, l->taille);
        exit(1);
    }
    return l->elements[(int)idx];
}

static void fpp_liste_definir(FppListe* l, long long idx, void* val) {
    if (idx < 0) idx = (long long)l->taille + idx;
    if (idx < 0 || idx >= (long long)l->taille) {
        fprintf(stderr, "F++: index %lld hors bornes (taille=%d)\n", idx, l->taille);
        exit(1);
    }
    free(l->elements[(int)idx]); /* libère l'ancien élément */
    l->elements[(int)idx] = val;
}

static void fpp_liste_supprimer_index(FppListe* l, long long idx) {
    if (idx < 0) idx = (long long)l->taille + idx;
    if (idx < 0 || idx >= (long long)l->taille) return;
    free(l->elements[(int)idx]);
    for (long long i = idx; i < (long long)l->taille - 1; i++)
        l->elements[(int)i] = l->elements[(int)(i + 1)];
    l->taille--;
}

static void* fpp_liste_pop(FppListe* l) {
    if (l->taille == 0) { fprintf(stderr, "F++: pop sur liste vide\n"); exit(1); }
    return l->elements[--l->taille];
}

static int fpp_cmp_ll(const void* a, const void* b) {
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);
}
static int fpp_cmp_dbl(const void* a, const void* b) {
    double x = *(const double*)a, y = *(const double*)b;
    return (x > y) - (x < y);
}
static int fpp_cmp_str(const void* a, const void* b) {
    return strcmp(*(const char* const*)a, *(const char* const*)b);
}

static void fpp_liste_afficher(FppListe* l, int type_elem) {
    printf("[");
    for (int i = 0; i < l->taille; i++) {
        if (i) printf(", ");
        if      (type_elem == 1) printf("%lld", *(const long long*)l->elements[i]);
        else if (type_elem == 2) printf("%g",   *(const double*)l->elements[i]);
        else if (type_elem == 3) printf("%s",   (const char*)l->elements[i]);
        else                     printf("?");
    }
    printf("]");
}

static void fpp_liste_ajouter_dbl(FppListe* l, double val) {
    double* p = malloc(sizeof(double));
    if (!p) { perror("malloc"); exit(1); }
    *p = val;
    fpp_liste_ajouter(l, p);
}

/* Alloue un double sur le tas (pour fpp_liste_definir) */
static double* fpp_dbl_alloc(double val) {
    double* p = malloc(sizeof(double));
    if (!p) { perror("malloc"); exit(1); }
    *p = val;
    return p;
}

/* ── Listes de chaînes (type=3) ───────────────────────────────── */

/* Ajoute une COPIE non-trackée de s dans la liste (la liste en est propriétaire) */
static void fpp_liste_ajouter_str(FppListe* l, const char* s) {
    char* copy = strdup(s ? s : "");
    if (!copy) { perror("strdup"); exit(1); }
    l->type = 3;
    fpp_liste_ajouter(l, copy);
}

static char* fpp_liste_obtenir_str(FppListe* l, long long idx) {
    return (char*)fpp_liste_obtenir(l, idx);
}

/* Découpe s selon sep et retourne une FppListe* de char* (type=3) */
static FppListe* fpp_diviser(const char* s, const char* sep) {
    FppListe* l = fpp_liste_creer();
    l->type = 3;
    if (!s || !sep || !*sep) {
        fpp_liste_ajouter_str(l, s ? s : "");
        return l;
    }
    size_t lsep = strlen(sep);
    const char* p = s;
    while (1) {
        const char* found = strstr(p, sep);
        if (!found) {
            fpp_liste_ajouter_str(l, p);
            break;
        }
        size_t len = (size_t)(found - p);
        char* tok = malloc(len + 1);
        if (!tok) { perror("malloc"); exit(1); }
        memcpy(tok, p, len);
        tok[len] = '\0';
        fpp_liste_ajouter(l, tok);  /* tok non-tracké, détenu par la liste */
        p = found + lsep;
    }
    return l;
}

static int _fpp_cmp_str_ptr(const void* a, const void* b) {
    return strcmp(*(const char* const*)a, *(const char* const*)b);
}

static void fpp_liste_trier_str(FppListe* l) {
    qsort(l->elements, (size_t)l->taille, sizeof(void*), _fpp_cmp_str_ptr);
}

static void fpp_liste_trier_dbl(FppListe* l) {
    /* trie en place les double* stockés dans la liste */
    for (int i = 0; i < l->taille - 1; i++) {
        for (int j = i + 1; j < l->taille; j++) {
            double a = *(double*)l->elements[i];
            double b = *(double*)l->elements[j];
            if (a > b) {
                void* tmp = l->elements[i];
                l->elements[i] = l->elements[j];
                l->elements[j] = tmp;
            }
        }
    }
}

/* Représentation textuelle d'une liste pour afficher() */
static char* fpp_liste_vers_texte(FppListe* l) {
    if (!l || l->taille == 0) {
        char* r = strdup("[]");
        _fpp_track(r);
        return r;
    }
    /* Première passe : calcul de la taille totale */
    size_t total = 3; /* "[\0" + "]" */
    for (int i = 0; i < l->taille; i++) {
        if (i) total += 2; /* ", " */
        if (l->type == 3)       total += strlen((char*)l->elements[i]);
        else if (l->type == 1)  total += 24;
        else                    total += 32;
    }
    char* buf = malloc(total);
    if (!buf) { perror("malloc"); exit(1); }
    size_t pos = 0;
    buf[pos++] = '[';
    for (int i = 0; i < l->taille; i++) {
        if (i) { buf[pos++] = ','; buf[pos++] = ' '; }
        if (l->type == 3) {
            const char* s = (const char*)l->elements[i];
            size_t ls = strlen(s);
            memcpy(buf + pos, s, ls);
            pos += ls;
        } else if (l->type == 1) {
            pos += (size_t)snprintf(buf + pos, total - pos, "%lld", *(long long*)l->elements[i]);
        } else {
            double v = *(double*)l->elements[i];
            if (v == (long long)v)
                pos += (size_t)snprintf(buf + pos, total - pos, "%lld", (long long)v);
            else
                pos += (size_t)snprintf(buf + pos, total - pos, "%g", v);
        }
    }
    buf[pos++] = ']';
    buf[pos]   = '\0';
    _fpp_track(buf);
    return buf;
}

/* ── Dictionnaires ────────────────────────────────────────────── */

typedef struct FppDictEntree {
    char*               cle;
    char*               val_str;  /* != NULL si valeur texte */
    double              val_num;  /* sinon numérique          */
    int                 est_str;
    struct FppDictEntree* suivant;
} FppDictEntree;

typedef struct {
    FppDictEntree** buckets;
    int             nb_buckets;
    int             taille;
} FppDict;

static FppDict** _fpp_dicts     = NULL;
static size_t    _fpp_ndicts    = 0;
static size_t    _fpp_dicts_cap = 0;

static unsigned int _fpp_hash(const char* s, int nb) {
    unsigned int h = 5381;
    while (*s) h = h * 33 ^ (unsigned char)*s++;
    return h % (unsigned int)nb;
}

static void _fpp_track_dict(FppDict* d) {
    if (!d) return;
    if (_fpp_ndicts >= _fpp_dicts_cap) {
        size_t nc = _fpp_dicts_cap ? _fpp_dicts_cap * 2 : 16;
        FppDict** t = realloc(_fpp_dicts, nc * sizeof(FppDict*));
        if (!t) return;
        _fpp_dicts     = t;
        _fpp_dicts_cap = nc;
    }
    _fpp_dicts[_fpp_ndicts++] = d;
}

static FppDict* fpp_dict_creer(void) {
    FppDict* d = malloc(sizeof(FppDict));
    if (!d) { perror("malloc"); exit(1); }
    d->nb_buckets = 16;
    d->taille     = 0;
    d->buckets    = calloc((size_t)d->nb_buckets, sizeof(FppDictEntree*));
    if (!d->buckets) { perror("calloc"); exit(1); }
    _fpp_track_dict(d);
    return d;
}

static void fpp_dict_definir_str(FppDict* d, const char* cle, const char* val) {
    unsigned int h = _fpp_hash(cle, d->nb_buckets);
    FppDictEntree* e = d->buckets[h];
    while (e) { if (strcmp(e->cle, cle) == 0) { free(e->val_str); e->val_str = strdup(val); e->est_str = 1; return; } e = e->suivant; }
    FppDictEntree* n = malloc(sizeof(FppDictEntree));
    if (!n) { perror("malloc"); exit(1); }
    n->cle = strdup(cle); n->val_str = strdup(val); n->val_num = 0; n->est_str = 1;
    n->suivant = d->buckets[h]; d->buckets[h] = n; d->taille++;
}

static void fpp_dict_definir_num(FppDict* d, const char* cle, double val) {
    unsigned int h = _fpp_hash(cle, d->nb_buckets);
    FppDictEntree* e = d->buckets[h];
    while (e) { if (strcmp(e->cle, cle) == 0) { if (e->est_str) { free(e->val_str); e->val_str = NULL; } e->val_num = val; e->est_str = 0; return; } e = e->suivant; }
    FppDictEntree* n = malloc(sizeof(FppDictEntree));
    if (!n) { perror("malloc"); exit(1); }
    n->cle = strdup(cle); n->val_str = NULL; n->val_num = val; n->est_str = 0;
    n->suivant = d->buckets[h]; d->buckets[h] = n; d->taille++;
}

/* Retourne la valeur comme char* (alloué tracké) */
static char* fpp_dict_obtenir_str(FppDict* d, const char* cle) {
    unsigned int h = _fpp_hash(cle, d->nb_buckets);
    FppDictEntree* e = d->buckets[h];
    while (e) {
        if (strcmp(e->cle, cle) == 0) {
            if (e->est_str) return fpp_strdup(e->val_str);
            char* buf = malloc(32); if (!buf) { perror("malloc"); exit(1); }
            if (e->val_num == (long long)e->val_num) snprintf(buf, 32, "%lld", (long long)e->val_num);
            else snprintf(buf, 32, "%g", e->val_num);
            _fpp_track(buf); return buf;
        }
        e = e->suivant;
    }
    return fpp_strdup("");
}

static double fpp_dict_obtenir_num(FppDict* d, const char* cle) {
    unsigned int h = _fpp_hash(cle, d->nb_buckets);
    FppDictEntree* e = d->buckets[h];
    while (e) { if (strcmp(e->cle, cle) == 0) return e->est_str ? 0.0 : e->val_num; e = e->suivant; }
    return 0.0;
}

static FppListe* fpp_dict_cles(FppDict* d) {
    FppListe* l = fpp_liste_creer(); l->type = 3;
    for (int i = 0; i < d->nb_buckets; i++) {
        FppDictEntree* e = d->buckets[i];
        while (e) { fpp_liste_ajouter_str(l, e->cle); e = e->suivant; }
    }
    return l;
}

static FppListe* fpp_dict_valeurs(FppDict* d) {
    FppListe* l = fpp_liste_creer(); l->type = 3;
    for (int i = 0; i < d->nb_buckets; i++) {
        FppDictEntree* e = d->buckets[i];
        while (e) {
            if (e->est_str) { fpp_liste_ajouter_str(l, e->val_str); }
            else { char buf[32]; if (e->val_num==(long long)e->val_num) snprintf(buf,32,"%lld",(long long)e->val_num); else snprintf(buf,32,"%g",e->val_num); fpp_liste_ajouter_str(l, buf); }
            e = e->suivant;
        }
    }
    return l;
}

static void fpp_dict_detruire(FppDict* d) {
    if (!d) return;
    for (int i = 0; i < d->nb_buckets; i++) {
        FppDictEntree* e = d->buckets[i];
        while (e) { FppDictEntree* n = e->suivant; free(e->cle); free(e->val_str); free(e); e = n; }
    }
    free(d->buckets); free(d);
}



static char* fpp_lire(const char* prompt) {
    if (prompt && *prompt) { printf("%s", prompt); fflush(stdout); }
    char* buf = malloc(4096);
    if (!buf) { perror("malloc"); exit(1); }
    if (!fgets(buf, 4096, stdin)) { buf[0] = '\0'; }
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') buf[len - 1] = '\0';
    _fpp_track(buf);
    return buf;
}

static long long fpp_lire_entier(const char* prompt) {
    char* s = fpp_lire(prompt); /* tracké, libéré par fpp_cleanup */
    return atoll(s);
}

static double fpp_lire_decimal(const char* prompt) {
    char* s = fpp_lire(prompt); /* tracké, libéré par fpp_cleanup */
    return atof(s);
}

/* ── Maths / utilitaires ──────────────────────────────────────── */

static int fpp_rand_init = 0;

static long long fpp_hasard_entier(long long a, long long b) {
    if (!fpp_rand_init) { srand((unsigned int)time(NULL)); fpp_rand_init = 1; }
    if (b < a) { long long t = a; a = b; b = t; }
    return a + (long long)((unsigned int)rand() % (unsigned long long)(b - a + 1));
}

static double fpp_hasard(void) {
    if (!fpp_rand_init) { srand((unsigned int)time(NULL)); fpp_rand_init = 1; }
    return (double)rand() / (double)RAND_MAX;
}

static double fpp_hasard_intervalle(double a, double b) {
    return a + fpp_hasard() * (b - a);
}

/* ── Nettoyage automatique (appelé via atexit) ────────────────── */

static void fpp_cleanup(void) {
    for (size_t i = 0; i < _fpp_nlistes; i++)
        fpp_liste_detruire(_fpp_listes[i]);
    free(_fpp_listes);
    _fpp_listes     = NULL;
    _fpp_nlistes    = 0;
    _fpp_listes_cap = 0;

    for (size_t i = 0; i < _fpp_ndicts; i++)
        fpp_dict_detruire(_fpp_dicts[i]);
    free(_fpp_dicts);
    _fpp_dicts     = NULL;
    _fpp_ndicts    = 0;
    _fpp_dicts_cap = 0;

    for (size_t i = 0; i < _fpp_nptrs; i++)
        free(_fpp_ptrs[i]);
    free(_fpp_ptrs);
    _fpp_ptrs     = NULL;
    _fpp_nptrs    = 0;
    _fpp_ptrs_cap = 0;
}

#pragma GCC diagnostic pop

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
    "ll":      "long long",
    "dbl":     "double",
    "str":     "char*",
    "int":     "int",
    "lst":     "FppListe*",
    "lst_str": "FppListe*",
    "dct":     "FppDict*",
}


class CodegenC:
    def __init__(self):
        self.lignes: List[str] = []
        self.indent_n = 0
        self._tmp_cpt = 0
        self._fn_param_types: dict = {}  # nom_fn -> [tc, tc, ...]

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

    # ── Inférence des types de paramètres de fonctions ───────────────────────

    def _inferer_types_params(self, fn: DefFonction, callee_info: dict = None) -> dict:
        """Scan le corps de la fonction pour déduire les types C des paramètres.
        callee_info: dict nom_fn -> [tc, ...] pour la propagation transitive."""
        types: dict = {p: "dbl" for p in fn.parametres}
        if callee_info is None:
            callee_info = {}

        def scan(node):
            if node is None:
                return
            if isinstance(node, OpBinaire):
                # Paramètre comparé à un string literal → c'est un str
                if node.operateur in ("==", "!=", "+"):
                    if isinstance(node.droite, TexteLitteral) and isinstance(node.gauche, Identifiant):
                        if node.gauche.nom in types:
                            types[node.gauche.nom] = "str"
                    if isinstance(node.gauche, TexteLitteral) and isinstance(node.droite, Identifiant):
                        if node.droite.nom in types:
                            types[node.droite.nom] = "str"
            if isinstance(node, AppelFonction):
                if node.nom == "__methode__" and len(node.arguments) >= 2:
                    # Méthode de liste appelée sur un paramètre
                    obj = node.arguments[0]
                    if isinstance(obj, Identifiant) and obj.nom in types:
                        types[obj.nom] = "lst"
                elif node.nom != "__methode__":
                    # Propagation transitive : si un paramètre est passé
                    # à une fonction connue qui attend lst/str, on l'infère
                    callee = callee_info.get(node.nom, [])
                    for i, arg in enumerate(node.arguments):
                        if isinstance(arg, Identifiant) and arg.nom in types:
                            expected = callee[i] if i < len(callee) else "dbl"
                            if expected in ("lst", "lst_str", "str"):
                                types[arg.nom] = expected
            if isinstance(node, PourDans):
                if isinstance(node.iterable, Identifiant) and node.iterable.nom in types:
                    types[node.iterable.nom] = "lst"
                for instr in node.corps:
                    scan(instr)
                return
            if isinstance(node, AccesIndex):
                if isinstance(node.objet, Identifiant) and node.objet.nom in types:
                    types[node.objet.nom] = "lst"
            # Récursion générique sur tous les champs
            for field in node.__dataclass_fields__:
                child = getattr(node, field)
                if isinstance(child, Noeud):
                    scan(child)
                elif isinstance(child, list):
                    for item in child:
                        if isinstance(item, Noeud):
                            scan(item)
                elif isinstance(child, tuple):
                    for item in child:
                        if isinstance(item, Noeud):
                            scan(item)

        for instr in fn.corps:
            scan(instr)
        return types

    def _signature_fn(self, fn: DefFonction, callee_info: dict = None) -> tuple:
        """Retourne (params_c_str, param_types_dict)."""
        param_types = self._inferer_types_params(fn, callee_info)
        parts = []
        for p in fn.parametres:
            tc = param_types.get(p, "dbl")
            ctype = C_DECL.get(tc, "double")
            parts.append(f"{ctype} {p}")
        params_str = ", ".join(parts) if parts else "void"
        return params_str, param_types

    def generer(self, programme: Programme) -> str:
        self.lignes = [RUNTIME]
        scope_global = Scope()

        # Forward declarations + fonctions
        fonctions = [n for n in programme.instructions if isinstance(n, DefFonction)]
        principal = [n for n in programme.instructions if not isinstance(n, DefFonction)]

        # Prototypes — deux passes pour l'inférence transitive de types
        # Passe 1 : inférence locale (usage direct dans chaque corps)
        for fn in fonctions:
            _, ptypes = self._signature_fn(fn, {})
            self._fn_param_types[fn.nom] = [ptypes.get(p, "dbl") for p in fn.parametres]

        # Passes 2-4 : propagation transitive jusqu'à stabilité
        for _ in range(3):
            prev = {k: list(v) for k, v in self._fn_param_types.items()}
            for fn in fonctions:
                _, ptypes = self._signature_fn(fn, self._fn_param_types)
                self._fn_param_types[fn.nom] = [ptypes.get(p, "dbl") for p in fn.parametres]
            if self._fn_param_types == prev:
                break

        # Émettre les prototypes avec les types stabilisés
        for fn in fonctions:
            params_str, _ = self._signature_fn(fn, self._fn_param_types)
            self._w(f"double {fn.nom}({params_str});")
        if fonctions:
            self._w()

        # Corps des fonctions
        for fn in fonctions:
            self._gen_fonction(fn, scope_global)
            self._w()

        # main
        self._ouvrir("int main(void)")
        self._w("atexit(fpp_cleanup);")
        scope_main = scope_global.enfant()
        for instr in principal:
            self._gen_instr(instr, scope_main)
        self._w("return 0;")
        self._fermer()

        return "\n".join(self.lignes)

    # ── Fonctions ─────────────────────────────────────────────────────────────

    def _gen_fonction(self, n: DefFonction, scope_parent: Scope):
        params_str, param_types = self._signature_fn(n, self._fn_param_types)
        self._ouvrir(f"double {n.nom}({params_str})")
        scope = scope_parent.enfant()
        for p in n.parametres:
            scope.definir(p, param_types.get(p, "dbl"))
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

        # Propager lst_str si la liste littérale contient des strings
        if val_tc == "lst_str":
            tc = "lst_str"

        val_expr = self._coercer(val_expr, val_tc, tc, n.ligne)

        scope.definir(n.nom, tc)
        type_c = C_DECL.get(tc, "double")

        if type_fpp == "const":
            self._w(f"const {type_c} {n.nom} = {val_expr};")
        elif tc in ("lst", "lst_str"):
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
            if obj_tc == "dct":
                if val_tc == "str":
                    self._w(f"fpp_dict_definir_str({obj_expr}, {idx_expr}, {val_expr});")
                else:
                    self._w(f"fpp_dict_definir_num({obj_expr}, {idx_expr}, (double)({val_expr}));")
            elif obj_tc in ("lst", "lst_str"):
                coerced = self._coercer(val_expr, val_tc, 'dbl', n.ligne)
                self._w(f"fpp_liste_definir({obj_expr}, (long long)({idx_expr}), fpp_dbl_alloc({coerced}));")
            else:
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
        elif tc in ("lst", "lst_str"):
            tmp = self._tmp()
            self._w(f'{{ char* {tmp} = fpp_liste_vers_texte({expr}); printf("%s", {tmp}); }}')
        elif tc == "dct":
            self._w(f'printf("[dict]");')
        else:
            self._w(f'printf("%g", (double)({expr}));')

    def _instr_ExprInstruction(self, n: ExprInstruction, scope: Scope):
        expr, _ = self._eval_expr(n.expression, scope)
        self._w(f"(void)({expr});")

    def _instr_Si(self, n: Si, scope: Scope):
        cond, _ = self._eval_expr(n.condition, scope)
        self._ouvrir(f"if ({cond})")
        alors_scope = scope.enfant()
        for instr in n.alors:
            self._gen_instr(instr, alors_scope)
        self._fermer()
        for cond_si, bloc in n.sinon_si:
            c, _ = self._eval_expr(cond_si, scope)
            self._ouvrir(f"else if ({c})")
            sinonsi_scope = scope.enfant()
            for instr in bloc:
                self._gen_instr(instr, sinonsi_scope)
            self._fermer()
        if n.sinon is not None:
            self._ouvrir("else")
            sinon_scope = scope.enfant()
            for instr in n.sinon:
                self._gen_instr(instr, sinon_scope)
            self._fermer()

    def _instr_TantQue(self, n: TantQue, scope: Scope):
        cond, _ = self._eval_expr(n.condition, scope)
        self._ouvrir(f"while ({cond})")
        corps_scope = scope.enfant()
        for instr in n.corps:
            self._gen_instr(instr, corps_scope)
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
        if obj_tc == "lst_str":
            sous.definir(n.variable, "str")
            self._ouvrir(f"for (int {idx} = 0; {idx} < ({obj_expr})->taille; {idx}++)")
            self._w(f"char* {n.variable} = fpp_liste_obtenir_str({obj_expr}, {idx});")
            for instr in n.corps:
                self._gen_instr(instr, sous)
            self._fermer()
        elif obj_tc == "lst":
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
            if tc == "str":
                self._w(f"return (double)0.0; /* retourner texte non supporté ici */")
            elif expr in ("NULL", "0LL") and tc in ("str", "ll"):
                self._w("return (double)NAN;")
            else:
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
            # Si l'un des deux est NULL (nul), comparer avec isnan pour les doubles
            if g == "NULL" and gtc == "str" and dtc == "dbl":
                return (f"(isnan({d}))" if op == "==" else f"(!isnan({d}))", "int")
            if d == "NULL" and dtc == "str" and gtc == "dbl":
                return (f"(isnan({g}))" if op == "==" else f"(!isnan({g}))", "int")
            cmp = f"strcmp({g}, {d})"
            return (f"({cmp} == 0)" if op == "==" else f"({cmp} != 0)", "int")

        if op == "%":
            return (f"((long long)({g}) % (long long)({d}))", "ll")

        cops = {"+":"+", "-":"-", "*":"*", "/":"/",
                "==":"==", "!=":"!=", "<":"<", ">":">", "<=":"<=", ">=":">="}
        cop = cops.get(op, op)
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
            "entier":  lambda: (
                f"((long long)(atoll({a(0)})))" if tcs and tcs[0]=="str" else
                f"((long long)({a(0)}))", "ll"
            ),
            "decimal": lambda: (
                f"(atof({a(0)}))" if tcs and tcs[0]=="str" else
                f"((double)({a(0)}))", "dbl"
            ),
            "bool":    lambda: (f"(({a(0)}) != 0)", "int"),
            "texte":   lambda: (
                (f"fpp_entier_vers_texte({a(0)})" if tcs[0]=="ll" else
                 f"fpp_decimal_vers_texte({a(0)})" if tcs[0]=="dbl" else
                 f"fpp_bool_vers_texte({a(0)})" if tcs[0]=="int" else
                 a(0)),
                "str"
            ),
            "longueur": lambda: (f"((long long)strlen({a(0)}))", "ll") if tcs and tcs[0]=="str" else
                                 (f"((long long)({a(0)})->taille)", "ll"),            "lire":         lambda: (f"fpp_lire({a(0) if exprs else 'NULL'})", "str"),
            "lire_entier":  lambda: (f"fpp_lire_entier({a(0) if exprs else 'NULL'})", "ll"),
            "lire_decimal": lambda: (f"fpp_lire_decimal({a(0) if exprs else 'NULL'})", "dbl"),
            "somme":        lambda: (f"/* somme TODO */0.0", "dbl"),
            "type":         lambda: (f'"/* type */"', "str"),
            "effacer":      lambda: ('((void)system("clear"), 0LL)', "ll"),
            "lire_fichier": lambda: self._builtin_lire_fichier(a(0)),
            "ecrire_fichier": lambda: self._builtin_ecrire_fichier(a(0), a(1)),
        }

        # Fonction utilisateur : priorité sur les builtins
        if nom in self._fn_param_types:
            param_types = self._fn_param_types[nom]
            cast_args = []
            for i, (e, tc) in enumerate(zip(exprs, tcs)):
                expected = param_types[i] if i < len(param_types) else "dbl"
                if expected == "str":
                    cast_args.append(e)
                elif expected in ("lst", "lst_str"):
                    cast_args.append(e)
                else:
                    cast_args.append(f"(double)({e})")
            args_str = ", ".join(cast_args)
            return (f"{nom}({args_str})", "dbl")

        if nom in builtins:
            return builtins[nom]()

        # Fonction utilisateur non encore vue (appel avant définition)
        param_types = []
        cast_args = [f"(double)({e})" for e in exprs]
        args_str = ", ".join(cast_args)
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
                "capitaliser":      lambda: (f"fpp_majuscule({obj_expr})", "str"),
                "supprimer_espaces":lambda: (f"fpp_trim({obj_expr})", "str"),
                "contient":         lambda: (f"(strstr({obj_expr}, {a(0)}) != NULL)", "int"),
                "remplacer":        lambda: (f"fpp_remplacer({obj_expr}, {a(0)}, {a(1)})", "str"),
                "commencer_par":    lambda: (f"fpp_commence_par({obj_expr}, {a(0)})", "int"),
                "finir_par":        lambda: (f"fpp_finit_par({obj_expr}, {a(0)})", "int"),
                "vide":             lambda: (f"(strlen(fpp_trim({obj_expr})) == 0)", "int"),
                "diviser":          lambda: (f"fpp_diviser({obj_expr}, {a(0)})", "lst_str"),
            }
            fn = m.get(methode)
            if fn:
                return fn()
            raise ErreurCompilation(f"Méthode texte inconnue: '{methode}'")

        # Méthodes sur liste (nombres ou strings)
        if obj_tc in ("lst", "lst_str"):
            m = {
                "longueur":  lambda: (f"((long long)({obj_expr})->taille)", "ll"),
                "vide":      lambda: (f"(({obj_expr})->taille == 0)", "int"),
                "contient":  lambda: (f"/* contient TODO */0", "int"),
                "pop":       lambda: (
                    (f"fpp_liste_obtenir_str({obj_expr}, ({obj_expr})->taille - 1)", "str")
                    if obj_tc == "lst_str" else
                    (f"(*(double*)fpp_liste_pop({obj_expr}))", "dbl")
                ),
                "ajouter":   lambda: self._methode_liste_ajouter(obj_expr, a(0), etcs[0] if etcs else "dbl", obj_tc),
                "trier":     lambda: (
                    (f"(fpp_liste_trier_str({obj_expr}), 0LL)", "ll")
                    if obj_tc == "lst_str" else
                    (f"(fpp_liste_trier_dbl({obj_expr}), 0LL)", "ll")
                ),
                "inverser":  lambda: (f"/* inverser TODO */(void)0", "int"),
            }
            fn = m.get(methode)
            if fn:
                return fn()
            raise ErreurCompilation(f"Méthode liste inconnue: '{methode}'")

        # Méthodes sur dict
        if obj_tc == "dct":
            m = {
                "cles":     lambda: (f"fpp_dict_cles({obj_expr})",    "lst_str"),
                "valeurs":  lambda: (f"fpp_dict_valeurs({obj_expr})", "lst_str"),
                "longueur": lambda: (f"((long long)({obj_expr})->taille)", "ll"),
            }
            fn = m.get(methode)
            if fn:
                return fn()
            raise ErreurCompilation(f"Méthode dict inconnue: '{methode}'")

        raise ErreurCompilation(
            f"Méthode '.{methode}()' non supportée sur ce type ({obj_tc})"
        )

    def _methode_liste_ajouter(self, lst_expr, val_expr, val_tc, lst_tc="lst"):
        if lst_tc == "lst_str":
            return (f"(fpp_liste_ajouter_str({lst_expr}, {val_expr}), 0LL)", "ll")
        return (
            f"(fpp_liste_ajouter_dbl({lst_expr}, {val_expr}), 0LL)",
            "ll"
        )

    def _expr_AccesIndex(self, n: AccesIndex, scope):
        obj_expr, obj_tc = self._eval_expr(n.objet, scope)
        idx_expr, _      = self._eval_expr(n.index, scope)
        if obj_tc == "lst_str":
            return (f"fpp_liste_obtenir_str({obj_expr}, (long long)({idx_expr}))", "str")
        if obj_tc == "lst":
            return (f"(*(double*)fpp_liste_obtenir({obj_expr}, (long long)({idx_expr})))", "dbl")
        if obj_tc == "dct":
            return (f"fpp_dict_obtenir_str({obj_expr}, {idx_expr})", "str")
        if obj_tc == "str":
            return (f"fpp_char_vers_texte(({obj_expr})[(int)({idx_expr})])", "str")
        return (f"{obj_expr}[{idx_expr}]", "dbl")

    def _expr_ListeLitterale(self, n: ListeLitterale, scope):
        tmp = self._tmp()
        # Détecter si la liste contient des strings
        is_str = any(isinstance(e, TexteLitteral) for e in n.elements)
        if not is_str and n.elements:
            first_tc = self._inferer_tc(n.elements[0], scope)
            is_str = (first_tc == "str")

        self._w(f"FppListe* {tmp} = fpp_liste_creer();")
        if is_str:
            for elem in n.elements:
                e_expr, _ = self._eval_expr(elem, scope)
                self._w(f"fpp_liste_ajouter_str({tmp}, {e_expr});")
            return (tmp, "lst_str")
        else:
            for elem in n.elements:
                e_expr, e_tc = self._eval_expr(elem, scope)
                self._w(f"fpp_liste_ajouter_dbl({tmp}, (double)({e_expr}));")
            return (tmp, "lst")

    def _expr_DictLitteral(self, n: DictLitteral, scope):
        tmp = self._tmp()
        self._w(f"FppDict* {tmp} = fpp_dict_creer();")
        for cle_noeud, val_noeud in n.paires:
            cle_expr, _     = self._eval_expr(cle_noeud, scope)
            val_expr, val_tc = self._eval_expr(val_noeud, scope)
            if val_tc == "str":
                self._w(f"fpp_dict_definir_str({tmp}, {cle_expr}, {val_expr});")
            else:
                self._w(f"fpp_dict_definir_num({tmp}, {cle_expr}, (double)({val_expr}));")
        return (tmp, "dct")

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
            if any(isinstance(e, TexteLitteral) for e in noeud.elements):
                return "lst_str"
            return "lst"
        if isinstance(noeud, DictLitteral):
            return "dct"
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
        return {"ll": "0LL", "dbl": "0.0", "str": '""', "int": "0",
                "lst": "fpp_liste_creer()", "lst_str": "fpp_liste_creer()",
                "dct": "fpp_dict_creer()"}.get(tc, "0")

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
