# ETDS

# Analizador con ETDS, AST, Tabla de Símbolos y Código en Tres Direcciones

## 1. Descripción General del Proyecto

Este proyecto implementa un **analizador sintáctico LL(1)** para expresiones aritméticas basado en una Gramática Independiente de Contexto (GIC). Incluye un **Esquema de Traducción Dirigido por la Sintaxis (ETDS)** que genera:

- **Árbol Sintáctico Abstracto (AST)** decorado
- **Tabla de Símbolos** asociada a los identificadores
- **Código en Tres Direcciones (TAC)** correspondiente al AST

El programa **no necesita ser modificado**: la expresión de entrada se escribe en `expr.txt` y el sistema genera los archivos de salida automáticamente.

---

## 2. Estructura del Proyecto

```
calculadora_edts/
│
├── edts_calc.py          # Código principal (parser + ETDS + AST + TAC)
├── expr.txt              # Archivo donde el usuario escribe la expresión
│
├── AST.txt               # Archivo generado con el AST decorado
├── TABLA_SIMBOLOS.txt    # Archivo generado con la tabla de símbolos
└── TAC.txt               # Archivo generado con código en tres direcciones
```

---

## 3. Gramática Utilizada

Se emplea una gramática **LL(1)** clásica para expresiones aritméticas:

### Elementos de la Gramática

- **No terminales:** `E`, `T`, `F`
- **Terminales:** `+`, `-`, `*`, `/`, `(`, `)`, `num`, `id`
- **Símbolo inicial:** `E`

### Producciones

1. `E → T E'`
2. `E' → + T E' | - T E' | ε`
3. `T → F T'`
4. `T' → * F T' | / F T' | ε`
5. `F → ( E ) | num | id`

Esta gramática está **factorizada** y **sin recursión izquierda**, por lo tanto es **LL(1)**.

---

## 4. Esquema de Traducción Dirigido por la Sintaxis (ETDS)

El ETDS se encarga de construir:

- El **AST** (atributo sintetizado `nodo`)
- La **Tabla de Símbolos**
- El **Código en Tres Direcciones**

### 4.1 Atributos Utilizados

Cada no terminal tiene un atributo sintetizado:

- `X.nodo` → referencia al subárbol construido para `X`

### 4.2 Acciones Semánticas Importantes

- Para `num` → se crea un nodo `Num(valor)`
- Para `id` → se crea un nodo `Id(nombre)` y se registra en la tabla de símbolos
- Para operadores binarios → se genera un nodo `BinOp(op, left, right)`

Estas acciones se integran directamente dentro del parser LL(1).

---

## 5. Árbol Sintáctico Abstracto (AST)

El AST está formado por tres tipos de nodos:

- **`Num(value)`** - Nodo para valores numéricos
- **`Id(name)`** - Nodo para identificadores, registrados en la tabla de símbolos
- **`BinOp(op, left, right)`** - Nodo para operaciones binarias

### Ejemplo de Salida

Para la expresión `a + 3 * (b - 2)`:

```
BinOp(+)
  Id(a)
  BinOp(*)
    Num(3.0)
    BinOp(-)
      Id(b)
      Num(2.0)
```

---

## 6. Tabla de Símbolos

La tabla de símbolos se genera automáticamente cuando aparecen identificadores en la expresión.

### Ejemplo

```
a          tipo=num valor=None
b          tipo=num valor=None
```

Como no hay asignaciones, `valor=None` y el tipo por defecto es numérico.

---

## 7. Código en Tres Direcciones (TAC)

El TAC se genera recorriendo el AST. Cada operación binaria produce:

```
tK = operandoIzq op operandoDer
```

### Ejemplo

Para `a + 3 * (b - 2)`:

```
t1 = 3.0
t2 = 2.0
t3 = b - t2
t4 = t1 * t3
t5 = a + t4
resultado en: t5
```

El último temporal contiene el resultado final.

---

## 8. Funcionamiento Interno del Sistema

### 8.1 Módulo Léxico

El lexer usa expresiones regulares para reconocer:

- Números (`NUM`)
- Identificadores (`ID`)
- Operadores y paréntesis
- Espacios y saltos de línea

Produce una lista de tokens terminada en `$`.

### 8.2 Parser LL(1)

El parser implementa las funciones:

- `E()`
- `T()`
- `F()`

Con estructuras:

- `while self.peek() in ("+", "-")`
- `while self.peek() in ("*", "/")`

para capturar las repeticiones de `E'` y `T'`.

### 8.3 Construcción del AST

Cada producción retorna un nodo sintáctico.

### 8.4 Tabla de Símbolos

Cada vez que se reconoce un identificador, se inserta:

```python
symtab[name] = { "tipo": "num", "valor": None }
```

### 8.5 Generación de TAC

El generador:

- Crea temporales (`t1`, `t2`, ...)
- Recorre el AST
- Escribe instrucciones en una lista
- Devuelve el temporal final que representa la expresión completa

---

## 9. Archivos Generados

### 9.1 `AST.txt`
Contiene el árbol decorado.

### 9.2 `TABLA_SIMBOLOS.txt`
Contiene los identificadores encontrados.

### 9.3 `TAC.txt`
Contiene el código en tres direcciones.

**Nota:** Cada ejecución sobrescribe estos tres archivos.

---

## 10. Cómo Usar el Programa

### Paso 1: Escribir la Expresión

Editar el archivo `expr.txt`:

```bash
nano expr.txt
```

**Ejemplo:**

```
a + 3 * (b - 2)
```

### Paso 2: Ejecutar el Programa

```bash
python3 edts_calc.py
```

### Paso 3: Revisar los Resultados Generados

Los siguientes archivos contendrán los resultados:

- `AST.txt`
- `TABLA_SIMBOLOS.txt`
- `TAC.txt`

---

## Requisitos

- Python 3.x
- No se requieren librerías externas

---

## Ejemplo Completo

### Entrada (`expr.txt`):
```
a + 3 * (b - 2)
```

### Salida esperada:

**`AST.txt`:**
```
BinOp(+)
  Id(a)
  BinOp(*)
    Num(3.0)
    BinOp(-)
      Id(b)
      Num(2.0)
```

**`TABLA_SIMBOLOS.txt`:**
```
a          tipo=num valor=None
b          tipo=num valor=None
```

**`TAC.txt`:**
```
t1 = 3.0
t2 = 2.0
t3 = b - t2
t4 = t1 * t3
t5 = a + t4
resultado en: t5
```

---

## Autor

Este proyecto fue desarrollado como parte del estudio de compiladores y análisis sintáctico.
