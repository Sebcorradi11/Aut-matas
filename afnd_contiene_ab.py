"""
Autómata Finito No Determinista (AFND) - Cadenas que contienen la subcadena "ab"
=================================================================================

Definición formal  M = (Q, Σ, δ, q0, F):

    Q  = {q0, q1, q2}          -- conjunto de estados
    Σ  = {a, b}                 -- alfabeto de entrada
    q0 = q0                     -- estado inicial
    F  = {q2}                   -- conjunto de estados finales (de aceptación)

    Función de transición δ (devuelve un CONJUNTO de estados, no uno solo):
        δ(q0, a) = {q0, q1}    ← no determinismo: ante "a" hay dos opciones
        δ(q0, b) = {q0}
        δ(q1, a) = {}          ← conjunto vacío: ninguna transición definida
        δ(q1, b) = {q2}
        δ(q2, a) = {q2}
        δ(q2, b) = {q2}

Intuición de los estados:
    q0 — "todavía no encontramos la 'a' que inicia la subcadena 'ab'", o bien
         acabamos de leer una 'b' que no completa ningún par útil.
    q1 — "acabamos de leer una 'a' que podría ser el inicio de 'ab'"; si a
         continuación viene una 'b', llegamos al estado de aceptación.
    q2 — "ya encontramos al menos una ocurrencia de 'ab'" → estado de aceptación.
         Desde aquí cualquier símbolo mantiene la aceptación (la subcadena ya
         fue encontrada y eso no se puede "deshacer").

El no determinismo aparece en δ(q0, a) = {q0, q1}: al leer una 'a' desde q0
el autómata "apuesta" simultáneamente a dos posibilidades — que esa 'a' sea el
inicio de un futuro "ab" (bifurcación a q1) y que no lo sea (bifurcación a q0).

Ejemplos:
    Aceptadas : "ab", "aab", "bab", "abbb", "babba"
    Rechazadas: "", "a", "b", "ba", "bbaa", "aaa"

Materia  : Teoría de la Computación
Trabajo  : TP1 — Autómata 2 de 3 (AFND)
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
ALFABETO = {"a", "b"}

# Estado inicial
ESTADO_INICIAL = "q0"

# Conjunto de estados finales (de aceptación).  Es un conjunto para que la
# verificación de pertenencia sea O(1) aunque haya muchos estados finales.
ESTADOS_FINALES = {"q2"}

# Función de transición representada como diccionario (estado, símbolo) → SET de estados.
# La diferencia fundamental con el AFD está aquí: el valor ya no es un único
# estado destino sino un set() de Python con todos los estados alcanzables.
# Usar set() vacío (en vez de None o ausencia de clave) para las transiciones
# sin salida es intencional: permite tratar todos los casos de forma uniforme
# con el operador de unión sin necesitar condiciones especiales (ver procesar_cadena).
TRANSICIONES = {
    ("q0", "a"): {"q0", "q1"},   # no determinismo: dos destinos posibles
    ("q0", "b"): {"q0"},
    ("q1", "a"): set(),          # trampa: ningún estado destino definido
    ("q1", "b"): {"q2"},
    ("q2", "a"): {"q2"},
    ("q2", "b"): {"q2"},
}


# ---------------------------------------------------------------------------
# Procesamiento de cadenas
# ---------------------------------------------------------------------------

def procesar_cadena(cadena: str) -> bool:
    """
    Simula la ejecución del AFND sobre `cadena` usando el método de subconjuntos
    "en línea": en lugar de explorar cada rama por separado (backtracking),
    mantenemos un único conjunto de estados activos que se actualiza en cada paso.

    Por cada símbolo imprime el conjunto de estados activos antes y después
    de aplicar las transiciones, junto al símbolo leído.

    Retorna True si al terminar la cadena el conjunto de estados activos tiene
    al menos un estado final; False en caso contrario.

    Parámetros
    ----------
    cadena : str
        Cadena sobre {a, b} a procesar.  Puede ser la cadena vacía.

    Retorna
    -------
    bool
        True → aceptada, False → rechazada.
    """
    print(f"\nProcesando cadena: '{cadena}'")

    # Caso especial: cadena vacía.  El AFND parte con {q0} y no lee ningún
    # símbolo, por lo que el conjunto de estados activos al final es {q0}.
    # Como q0 no es estado final, la cadena vacía siempre se rechaza.
    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estados activos finales: {{{ESTADO_INICIAL}}}  →  RECHAZADA")
        return False

    # El AFND comienza con un conjunto de un solo estado: el estado inicial.
    # Conceptualmente esto representa que, antes de leer cualquier símbolo,
    # hay exactamente una "rama de cómputo" activa.
    estados_activos = {ESTADO_INICIAL}

    for simbolo in cadena:
        # Validación: si el símbolo no pertenece a Σ, no tiene sentido buscar
        # transiciones; abortamos con el mismo criterio que el AFD.
        if simbolo not in ALFABETO:
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False

        # Calculamos el nuevo conjunto de estados activos como la UNIÓN de todos
        # los conjuntos destino de cada estado activo ante el símbolo leído.
        # Usamos |= (unión in-place) para acumular: es equivalente a una unión
        # matemática de conjuntos y evita crear listas intermedias.
        # El .get(..., set()) garantiza que los pares sin transición definida
        # aporten el conjunto vacío (neutro de la unión) en vez de lanzar KeyError.
        # Esto es lo que simula el no determinismo: en lugar de "elegir" un camino,
        # seguimos TODOS los caminos posibles en paralelo; el conjunto resultante
        # representa todos los estados que el AFND podría haber alcanzado.
        nuevos_estados: set[str] = set()
        for estado in estados_activos:
            nuevos_estados |= TRANSICIONES.get((estado, simbolo), set())

        # Notación de paso: mostramos los estados antes → símbolo → estados después.
        estados_antes = "{" + ", ".join(sorted(estados_activos)) + "}"
        estados_despues = "{" + ", ".join(sorted(nuevos_estados)) + "}" if nuevos_estados else "∅"
        print(f"  {estados_antes}  --{simbolo}-->  {estados_despues}")

        estados_activos = nuevos_estados

        # Optimización: si el conjunto quedó vacío, ninguna rama sobrevivió.
        # No tiene sentido seguir leyendo: la cadena no puede ser aceptada
        # porque una vez que no hay estados activos, la unión con cualquier
        # conjunto seguirá siendo vacía en todos los pasos restantes.
        if not estados_activos:
            print("  (conjunto de estados activos vacío — ejecución detenida)")
            print("  Estados activos finales: ∅  →  RECHAZADA")
            return False

    # La condición de aceptación en un AFND es que la INTERSECCIÓN entre el
    # conjunto de estados activos al finalizar y el conjunto F de estados
    # finales sea NO VACÍA.  No hace falta que todos los estados activos sean
    # finales, ni que el conjunto activo iguale exactamente a F: basta con que
    # al menos UNA de las ramas de cómputo haya llegado a un estado final.
    # Esto refleja la semántica del no determinismo: la cadena se acepta si
    # EXISTE al menos un cómputo aceptador, aunque haya otros que no lo sean.
    estados_finales_alcanzados = estados_activos & ESTADOS_FINALES
    aceptada = bool(estados_finales_alcanzados)
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    estados_str = "{" + ", ".join(sorted(estados_activos)) + "}"
    print(f"  Estados activos finales: {estados_str}  →  {veredicto}")
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
        ∅  indica que no hay transición definida (conjunto vacío).
    """
    # Ordenamos los estados y símbolos para que la tabla siempre se muestre
    # en el mismo orden, independientemente del orden interno del set/dict.
    estados_ord = sorted(ESTADOS)
    simbolos_ord = sorted(ALFABETO)

    # Calculamos el ancho de la columna de estados considerando que pueden
    # llevar el prefijo "→ " o "* " (2 caracteres + espacio).
    ancho_estado = max(len(e) + 3 for e in estados_ord)  # +3 para "→ " o "* "

    # El ancho de columna de símbolos debe acomodar el contenido más ancho
    # posible: "{q0, q1}" tiene 8 caracteres; usamos 10 para dejar margen.
    ancho_simbolo = 10

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
        # El código es general por si en otro autómata un estado fuera ambos.
        prefijo = ""
        if estado == ESTADO_INICIAL:
            prefijo += "→ "
        if estado in ESTADOS_FINALES:
            prefijo += "* "
        # Alineamos la celda de estado a la izquierda para que los prefijos
        # queden pegados al nombre del estado.
        celda_estado = f"{prefijo}{estado}"

        def formatear_destinos(destinos: set) -> str:
            # Convertimos el set de destinos a una cadena legible.
            # El conjunto vacío se muestra como ∅ (notación matemática estándar)
            # en lugar de "{}" para que sea inmediatamente reconocible en la tabla.
            if not destinos:
                return "∅"
            return "{" + ", ".join(sorted(destinos)) + "}"

        celdas_transicion = "".join(
            f"│{formatear_destinos(TRANSICIONES.get((estado, s), set())):^{ancho_simbolo}}"
            for s in simbolos_ord
        )
        print(f"│{celda_estado:<{ancho_estado}}{celdas_transicion}│")

    print(sep_bot)
    print("  → estado inicial     * estado(s) final(es)     ∅ sin transición")


