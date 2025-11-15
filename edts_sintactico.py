# edts_sintactico.py
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Set
from edts_lexer import Token, lex

# ===== AST =====
@dataclass
class AST: pass

@dataclass
class Num(AST):
    value: float
    line: int; col: int
    tipo: str = "num"
    val: float = field(init=False)
    def __post_init__(self): self.val = self.value

@dataclass
class Var(AST):
    name: str
    line: int; col: int
    tipo: str = "num"
    val: Optional[float] = None

@dataclass
class BinOp(AST):
    op: str
    left: AST
    right: AST
    line: int; col: int
    tipo: str = "num"
    val: Optional[float] = None

# ===== Símbolos =====
@dataclass
class Sym:
    name: str
    tipo: str = "num"
    valor: Optional[float] = None
    ocurrencias: List[Tuple[int,int]] = field(default_factory=list)

class SymbolTable:
    def __init__(self):
        self.tab: Dict[str, Sym] = {}
    def touch(self, name: str, line: int, col: int):
        if name not in self.tab:
            self.tab[name] = Sym(name)
        self.tab[name].ocurrencias.append((line,col))
    def set_value(self, name: str, value: float):
        if name not in self.tab: self.tab[name] = Sym(name)
        self.tab[name].valor = value
    def __iter__(self):
        return iter(self.tab.values())

# ===== Gramática LL(1) =====
# E  → T E'
# E' → + T E' | - T E' | ε
# T  → F T'
# T' → * F T' | / F T' | ε
# F  → NUMBER | ID | '(' E ')'
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.symtab = SymbolTable()

    def peek(self) -> Token: return self.tokens[self.i]
    def eat(self, ttype: str) -> Token:
        tok = self.peek()
        if tok.type != ttype:
            raise SyntaxError(f"Se esperaba {ttype} y llegó {tok.type} en línea {tok.line}, col {tok.col}")
        self.i += 1
        return tok

    def parse_E(self) -> AST:
        node = self.parse_T()
        return self.parse_Ep(node)

    def parse_Ep(self, inherited: AST) -> AST:
        tok = self.peek()
        if tok.type in ("PLUS", "MINUS"):
            op = tok.value
            self.eat(tok.type)
            t = self.parse_T()
            merged = BinOp(op=op, left=inherited, right=t, line=tok.line, col=tok.col)
            return self.parse_Ep(merged)
        return inherited

    def parse_T(self) -> AST:
        node = self.parse_F()
        return self.parse_Tp(node)

    def parse_Tp(self, inherited: AST) -> AST:
        tok = self.peek()
        if tok.type in ("TIMES", "DIV"):
            op = tok.value
            self.eat(tok.type)
            f = self.parse_F()
            merged = BinOp(op=op, left=inherited, right=f, line=tok.line, col=tok.col)
            return self.parse_Tp(merged)
        return inherited

    def parse_F(self) -> AST:
        tok = self.peek()
        if tok.type == "NUMBER":
            t = self.eat("NUMBER")
            return Num(float(t.value), t.line, t.col)
        if tok.type == "ID":
            t = self.eat("ID")
            self.symtab.touch(t.value, t.line, t.col)
            return Var(t.value, t.line, t.col)
        if tok.type == "LPAREN":
            self.eat("LPAREN")
            e = self.parse_E()
            self.eat("RPAREN")
            return e
        raise SyntaxError(f"Token inesperado {tok.type} en línea {tok.line}, col {tok.col}")

    def parse(self) -> AST:
        tree = self.parse_E()
        if self.peek().type != "EOF":
            tok = self.peek()
            raise SyntaxError(f"Sobra entrada desde {tok.type} en línea {tok.line}, col {tok.col}")
        return tree

# ===== Evaluación/Decoración =====
def eval_ast(node: AST, symtab: SymbolTable) -> float:
    if isinstance(node, Num):
        node.val = node.value
        return node.val
    if isinstance(node, Var):
        sym = symtab.tab.get(node.name)
        if sym is None or sym.valor is None:
            raise NameError(f"Variable '{node.name}' sin valor")
        node.val = float(sym.valor)
        return node.val
    if isinstance(node, BinOp):
        lv = eval_ast(node.left, symtab)
        rv = eval_ast(node.right, symtab)
        if node.op == '+': node.val = lv + rv
        elif node.op == '-': node.val = lv - rv
        elif node.op == '*': node.val = lv * rv
        elif node.op == '/':
            if rv == 0: raise ZeroDivisionError("División por cero")
            node.val = lv / rv
        else:
            raise RuntimeError(f"Operador desconocido {node.op}")
        return node.val
    raise RuntimeError("Nodo AST desconocido")

# ===== Impresión del AST =====
def print_ast(n: AST, pref: str = "", is_last: bool = True):
    con = "└── " if is_last else "├── "
    if isinstance(n, Num):
        print(pref + con + f"Num({n.value})")
    elif isinstance(n, Var):
        print(pref + con + f"Var({n.name})")
    elif isinstance(n, BinOp):
        print(pref + con + f"BinOp('{n.op}')")
        child_pref = pref + ("    " if is_last else "│   ")
        print_ast(n.left,  child_pref, False)
        print_ast(n.right, child_pref, True)
    else:
        print(pref + con + "¿?")

