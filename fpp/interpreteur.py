"""
Interpréteur F++ — Évalue l'AST.
"""

import math
import random
import os
from typing import Any, Dict, List, Optional
from .ast_noeuds import *


class ErreurExecution(Exception):
    def __init__(self, message, ligne=0, colonne=0):
        super().__init__(f"Erreur ligne {ligne}: {message}")
        self.ligne = ligne
        self.colonne = colonne


class ErreurType(ErreurExecution):
    pass


class SignalRetour(Exception):
    def __init__(self, valeur):
        self.valeur = valeur


class SignalCasser(Exception):
    pass


class SignalContinuer(Exception):
    pass


# ── Environnement (portée des variables) ─────────────────────────────────────

class Environnement:
    def __init__(self, parent: Optional["Environnement"] = None):
        self.vars: Dict[str, Any] = {}
        self.consts: set = set()
        self.parent = parent

    def definir(self, nom: str, valeur: Any, const=False):
        self.vars[nom] = valeur
        if const:
            self.consts.add(nom)

    def assigner(self, nom: str, valeur: Any):
        if nom in self.vars:
            if nom in self.consts:
                raise ErreurExecution(f"Impossible de modifier la constante '{nom}'")
            self.vars[nom] = valeur
            return
        if self.parent:
            self.parent.assigner(nom, valeur)
            return
        raise ErreurExecution(f"Variable '{nom}' non déclarée")

    def obtenir(self, nom: str) -> Any:
        if nom in self.vars:
            return self.vars[nom]
        if self.parent:
            return self.parent.obtenir(nom)
        raise ErreurExecution(f"Variable '{nom}' non définie")

    def existe(self, nom: str) -> bool:
        if nom in self.vars:
            return True
        if self.parent:
            return self.parent.existe(nom)
        return False


# ── Fonctions F++ ─────────────────────────────────────────────────────────────

class FonctionFpp:
    def __init__(self, nom, parametres, corps, fermeture):
        self.nom = nom
        self.parametres = parametres
        self.corps = corps
        self.fermeture = fermeture

    def __repr__(self):
        return f"<fonction {self.nom}>"


# ── Interpréteur ──────────────────────────────────────────────────────────────

