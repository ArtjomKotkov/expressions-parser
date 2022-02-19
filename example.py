import ast
import re

import pandas as pd

from src.parseo import Parseo
from src.parseo.expressions import AbstractVariable, AbstractAttributedVariable


class MetricVariable(AbstractVariable):
    """
    Класс переменной для метрики.
    """

    name: str = 'M*'
    mask: re.Pattern = re.compile(r'[mM](\d+)')
    context: str = 'source'

    @classmethod
    def value_getter_link(cls, node: ast.Name):
        matches = cls._get_mask_matches(node.id)

        index = f'{matches[0]}'
        getter_string = f'{cls.context}[{index}]'  # Указываем текстовую ссылку на дата фрейм с данными.

        getter_tree = ast.parse(getter_string, mode='eval')  # Преобразуем в дерево.

        return getter_tree.body


class ConfigVariable(AbstractVariable):
    """
    Класс переменной для опции конфига.
    """

    name: str = 'C*'
    mask: re.Pattern = re.compile(r'[cC](\d+)')
    context: str = 'config_list'

    @classmethod
    def value_getter_link(cls, node: ast.Name):
        matches = cls._get_mask_matches(node.id)

        index = f'{matches[0]}'
        getter_string = f'{cls.context}[{index}]'  # Указываем текстовую ссылку на список с данными.

        getter_tree = ast.parse(getter_string, mode='eval')  # Преобразуем в дерево.

        return getter_tree.body


class ConfigIdVariable(AbstractVariable):
    """
    Класс переменной для опции конфига с выбором по id.
    """

    name: str = 'config.(id: str)'
    mask: re.Pattern = re.compile(r'config_([a-z0-9_]+)')  # Реализовать через точку сложнее, т.к. это уже не нода Name а нода Attribute с под нодами.
    context: str = 'config_map'

    @classmethod
    def value_getter_link(cls, node: ast.Name):
        matches = cls._get_mask_matches(node.id)

        index = f'{matches[0]}'
        getter_string = f'{cls.context}.get("{index}")'  # Указываем текстовую ссылку на список с данными.

        getter_tree = ast.parse(getter_string, mode='eval')  # Преобразуем в дерево.

        return getter_tree.body


class ConfigAttributedVariable(AbstractAttributedVariable):
    name: str = 'config'
    context: str = 'config_map'

    @classmethod
    def value_getter_link(cls, node: ast.Attribute):
        attribute = node.attr

        getter_string = f'{cls.context}.get("{attribute}")'  # Указываем текстовую ссылку на список с данными.

        getter_tree = ast.parse(getter_string, mode='eval')  # Преобразуем в дерево.

        return getter_tree.body


config = {  # Словарик с данными конфига.
    'some_config_option': 1,
    'another_config_option': 2,
    "operator_max_online": 40
}


# Кастомные функции
def IF(condition, on_true, on_false):
    return on_true if condition else on_false


def count(df_column) -> int:
    return df_column.count()


def coalesce(*args) -> int:
    return next(arg for arg in args if arg is not None)


def get_config(key: str):
    return config.get(key)



source_frame = pd.DataFrame([[1, 4, 'Builder'],  # Какие-то данные метрики.
                             [2, 5, 'Baker'],
                             [3, 6, 'Candle Stick Maker']]
                            )

result_df = pd.DataFrame([[] for i in range(source_frame[0].count())])  # Выходной дата фрейм с количеством строк как в исходном.

report_config_account_config_sequence = ['another_config_option', 'some_config_option']  # Опции конфига используемые в отчете,с сохранением поряка.

result_data = [config[key] for key in report_config_account_config_sequence]


expressions = [
    "IF(C0 == 2, 'Успех', 'Неудача')",
    "get_config('some_config_option')",
    "config.some_config_option + get_config('some_config_option') + C1",  # 3 способа получения переменных.
    "coalesce(None, config.some_config_option, 12)",
    "count(m0)",
]

parser = Parseo(
    variables=[
        MetricVariable,
        ConfigVariable,
        ConfigIdVariable,
        ConfigAttributedVariable,
    ],
    functions=[
        IF,
        count,
        coalesce,
        get_config,
    ],

)

for index, expr in enumerate(expressions):
    print(f'Expr {index}\t\tSource expr: "{expr}"\t\tFinal expr: "{parser.test(expr)}"')
    result = parser.compile(expr)(source=source_frame, config_list=result_data, config_map=config)

    result_df[index] = result


print(f'Final result:\n{result_df}')
