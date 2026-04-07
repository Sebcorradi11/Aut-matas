# Trabajo Práctico Nº 1 - Teoría de la Computación

Implementación en Python de tres tipos distintos de autómatas, desarrollados desde cero como parte del Trabajo Práctico Nº 1 de la cátedra **Teoría de la Computación**.

**Universidad de la Cuenca del Plata**
Facultad de Ingeniería, Tecnología y Arquitectura
Carrera: Ingeniería en Sistemas de Información
Sede: Corrientes
Cátedra: Ing. Sergio Lapertosa

---

## 📋 Descripción del proyecto

El objetivo del trabajo es identificar distintos tipos de autómatas vistos en clase y programar su funcionamiento, mostrando para cada uno:

- Su **definición formal** como tupla de conjuntos.
- Su **tabla de transición**.
- Su **diagrama de transición** (generado con librería gráfica).
- La **simulación paso a paso** del procesamiento de cadenas de entrada.

Se eligieron tres tipos distintos de autómatas para cubrir la mayor diversidad posible, criterio que la consigna indica como de mayor valoración.

---

## 🤖 Autómatas implementados

| Archivo | Tipo | Lenguaje reconocido | Estado |
|---|---|---|---|
| `afd_termina_en_01.py` | Autómata Finito Determinista (AFD) | Cadenas binarias que terminan en `01` | ✓ Completo |
| `afnd_contiene_ab.py`  | Autómata Finito No Determinista (AFND) | Cadenas sobre `{a,b}` que contienen la subcadena `ab` | Pendiente |
| `ap_anbn.py`           | Autómata con Pila (AP / PDA) | Lenguaje `L = { aⁿbⁿ | n ≥ 1 }` | Pendiente |

### 1. AFD — Cadenas terminadas en `01`

Autómata finito determinista que reconoce cadenas sobre el alfabeto `{0, 1}` que finalizan con la subcadena `01`.

**Definición formal:** `M = (Q, Σ, δ, q₀, F)`
- `Q  = {q0, q1, q2}`
- `Σ  = {0, 1}`
- `q₀ = q0`
- `F  = {q2}`

**Ejemplos aceptados:** `01`, `001`, `1101`, `111101`
**Ejemplos rechazados:** `""`, `0`, `1`, `10`, `100`

### 2. AFND — Cadenas que contienen `ab`

Autómata finito no determinista que reconoce cadenas sobre el alfabeto `{a, b}` que contienen al menos una ocurrencia de la subcadena `ab`.

**Definición formal:** `M = (Q, Σ, δ, q₀, F)`
- `Q  = {q0, q1, q2}`
- `Σ  = {a, b}`
- `q₀ = q0`
- `F  = {q2}`

A diferencia del AFD, la función de transición devuelve un **conjunto** de estados destino. Esto se simula manteniendo varios estados activos en paralelo durante el procesamiento de la cadena.

**Ejemplos aceptados:** `ab`, `aab`, `bab`, `abbb`, `babba`
**Ejemplos rechazados:** `""`, `a`, `b`, `ba`, `bbaa`, `aaa`

### 3. AP — Lenguaje `aⁿbⁿ`

Autómata con pila que reconoce el lenguaje formado por una cantidad `n` de símbolos `a` seguida de exactamente la misma cantidad de símbolos `b`.

**Definición formal:** `M = (Q, Σ, Γ, δ, q₀, Z₀, F)`
- `Q  = {q0, q1, q2}`
- `Σ  = {a, b}`
- `Γ  = {A, Z}` (alfabeto de la pila)
- `q₀ = q0`
- `Z₀ = Z` (símbolo inicial de la pila)
- `F  = {q2}`

Este autómata **no puede ser reconocido por un autómata finito**, ya que requiere "contar" la cantidad de símbolos `a` para luego compararla con la cantidad de `b`. La pila proporciona la memoria necesaria para hacerlo: se apila una marca por cada `a` y se desapila por cada `b`.

