__all__ = [
    'ContextMissMatchError',
    'ForbiddenFunctionCall',
    'ForbiddenVariableDefinition',
]


class ContextMissMatchError(BaseException):
    ...


class ForbiddenVariableDefinition(BaseException):
    ...


class ForbiddenFunctionCall(BaseException):
    ...