# ===== Conjuntos FIRST/FOLLOW/PREDICT =====
GRAMMAR = {
    "E":  [["T","Ep"]],
    "Ep": [["PLUS","T","Ep"],["MINUS","T","Ep"],["ε"]],
    "T":  [["F","Tp"]],
    "Tp": [["TIMES","F","Tp"],["DIV","F","Tp"],["ε"]],
    "F":  [["NUMBER"],["ID"],["LPAREN","E","RPAREN"]],
}
SYM_SHOW = {"PLUS":"+","MINUS":"-","TIMES":"*","DIV":"/","LPAREN":"(","RPAREN":")","ID":"id","NUMBER":"num","ε":"ε"}

def first_of_seq(seq: List[str], FIRST: Dict[str, Set[str]]) -> Set[str]:
    res: Set[str] = set()
    for X in seq:
        if X == "ε": 
            res.add("ε"); 
            break
        if X not in GRAMMAR:
            res.add(X); 
            break
        res |= (FIRST[X] - {"ε"})
        if "ε" not in FIRST[X]:
            break
    else:
        res.add("ε")
    return res

def compute_FIRST() -> Dict[str, Set[str]]:
    FIRST = {A:set() for A in GRAMMAR}
    changed = True
    while changed:
        changed = False
        for A, prods in GRAMMAR.items():
            before = len(FIRST[A])
            for alpha in prods:
                if alpha == ["ε"]:
                    FIRST[A].add("ε")
                else:
                    FIRST[A] |= first_of_seq(alpha, FIRST)
            if len(FIRST[A]) != before:
                changed = True
    return FIRST

def compute_FOLLOW(FIRST: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    FOLLOW = {A:set() for A in GRAMMAR}
    FOLLOW["E"].add("$")
    changed = True
    while changed:
        changed = False
        for A, prods in GRAMMAR.items():
            for alpha in prods:
                for i, B in enumerate(alpha):
                    if B in GRAMMAR:
                        beta = alpha[i+1:]
                        if beta:
                            first_beta = first_of_seq(beta, FIRST)
                            add = (first_beta - {"ε"})
                            old = len(FOLLOW[B])
                            FOLLOW[B] |= add
                            if "ε" in first_beta:
                                FOLLOW[B] |= FOLLOW[A]
                            if len(FOLLOW[B]) != old:
                                changed = True
                        else:
                            old = len(FOLLOW[B])
                            FOLLOW[B] |= FOLLOW[A]
                            if len(FOLLOW[B]) != old:
                                changed = True
    return FOLLOW

def compute_PREDICT(FIRST: Dict[str, Set[str]], FOLLOW: Dict[str, Set[str]]):
    PRED = {}
    for A, prods in GRAMMAR.items():
        PRED[A] = []
        for alpha in prods:
            if alpha == ["ε"]:
                P = FOLLOW[A].copy()
            else:
                first_alpha = first_of_seq(alpha, FIRST)
                P = (first_alpha - {"ε"})
                if "ε" in first_alpha:
                    P |= FOLLOW[A]
            PRED[A].append((alpha, P))
    return PRED

def show_sets(FIRST, FOLLOW, PRED) -> str:
    def fmt(symset: Set[str]) -> str:
        return "{" + ", ".join(SYM_SHOW.get(x,x) for x in sorted(symset)) + "}"
    lines = []
    lines.append("=== FIRST ===")
    for A in GRAMMAR:
        lines.append(f"FIRST({A}) = {fmt(FIRST[A])}")
    lines.append("\n=== FOLLOW ===")
    for A in GRAMMAR:
        lines.append(f"FOLLOW({A}) = {fmt(FOLLOW[A])}")
    lines.append("\n=== PREDICT ===")
    for A, lst in PRED.items():
        for alpha, P in lst:
            rhs = " ".join(SYM_SHOW.get(x,x) for x in alpha)
            lines.append(f"PREDICT({A} -> {rhs}) = {fmt(P)}")
    return "\n".join(lines)

# ===== Gramática de atributos + ETDS (texto) =====
ATTR_GRAMMAR = r"""
Gramática:
E  → T E'
E' → + T E' | - T E' | ε
T  → F T'
T' → * F T' | / F T' | ε
F  → num | id | ( E )

Atributos sintetizados:
- Num.val := literal
- Var.val := lookup(id)  (error si no definido)
- BinOp.val := aplicar(op, left.val, right.val)
- tipo := 'num' en todos

SDD:
F → num        { F.node := Num(num.lexeme) }
F → id         { F.node := Var(id.lexeme); touch(id) }
F → ( E )      { F.node := E.node }
T → F T'       { T.node := fold(T', F.node) }
T'→ * F T'     { T'.node := Bin(prev, '*', F.node) … }
T'→ / F T'     { T'.node := Bin(prev, '/', F.node) … }
T'→ ε          { T'.node := prev }
E → T E'       { E.node := fold(E', T.node) }
E'→ + T E'     { E'.node := Bin(prev, '+', T.node) … }
E'→ - T E'     { E'.node := Bin(prev, '-', T.node) … }
E'→ ε          { E'.node := prev }

ETDS (acciones embebidas conceptuales):
- Construir BinOp en E', T'
- Crear Num/Var en F
- Registrar id en tabla de símbolos
"""

def dump_attr_and_sdt() -> str:
    return ATTR_GRAMMAR.strip()
