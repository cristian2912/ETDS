# app.py
import os
from edts_lexer import lex
from edts_sintactico import (
    Parser, eval_ast, print_ast,
    compute_FIRST, compute_FOLLOW, compute_PREDICT, show_sets, dump_attr_and_sdt
)

BANNER = (
    "Calculadora GIC (+,-,*,/) con AST, ETDS y reportes\n"
    "Ejemplos de expresión: 3+4*2-(1/5)   ó   (x+3)*y - z/2\n"
    "Valores opcionales: x=2,y=5,z=4   (vacío si no aplica)\n"
    "Directorio de reportes: out por defecto\n"
)

def parse_vars(env_str: str):
    env = {}
    if not env_str.strip():
        return env
    parts = [p for p in env_str.split(",") if p.strip()]
    for part in parts:
        if "=" not in part:
            raise ValueError(f"Formato inválido: {part}  (use x=2,y=3)")
        k, v = part.split("=", 1)
        env[k.strip()] = float(v.strip())
    return env

def one_run(expr: str, vars_str: str, report_dir: str):
    tokens = list(lex(expr))
    parser = Parser(tokens)
    tree = parser.parse()

    env = parse_vars(vars_str)
    for k, v in env.items():
        parser.symtab.set_value(k, v)

    value = eval_ast(tree, parser.symtab)

    print("\n== AST ==")
    print_ast(tree)

    print("\n== Tabla de símbolos ==")
    any_sym = False
    for s in parser.symtab:
        any_sym = True
        print(f"{s.name:10s} tipo={s.tipo:3s} valor={s.valor} ocurrencias={s.ocurrencias}")
    if not any_sym:
        print("(sin identificadores)")

    print("\n== Valor de la expresión ==")
    print(value)

    FIRST = compute_FIRST()
    FOLLOW = compute_FOLLOW(FIRST)
    PRED = compute_PREDICT(FIRST, FOLLOW)
    text_sets = show_sets(FIRST, FOLLOW, PRED)
    attr_text = dump_attr_and_sdt()

    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "FFP.txt"), "w", encoding="utf-8") as f:
        f.write(text_sets + "\n")
    with open(os.path.join(report_dir, "ATRIBUTOS_ETDS.txt"), "w", encoding="utf-8") as f:
        f.write(attr_text + "\n")

    print(f"\nReportes escritos en: {os.path.abspath(report_dir)}/")
    print(" - FFP.txt")
    print(" - ATRIBUTOS_ETDS.txt")

def main():
    print(BANNER)
    while True:
        expr = input("Expresión (ENTER para salir): ").strip()
        if not expr:
            print("Fin.")
            break

        # Atajo: @file ruta.txt  (lee la primera línea como expresión)
        if expr.startswith("@file "):
            ruta = expr[6:].strip()
            with open(ruta, "r", encoding="utf-8") as f:
                expr = f.readline().strip()
            print(f"Usando expresión desde {ruta}: {expr}")

        vars_str = input("Valores de variables [opcional, ej x=2,y=3]: ").strip()
        report_dir = input("Carpeta de reportes [default: out]: ").strip() or "out"

        try:
            one_run(expr, vars_str, report_dir)
        except Exception as e:
            print(f"[Error] {e}")

        otra = input("\n¿Otra expresión? [s/N]: ").strip().lower()
        if otra != "s":
            print("Fin.")
            break

if __name__ == "__main__":
    main()