# ---------------------------------------------------------------------------
# Diagrama con Graphviz
# ---------------------------------------------------------------------------

def generar_diagrama() -> None:
    """
    Genera el diagrama de transición del AFND y lo guarda como diagrama_afnd.png.

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
        - Agrupación de aristas: cuando dos símbolos distintos van del mismo
          origen al mismo destino, dibujamos una sola flecha con etiqueta "a, b"
          en lugar de dos flechas paralelas (más limpio y menos cruce de líneas).
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
    diagrama = Digraph(name="AFND_contiene_ab", format="png")
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
    # En el AFND, un par (origen, símbolo) puede tener VARIOS destinos (es un set).
    # Para construir el diagrama necesitamos aristas individuales (origen → destino),
    # así que expandemos los sets antes de agrupar por par (origen, destino).
    # La agrupación posterior sigue la misma lógica que el AFD: si "a" y "b"
    # van del mismo origen al mismo destino, los consolidamos en una sola flecha.
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, simbolo), destinos in TRANSICIONES.items():
        for destino in destinos:
            # Para cada destino individual del set registramos qué símbolo lo activa.
            aristas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        diagrama.edge(origen, destino, label=etiqueta)

    # Renderizamos el diagrama.  cleanup=True elimina el archivo .gv intermedio
    # para no dejar archivos temporales en el directorio.
    nombre_archivo = "diagrama_afnd"
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
    #    - Casos que deben ser aceptados  : "ab", "aab", "bab", "abbb", "babba"
    #    - Casos que deben ser rechazados : "", "a", "b", "ba", "bbaa", "aaa"
    cadenas_prueba = ["ab", "aab", "bab", "abbb", "babba", "", "a", "b", "ba", "bbaa", "aaa"]

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
