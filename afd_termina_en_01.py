"""
Autómata Finito Determinista (AFD) - Cadenas binarias que terminan en "01"
==========================================================================

Definición formal  M = (Q, Σ, δ, q0, F):

    Q  = {q0, q1, q2}          -- conjunto de estados
    Σ  = {0, 1}                 -- alfabeto de entrada
    q0 = q0                     -- estado inicial
    F  = {q2}                   -- conjunto de estados finales (de aceptación)

    Función de transición δ:
        δ(q0, 0) = q1
        δ(q0, 1) = q0
        δ(q1, 0) = q1
        δ(q1, 1) = q2
        δ(q2, 0) = q1
        δ(q2, 1) = q0

Intuición de los estados:
    q0 — estado inicial / "no hemos visto nada útil todavía" (o el último
         símbolo fue un 1 que rompe cualquier sufijo "0·").
    q1 — "el último símbolo leído fue un 0" (tenemos la primera parte del
         sufijo "01" cubierta).
    q2 — "los últimos dos símbolos leídos fueron 0 seguido de 1", es decir,
         la cadena termina en "01" → estado de aceptación.

Ejemplos:
    Aceptadas : "01", "001", "1101", "111101", "0101"
    Rechazadas: "", "0", "1", "10", "100", "11"

Materia  : Teoría de la Computación
Trabajo  : TP1 — Autómata 1 de 3 (AFD)
Institución: Universidad de la Cuenca del Plata
"""

# ---------------------------------------------------------------------------
# Definición del autómata
# ---------------------------------------------------------------------------

# Conjunto de estados como conjunto de Python; usamos strings para que sean
# legibles al imprimir transiciones y en el diagrama.
ESTADOS = {"q0", "q1", "q2"}

# Alfabeto explícito: lo necesitamos para validar cada símbolo antes de
# consultar la tabla de transición y para recorrer columnas en la tabla.
ALFABETO = {"0", "1"}

# Estado inicial
ESTADO_INICIAL = "q0"

# Conjunto de estados finales (de aceptación).  Es un conjunto para que la
# verificación de pertenencia sea O(1) aunque haya muchos estados finales.
ESTADOS_FINALES = {"q2"}

# Función de transición representada como diccionario (estado, símbolo) → estado.
# Esta estructura es la traducción directa de la tabla δ de la definición formal:
# clave = par (estado actual, símbolo leído), valor = estado destino.
TRANSICIONES = {
    ("q0", "0"): "q1",
    ("q0", "1"): "q0",
    ("q1", "0"): "q1",
    ("q1", "1"): "q2",
    ("q2", "0"): "q1",
    ("q2", "1"): "q0",
}


# ---------------------------------------------------------------------------
# Procesamiento de cadenas
# ---------------------------------------------------------------------------

def procesar_cadena(cadena: str) -> bool:
    """
    Simula la ejecución del AFD sobre `cadena` símbolo a símbolo.

    Por cada símbolo imprime la transición aplicada con notación formal:
        δ(estado_actual, símbolo) = estado_siguiente

    Retorna True si la cadena es aceptada (el estado final pertenece a F),
    False en caso contrario.

    Parámetros
    ----------
    cadena : str
        Cadena binaria a procesar.  Puede ser la cadena vacía.

    Retorna
    -------
    bool
        True → aceptada, False → rechazada.
    """
    print(f"\nProcesando cadena: '{cadena}'")

    # Caso especial: cadena vacía.  El AFD permanece en q0, que no es estado
    # final, por lo que la cadena vacía siempre se rechaza.
    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estado final: {ESTADO_INICIAL}  →  RECHAZADA")
        return False

    estado_actual = ESTADO_INICIAL

    for simbolo in cadena:
        # Validación: rechazamos de inmediato si el símbolo no es del alfabeto,
        # porque consultar TRANSICIONES con una clave inexistente lanzaría KeyError
        # y daría un error confuso al usuario.
        if simbolo not in ALFABETO:
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False

        estado_siguiente = TRANSICIONES[(estado_actual, simbolo)]
        # Notación formal de transición: δ(estado, símbolo) = nuevo_estado
        print(f"  δ({estado_actual}, {simbolo}) = {estado_siguiente}")
        estado_actual = estado_siguiente

    # La cadena es aceptada si y solo si el estado en el que detuvimos la
    # lectura pertenece al conjunto de estados finales F.
    aceptada = estado_actual in ESTADOS_FINALES
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    print(f"  Estado final: {estado_actual}  →  {veredicto}")
    return aceptada


# ---------------------------------------------------------------------------
# Tabla de transición
# ---------------------------------------------------------------------------

