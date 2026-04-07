"""
Autómata con Pila (AP / PDA) - Lenguaje L = { aⁿbⁿ | n ≥ 1 }
==============================================================

Definición formal  M = (Q, Σ, Γ, δ, q0, Z0, F):

    Q  = {q0, q1, q2}          -- conjunto de estados
    Σ  = {a, b}                 -- alfabeto de entrada
    Γ  = {A, Z}                 -- alfabeto de la pila (A = marca de conteo,
                                   Z = símbolo de fondo, marca que la pila
                                   está "limpia")
    q0 = q0                     -- estado inicial
    Z0 = Z                      -- símbolo inicial de la pila
    F  = {q2}                   -- conjunto de estados finales (de aceptación)

    Función de transición δ (formato: (estado, entrada, tope) → (nuevo_estado, a_apilar)):
        δ(q0, a, Z) = (q0, [A, Z])   apila A sobre Z (primera 'a' leída)
        δ(q0, a, A) = (q0, [A, A])   apila otra A (una 'a' más)
        δ(q0, b, A) = (q1, [])       primera 'b': desapila la A sin reemplazarla
        δ(q1, b, A) = (q1, [])       'b' siguientes: sigue desapilando
        δ(q1, ε, Z) = (q2, [Z])      transición vacía: si solo queda Z, acepta

    Nota sobre la lista a_apilar:
        El PRIMER elemento de la lista queda en el TOPE de la pila (se apila
        último). La lista [] significa "desapilar sin reemplazar".

Intuición de los estados:
    q0 — "estamos leyendo las 'a'": por cada 'a' apilamos una marca A.
    q1 — "estamos leyendo las 'b'": por cada 'b' desapilamos una A.
         Si hay más 'b' que 'A' en la pila, no hay transición → rechazo.
    q2 — "las cantidades coincidieron": la pila quedó con solo Z (fondo),
         lo que prueba que hubo exactamente la misma cantidad de 'a' que de 'b'.

¿Por qué necesitamos una pila?
    El lenguaje aⁿbⁿ es LIBRE DE CONTEXTO pero NO REGULAR.  Un autómata finito
    (AFD o AFND) no puede reconocerlo porque tiene solo un conjunto finito de
    estados: no importa cuántos estados se definan, siempre existe un n lo
    suficientemente grande como para que el autómata "pierda la cuenta" de
    cuántas 'a' vio (Lema del Bombeo para lenguajes regulares).  La pila
    resuelve esto porque actúa como memoria dinámica de tamaño ilimitado:
    apilamos una marca por cada 'a' y la desapilamos por cada 'b'.  Si al
    terminar la cadena la pila volvió exactamente a su estado inicial (solo Z),
    es porque hubo la misma cantidad de 'a' que de 'b'.  Esta capacidad de
    contar con memoria ilimitada es lo que distingue a los AP de los autómatas
    finitos y los hace equivalentes a las gramáticas libres de contexto.

Ejemplos:
    Aceptadas : "ab", "aabb", "aaabbb", "aaaabbbb"
    Rechazadas: "", "a", "b", "abab", "aab", "abb", "ba"

Materia  : Teoría de la Computación
Trabajo  : TP1 — Autómata 3 de 3 (AP)
Institución: Universidad de la Cuenca del Plata
"""

# ---------------------------------------------------------------------------
# Definición del autómata
# ---------------------------------------------------------------------------

# Conjunto de estados como conjunto de Python; usamos strings para que sean
# legibles al imprimir transiciones y en el diagrama.
ESTADOS = {"q0", "q1", "q2"}

# Alfabeto de entrada explícito: lo necesitamos para validar cada símbolo antes
# de consultar la tabla de transición y para recorrer columnas en la tabla.
ALFABETO = {"a", "b"}

# Estado inicial
ESTADO_INICIAL = "q0"

# Conjunto de estados finales (de aceptación).  Es un conjunto para que la
# verificación de pertenencia sea O(1) aunque haya muchos estados finales.
ESTADOS_FINALES = {"q2"}

# Alfabeto de la pila: los símbolos que pueden aparecer en la pila.
# Z es el símbolo de fondo (siempre está al inicio y marca que la pila está vacía
# de marcas de conteo). A es la marca que apilamos por cada 'a' leída.
ALFABETO_PILA = {"A", "Z"}

# Símbolo inicial de la pila: la pila arranca con solo este símbolo.
SIMBOLO_INICIAL_PILA = "Z"

