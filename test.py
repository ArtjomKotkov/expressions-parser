import ast
import re

import pandas as pd

from main import Parser, AbstractVariable


class MetricVariable(AbstractVariable):
    """
    Класс переменной для метрики.
    """

    name: str = 'M*'
    mask: re.Pattern = re.compile(r'[mM](\d+)')

    @classmethod
    def value_getter_link(cls, node: ast.Name):
        matches = cls._get_mask_matches(node.id)

        index = f'{matches[0]}'
        getter_string = f'source[{index}]'  # Указываем текстовую ссылку на дата фрейм с данными.

        getter_tree = ast.parse(getter_string, mode='eval')  # Преобразуем в дерево.

        return getter_tree.body


class ConfigVariable(AbstractVariable):
    """
    Класс переменной для опции конфига.
    """

    name: str = 'C*'
    mask: re.Pattern = re.compile(r'[cC](\d+)')

    @classmethod
    def value_getter_link(cls, node: ast.Name):
        matches = cls._get_mask_matches(node.id)

        index = f'{matches[0]}'
        getter_string = f'config[{index}]'  # Указываем текстовую ссылку на список с данными.

        getter_tree = ast.parse(getter_string, mode='eval')  # Преобразуем в дерево.

        return getter_tree.body


source_frame = pd.DataFrame([[1, 4, 'Builder'],  # Какие-то данные метрики.
                             [2, 5, 'Baker'],
                             [3, 6, 'Candle Stick Maker']]
                            )

result_df = pd.DataFrame([[] for i in range(source_frame[0].count())])  # Выходной дата фрейм с количеством строк как в исходном.

config = {  # Словарик с данными конфига.
    'some_config_option': 1,
    'another_config_option': 2,
    "operator_max_online": 40
}

report_config_account_config_sequence = ['another_config_option', 'some_config_option']  # Опции конфига используемые в отчете,с сохранением поряка.

result_data = [config[key] for key in report_config_account_config_sequence]

expr1 = "IF(C0 == 0, 'Успех', 'Неудача')"  # Текстовые выражения.
expr2 = "M0 + M1 + C0"

expressions = [expr1, expr2]

parser = Parser(variables=[MetricVariable, ConfigVariable])


for index, expr in enumerate(expressions):
    print(f'Expr {index}\t\tSource expr: "{expr}"\t\tFinal expr: "{parser.test(expr)}"')
    result = parser.compile(expr)(source=source_frame, config=result_data)

    result_df[index] = result


print(f'Final result:\n{result_df}')