def imprimir_tabla_transicion() -> None:
    """
    Imprime la tabla de transición δ en la consola usando caracteres de cuadro
    Unicode para que sea legible y presentable en el informe.

    Convenciones de la tabla:
        →  marca el estado inicial (q0).
        *  marca los estados finales (q2).
    """
    # Ordenamos los estados y símbolos para que la tabla siempre se muestre
    # en el mismo orden, independientemente del orden interno del set/dict.
    estados_ord = sorted(ESTADOS)
    simbolos_ord = sorted(ALFABETO)

    # Calculamos el ancho de la columna de estados considerando que pueden
    # llevar el prefijo "→ " o "* " (2 caracteres + espacio).
    ancho_estado = max(len(e) + 3 for e in estados_ord)  # +3 para "→ " o "* "
    ancho_simbolo = 6  # ancho fijo para las columnas de símbolos

    # Línea superior de la tabla
    sep_top = (
        "┌" + "─" * ancho_estado + "┬"
        + ("┬".join("─" * ancho_simbolo for _ in simbolos_ord))
        + "┐"
    )
    # Línea separadora intermedia
    sep_mid = (
        "├" + "─" * ancho_estado + "┼"
        + ("┼".join("─" * ancho_simbolo for _ in simbolos_ord))
        + "┤"
    )
    # Línea inferior
    sep_bot = (
        "└" + "─" * ancho_estado + "┴"
        + ("┴".join("─" * ancho_simbolo for _ in simbolos_ord))
        + "┘"
    )

    print("\nTabla de transición δ:")
    print(sep_top)

    # Encabezado: columna de estado + una columna por símbolo del alfabeto
    encabezado_simbolos = "".join(
        f"│{s:^{ancho_simbolo}}" for s in simbolos_ord
    )
    print(f"│{'δ':^{ancho_estado}}{encabezado_simbolos}│")
    print(sep_mid)

    # Filas: una por estado
    for estado in estados_ord:
        # Prefijo que indica si es inicial (→) y/o final (*).
        # En este AFD q0 es inicial y q2 es final; no coinciden, pero el
        # código es general por si en otro autómata un estado fuera ambos.
        prefijo = ""
        if estado == ESTADO_INICIAL:
            prefijo += "→ "
        if estado in ESTADOS_FINALES:
            prefijo += "* "
        # Alineamos la celda de estado a la izquierda para que los prefijos
        # queden pegados al nombre del estado.
        celda_estado = f"{prefijo}{estado}"

        celdas_transicion = "".join(
            f"│{TRANSICIONES.get((estado, s), '-'):^{ancho_simbolo}}"
            for s in simbolos_ord
        )
        print(f"│{celda_estado:<{ancho_estado}}{celdas_transicion}│")

    print(sep_bot)
    print("  → estado inicial     * estado(s) final(es)")


# ---------------------------------------------------------------------------
# Diagrama con Graphviz
# ---------------------------------------------------------------------------

def generar_diagrama() -> None:
    """
    Genera el diagrama de transición del AFD y lo guarda como diagrama_afd.png.

    Usamos la librería `graphviz` de Python (wrapper sobre el binario de Graphviz)
    para describir el grafo en formato DOT y renderizarlo a PNG.

    Decisiones de diseño:
        - rankdir="LR": el diagrama crece de izquierda a derecha, que es la
          convención más común en libros de Teoría de la Computación.
        - Nodo invisible "__inicio__": la flecha de inicio que apunta al estado
          inicial (q0) no tiene un estado fuente real; se modela con un nodo
          invisible de tamaño 0.
        - doublecircle para estados finales, circle para los demás: notación
          estándar de autómatas.
    """
    try:
        from graphviz import Digraph
    except ImportError:
        # Avisamos con claridad para que el usuario sepa qué instalar,
        # en lugar de dejar que Python lance un ImportError críptico.
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        print("    También necesitás el binario de Graphviz del sistema:")
        print("    https://graphviz.org/download/")
        return

    # Creamos un dígrafo (grafo dirigido) con el motor "dot", que respeta
    # jerarquías y es el más adecuado para autómatas.
    diagrama = Digraph(name="AFD_termina_en_01", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")

    # --- Nodos ---
    # Nodo invisible que sirve como origen de la flecha de inicio.
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        if estado in ESTADOS_FINALES:
            # Los estados finales se dibujan con doble círculo (notación estándar).
            diagrama.node(estado, shape="doublecircle")
        else:
            diagrama.node(estado, shape="circle")

    # --- Flecha de inicio ---
    # Conectamos el nodo invisible con el estado inicial para representar la
    # convención gráfica de "aquí empieza la lectura".
    diagrama.edge("__inicio__", ESTADO_INICIAL)

    # --- Aristas de transición ---
    # Agrupamos las transiciones por par (origen, destino) para que múltiples
    # símbolos entre los mismos estados aparezcan en una sola arista etiquetada
    # con "0,1" en lugar de dos aristas separadas (más limpio visualmente).
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, simbolo), destino in TRANSICIONES.items():
        aristas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        diagrama.edge(origen, destino, label=etiqueta)

    # Renderizamos el diagrama.  cleanup=True elimina el archivo .gv intermedio
    # para no dejar archivos temporales en el directorio.
    nombre_archivo = "diagrama_afd"
    diagrama.render(nombre_archivo, cleanup=True)
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 1. Mostrar la tabla de transición para verificar visualmente el autómata
    #    antes de procesar cadenas.
    imprimir_tabla_transicion()

    # 2. Cadenas de prueba que cubren distintos casos:
    #    - Casos que deben ser aceptados  : "01", "001", "1101", "111101"
    #    - Casos que deben ser rechazados : "", "0", "1", "10", "100"
    cadenas_prueba = ["01", "001", "1101", "111101", "", "0", "1", "10", "100"]

    print("\n" + "=" * 55)
    print("PROCESAMIENTO DE CADENAS DE PRUEBA")
    print("=" * 55)

    resultados = {}
    for cadena in cadenas_prueba:
        resultados[cadena] = procesar_cadena(cadena)

    # Resumen final: útil para contrastar de un vistazo con la tabla teórica.
    print("\n" + "=" * 55)
    print("RESUMEN")
    print("=" * 55)
    print(f"{'Cadena':<12} {'Resultado'}")
    print("-" * 25)
    for cadena, aceptada in resultados.items():
        etiqueta = "ACEPTADA" if aceptada else "RECHAZADA"
        print(f"'{cadena}'  {' ' * (10 - len(cadena))}{etiqueta}")

    # 3. Generar el diagrama PNG del autómata.
    generar_diagrama()