# Función de transición representada como diccionario
#   (estado, símbolo_entrada, tope_pila) → (nuevo_estado, lista_a_apilar)
#
# Diferencias clave respecto al AFD y el AFND:
#   1. La clave tiene TRES componentes: estado, símbolo de entrada y tope de pila.
#      Esto refleja que la decisión del AP depende no solo de lo que lee sino
#      también de lo que hay en el tope de la pila.
#   2. El valor incluye una LISTA de símbolos a apilar.  Una lista vacía []
#      significa "desapilar el tope sin poner nada en su lugar" (el tope
#      simplemente desaparece).  El primer elemento de la lista quedará en el
#      tope después de la transición.
#   3. None como símbolo de entrada representa la transición ε (épsilon):
#      se aplica sin consumir ningún símbolo de la cadena.  Es necesaria para
#      poder pasar al estado final q2 una vez que la cadena ya fue leída
#      completamente (ver procesar_cadena).
TRANSICIONES = {
    ("q0", "a", "Z"): ("q0", ["A", "Z"]),   # primera 'a': apila A, deja Z debajo
    ("q0", "a", "A"): ("q0", ["A", "A"]),   # 'a' siguientes: apila otra A
    ("q0", "b", "A"): ("q1", []),           # primera 'b': desapila la A
    ("q1", "b", "A"): ("q1", []),           # 'b' siguientes: sigue desapilando
    ("q1", None,  "Z"): ("q2", ["Z"]),      # ε: pila en fondo → aceptar
}


# ---------------------------------------------------------------------------
# Procesamiento de cadenas
# ---------------------------------------------------------------------------

