import ast
import re
from typing import List, Iterable

__all__ = [
    'AbstractVariable',
    'AbstractAttributedVariable',
]

import astunparse


class AbstractVariable:
    """Базовый класс определяющий переменные в выражении."""

    name: str  # Имя переменной, нужно лишь для отображения ошибки.
    mask: re.Pattern  # Маска имени переменной.
    context: str

    @classmethod
    def value_getter_str(cls, node: ast.Name, name_matches: Iterable[str]) -> str:
        """
        Геттер ссылки на нужные данные для переменной.

        :param name_matches: Совпадения в имени ноды по маске переменной.
        :param node: Текущая нода.
        :return: Текстовое представление геттера данных из источника.
        """
        return astunparse.unparse(node)

    @classmethod
    def replace(cls, node: ast.Name):
        """
        Метод подмены ноды.

        :param node: Текущая нода.
        :return:
        """
        return cls._value_getter_tree(node)

    @classmethod
    def correspond(cls, node_name: str) -> bool:
        """
        Проверяем подходит ли класс для обработки переменной.

        :param node_name: Id ноды.
        :return: true | false
        """
        return bool(cls.mask.fullmatch(node_name))

    @classmethod
    def _value_getter_tree(cls, node: ast.Name):
        matches = cls._get_mask_matches(node.id)

        getter_tree = ast.parse(  # Преобразуем в дерево.
            cls.value_getter_str(node, matches),
            mode='eval',
        )

        return getter_tree.body

    @classmethod
    def _get_mask_matches(cls, node_name: str) -> List[str]:
        """
        Получаем группы совпадений по имени переменной.

        :param node_name: Id ноды.
        :return:
        """
        return cls.mask.findall(node_name)


class AbstractAttributedVariable:
    """Базовый класс определяющий переменные с атрибутами, например: config.some_option."""

    name: str  # Имя выражения.
    context: str

    @classmethod
    def value_getter_str(cls, node: ast.Attribute) -> str:
        """
        Геттер ссылки на нужные данные для переменной.

        :param node: Текущая нода.
        :return: Текстовое представление геттера данных из источника.
        """
        return astunparse.unparse(node)

    @classmethod
    def replace(cls, node: ast.Attribute):
        """
        Метод подмены ноды.

        :param node: Текущая нода.
        :return:
        """
        return cls._value_getter_tree(node)

    @classmethod
    def correspond(cls, node_name: str) -> bool:
        """
        Проверяем подходит ли класс для обработки переменной.

        :param node_name: Id ноды.
        :return: true | false
        """
        return cls.name == node_name

    @classmethod
    def _value_getter_tree(cls, node: ast.Attribute):
        getter_tree = ast.parse(  # Преобразуем в дерево.
            cls.value_getter_str(node),
            mode='eval',
        )

        return getter_tree.body
