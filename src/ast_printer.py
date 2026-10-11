import json


class AstPrinter:
    def print(self, expression):
        return expression.accept(self)

    def visit_binary_expr(self, expression):
        return self.parenthesize(
            expression.operator.lexeme,
            expression.left,
            expression.right,
        )

    def visit_grouping_expr(self, expression):
        return self.parenthesize("group", expression.expression)

    def visit_literal_expr(self, expression):
        if expression.value is None:
            return "null"
        if expression.value is True:
            return "true"
        if expression.value is False:
            return "false"
        if isinstance(expression.value, str):
            return json.dumps(expression.value)
        return str(expression.value)

    def visit_unary_expr(self, expression):
        return self.parenthesize(expression.operator.lexeme, expression.right)

    def parenthesize(self, name, *expressions):
        contents = " ".join(expression.accept(self) for expression in expressions)
        return f"({name} {contents})"