**Ejemplos aceptados:** `ab`, `aabb`, `aaabbb`, `aaaabbbb`
**Ejemplos rechazados:** `""`, `a`, `b`, `abab`, `aab`, `abb`, `ba`

---

## ⚙️ Requisitos

- **Python 3.8** o superior
- Librería **graphviz** de Python:
  ```bash
  pip install graphviz
  ```
- Binario de **Graphviz** instalado en el sistema (necesario para renderizar los diagramas a PNG):
  - **Windows:** descargar desde [graphviz.org/download](https://graphviz.org/download/) y agregarlo al PATH
  - **Linux (Debian/Ubuntu):** `sudo apt install graphviz`
  - **macOS:** `brew install graphviz`

---

## ▶️ Cómo ejecutar

Cada autómata es un script independiente. Al ejecutarlo realiza tres acciones:

1. Imprime su **tabla de transición** por consola.
2. Procesa una serie de **cadenas de prueba** mostrando cada transición aplicada.
3. Genera un archivo `diagrama_*.png` con el **diagrama de transición**.

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd <nombre-del-repo>

# Instalar dependencias
pip install graphviz

# Ejecutar el AFD (único autómata implementado por ahora)
python afd_termina_en_01.py

# Los siguientes scripts se agregarán en próximas entregas:
# python afnd_contiene_ab.py
# python ap_anbn.py
```

---

## 🧱 Estructura del código

Los tres scripts siguen la **misma estructura** para facilitar la comparación entre los distintos tipos de autómatas:

1. **Docstring inicial** con la definición formal del autómata, ejemplos de cadenas aceptadas/rechazadas y explicación del lenguaje reconocido.
2. **Diccionario `TRANSICIONES`** que representa la función de transición δ.
3. **Constantes** del autómata: `ESTADO_INICIAL`, `ESTADOS_FINALES`, `ALFABETO`.
4. **Función `procesar_cadena(cadena)`** que ejecuta el autómata sobre una entrada e imprime el rastro de ejecución paso a paso.
5. **Función `imprimir_tabla_transicion()`** que muestra la tabla de transición formateada por consola.
6. **Función `generar_diagrama()`** que dibuja el diagrama de transición usando `graphviz`.
7. **Bloque `if __name__ == "__main__"`** con los casos de prueba.

---

## 🔍 Diferencias clave entre los tres autómatas

| Característica | AFD | AFND | AP |
|---|---|---|---|
| Función de transición | Devuelve **un único** estado | Devuelve **un conjunto** de estados | Devuelve estado + operación sobre la pila |
| Memoria adicional | Ninguna | Ninguna | **Pila** (LIFO) |
| Simulación | Un estado activo a la vez | Conjunto de estados activos en paralelo | Estado actual + contenido de la pila |
| Transiciones ε | No usa | No usa (en esta implementación) | Sí (al final, para llegar a `q2`) |
| Poder expresivo | Lenguajes regulares | Lenguajes regulares (equivale al AFD) | Lenguajes libres de contexto |

---

## 🛠️ Tecnologías utilizadas

- **Python 3** — lenguaje de implementación
- **graphviz** — librería para generar los diagramas de transición
- **Git / GitHub** — control de versiones

---

## 📚 Bibliografía consultada

- Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2007). *Introducción a la teoría de autómatas, lenguajes y computación* (3ª ed.). Pearson Addison-Wesley.
- Sipser, M. (2013). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.
- Kelley, D. (1995). *Teoría de autómatas y lenguajes formales*. Prentice Hall.
- Material de cátedra disponible en el Aula Virtual.

---

## 👥 Autores

- *Sebastiano Corradi* — DNI: *45103869*
- *Juan Martin Quiroz Solla* — DNI: *XXXXXXXX*
- *Juan Martin Quiroz Solla* — DNI: *XXXXXXXX*

---

## 📅 Información académica

- **Asignatura:** Teoría de la Computación
- **Eje temático:** Nº 1 - Expresiones Regulares y lenguajes de contexto libre
- **Docente:** Ing. Sergio Lapertosa
- **Fecha de entrega del documento:** 9 de abril
- **Fecha de exposición:** 10 de abril
