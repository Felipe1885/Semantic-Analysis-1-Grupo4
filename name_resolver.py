from __future__ import annotations

from ast_nodes import Program, TypeName, IfStmt, VarDecl, WhileStmt, Block
from symbols import FunctionSymbol, SymbolKind, Scope, Symbol
from semantic_errors import SemanticError, SemanticErrorKind, SemanticDiagnostic


class NameResolver:
    def __init__(self):
        self.diagnostics = []
        self.functions = {}
        self.scopes = []

    def resolve(self, program: Program) -> None:
        # 1. Colete todas as assinaturas de função.
        self.collect_functions(program)

        # 2. Valide a existência e a assinatura de main.
        self.validate_main(program)

        # 3. Percorra os corpos em ordem, criando um escopo para cada bloco.
        for func in program.functions:
            parameters = dict()
            for param in func.parameters:
                parameters[param.name] = Symbol(
                    name=param.name,
                    kind=SymbolKind.PARAMETER,
                    type=param.type,
                    declaration=param,
                )
            self.visit_block(func.body, None, parameters)
        
        # 4. Anote declarações, usos e blocos na AST.

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
            
    def visit_block(self, block, parent, parameters=None):
        symbols = parameters.copy() if parameters else {}
        # Visita cada declaração e expressão no bloco
        for statement in block.statements:
            if isinstance(statement, VarDecl):
                # Verifica se a variável já foi declarada no escopo atual
                if statement.name in symbols:
                    self.diagnostics.append(
                        SemanticDiagnostic(
                            kind=SemanticErrorKind.DUPLICATE_VARIABLE,
                            message=f"Variável '{statement.name}' já foi declarada neste escopo.",
                            span=statement.span,
                        )
                    )
                else:
                    # Adiciona a variável ao escopo atual
                    symbol = Symbol(
                        name=statement.name,
                        kind=SymbolKind.VARIABLE,
                        type=statement.type,
                        declaration=statement,
                    )
                    symbols[statement.name] = symbol
                    statement.metadata["symbol"] = symbol
                
            
        
        # Cria um novo escopo para o bloco
        new_scope = Scope(parent=parent, symbols=symbols)
        self.scopes.append(new_scope)
            
        for statement in block.statements:
            if isinstance(statement, Block):
                self.visit_block(statement, new_scope)
            if isinstance(statement, IfStmt):
                self.visit_block(statement.then_block, new_scope)
                if statement.else_block:
                    self.visit_block(statement.else_block, new_scope)
            if isinstance(statement, WhileStmt):
                self.visit_block(statement.body, new_scope)


"""Construa escopos, símbolos e vínculos entre usos e declarações."""
def resolve_names(program: Program) -> None:
    resolver = NameResolver()
    resolver.resolve(program)
