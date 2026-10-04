from __future__ import annotations

from ast_nodes import Program
from name_resolver import resolve_names
from type_checker import check_types
from semantic_errors import SemanticError

class SemanticAnalyzer:
    """Coordena as duas passagens da Análise Semântica 1."""

    def analyze(self, program: Program) -> Program:
        diagnostics = []
        # caso tenha erro, acumula o erro e vai pro proximo
        try:
            resolve_names(program)
        except SemanticError as e:
            diagnostics.extend(e.diagnostics)
        # execura memso com erro anterior, se tiver erro, acumula e vai pro proximo
        try:
            check_types(program)
        except SemanticError as e:
            diagnostics.extend(e.diagnostics)
        # com erros acumulados, lança todos os erros de uma vez
        if diagnostics:
            raise SemanticError(diagnostics)
        return program
