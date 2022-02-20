import ast
from typing import Optional, Iterable, Callable, Type, Mapping, Union

import astunparse

from .exceptions import ContextMissMatchError
from .expressions import AbstractVariable, AbstractAttributedVariable
from .replacer import NodeReplacer


__all__ = [
    'Parseo',
]


class Parseo:
    def __init__(
        self,
        functions: Optional[Iterable[Callable]] = None,
        variables: Optional[
            Iterable[Union[Type[AbstractVariable], Type[AbstractAttributedVariable]]]
        ] = None,
    ):
        self._functions = functions
        self._variables = variables

        self.replacer = NodeReplacer(self._functions, self._variables)

    def test(self, expression: str) -> str:
        """
        Получить тексстовое представление кода после подмены.

        :param expression: Калькулируемое выражение.
        :return:
        """
        tree = ast.parse(expression, mode='eval')
        tree = self.replacer.visit(tree)

        return astunparse.unparse(tree)

    def compile(self, expression: str) -> Callable:
        """
        Получить скомпилированный код выражения.

        :param expression: Калькулируемое выражение.
        :return:
        """
        tree = ast.parse(expression, mode='eval')
        tree = self.replacer.visit(tree)

        code = compile(tree, "<string>", "eval")

        expected_context_vars = [var.context for var in self._variables] if self._variables else []
        functions_context = self._get_functions_context()

        def evaluate(**kwargs):
            absent_context = [context_var for context_var in expected_context_vars if context_var not in kwargs.keys()]
            if absent_context:
                miss_match_context = ', '.join(absent_context)
                raise ContextMissMatchError(f'Awaited context wasn\'t provided [{miss_match_context}].')

            context = {
                **kwargs,
                **functions_context,
            }

            return eval(code, context)

        return evaluate

    def _get_functions_context(self) -> Mapping[str, Callable]:
        return {func.__name__: func for func in self._functions} if self._functions else {}