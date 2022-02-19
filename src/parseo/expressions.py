import ast
import re
from typing import List


__all__ = [
    'AbstractVariable',
    'AbstractAttributedVariable',
]


class AbstractVariable:
    """Базовый класс определяющий переменные в выражении."""

    name: str  # Имя переменной, нужно лишь для отображения ошибки.
    mask: re.Pattern  # Маска имени переменной.
    context: str

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


class AbstractAttributedVariable:
    """Базовый класс определяющий переменные с атрибутами, например: config.some_option."""

    name: str  # Имя выражения.
    context: str

    @classmethod
    def value_getter_link(cls, node: ast.Name):
        """
        Геттер ссылки на нужные данные для переменной.

        :param node: Текущая нода.
        :return: Распаршенное дерево представления данных. ast.patse('list[0]')
        """
        return node

    @classmethod
    def replace(cls, node: ast.Name):
        """
        Метод подмены ноды.

        :param node: Текущая нода.
        :return:
        """

        return ast.copy_location(cls.value_getter_link(node), node)

    @classmethod
    def correspond(cls, node_name: str) -> bool:
        """
        Проверяем подходит ли класс для обработки переменной.

        :param node_name: Id ноды.
        :return: true | false
        """
        return cls.name == node_name