class Interpreteur:
    def __init__(self):
        self.global_env = Environnement()
        self._enregistrer_builtins()

    def _enregistrer_builtins(self):
        env = self.global_env
        # Mathématiques
        env.definir("pi", math.pi)
        env.definir("e", math.e)
        env.definir("infini", math.inf)

    # ── Exécution principale ──────────────────────────────────────────────────

    def executer(self, programme: Programme):
        env = self.global_env
        for instr in programme.instructions:
            self._exec(instr, env)

    def _exec(self, noeud: Noeud, env: Environnement):
        methode = f"_exec_{type(noeud).__name__}"
        handler = getattr(self, methode, None)
        if handler is None:
            raise ErreurExecution(f"Nœud inconnu: {type(noeud).__name__}",
                                  noeud.ligne, noeud.colonne)
        return handler(noeud, env)

    def _eval(self, noeud: Noeud, env: Environnement) -> Any:
        methode = f"_eval_{type(noeud).__name__}"
        handler = getattr(self, methode, None)
        if handler is None:
            # Essayer exec comme fallback
            return self._exec(noeud, env)
        return handler(noeud, env)

    # ── Instructions ─────────────────────────────────────────────────────────

    def _exec_Programme(self, noeud: Programme, env: Environnement):
        for instr in noeud.instructions:
            self._exec(instr, env)

    def _exec_Declaration(self, noeud: Declaration, env: Environnement):
        valeur = None
        if noeud.valeur is not None:
            valeur = self._eval(noeud.valeur, env)
            valeur = self._convertir(valeur, noeud.type_var, noeud.ligne)
        else:
            valeur = self._valeur_defaut(noeud.type_var)
        const = noeud.type_var == "const"
        env.definir(noeud.nom, valeur, const=const)

    def _exec_Assignation(self, noeud: Assignation, env: Environnement):
        valeur = self._eval(noeud.valeur, env)
        op = noeud.operateur

        if isinstance(noeud.cible, Identifiant):
            nom = noeud.cible.nom
            if op != "=":
                ancienne = env.obtenir(nom)
                valeur = self._op_compose(ancienne, op, valeur, noeud.ligne)
            env.assigner(nom, valeur)

        elif isinstance(noeud.cible, AccesIndex):
            obj = self._eval(noeud.cible.objet, env)
            idx = self._eval(noeud.cible.index, env)
            if op != "=":
                ancienne = obj[idx]
                valeur = self._op_compose(ancienne, op, valeur, noeud.ligne)
            obj[idx] = valeur
        else:
            raise ErreurExecution("Cible d'assignation invalide", noeud.ligne, noeud.colonne)

    def _exec_Afficher(self, noeud: Afficher, env: Environnement):
        parties = [self._vers_texte(self._eval(a, env)) for a in noeud.arguments]
        print(" ".join(parties))

    def _exec_ExprInstruction(self, noeud: ExprInstruction, env: Environnement):
        self._eval(noeud.expression, env)

    def _exec_Si(self, noeud: Si, env: Environnement):
        if self._est_vrai(self._eval(noeud.condition, env)):
            self._exec_bloc(noeud.alors, env)
        else:
            for cond, bloc in noeud.sinon_si:
                if self._est_vrai(self._eval(cond, env)):
                    self._exec_bloc(bloc, env)
                    return
            if noeud.sinon is not None:
                self._exec_bloc(noeud.sinon, env)

    def _exec_TantQue(self, noeud: TantQue, env: Environnement):
        while self._est_vrai(self._eval(noeud.condition, env)):
            try:
                self._exec_bloc(noeud.corps, env)
            except SignalCasser:
                break
            except SignalContinuer:
                continue

    def _exec_Pour(self, noeud: Pour, env: Environnement):
        debut = self._eval(noeud.debut, env)
        fin = self._eval(noeud.fin, env)
        pas = self._eval(noeud.pas, env) if noeud.pas else 1
        sous_env = Environnement(parent=env)
        sous_env.definir(noeud.variable, debut)
        i = debut
        while (pas > 0 and i <= fin) or (pas < 0 and i >= fin):
            sous_env.assigner(noeud.variable, i)
            try:
                self._exec_bloc(noeud.corps, sous_env)
            except SignalCasser:
                break
            except SignalContinuer:
                pass
            i += pas

    def _exec_PourDans(self, noeud: PourDans, env: Environnement):
        iterable = self._eval(noeud.iterable, env)
        if not hasattr(iterable, "__iter__"):
            raise ErreurExecution("La valeur n'est pas itérable", noeud.ligne, noeud.colonne)
        sous_env = Environnement(parent=env)
        sous_env.definir(noeud.variable, None)
        for element in iterable:
            sous_env.assigner(noeud.variable, element)
            try:
                self._exec_bloc(noeud.corps, sous_env)
            except SignalCasser:
                break
            except SignalContinuer:
                continue

    def _exec_DefFonction(self, noeud: DefFonction, env: Environnement):
        fn = FonctionFpp(noeud.nom, noeud.parametres, noeud.corps, env)
        env.definir(noeud.nom, fn)

    def _exec_Retourner(self, noeud: Retourner, env: Environnement):
        valeur = self._eval(noeud.valeur, env) if noeud.valeur else None
        raise SignalRetour(valeur)

    def _exec_Casser(self, noeud: Casser, env: Environnement):
        raise SignalCasser()

    def _exec_Continuer(self, noeud: Continuer, env: Environnement):
        raise SignalContinuer()

    def _exec_bloc(self, instructions: list, env: Environnement):
        sous_env = Environnement(parent=env)
        for instr in instructions:
            self._exec(instr, sous_env)

    # ── Évaluation des expressions ────────────────────────────────────────────

    def _eval_NombreLitteral(self, noeud: NombreLitteral, env) -> Any:
        return noeud.valeur

    def _eval_TexteLitteral(self, noeud: TexteLitteral, env) -> str:
        return noeud.valeur

    def _eval_BoolLitteral(self, noeud: BoolLitteral, env) -> bool:
        return noeud.valeur

    def _eval_NulLitteral(self, noeud: NulLitteral, env):
        return None

    def _eval_ListeLitterale(self, noeud: ListeLitterale, env) -> list:
        return [self._eval(e, env) for e in noeud.elements]

    def _eval_DictLitteral(self, noeud: DictLitteral, env) -> dict:
        return {self._eval(k, env): self._eval(v, env) for k, v in noeud.paires}

    def _eval_Identifiant(self, noeud: Identifiant, env) -> Any:
        return env.obtenir(noeud.nom)

    def _eval_OpBinaire(self, noeud: OpBinaire, env) -> Any:
        # Court-circuit logique
        if noeud.operateur == "et":
            g = self._eval(noeud.gauche, env)
            if not self._est_vrai(g):
                return False
            return self._est_vrai(self._eval(noeud.droite, env))
        if noeud.operateur == "ou":
            g = self._eval(noeud.gauche, env)
            if self._est_vrai(g):
                return True
            return self._est_vrai(self._eval(noeud.droite, env))

        g = self._eval(noeud.gauche, env)
        d = self._eval(noeud.droite, env)
        op = noeud.operateur

        try:
            if op == "+":
                if isinstance(g, str) or isinstance(d, str):
                    return self._vers_texte(g) + self._vers_texte(d)
                return g + d
            if op == "-": return g - d
            if op == "*":
                if isinstance(g, str) and isinstance(d, int): return g * d
                if isinstance(g, int) and isinstance(d, str): return d * g
                return g * d
            if op == "/":
                if d == 0:
                    raise ErreurExecution("Division par zéro", noeud.ligne, noeud.colonne)
                return g / d
            if op == "%":
                if d == 0:
                    raise ErreurExecution("Modulo par zéro", noeud.ligne, noeud.colonne)
                return g % d
            if op == "**": return g ** d
            if op == "==": return g == d
            if op == "!=": return g != d
            if op == "<":  return g < d
            if op == ">":  return g > d
            if op == "<=": return g <= d
            if op == ">=": return g >= d
        except TypeError as ex:
            raise ErreurType(
                f"Opération '{op}' impossible entre {type(g).__name__} et {type(d).__name__}",
                noeud.ligne, noeud.colonne
            )

        raise ErreurExecution(f"Opérateur inconnu: {op}", noeud.ligne, noeud.colonne)

    def _eval_OpUnaire(self, noeud: OpUnaire, env) -> Any:
        val = self._eval(noeud.operande, env)
        if noeud.operateur == "-": return -val
        if noeud.operateur == "non": return not self._est_vrai(val)
        raise ErreurExecution(f"Opérateur unaire inconnu: {noeud.operateur}")

    def _eval_AppelFonction(self, noeud: AppelFonction, env) -> Any:
        # Méthode d'objet
        if noeud.nom == "__methode__":
            return self._appeler_methode(noeud, env)

        # Fonctions builtin
        builtin = self._obtenir_builtin(noeud.nom)
        if builtin:
            args = [self._eval(a, env) for a in noeud.arguments]
            return builtin(args, noeud.ligne, noeud.colonne)

        # Fonctions définies par l'utilisateur
        fn = env.obtenir(noeud.nom)
        if not isinstance(fn, FonctionFpp):
            raise ErreurExecution(f"'{noeud.nom}' n'est pas une fonction",
                                  noeud.ligne, noeud.colonne)
        if len(noeud.arguments) != len(fn.parametres):
            raise ErreurExecution(
                f"'{noeud.nom}' attend {len(fn.parametres)} argument(s), "
                f"reçu {len(noeud.arguments)}",
                noeud.ligne, noeud.colonne
            )
        fn_env = Environnement(parent=fn.fermeture)
        for param, arg_noeud in zip(fn.parametres, noeud.arguments):
            fn_env.definir(param, self._eval(arg_noeud, env))
        try:
            for instr in fn.corps:
                self._exec(instr, fn_env)
        except SignalRetour as r:
            return r.valeur
        return None

    def _appeler_methode(self, noeud: AppelFonction, env) -> Any:
        # arguments: [objet, nom_methode, ...args]
        objet = self._eval(noeud.arguments[0], env)
        methode = noeud.arguments[1].valeur  # TexteLitteral
        args = [self._eval(a, env) for a in noeud.arguments[2:]]

        # Listes
        if isinstance(objet, list):
            return self._methode_liste(objet, methode, args, noeud.ligne)
        # Texte
        if isinstance(objet, str):
            return self._methode_texte(objet, methode, args, noeud.ligne)
        # Dict
        if isinstance(objet, dict):
            return self._methode_dict(objet, methode, args, noeud.ligne)

        raise ErreurExecution(f"Type sans méthodes: {type(objet).__name__}", noeud.ligne)

    def _methode_liste(self, lst, methode, args, ligne):
        if methode == "ajouter":
            lst.append(args[0]); return None
        if methode == "supprimer":
            lst.remove(args[0]); return None
        if methode == "longueur":
            return len(lst)
        if methode == "trier":
            lst.sort(); return None
        if methode == "inverser":
            lst.reverse(); return None
        if methode == "contient":
            return args[0] in lst
        if methode == "pop":
            return lst.pop() if not args else lst.pop(int(args[0]))
        if methode == "inserer":
            lst.insert(int(args[0]), args[1]); return None
        if methode == "compter":
            return lst.count(args[0])
        if methode == "vide":
            return len(lst) == 0
        raise ErreurExecution(f"Méthode liste inconnue: '{methode}'", ligne)

    def _methode_texte(self, txt, methode, args, ligne):
        if methode == "longueur":
            return len(txt)
        if methode == "majuscule":
            return txt.upper()
        if methode == "minuscule":
            return txt.lower()
        if methode == "capitaliser":
            return txt.capitalize()
        if methode == "contient":
            return str(args[0]) in txt
        if methode == "remplacer":
            return txt.replace(str(args[0]), str(args[1]))
        if methode == "diviser":
            sep = str(args[0]) if args else " "
            return txt.split(sep)
        if methode == "commencer_par":
            return txt.startswith(str(args[0]))
        if methode == "finir_par":
            return txt.endswith(str(args[0]))
        if methode == "supprimer_espaces":
            return txt.strip()
        if methode == "vide":
            return len(txt.strip()) == 0
        raise ErreurExecution(f"Méthode texte inconnue: '{methode}'", ligne)

    def _methode_dict(self, d, methode, args, ligne):
        if methode == "cles":
            return list(d.keys())
        if methode == "valeurs":
            return list(d.values())
        if methode == "contient":
            return args[0] in d
        if methode == "supprimer":
            d.pop(args[0], None); return None
        if methode == "longueur":
            return len(d)
        if methode == "vide":
            return len(d) == 0
        raise ErreurExecution(f"Méthode dict inconnue: '{methode}'", ligne)

    def _eval_AccesIndex(self, noeud: AccesIndex, env) -> Any:
        obj = self._eval(noeud.objet, env)
        idx = self._eval(noeud.index, env)
        try:
            return obj[idx]
        except (IndexError, KeyError) as e:
            raise ErreurExecution(f"Index/clé invalide: {idx}", noeud.ligne, noeud.colonne)
        except TypeError:
            raise ErreurType(f"Type non indexable: {type(obj).__name__}",
                             noeud.ligne, noeud.colonne)

    def _eval_Lire(self, noeud: Lire, env) -> Any:
        prompt = ""
        if noeud.prompt:
            prompt = self._vers_texte(self._eval(noeud.prompt, env))
        valeur = input(prompt)
        if noeud.mode == "entier":
            try:
                return int(valeur)
            except ValueError:
                raise ErreurExecution(f"'{valeur}' n'est pas un entier valide",
                                      noeud.ligne, noeud.colonne)
        if noeud.mode == "decimal":
            try:
                return float(valeur)
            except ValueError:
                raise ErreurExecution(f"'{valeur}' n'est pas un décimal valide",
                                      noeud.ligne, noeud.colonne)
        return valeur

    # ── Fonctions built-in ────────────────────────────────────────────────────

    def _obtenir_builtin(self, nom: str):
        builtins = {
            # Conversion
            "entier": lambda args, l, c: int(args[0]),
            "decimal": lambda args, l, c: float(args[0]),
            "texte": lambda args, l, c: self._vers_texte(args[0]),
            "bool": lambda args, l, c: bool(args[0]),
            # Mathématiques
            "arrondir": lambda args, l, c: round(args[0], int(args[1]) if len(args) > 1 else 0),
            "absolu": lambda args, l, c: abs(args[0]),
            "minimum": lambda args, l, c: min(args),
            "maximum": lambda args, l, c: max(args),
            "racine": lambda args, l, c: math.sqrt(args[0]),
            "puissance": lambda args, l, c: args[0] ** args[1],
            "sinus": lambda args, l, c: math.sin(args[0]),
            "cosinus": lambda args, l, c: math.cos(args[0]),
            "tangente": lambda args, l, c: math.tan(args[0]),
            "logarithme": lambda args, l, c: math.log(args[0]) if len(args) == 1 else math.log(args[0], args[1]),
            "plancher": lambda args, l, c: math.floor(args[0]),
            "plafond": lambda args, l, c: math.ceil(args[0]),
            # Listes / texte
            "longueur": lambda args, l, c: len(args[0]),
            "trier": lambda args, l, c: sorted(args[0]),
            "inverser": lambda args, l, c: list(reversed(args[0])),
            "type": lambda args, l, c: self._nom_type(args[0]),
            "somme": lambda args, l, c: sum(args[0]),
            "enumerer": lambda args, l, c: list(enumerate(args[0])),
            "intervalle": self._builtin_intervalle,
            "hasard": lambda args, l, c: random.random() if not args else random.uniform(args[0], args[1]),
            "hasard_entier": lambda args, l, c: random.randint(int(args[0]), int(args[1])),
            "melanger": lambda args, l, c: (random.shuffle(args[0]), args[0])[1],
            # I/O fichiers
            "lire_fichier": self._builtin_lire_fichier,
            "ecrire_fichier": self._builtin_ecrire_fichier,
            # Divers
            "effacer": lambda args, l, c: os.system("clear"),
            "existe": lambda args, l, c: env.existe(args[0]) if isinstance(args[0], str) else args[0] is not None,
        }
        return builtins.get(nom)

    def _builtin_intervalle(self, args, ligne, colonne):
        if len(args) == 1:
            return list(range(int(args[0])))
        if len(args) == 2:
            return list(range(int(args[0]), int(args[1])))
        return list(range(int(args[0]), int(args[1]), int(args[2])))

    def _builtin_lire_fichier(self, args, ligne, colonne):
        if not args:
            raise ErreurExecution("lire_fichier attend un chemin", ligne, colonne)
        try:
            with open(str(args[0]), "r", encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            raise ErreurExecution(f"Impossible de lire le fichier: {e}", ligne, colonne)

    def _builtin_ecrire_fichier(self, args, ligne, colonne):
        if len(args) < 2:
            raise ErreurExecution("ecrire_fichier attend un chemin et un contenu", ligne, colonne)
        try:
            with open(str(args[0]), "w", encoding="utf-8") as f:
                f.write(self._vers_texte(args[1]))
            return None
        except OSError as e:
            raise ErreurExecution(f"Impossible d'écrire le fichier: {e}", ligne, colonne)

    # ── Utilitaires ───────────────────────────────────────────────────────────

    def _est_vrai(self, valeur) -> bool:
        if valeur is None: return False
        if isinstance(valeur, bool): return valeur
        if isinstance(valeur, (int, float)): return valeur != 0
        if isinstance(valeur, str): return len(valeur) > 0
        if isinstance(valeur, (list, dict)): return len(valeur) > 0
        return True

    def _vers_texte(self, valeur) -> str:
        if valeur is None: return "nul"
        if isinstance(valeur, bool): return "vrai" if valeur else "faux"
        if isinstance(valeur, float):
            if valeur == int(valeur) and not math.isinf(valeur):
                return str(int(valeur)) + ".0"
            return str(valeur)
        if isinstance(valeur, list):
            return "[" + ", ".join(self._vers_texte(e) for e in valeur) + "]"
        if isinstance(valeur, dict):
            paires = ", ".join(
                f"{self._vers_texte(k)}: {self._vers_texte(v)}"
                for k, v in valeur.items()
            )
            return "{" + paires + "}"
        if isinstance(valeur, FonctionFpp):
            return repr(valeur)
        return str(valeur)

    def _convertir(self, valeur, type_var: str, ligne: int) -> Any:
        if type_var == "const":
            return valeur
        conversions = {
            "entier": int,
            "decimal": float,
            "texte": str,
            "bool": bool,
            "liste": list,
            "dict": dict,
        }
        fn = conversions.get(type_var)
        if fn is None:
            return valeur
        try:
            return fn(valeur)
        except (ValueError, TypeError):
            raise ErreurType(
                f"Impossible de convertir '{valeur}' en {type_var}", ligne
            )

    def _valeur_defaut(self, type_var: str) -> Any:
        defaults = {
            "entier": 0,
            "decimal": 0.0,
            "texte": "",
            "bool": False,
            "liste": [],
            "dict": {},
            "const": None,
        }
        return defaults.get(type_var, None)

    def _op_compose(self, ancienne, op: str, valeur, ligne: int) -> Any:
        if op == "+=": return ancienne + valeur
        if op == "-=": return ancienne - valeur
        if op == "*=": return ancienne * valeur
        if op == "/=":
            if valeur == 0:
                raise ErreurExecution("Division par zéro", ligne)
            return ancienne / valeur
        raise ErreurExecution(f"Opérateur composé inconnu: {op}", ligne)

    def _nom_type(self, valeur) -> str:
        if valeur is None: return "nul"
        if isinstance(valeur, bool): return "bool"
        if isinstance(valeur, int): return "entier"
        if isinstance(valeur, float): return "decimal"
        if isinstance(valeur, str): return "texte"
        if isinstance(valeur, list): return "liste"
        if isinstance(valeur, dict): return "dict"
        if isinstance(valeur, FonctionFpp): return "fonction"
        return "inconnu"
