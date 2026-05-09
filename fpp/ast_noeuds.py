"""
Nœuds de l'AST (Arbre Syntaxique Abstrait) pour F++.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class Noeud:
    ligne: int = 0
    colonne: int = 0


# ── Expressions ──────────────────────────────────────────────────────────────

@dataclass
class NombreLitteral(Noeud):
    valeur: Any = None  # int ou float


@dataclass
class TexteLitteral(Noeud):
    valeur: str = ""


@dataclass
class BoolLitteral(Noeud):
    valeur: bool = True


@dataclass
class NulLitteral(Noeud):
    pass


@dataclass
class ListeLitterale(Noeud):
    elements: List[Noeud] = field(default_factory=list)


@dataclass
class DictLitteral(Noeud):
    paires: List[tuple] = field(default_factory=list)  # [(clé, valeur)]


@dataclass
class Identifiant(Noeud):
    nom: str = ""


@dataclass
class OpBinaire(Noeud):
    gauche: Noeud = None
    operateur: str = ""
    droite: Noeud = None


@dataclass
class OpUnaire(Noeud):
    operateur: str = ""
    operande: Noeud = None


@dataclass
class AppelFonction(Noeud):
    nom: str = ""
    arguments: List[Noeud] = field(default_factory=list)


@dataclass
class AccesIndex(Noeud):
    objet: Noeud = None
    index: Noeud = None


@dataclass
class AccesAttribut(Noeud):
    objet: Noeud = None
    attribut: str = ""


# ── Instructions ─────────────────────────────────────────────────────────────

@dataclass
class Programme(Noeud):
    instructions: List[Noeud] = field(default_factory=list)


@dataclass
class Declaration(Noeud):
    type_var: str = ""         # "entier", "decimal", "texte", "bool", "liste", "dict", "const"
    nom: str = ""
    valeur: Optional[Noeud] = None


@dataclass
class Assignation(Noeud):
    cible: Noeud = None        # Identifiant ou AccesIndex
    operateur: str = "="
    valeur: Noeud = None


@dataclass
class Afficher(Noeud):
    arguments: List[Noeud] = field(default_factory=list)


@dataclass
class Lire(Noeud):
    mode: str = "texte"        # "texte", "entier", "decimal"
    prompt: Optional[Noeud] = None


@dataclass
class Si(Noeud):
    condition: Noeud = None
    alors: List[Noeud] = field(default_factory=list)
    sinon_si: List[tuple] = field(default_factory=list)   # [(condition, bloc)]
    sinon: Optional[List[Noeud]] = None


@dataclass
class TantQue(Noeud):
    condition: Noeud = None
    corps: List[Noeud] = field(default_factory=list)


@dataclass
class Pour(Noeud):
    variable: str = ""
    debut: Noeud = None
    fin: Noeud = None
    pas: Optional[Noeud] = None
    corps: List[Noeud] = field(default_factory=list)


@dataclass
class PourDans(Noeud):
    variable: str = ""
    iterable: Noeud = None
    corps: List[Noeud] = field(default_factory=list)


@dataclass
class DefFonction(Noeud):
    nom: str = ""
    parametres: List[str] = field(default_factory=list)
    corps: List[Noeud] = field(default_factory=list)


@dataclass
class Retourner(Noeud):
    valeur: Optional[Noeud] = None


@dataclass
class Casser(Noeud):
    pass


@dataclass
class Continuer(Noeud):
    pass


@dataclass
class ExprInstruction(Noeud):
    """Une expression utilisée comme instruction (ex: appel de fonction)."""
    expression: Noeud = None
