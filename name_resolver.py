from __future__ import annotations

from ast_nodes import Program, TypeName
from symbols import FunctionSymbol, SymbolKind
from semantic_errors import SemanticError, SemanticErrorKind, SemanticDiagnostic


class NameResolver:
    def __init__(self):
        self.diagnostics = []
        self.functions = {}

    def resolve(self, program: Program) -> None:
        # 1. Colete todas as assinaturas de função.
        self.collect_functions(program)

        # 2. Valide a existência e a assinatura de main.
        self.validate_main(program)

        # 3. Percorra os corpos em ordem, criando um escopo para cada bloco.
        # 4. Anote declarações, usos e blocos na AST.
        for func in program.functions:
            self.visit_function(func)

        # 5. Acumule os diagnósticos desta passagem antes de lançar SemanticError.
        if self.diagnostics:
            raise SemanticError(self.diagnostics)

    # Coleta as assinaturas de função
    def collect_functions(self, program: Program) -> None:
        for func in program.functions:
            # Verifica se a função já foi declarada, se sim, adiciona um diagnóstico de erro
            if func.name in self.functions:
                self.diagnostics.append(
                   SemanticDiagnostic(
                      kind=SemanticErrorKind.DUPLICATE_FUNCTION,
                      message=f"Função '{func.name}' já foi declarada.",
                      span=func.span,
                   )
                )
            # Se não foi, adiciona a função à tabela de símbolos
            else:
                param_types = tuple(param.type for param in func.parameters)
                symbol = FunctionSymbol (
                    name=func.name,
                    kind=SymbolKind.FUNCTION,
                    type=func.return_type,
                    declaration=func,
                    parameter_types=param_types,
                )
                self.functions[func.name] = symbol
                func.metadata["symbol"] = symbol


    # Valida a existência e a assinatura da main
    def validate_main(self, program: Program) -> None:
        main_sym = self.functions.get("main")
        # Main não existe
        if main_sym is None:
            self.diagnostics.append(
                SemanticDiagnostic(
                    kind=SemanticErrorKind.INVALID_MAIN,
                    message="Função 'main' ausente.",
                    span=program.span,
                )
            )
        # Main existe, mas não tem a assinatura correta
        elif main_sym.type != TypeName.INT or len(main_sym.parameter_types) != 0:
            self.diagnostics.append(
                SemanticDiagnostic(
                    kind=SemanticErrorKind.INVALID_MAIN,
                    message="Função 'main' deve ter assinatura 'int main()'.",
                    span=main_sym.declaration.span,
                )
            )



"""Construa escopos, símbolos e vínculos entre usos e declarações."""
def resolve_names(program: Program) -> None:
    resolver = NameResolver()
    resolver.resolve(program)

    #raise NotImplementedError("implemente a resolução de nomes")
