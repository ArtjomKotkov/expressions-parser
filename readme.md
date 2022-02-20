# Parseo
 Simple python dynamic expressions calculator.
 
## Base Information
Provides simple interface to describe and calculate arithmetic expression with provided context.

## Example
```python
import ast
import re
from typing import Iterable

from parseo import Parseo, expressions


class DynamicVariable(expressions.AbstractVariable):
    name: str = 'var_(id: str)'  # For debug purpose.
    mask: re.Pattern = re.compile(r'var_([a-z_]+)')  # Variable expression mask.
    context: str = 'dynamic_source'  # Source context.

    @classmethod
    def value_getter_str(cls, node: ast.Name, name_matches: Iterable[str]):
        index = f'{name_matches[0]}'  # Obtain first match.
        return f'{cls.context}["{index}"]'  # Define text link to corresponding data in source.

    
def If(condition, on_true, on_false):  # Define custom function.
    return on_true if condition else on_false


parser = Parseo(  # Define parser instance.
    variables=[DynamicVariable],
    functions=[If],
)

dynamic_variable_source = {
    'some_key': 15
}

expression = 'If(var_some_key > 0, var_some_key, 0)'

print(parser.test(expression))  # If((source["some_key"] > 0), source["some_key"], 0)

result = parser.compile(expression)(dynamic_source=dynamic_variable_source)

print(result)  # 15
```