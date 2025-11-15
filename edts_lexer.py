# edts_lexer.py
import re
from dataclasses import dataclass

TOKEN_SPEC = [
    ("NUMBER",  r'\d+(?:\.\d+)?'),
    ("ID",      r'[A-Za-z_][A-Za-z0-9_]*'),
    ("PLUS",    r'\+'),
    ("MINUS",   r'-'),
    ("TIMES",   r'\*'),
    ("DIV",     r'/'),
    ("ASSIGN",  r'='),
    ("LPAREN",  r'\('),
    ("RPAREN",  r'\)'),
    ("SKIP",    r'[ \t]+'),
    ("MISMATCH",r'.'),
]

TOK_REGEX = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))

@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

def lex(src: str):
    line = 1
    pos_line_start = 0
    i = 0
    n = len(src)
    while i < n:
        m = TOK_REGEX.match(src, i)
        if not m:
            raise SyntaxError(f"Lexing error en pos {i}")
        kind = m.lastgroup
        text = m.group()
        if kind == "SKIP":
            pass
        elif kind == "MISMATCH":
            raise SyntaxError(f"Caracter inesperado '{text}' en línea {line}, col {i - pos_line_start + 1}")
        else:
            yield Token(kind, text, line, i - pos_line_start + 1)
        if text == "\n":
            line += 1
            pos_line_start = m.end()
        i = m.end()
    yield Token("EOF", "", line, (n - pos_line_start) + 1)
