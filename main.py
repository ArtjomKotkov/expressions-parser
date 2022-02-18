import ast
import re
from typing import Any, Iterable, List, Optional, Set, Type

import astunparse


class VariableValidationError(BaseException): ...


class ForbiddenVariableDefinition(BaseException): ...


class FunctionValidationError(BaseException): ...


class ForbiddenFunctionCall(BaseException): ...


class AbstractVariable:
    """Базовый класс определяющий переменные в выражении."""

    name: str  # Имя переменной, нужно лишь для отображения ошибки.
    mask: re.Pattern  # Маска имени переменной.

    @classmethod
    def value_getter_link(cls, node: ast.Name):
        """
        Геттер ссылки на нужные данные для переменной.

        :param node: Текущая нода.
        :return: РАспаршенное дерево представления данных. ast.patse('list[0]')
        """
        return node

    @classmethod
    def replace(cls, node: ast.Name):
        """
        Метод подмены ноды.

        :param node: Текущая нода.
        :return:
        """
        return cls.value_getter_link(node)

    @classmethod
    def correspond(cls, node_name: str) -> bool:
        """
        Проверяем подходит ли класс для обработки переменной.

        :param node_name: Id ноды.
        :return: true | false
        """
        return bool(cls.mask.fullmatch(node_name))

    @classmethod
    def _get_mask_matches(cls, node_name: str) -> List[str]:
        """
        Получаем группы совпадений по имени переменной.

        :param node_name: Id ноды.
        :return:
        """
        return cls.mask.findall(node_name)


class AbstractFuncCall:
    """Базовый класс определяющий вызов функций в выражении."""

    name: str = 'func'  # Сигнатура функций func(..)

    @classmethod
    def _validate(cls, node: ast.Call) -> ast.Call:
        """
        Правила валидации для метода.

        :param node: Текущая нода.
        :return:
        """
        return node

    @classmethod
    def replace(cls, node: ast.Call) -> ast.Call | ast.Expression:
        """
       Метод подмены ноды.

       :param node: Текущая нода.
       :return:
       """
        validated_node = cls._validate(node)

        return validated_node


class IfFuncCall(AbstractFuncCall):
    """
    Класс определяющий условную функцию: IF(condition, true, false).
    """

    name: str = 'IF'

    # Доступные типы для условияю
    available_test_types = (
        ast.And,
        ast.Or,
        ast.Compare,
        ast.Constant,
    )

    @classmethod
    def replace(cls, node: ast.Call) -> ast.IfExp:
        validated_node = cls._validate(node)

        return ast.IfExp(*validated_node.args)  # Подменяем функцию на условное выражение.

    @classmethod
    def _validate(cls, node: ast.Call) -> ast.Call:
        if len(node.args) != 3:  # Проверяем количество аргументов.
            raise FunctionValidationError(f'Number of function positional arguments must be 3.')
        elif not isinstance(node.args[0], cls.available_test_types):  # Проверяем тип условного выражения.
            raise FunctionValidationError(f'Expected conditional expression as first argument got {type(node.args[0])} type.')
        return node


class MaxFuncCall(AbstractFuncCall):
    """
    Класс определяющий метод max(a1, a2, a3, ..., a*).
    """
    name: str = 'max'


class MinFuncCall(AbstractFuncCall):
    """
    Класс определяющий метод min(a1, a2, a3, ..., a*).
    """
    name: str = 'min'


class NodeReplacer(ast.NodeTransformer):

    def __init__(self, functions: Iterable[Type[AbstractFuncCall]], variables: Iterable[Type[AbstractVariable]], *args, **kwargs):
        self._functions = functions
        self._variables = variables

        super().__init__(*args, **kwargs)

    def _get_func_map(self):
        return {
            func_class.name: func_class for func_class in self._functions
        }

    def visit_Name(self, node: ast.Name):
        # Получаем нужный класс для обработки перменной или выкидываем ошибку.
        try:
            var = next(var_ for var_ in self._variables if var_.correspond(node.id))
        except StopIteration:
            variable_names = ', '.join(variable.name for variable in self._variables)
            raise ForbiddenVariableDefinition(
                f'{node.id} is not available variable name, supported names [{variable_names}]')

        replaced_node = var.replace(node)

        return ast.copy_location(replaced_node, node)

    def visit_Call(self, node: ast.Call):
        func_map = self._get_func_map()

        # Получаем нужный класс для обработки вызова функции или выкидываем ошибку.
        func = func_map.get(node.func.id)

        if not func:
            raise ForbiddenFunctionCall()

        replaced_node = func.replace(node)

        # Проваливаемся во внутрь пересобранной функции.
        replaced_node = self.visit(replaced_node)

        return ast.copy_location(replaced_node, node)


class Parser:

    # Поддерживаемые функции.
    _functions: Set[Type[AbstractFuncCall]] = {
        IfFuncCall,
        MaxFuncCall,
        MinFuncCall,
    }

    # Поддерживаемые перемнные.
    _variables: Set[Type[AbstractVariable]] = set()

    def __init__(
        self,
        functions: Optional[Iterable[Type[AbstractFuncCall]]] = None,
        variables: Optional[Iterable[Type[AbstractVariable]]] = None,
    ):
        if functions:
            self._functions.update(functions)
        if variables:
            self._variables.update(variables)

        self._optimiser = NodeReplacer(self._functions, self._variables)

    def test(self, expression: str) -> str:
        """
        Получить тексстовое представление кода после подмены.

        :param expression: Калькулируемое выражение.
        :return:
        """
        tree = ast.parse(expression, mode='eval')
        tree = self._optimiser.visit(tree)

        return astunparse.unparse(tree)

    def compile(self, expression: str) -> Any:
        """
        Получить скомпилированный код выражения.

        :param expression: Калькулируемое выражение.
        :return:
        """
        tree = ast.parse(expression, mode='eval')
        tree = self._optimiser.visit(tree)

        code = compile(tree, "<string>", "eval")

        return code
