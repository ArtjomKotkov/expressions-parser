import ast
from typing import Any, Iterable, Optional, Type, Callable, Union

from .expressions import AbstractVariable, AbstractAttributedVariable
from .exceptions import (
    ForbiddenFunctionCall,
    ForbiddenVariableDefinition,
)


class NodeReplacer(ast.NodeTransformer):

    def __init__(
        self,
        functions: Optional[Iterable[Callable]],
        variables: Optional[
            Iterable[Union[Type[AbstractVariable], Type[AbstractAttributedVariable]]]
        ],
        *args,
        **kwargs
    ):
        self._functions = functions
        self._variables = variables

        super().__init__(*args, **kwargs)

    def _get_available_functions(self):
        return [func.__name__ for func in self._functions] if self._functions else []

    def _get_simple_variables(self) -> Iterable[Type[AbstractVariable]]:
        return [var_ for var_ in self._variables if issubclass(var_, AbstractVariable)] if self._variables else []

    def _get_attributes_variables(self) -> Iterable[Type[AbstractAttributedVariable]]:
        return [var_ for var_ in self._variables if issubclass(var_, AbstractAttributedVariable)] if self._variables else []

    def visit_Name(self, node: ast.Name):
        # Игнорируем имена переменных.
        if node.id in self._get_available_functions():
            self.generic_visit(node)
            return node
        else:
            # Получаем нужный класс для обработки переменной или выкидываем ошибку.
            simple_variables = self._get_simple_variables()
            try:
                var = next(var_ for var_ in simple_variables if var_.correspond(node.id))
            except (StopIteration, TypeError):
                variable_names = ', '.join(variable.name for variable in simple_variables)
                raise ForbiddenVariableDefinition(
                    f'{node.id} is not available variable name, supported names [{variable_names}]')

            replaced_node = var.replace(node)

            return ast.copy_location(replaced_node, node)

    def visit_Call(self, node: ast.Call):
        available_functions = self._get_available_functions()

        if node.func.id not in available_functions:
            func_str = ', '.join(available_functions)
            raise ForbiddenFunctionCall(f'Forbidden function call {node.func.id}, possible functions [{func_str}]')

        self.generic_visit(node)

        return node

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        attributed_variables = self._get_attributes_variables()
        try:
            var = next(var_ for var_ in attributed_variables if var_.correspond(node.value.id))
        except (StopIteration, TypeError):
            variable_names = ', '.join(variable.name for variable in attributed_variables)
            raise ForbiddenVariableDefinition(
                f'{node.id} is not available variable name, supported names [{variable_names}]')

        replaced_node = var.replace(node)

        return ast.copy_location(replaced_node, node)