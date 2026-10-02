from __future__ import annotations

from ast_nodes import CallExpr, Program, TypeName, VarDecl, IdentifierExpr, IntLiteral, BoolLiteral, Assignment
from semantic_errors import SemanticError, SemanticErrorKind, SemanticDiagnostic

class TypeChecker:
    def __init__(self):
        self.diagnostics = []

    def check(self, program: Program) -> None:
        for func in program.functions:
            self.current_function = func
            self.visit_block(func.body)

    def visit_block(self, block):
        for stmt in block.statements:
            self.visit_statement(stmt)

    def visit_statement(self, stmt):
        if isinstance(stmt, VarDecl):
            if stmt.initializer is not None:
                initializer_type = self.visit_expr(stmt.initializer)
                if initializer_type is not None and initializer_type != stmt.type:
                    self.diagnostics.append(
                        SemanticDiagnostic(
                            kind=SemanticErrorKind.INITIALIZER_TYPE_MISMATCH,
                            message=f"Tipo do inicializador '{initializer_type.value}' não corresponde ao tipo declarado '{stmt.type.value}'.",
                            span=stmt.initializer.span,
                        )
                    )
            return

        if isinstance(stmt, Assignment):
            target_type = self.visit_expr(stmt.target)
            value_type = self.visit_expr(stmt.value)
            if target_type is not None and value_type is not None and target_type != value_type:
                self.diagnostics.append(
                    SemanticDiagnostic(
                        kind=SemanticErrorKind.ASSIGNMENT_TYPE_MISMATCH,
                        message=f"Tipo do valor '{value_type.value}' não corresponde ao tipo do alvo '{target_type.value}'.",
                        span=stmt.value.span,
                    )
                )
            return


    def visit_expr(self, expr):
        if isinstance(expr, IntLiteral):
            expr.metadata["type"] = TypeName.INT
            return TypeName.INT

        if isinstance(expr, BoolLiteral):
            expr.metadata["type"] = TypeName.BOOL
            return TypeName.BOOL
        
        if isinstance(expr, IdentifierExpr):
            symbol = expr.metadata.get("symbol")
            if symbol is None:
                return None

            expr.metadata["type"] = symbol.type
            return symbol.type

        if isinstance(expr, CallExpr):
            symbol = expr.metadata.get("symbol")
            if symbol is None:
                return None

            arg_types = []
            for argument in expr.arguments:
                arg_types.append(self.visit_expr(argument))

            expected_types = symbol.parameter_types
            if len(arg_types) != len(expected_types):
                self.diagnostics.append(
                    SemanticDiagnostic(
                        kind=SemanticErrorKind.ARITY_MISMATCH,
                        message=f"Função '{expr.name}' espera {len(expected_types)} argumentos, mas recebeu {len(arg_types)}.",
                        span=expr.span,
                    )
                )
            else:
                for i in range(len(arg_types)):
                    expected_type = expected_types[i]
                    actual_type = arg_types[i]

                    if actual_type is not None and expected_type != actual_type:
                        self.diagnostics.append(
                            SemanticDiagnostic(
                                kind=SemanticErrorKind.ARGUMENT_TYPE_MISMATCH,
                                message=f"Argumento {i + 1} da função '{expr.name}' espera tipo '{expected_type.value}', mas recebeu tipo '{actual_type.value}'.",
                                span=expr.arguments[i].span,
                            )
                        )

            expr.metadata["type"] = symbol.type
            return symbol.type

     

def check_types(program: Program) -> None:
    # 1. Use os símbolos anexados pela resolução de nomes.
    # 2. Determine cada expressão de baixo para cima.
    # 3. Valide operadores, chamadas, comandos e declarações.
    # 4. Anote expressões válidas e acumule os diagnósticos da passagem.
    """Determine tipos de expressões e valide seus contextos."""

    checker = TypeChecker()
    checker.check(program)
    if checker.diagnostics:
        raise SemanticError(checker.diagnostics)
    #raise NotImplementedError("implemente a verificação de tipos")
