"""
Lexer F++ — Transforme le code source en tokens.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Littéraux
    NOMBRE_ENTIER = auto()
    NOMBRE_DECIMAL = auto()
    TEXTE = auto()
    VRAI = auto()
    FAUX = auto()
    NULK = auto()

    # Identifiants / mots-clés
    IDENTIFIANT = auto()

    # Mots-clés de déclaration
    ENTIER = auto()
    DECIMAL = auto()
    TEXTE_TYPE = auto()
    BOOL = auto()
    LISTE = auto()
    DICT = auto()
    CONST = auto()

    # Mots-clés de contrôle
    SI = auto()
    ALORS = auto()
    SINON_SI = auto()
    SINON = auto()
    TANTQUE = auto()
    POUR = auto()
    DE = auto()
    A = auto()
    FAIRE = auto()
    FIN = auto()
    CASSER = auto()
    CONTINUER = auto()

    # Mots-clés de fonction
    FONCTION = auto()
    RETOURNER = auto()

    # Mots-clés d'E/S
    AFFICHER = auto()
    LIRE = auto()
    LIRE_ENTIER = auto()
    LIRE_DECIMAL = auto()

    # Opérateurs arithmétiques
    PLUS = auto()
    MOINS = auto()
    FOIS = auto()
    DIVISE = auto()
    MODULO = auto()
    PUISSANCE = auto()

    # Opérateurs de comparaison
    EGAL_EGAL = auto()
    DIFFERENT = auto()
    INFERIEUR = auto()
    SUPERIEUR = auto()
    INF_EGAL = auto()
    SUP_EGAL = auto()

    # Opérateurs logiques
    ET = auto()
    OU = auto()
    NON = auto()

    # Opérateurs d'assignation
    EGAL = auto()
    PLUS_EGAL = auto()
    MOINS_EGAL = auto()
    FOIS_EGAL = auto()
    DIV_EGAL = auto()

    # Ponctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    VIRGULE = auto()
    DEUX_POINTS = auto()
    POINT = auto()

    # Divers
    NEWLINE = auto()
    EOF = auto()
    COMMENTAIRE = auto()


MOTS_CLES = {
    "vrai": TokenType.VRAI,
    "faux": TokenType.FAUX,
    "nul": TokenType.NULK,
    "entier": TokenType.ENTIER,
    "decimal": TokenType.DECIMAL,
    "texte": TokenType.TEXTE_TYPE,
    "bool": TokenType.BOOL,
    "liste": TokenType.LISTE,
    "dict": TokenType.DICT,
    "const": TokenType.CONST,
    "si": TokenType.SI,
    "alors": TokenType.ALORS,
    "sinonsi": TokenType.SINON_SI,
    "sinon": TokenType.SINON,
    "tantque": TokenType.TANTQUE,
    "pour": TokenType.POUR,
    "de": TokenType.DE,
    # "a" retiré — reconnu par le parser comme identifiant "a" dans le contexte "pour"
    "faire": TokenType.FAIRE,
    "fin": TokenType.FIN,
    "casser": TokenType.CASSER,
    "continuer": TokenType.CONTINUER,
    "fonction": TokenType.FONCTION,
    "retourner": TokenType.RETOURNER,
    "afficher": TokenType.AFFICHER,
    "lire": TokenType.LIRE,
    "lire_entier": TokenType.LIRE_ENTIER,
    "lire_decimal": TokenType.LIRE_DECIMAL,
    "et": TokenType.ET,
    "ou": TokenType.OU,
    "non": TokenType.NON,
}


@dataclass
class Token:
    type: TokenType
    value: object
    ligne: int
    colonne: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, L{self.ligne}:C{self.colonne})"


class ErreurLexicale(Exception):
    def __init__(self, message, ligne, colonne):
        super().__init__(f"Erreur lexicale ligne {ligne}, colonne {colonne}: {message}")
        self.ligne = ligne
        self.colonne = colonne


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.ligne = 1
        self.colonne = 1
        self.tokens: List[Token] = []

    def courant(self) -> Optional[str]:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def suivant(self, offset=1) -> Optional[str]:
        p = self.pos + offset
        if p < len(self.source):
            return self.source[p]
        return None

    def avancer(self) -> str:
        c = self.source[self.pos]
        self.pos += 1
        if c == "\n":
            self.ligne += 1
            self.colonne = 1
        else:
            self.colonne += 1
        return c

    def ajouter(self, type: TokenType, value, ligne, colonne):
        self.tokens.append(Token(type, value, ligne, colonne))

    def tokeniser(self) -> List[Token]:
        while self.pos < len(self.source):
            self._lire_token()
        self.ajouter(TokenType.EOF, None, self.ligne, self.colonne)
        return self.tokens

    def _lire_token(self):
        c = self.courant()
        ligne, colonne = self.ligne, self.colonne

        # Espaces (pas les newlines)
        if c in (" ", "\t", "\r"):
            self.avancer()
            return

        # Commentaires (#)
        if c == "#":
            while self.courant() and self.courant() != "\n":
                self.avancer()
            return

        # Newline
        if c == "\n":
            self.avancer()
            # Éviter les newlines consécutifs
            if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
                self.ajouter(TokenType.NEWLINE, "\n", ligne, colonne)
            return

        # Chaînes de caractères
        if c in ('"', "'"):
            self._lire_chaine(ligne, colonne)
            return

        # Nombres
        if c.isdigit() or (c == "-" and self.suivant() and self.suivant().isdigit()
                           and (not self.tokens or self.tokens[-1].type in (
                               TokenType.EGAL, TokenType.LPAREN, TokenType.VIRGULE,
                               TokenType.PLUS, TokenType.MOINS, TokenType.FOIS,
                               TokenType.DIVISE, TokenType.NEWLINE, TokenType.RETOURNER,
                               TokenType.AFFICHER,
                           ))):
            self._lire_nombre(ligne, colonne)
            return

        # Identifiants et mots-clés
        if c.isalpha() or c == "_":
            self._lire_identifiant(ligne, colonne)
            return

        # Opérateurs multi-caractères
        double = c + (self.suivant() or "")
        operateurs_doubles = {
            "==": TokenType.EGAL_EGAL,
            "!=": TokenType.DIFFERENT,
            "<=": TokenType.INF_EGAL,
            ">=": TokenType.SUP_EGAL,
            "+=": TokenType.PLUS_EGAL,
            "-=": TokenType.MOINS_EGAL,
            "*=": TokenType.FOIS_EGAL,
            "/=": TokenType.DIV_EGAL,
            "**": TokenType.PUISSANCE,
        }
        if double in operateurs_doubles:
            self.avancer()
            self.avancer()
            self.ajouter(operateurs_doubles[double], double, ligne, colonne)
            return

        # Opérateurs simples
        operateurs_simples = {
            "+": TokenType.PLUS,
            "-": TokenType.MOINS,
            "*": TokenType.FOIS,
            "/": TokenType.DIVISE,
            "%": TokenType.MODULO,
            "=": TokenType.EGAL,
            "<": TokenType.INFERIEUR,
            ">": TokenType.SUPERIEUR,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.VIRGULE,
            ":": TokenType.DEUX_POINTS,
            ".": TokenType.POINT,
        }
        if c in operateurs_simples:
            self.avancer()
            self.ajouter(operateurs_simples[c], c, ligne, colonne)
            return

        raise ErreurLexicale(f"Caractère inattendu: '{c}'", ligne, colonne)

    def _lire_chaine(self, ligne, colonne):
        quote = self.avancer()
        resultat = []
        while self.courant() and self.courant() != quote:
            if self.courant() == "\\" and self.suivant():
                self.avancer()
                echap = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'"}
                c = self.avancer()
                resultat.append(echap.get(c, c))
            else:
                resultat.append(self.avancer())
        if not self.courant():
            raise ErreurLexicale("Chaîne non fermée", ligne, colonne)
        self.avancer()  # fermer la quote
        self.ajouter(TokenType.TEXTE, "".join(resultat), ligne, colonne)

    def _lire_nombre(self, ligne, colonne):
        debut = self.pos
        if self.courant() == "-":
            self.avancer()
        while self.courant() and self.courant().isdigit():
            self.avancer()
        if self.courant() == "." and self.suivant() and self.suivant().isdigit():
            self.avancer()
            while self.courant() and self.courant().isdigit():
                self.avancer()
            self.ajouter(TokenType.NOMBRE_DECIMAL, float(self.source[debut:self.pos]), ligne, colonne)
        else:
            self.ajouter(TokenType.NOMBRE_ENTIER, int(self.source[debut:self.pos]), ligne, colonne)

    def _lire_identifiant(self, ligne, colonne):
        debut = self.pos
        while self.courant() and (self.courant().isalnum() or self.courant() == "_"):
            self.avancer()
        mot = self.source[debut:self.pos]
        type_ = MOTS_CLES.get(mot.lower(), TokenType.IDENTIFIANT)
        # Conserver la casse pour les identifiants, minuscule pour mots-clés
        if type_ == TokenType.IDENTIFIANT:
            self.ajouter(type_, mot, ligne, colonne)
        else:
            self.ajouter(type_, mot.lower(), ligne, colonne)
