__all__ = [
    "dshell_operators",
    "dshell_logical_word_operators",
    "dshell_mathematical_operators",
    "dshell_logical_operators"]


from typing import Callable

"""
Tuple format: (function, precedence, number of operands)
"""

dshell_mathematical_operators: dict[str, tuple[Callable, int, int]] = {

    r"++": (lambda a: a + 1, 6, 1),
    r"--": (lambda a: a - 1, 6, 1),
    r"**": (lambda a, b: a ** b, 8, 2),
    r"//": (lambda a, b: a // b, 7, 2),
    r">>": (lambda a, b: a >> b, 5, 2),
    r"<<": (lambda a, b: a << b, 5, 2),
    r"^": (lambda a, b: a ^ b, 5, 2),
    r"/": (lambda a, b: a / b, 7, 2),
    r"*": (lambda a, b: a * b, 7, 2),
    r"%": (lambda a, b: a % b, 7, 2),
    r"-": (lambda a, b=None: a - b if b is not None else -a, 6, -1),
    r"+": (lambda a, b: a + b, 6, 2),
    # warning: ambiguity between unary and binary to be handled in your parser

}

dshell_logical_word_operators: dict[str, tuple[Callable, int, int]] = {
    r"and": (lambda a, b: bool(a and b), 2, 2),
    r"or": (lambda a, b: bool(a or b), 1, 2),
    r"not": (lambda a: not a, 3, 1),
    r"in": (lambda a, b: a in b, 4, 2),
}

dshell_logical_operators: dict[str, tuple[Callable, int, int]] = {

    r"<=": (lambda a, b: a <= b, 4, 2),
    r"=<": (lambda a, b: a <= b, 4, 2),
    r"!=": (lambda a, b: a != b, 4, 2),
    r"=!": (lambda a, b: a != b, 4, 2),
    r">=": (lambda a, b: a >= b, 4, 2),
    r"=>": (lambda a, b: a >= b, 4, 2),
    r"&&": (lambda a, b: a and b, 2, 2),
    r"||": (lambda a, b: a or b, 1, 2),
    r"&": (lambda a, b: a & b, 2, 2),
    r"|": (lambda a, b: a | b, 1, 2),
    r"=": (lambda a, b: a == b, 4, 2),
    r"<": (lambda a, b: a < b, 4, 2),
    r">": (lambda a, b: a > b, 4, 2),
    r"!": (lambda a: not a, 3, 1),

}

dshell_operators: dict[str, tuple[Callable, int, int]] = dshell_logical_operators.copy()
dshell_operators.update(dshell_logical_word_operators)
dshell_operators.update(dshell_mathematical_operators)