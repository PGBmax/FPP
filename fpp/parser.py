"""
Parser F++ — Transforme les tokens en AST.
"""

from typing import List, Optional
from .lexer import Token, TokenType, Lexer
from .ast_noeuds import *


class ErreurSyntaxique(Exception):
    def __init__(self, message, ligne, colonne):
        super().__init__(f"Erreur syntaxique ligne {ligne}, colonne {colonne}: {message}")
        self.ligne = ligne
        self.colonne = colonne


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.COMMENTAIRE]
        self.pos = 0

    # ── Utilitaires ──────────────────────────────────────────────────────────

    def courant(self) -> Token:
        return self.tokens[self.pos]

    def regarder(self, offset=1) -> Token:
        p = self.pos + offset
        if p < len(self.tokens):
            return self.tokens[p]
        return self.tokens[-1]

    def est(self, *types: TokenType) -> bool:
        return self.courant().type in types

    def consommer(self, *types: TokenType) -> Token:
        t = self.courant()
        if types and t.type not in types:
            attendu = " ou ".join(tt.name for tt in types)
            raise ErreurSyntaxique(
                f"Attendu {attendu}, obtenu '{t.value}' ({t.type.name})",
                t.ligne, t.colonne
            )
        self.pos += 1
        return t

    def ignorer_newlines(self):
        while self.est(TokenType.NEWLINE):
            self.consommer()

    def ligne_col(self) -> tuple:
        t = self.courant()
        return t.ligne, t.colonne

    # ── Point d'entrée ───────────────────────────────────────────────────────

    def analyser(self) -> Programme:
        self.ignorer_newlines()
        instructions = []
        while not self.est(TokenType.EOF):
            instructions.append(self.instruction())
            while self.est(TokenType.NEWLINE):
                self.consommer()
        return Programme(instructions=instructions)

    # ── Instructions ─────────────────────────────────────────────────────────

    def instruction(self) -> Noeud:
        t = self.courant()

        if t.type in (TokenType.ENTIER, TokenType.DECIMAL, TokenType.TEXTE_TYPE,
                      TokenType.BOOL, TokenType.LISTE, TokenType.DICT, TokenType.CONST):
            return self.declaration()

        if t.type == TokenType.AFFICHER:
            return self.inst_afficher()

        if t.type in (TokenType.LIRE, TokenType.LIRE_ENTIER, TokenType.LIRE_DECIMAL):
            return self.inst_lire_seule()

        if t.type == TokenType.SI:
            return self.inst_si()

        if t.type == TokenType.TANTQUE:
            return self.inst_tantque()

        if t.type == TokenType.POUR:
            return self.inst_pour()

        if t.type == TokenType.FONCTION:
            return self.def_fonction()

        if t.type == TokenType.RETOURNER:
            return self.inst_retourner()

        if t.type == TokenType.CASSER:
            self.consommer()
            return Casser(ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.CONTINUER:
            self.consommer()
            return Continuer(ligne=t.ligne, colonne=t.colonne)

        # Assignation ou expression
        return self.assignation_ou_expression()

    def declaration(self) -> Declaration:
        ligne, col = self.ligne_col()
        type_tok = self.consommer()
        type_var = type_tok.value  # "entier", "decimal", "texte", "bool", "liste", "dict", "const"

        # Syntaxe : const entier NOM, const decimal NOM, etc.
        # Le mot-clé de type après "const" est facultatif ; on le consomme s'il est là.
        if type_tok.type == TokenType.CONST:
            if self.courant().type in (TokenType.ENTIER, TokenType.DECIMAL,
                                       TokenType.TEXTE_TYPE, TokenType.BOOL,
                                       TokenType.LISTE, TokenType.DICT):
                self.consommer()   # consomme le type, l'inférence se fait sur la valeur

        nom_tok = self.consommer(TokenType.IDENTIFIANT)
        valeur = None
        if self.est(TokenType.EGAL):
            self.consommer()
            valeur = self.expression()
        return Declaration(type_var=type_var, nom=nom_tok.value, valeur=valeur,
                           ligne=ligne, colonne=col)

    def inst_afficher(self) -> Afficher:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.AFFICHER)
        self.consommer(TokenType.LPAREN)
        args = []
        if not self.est(TokenType.RPAREN):
            args.append(self.expression())
            while self.est(TokenType.VIRGULE):
                self.consommer()
                args.append(self.expression())
        self.consommer(TokenType.RPAREN)
        return Afficher(arguments=args, ligne=ligne, colonne=col)

    def inst_lire_seule(self) -> ExprInstruction:
        ligne, col = self.ligne_col()
        return ExprInstruction(expression=self.expr_lire(), ligne=ligne, colonne=col)

    def inst_si(self) -> Si:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.SI)
        condition = self.expression()
        self.consommer(TokenType.ALORS)
        self.ignorer_newlines()
        alors = self.bloc()
        sinon_si = []
        sinon = None
        while self.est(TokenType.SINON_SI):
            self.consommer()
            cond_si = self.expression()
            self.consommer(TokenType.ALORS)
            self.ignorer_newlines()
            bloc_si = self.bloc()
            sinon_si.append((cond_si, bloc_si))
        if self.est(TokenType.SINON):
            self.consommer()
            self.ignorer_newlines()
            sinon = self.bloc()
        self.consommer(TokenType.FIN)
        return Si(condition=condition, alors=alors, sinon_si=sinon_si, sinon=sinon,
                  ligne=ligne, colonne=col)

    def inst_tantque(self) -> TantQue:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.TANTQUE)
        condition = self.expression()
        self.consommer(TokenType.FAIRE)
        self.ignorer_newlines()
        corps = self.bloc()
        self.consommer(TokenType.FIN)
        return TantQue(condition=condition, corps=corps, ligne=ligne, colonne=col)

    def inst_pour(self) -> Noeud:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.POUR)
        var_tok = self.consommer(TokenType.IDENTIFIANT)

        # pour x dans liste faire ... fin
        if self.est(TokenType.IDENTIFIANT) and self.courant().value == "dans":
            self.consommer()
            iterable = self.expression()
            self.consommer(TokenType.FAIRE)
            self.ignorer_newlines()
            corps = self.bloc()
            self.consommer(TokenType.FIN)
            return PourDans(variable=var_tok.value, iterable=iterable, corps=corps,
                            ligne=ligne, colonne=col)

        # pour x de debut a fin [pas p] faire ... fin
        self.consommer(TokenType.DE)
        debut = self.expression()
        # accepter le token A ou l'identifiant "a"
        if self.est(TokenType.A):
            self.consommer(TokenType.A)
        elif self.est(TokenType.IDENTIFIANT) and self.courant().value == "a":
            self.consommer(TokenType.IDENTIFIANT)
        else:
            t = self.courant()
            raise ErreurSyntaxique(f"Attendu 'a', obtenu '{t.value}'", t.ligne, t.colonne)
        fin = self.expression()
        pas = None
        if self.est(TokenType.IDENTIFIANT) and self.courant().value == "pas":
            self.consommer()
            pas = self.expression()
        self.consommer(TokenType.FAIRE)
        self.ignorer_newlines()
        corps = self.bloc()
        self.consommer(TokenType.FIN)
        return Pour(variable=var_tok.value, debut=debut, fin=fin, pas=pas, corps=corps,
                    ligne=ligne, colonne=col)

    def def_fonction(self) -> DefFonction:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.FONCTION)
        nom_tok = self.consommer(TokenType.IDENTIFIANT)
        self.consommer(TokenType.LPAREN)
        params = []
        if not self.est(TokenType.RPAREN):
            params.append(self.consommer(TokenType.IDENTIFIANT).value)
            while self.est(TokenType.VIRGULE):
                self.consommer()
                params.append(self.consommer(TokenType.IDENTIFIANT).value)
        self.consommer(TokenType.RPAREN)
        self.consommer(TokenType.FAIRE)
        self.ignorer_newlines()
        corps = self.bloc()
        self.consommer(TokenType.FIN)
        return DefFonction(nom=nom_tok.value, parametres=params, corps=corps,
                           ligne=ligne, colonne=col)

    def inst_retourner(self) -> Retourner:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.RETOURNER)
        valeur = None
        if not self.est(TokenType.NEWLINE, TokenType.EOF, TokenType.FIN):
            valeur = self.expression()
        return Retourner(valeur=valeur, ligne=ligne, colonne=col)

    def assignation_ou_expression(self) -> Noeud:
        ligne, col = self.ligne_col()
        expr = self.expression()

        OPS_ASSIGN = {
            TokenType.EGAL: "=",
            TokenType.PLUS_EGAL: "+=",
            TokenType.MOINS_EGAL: "-=",
            TokenType.FOIS_EGAL: "*=",
            TokenType.DIV_EGAL: "/=",
        }
        if self.courant().type in OPS_ASSIGN:
            op = OPS_ASSIGN[self.consommer().type]
            valeur = self.expression()
            return Assignation(cible=expr, operateur=op, valeur=valeur,
                               ligne=ligne, colonne=col)

        return ExprInstruction(expression=expr, ligne=ligne, colonne=col)

    def bloc(self) -> List[Noeud]:
        instructions = []
        fins = {TokenType.FIN, TokenType.SINON, TokenType.SINON_SI, TokenType.EOF}
        while not self.est(*fins):
            if self.est(TokenType.NEWLINE):
                self.consommer()
                continue
            instructions.append(self.instruction())
            while self.est(TokenType.NEWLINE):
                self.consommer()
        return instructions

    # ── Expressions (précédence croissante) ──────────────────────────────────

    def expression(self) -> Noeud:
        return self.expr_ou()

    def expr_ou(self) -> Noeud:
        gauche = self.expr_et()
        while self.est(TokenType.OU):
            ligne, col = self.ligne_col()
            self.consommer()
            droite = self.expr_et()
            gauche = OpBinaire(gauche=gauche, operateur="ou", droite=droite,
                               ligne=ligne, colonne=col)
        return gauche

    def expr_et(self) -> Noeud:
        gauche = self.expr_non()
        while self.est(TokenType.ET):
            ligne, col = self.ligne_col()
            self.consommer()
            droite = self.expr_non()
            gauche = OpBinaire(gauche=gauche, operateur="et", droite=droite,
                               ligne=ligne, colonne=col)
        return gauche

    def expr_non(self) -> Noeud:
        if self.est(TokenType.NON):
            ligne, col = self.ligne_col()
            self.consommer()
            operande = self.expr_non()
            return OpUnaire(operateur="non", operande=operande, ligne=ligne, colonne=col)
        return self.expr_comparaison()

    def expr_comparaison(self) -> Noeud:
        gauche = self.expr_addition()
        OPS = {
            TokenType.EGAL_EGAL: "==",
            TokenType.DIFFERENT: "!=",
            TokenType.INFERIEUR: "<",
            TokenType.SUPERIEUR: ">",
            TokenType.INF_EGAL: "<=",
            TokenType.SUP_EGAL: ">=",
        }
        while self.courant().type in OPS:
            ligne, col = self.ligne_col()
            op = OPS[self.consommer().type]
            droite = self.expr_addition()
            gauche = OpBinaire(gauche=gauche, operateur=op, droite=droite,
                               ligne=ligne, colonne=col)
        return gauche

    def expr_addition(self) -> Noeud:
        gauche = self.expr_multiplication()
        while self.est(TokenType.PLUS, TokenType.MOINS):
            ligne, col = self.ligne_col()
            op = self.consommer().value
            droite = self.expr_multiplication()
            gauche = OpBinaire(gauche=gauche, operateur=op, droite=droite,
                               ligne=ligne, colonne=col)
        return gauche

    def expr_multiplication(self) -> Noeud:
        gauche = self.expr_puissance()
        while self.est(TokenType.FOIS, TokenType.DIVISE, TokenType.MODULO):
            ligne, col = self.ligne_col()
            op = self.consommer().value
            droite = self.expr_puissance()
            gauche = OpBinaire(gauche=gauche, operateur=op, droite=droite,
                               ligne=ligne, colonne=col)
        return gauche

    def expr_puissance(self) -> Noeud:
        gauche = self.expr_unaire()
        if self.est(TokenType.PUISSANCE):
            ligne, col = self.ligne_col()
            self.consommer()
            droite = self.expr_puissance()  # droite-associatif
            return OpBinaire(gauche=gauche, operateur="**", droite=droite,
                             ligne=ligne, colonne=col)
        return gauche

    def expr_unaire(self) -> Noeud:
        if self.est(TokenType.MOINS):
            ligne, col = self.ligne_col()
            self.consommer()
            operande = self.expr_unaire()
            return OpUnaire(operateur="-", operande=operande, ligne=ligne, colonne=col)
        return self.expr_postfixe()

    def expr_postfixe(self) -> Noeud:
        expr = self.expr_primaire()
        while True:
            if self.est(TokenType.LBRACKET):
                ligne, col = self.ligne_col()
                self.consommer()
                index = self.expression()
                self.consommer(TokenType.RBRACKET)
                expr = AccesIndex(objet=expr, index=index, ligne=ligne, colonne=col)
            elif self.est(TokenType.POINT):
                ligne, col = self.ligne_col()
                self.consommer()
                attr = self.consommer(TokenType.IDENTIFIANT).value
                if self.est(TokenType.LPAREN):
                    self.consommer()
                    args = []
                    if not self.est(TokenType.RPAREN):
                        args.append(self.expression())
                        while self.est(TokenType.VIRGULE):
                            self.consommer()
                            args.append(self.expression())
                    self.consommer(TokenType.RPAREN)
                    # Méthode: on encode comme AppelFonction avec nom "obj.methode"
                    expr = AppelFonction(
                        nom=f"__methode__",
                        arguments=[expr, TexteLitteral(valeur=attr), *args],
                        ligne=ligne, colonne=col
                    )
                else:
                    expr = AccesAttribut(objet=expr, attribut=attr, ligne=ligne, colonne=col)
            elif self.est(TokenType.LPAREN) and isinstance(expr, Identifiant):
                # Appel de fonction
                ligne, col = expr.ligne, expr.colonne
                self.consommer()
                args = []
                if not self.est(TokenType.RPAREN):
                    args.append(self.expression())
                    while self.est(TokenType.VIRGULE):
                        self.consommer()
                        args.append(self.expression())
                self.consommer(TokenType.RPAREN)
                expr = AppelFonction(nom=expr.nom, arguments=args, ligne=ligne, colonne=col)
            else:
                break
        return expr

    def expr_primaire(self) -> Noeud:
        t = self.courant()

        if t.type == TokenType.NOMBRE_ENTIER:
            self.consommer()
            return NombreLitteral(valeur=t.value, ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.NOMBRE_DECIMAL:
            self.consommer()
            return NombreLitteral(valeur=t.value, ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.TEXTE:
            self.consommer()
            return TexteLitteral(valeur=t.value, ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.VRAI:
            self.consommer()
            return BoolLitteral(valeur=True, ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.FAUX:
            self.consommer()
            return BoolLitteral(valeur=False, ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.NULK:
            self.consommer()
            return NulLitteral(ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.IDENTIFIANT:
            self.consommer()
            return Identifiant(nom=t.value, ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.LPAREN:
            self.consommer()
            expr = self.expression()
            self.consommer(TokenType.RPAREN)
            return expr

        # Types utilisés comme fonctions de conversion: entier(...), decimal(...), texte(...), bool(...)
        TYPE_FN = {
            TokenType.ENTIER: "entier",
            TokenType.DECIMAL: "decimal",
            TokenType.TEXTE_TYPE: "texte",
            TokenType.BOOL: "bool",
        }
        if t.type in TYPE_FN and self.regarder().type == TokenType.LPAREN:
            self.consommer()
            self.consommer(TokenType.LPAREN)
            args = []
            if not self.est(TokenType.RPAREN):
                args.append(self.expression())
                while self.est(TokenType.VIRGULE):
                    self.consommer()
                    args.append(self.expression())
            self.consommer(TokenType.RPAREN)
            return AppelFonction(nom=TYPE_FN[t.type], arguments=args,
                                 ligne=t.ligne, colonne=t.colonne)

        if t.type == TokenType.LBRACKET:
            return self.expr_liste()

        if t.type == TokenType.LBRACE:
            return self.expr_dict()

        if t.type in (TokenType.LIRE, TokenType.LIRE_ENTIER, TokenType.LIRE_DECIMAL):
            return self.expr_lire()

        raise ErreurSyntaxique(
            f"Expression attendue, obtenu '{t.value}' ({t.type.name})",
            t.ligne, t.colonne
        )

    def expr_liste(self) -> ListeLitterale:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.LBRACKET)
        elements = []
        self.ignorer_newlines()
        if not self.est(TokenType.RBRACKET):
            elements.append(self.expression())
            while self.est(TokenType.VIRGULE):
                self.consommer()
                self.ignorer_newlines()
                if self.est(TokenType.RBRACKET):
                    break
                elements.append(self.expression())
        self.ignorer_newlines()
        self.consommer(TokenType.RBRACKET)
        return ListeLitterale(elements=elements, ligne=ligne, colonne=col)

    def expr_dict(self) -> DictLitteral:
        ligne, col = self.ligne_col()
        self.consommer(TokenType.LBRACE)
        paires = []
        self.ignorer_newlines()
        if not self.est(TokenType.RBRACE):
            cle = self.expression()
            self.consommer(TokenType.DEUX_POINTS)
            val = self.expression()
            paires.append((cle, val))
            while self.est(TokenType.VIRGULE):
                self.consommer()
                self.ignorer_newlines()
                if self.est(TokenType.RBRACE):
                    break
                cle = self.expression()
                self.consommer(TokenType.DEUX_POINTS)
                val = self.expression()
                paires.append((cle, val))
        self.ignorer_newlines()
        self.consommer(TokenType.RBRACE)
        return DictLitteral(paires=paires, ligne=ligne, colonne=col)

    def expr_lire(self) -> Lire:
        ligne, col = self.ligne_col()
        t = self.consommer()
        mode = {"lire": "texte", "lire_entier": "entier", "lire_decimal": "decimal"}[t.value]
        prompt = None
        if self.est(TokenType.LPAREN):
            self.consommer()
            if not self.est(TokenType.RPAREN):
                prompt = self.expression()
            self.consommer(TokenType.RPAREN)
        return Lire(mode=mode, prompt=prompt, ligne=ligne, colonne=col)


def analyser(source: str) -> Programme:
    lexer = Lexer(source)
    tokens = lexer.tokeniser()
    parser = Parser(tokens)
    return parser.analyser()