def procesar_cadena(cadena: str) -> bool:
    """
    Simula la ejecución del AP sobre `cadena` símbolo a símbolo, manejando
    explícitamente el estado de la pila en cada paso.

    Por cada símbolo imprime el paso aplicado con el formato:
        δ(estado, símbolo, tope) -> (nuevo_estado, apilado) | Pila: [...]

    Al terminar la cadena aplica en bucle las transiciones ε disponibles,
    lo que permite llegar al estado final q2 sin consumir más entrada.

    Retorna True si el estado final pertenece a F, False en caso contrario.

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

    # Inicializamos el estado y la pila.
    # Representamos la pila como una lista de Python donde el ÚLTIMO elemento
    # (pila[-1]) es el TOPE.  Esta convención nos permite usar append() y pop()
    # sin argumentos, que operan sobre el final de la lista en O(1) y son la
    # forma más directa de implementar el comportamiento LIFO de una pila.
    estado = ESTADO_INICIAL
    pila: list[str] = [SIMBOLO_INICIAL_PILA]

    print(f"  Estado inicial: {estado} | Pila: {pila}")

    for simbolo in cadena:
        # Validación: rechazamos de inmediato si el símbolo no es del alfabeto.
        if simbolo not in ALFABETO:
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False

        # Verificamos que la pila no esté vacía antes de intentar leer el tope.
        # En teoría esto no debería ocurrir en este AP (siempre queda al menos Z),
        # pero la guarda evita un IndexError y hace el código defensivo.
        if not pila:
            print(f"  Pila vacía — no hay transición posible para '{simbolo}'")
            return False

        tope = pila[-1]

        # Buscamos la transición correspondiente al triple (estado, símbolo, tope).
        # Si no existe, el AP se "traba": no hay movimiento posible y la cadena
        # se rechaza.  Esto ocurre, por ejemplo, si leemos 'b' cuando el tope
        # es Z (más 'b' que 'a'), o si leemos 'a' estando en q1 (después de
        # haber comenzado a leer 'b').
        if (estado, simbolo, tope) not in TRANSICIONES:
            print(f"  No hay transición para δ({estado}, {simbolo}, {tope}) — RECHAZADA")
            return False

        nuevo_estado, a_apilar = TRANSICIONES[(estado, simbolo, tope)]

        # Aplicamos la transición sobre la pila:
        # 1. Desapilamos el tope actual (siempre, en toda transición).
        pila.pop()
        # 2. Apilamos los nuevos símbolos en orden INVERSO al de la lista.
        #    Usamos reversed() porque queremos que el PRIMER elemento de la
        #    lista quede en el TOPE de la pila, y con append() el último en
        #    agregarse queda arriba.  Ejemplo: a_apilar = ["A", "Z"] → primero
        #    hacemos append("Z") y luego append("A"), dejando A en el tope.
        for sym in reversed(a_apilar):
            pila.append(sym)

        apilado_str = "".join(a_apilar) if a_apilar else "ε"
        print(f"  δ({estado}, {simbolo}, {tope}) -> ({nuevo_estado}, {apilado_str}) | Pila: {pila}")

        estado = nuevo_estado

    # --- Transiciones ε (épsilon) ---
    # Una transición ε se aplica sin consumir ningún símbolo de entrada.
    # Es necesaria en este AP porque, después de desapilar la última A con la
    # última 'b', el autómata queda en q1 con solo Z en la pila, y la cadena
    # ya terminó.  Sin una transición ε no habría forma de pasar a q2 (estado
    # final) sin leer otro símbolo — pero no hay más símbolos que leer.
    # El bucle sigue aplicando transiciones ε mientras existan para el estado
    # y tope actuales.  En este AP hay a lo sumo una ε-transición, pero el
    # bucle es general y funciona para cualquier AP con cadenas de ε.
    while True:
        if not pila:
            break
        tope = pila[-1]
        if (estado, None, tope) not in TRANSICIONES:
            break  # no hay ε-transición disponible, salimos del bucle

        nuevo_estado, a_apilar = TRANSICIONES[(estado, None, tope)]
        pila.pop()
        for sym in reversed(a_apilar):
            pila.append(sym)

        apilado_str = "".join(a_apilar) if a_apilar else "ε"
        print(f"  δ({estado}, ε, {tope}) -> ({nuevo_estado}, {apilado_str}) | Pila: {pila}")

        estado = nuevo_estado

    # La cadena es aceptada si y solo si el estado en el que nos detuvimos
    # pertenece al conjunto de estados finales F.
    aceptada = estado in ESTADOS_FINALES
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    print(f"  Estado final: {estado} | Pila: {pila}  →  {veredicto}")
    return aceptada


# ---------------------------------------------------------------------------
# Tabla de transición
# ---------------------------------------------------------------------------

def imprimir_tabla_transicion() -> None:
    """
    Imprime la tabla de transición δ en la consola usando caracteres de cuadro
    Unicode para que sea legible y presentable en el informe.

    A diferencia del AFD y el AFND (cuyas tablas son grillas estado × símbolo),
    la tabla del AP tiene una FILA POR REGLA, ya que la función de transición
    depende de tres argumentos: estado, símbolo de entrada y tope de pila.
    Las columnas son: Estado | Entrada | Tope | Nuevo estado | A apilar.

    Convenciones de la tabla:
        →  marca el estado inicial (q0).
        *  marca los estados finales (q2).
        ε  indica transición sin consumir entrada (símbolo None) o lista vacía.
    """
    # Ordenamos los estados para que los prefijos y el recorrido sean consistentes.
    estados_ord = sorted(ESTADOS)

    # Anchos de cada columna, elegidos para que el contenido más ancho quepa
    # con margen.  "Nuevo estado" es la columna más larga en el encabezado.
    ancho_estado   = max(len(e) + 3 for e in estados_ord)  # +3 para "→ " o "* "
    ancho_entrada  = 9    # "Entrada" tiene 7 letras; 9 deja margen para "a", "b", "ε"
    ancho_tope     = 7    # "Tope" tiene 4; 7 cabe "Z" y "A" con holgura
    ancho_nuevo    = 14   # "Nuevo estado" tiene 12 letras
    ancho_apilar   = 10   # "A apilar" tiene 8; 10 cabe "AZ", "AA", "Z", "ε"

    anchos = [ancho_estado, ancho_entrada, ancho_tope, ancho_nuevo, ancho_apilar]

    def linea(izq, sep, der):
        # Construye una línea horizontal usando los anchos definidos.
        return izq + sep.join("─" * a for a in anchos) + der

    sep_top = linea("┌", "┬", "┐")
    sep_mid = linea("├", "┼", "┤")
    sep_bot = linea("└", "┴", "┘")

    print("\nTabla de transición δ:")
    print(sep_top)

    # Encabezado
    print(
        f"│{'δ':^{ancho_estado}}"
        f"│{'Entrada':^{ancho_entrada}}"
        f"│{'Tope':^{ancho_tope}}"
        f"│{'Nuevo estado':^{ancho_nuevo}}"
        f"│{'A apilar':^{ancho_apilar}}│"
    )
    print(sep_mid)

    # Filas: una por cada regla de transición, en orden canónico
    # (por estado origen, luego ε al final dentro de cada estado).
    def clave_orden(item):
        (est, ent, tope), _ = item
        # None (ε) va después de los símbolos concretos dentro del mismo estado.
        return (est, "" if ent is None else ent, tope)

    for (est, ent, tope), (nuevo_est, a_apilar) in sorted(TRANSICIONES.items(), key=clave_orden):
        # Prefijo de estado: → para inicial, * para final.
        prefijo = ""
        if est == ESTADO_INICIAL:
            prefijo += "→ "
        if est in ESTADOS_FINALES:
            prefijo += "* "
        celda_estado = f"{prefijo}{est}"

        entrada_str  = "ε" if ent is None else ent
        apilar_str   = "ε" if not a_apilar else "".join(a_apilar)

        print(
            f"│{celda_estado:<{ancho_estado}}"
            f"│{entrada_str:^{ancho_entrada}}"
            f"│{tope:^{ancho_tope}}"
            f"│{nuevo_est:^{ancho_nuevo}}"
            f"│{apilar_str:^{ancho_apilar}}│"
        )

    print(sep_bot)
    print("  → estado inicial     * estado(s) final(es)     ε transición/apilado vacío")


# ---------------------------------------------------------------------------
# Diagrama con Graphviz
# ---------------------------------------------------------------------------

def generar_diagrama() -> None:
    """
    Genera el diagrama de transición del AP y lo guarda como diagrama_ap.png.

    Usamos la librería `graphviz` de Python (wrapper sobre el binario de Graphviz)
    para describir el grafo en formato DOT y renderizarlo a PNG.

    Decisiones de diseño:
        - rankdir="LR": el diagrama crece de izquierda a derecha, convención
          estándar en libros de Teoría de la Computación.
        - Nodo invisible "__inicio__": la flecha de inicio hacia q0 no tiene
          estado fuente real; se modela con un nodo invisible de tamaño 0.
        - doublecircle para estados finales, circle para los demás.
        - Etiqueta de arista en formato "entrada, tope / apilar", por ejemplo
          "a, Z / AZ" significa "leer 'a' con Z en el tope y apilar AZ".
          Para ε se usa el símbolo ε directamente en la etiqueta.
        - Agrupación de aristas: cuando dos reglas distintas van del mismo
          estado origen al mismo estado destino, sus etiquetas se combinan
          separadas por salto de línea (\n) en una sola flecha, para mantener
          el diagrama limpio y legible.
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
    diagrama = Digraph(name="AP_anbn", format="png")
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
    # Construimos la etiqueta de cada transición en el formato estándar para AP:
    #   "entrada, tope / apilar"
    # Luego agrupamos por par (origen, destino) para que varias reglas entre
    # los mismos estados aparezcan en una sola flecha (etiquetas en líneas
    # separadas), manteniendo el diagrama limpio.
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, ent, tope), (destino, a_apilar) in TRANSICIONES.items():
        entrada_str = "ε" if ent is None else ent
        apilar_str  = "ε" if not a_apilar else "".join(a_apilar)
        etiqueta    = f"{entrada_str}, {tope} / {apilar_str}"
        aristas.setdefault((origen, destino), []).append(etiqueta)

    for (origen, destino), etiquetas in aristas.items():
        # Ordenamos las etiquetas para que el diagrama sea determinista entre
        # ejecuciones (los dicts de Python no garantizan orden de inserción
        # estable ante distintas versiones del intérprete).
        etiqueta_final = "\n".join(sorted(etiquetas))
        diagrama.edge(origen, destino, label=etiqueta_final)

    # Renderizamos el diagrama.  cleanup=True elimina el archivo .gv intermedio
    # para no dejar archivos temporales en el directorio.
    nombre_archivo = "diagrama_ap"
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
    #    - Casos que deben ser aceptados  : "ab", "aabb", "aaabbb", "aaaabbbb"
    #    - Casos que deben ser rechazados : "", "a", "b", "abab", "aab", "abb", "ba"
    cadenas_prueba = ["ab", "aabb", "aaabbb", "aaaabbbb", "", "a", "b", "abab", "aab", "abb", "ba"]

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
    print(f"{'Cadena':<14} {'Resultado'}")
    print("-" * 27)
    for cadena, aceptada in resultados.items():
        etiqueta = "ACEPTADA" if aceptada else "RECHAZADA"
        print(f"'{cadena}'  {' ' * (12 - len(cadena))}{etiqueta}")

    # 3. Generar el diagrama PNG del autómata.
    generar_diagrama()
