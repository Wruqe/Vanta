from abc import ABC, abstractmethod
from dataclasses import dataclass

try:
    from .vanta_token import Token
except ImportError:  # Support importing from a directly executed script.
    from vanta_token import Token


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        """Dispatch this expression to the matching visitor method."""


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True)
class Literal(Expr):
    value: object

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)
