"""
Package fpp — Langage F++ (Français++)
"""

from .lexer import Lexer, ErreurLexicale
from .parser import analyser, ErreurSyntaxique
from .interpreteur import Interpreteur, ErreurExecution
from .codegen import CodegenC, ErreurCompilation

__version__ = "1.0.0"
__all__ = ["Lexer", "analyser", "Interpreteur", "ErreurLexicale",
           "ErreurSyntaxique", "ErreurExecution", "CodegenC", "ErreurCompilation"]
