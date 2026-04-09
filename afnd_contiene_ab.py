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
# Importaciones
# ---------------------------------------------------------------------------

# Pillow se usa en graficar_recorrido para combinar verticalmente la imagen del
# diagrama con la tabla de descripciones instantáneas.  Usamos Pillow porque
# graphviz no posiciona bien una tabla como "pie" de un diagrama horizontal.
try:
    from PIL import Image
    _PIL_DISPONIBLE = True
except ImportError:
    _PIL_DISPONIBLE = False


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

def procesar_cadena(cadena: str) -> tuple:
    """
    Simula la ejecución del AFND sobre `cadena` usando el método de subconjuntos
    "en línea": en lugar de explorar cada rama por separado (backtracking),
    mantenemos un único conjunto de estados activos que se actualiza en cada paso.

    Por cada símbolo imprime el conjunto de estados activos antes y después
    de aplicar las transiciones, junto al símbolo leído.

    Retorna una tupla (aceptada, traza) donde traza es una lista de pasos
    (frozenset_origen, símbolo, frozenset_destino). Los frozensets son hashables,
    lo que permite que graficar_recorrido los use sin convertirlos. Devolver la
    traza desde aquí asegura que refleje exactamente la simulación impresa,
    incluyendo el caso de detención anticipada por conjunto vacío.

    Parámetros
    ----------
    cadena : str
        Cadena sobre {a, b} a procesar.  Puede ser la cadena vacía.

    Retorna
    -------
    tuple
        (True, traza) → aceptada, (False, traza) → rechazada.
    """
    print(f"\nProcesando cadena: '{cadena}'")

    # Caso especial: cadena vacía.  El AFND parte con {q0} y no lee ningún
    # símbolo, por lo que el conjunto de estados activos al final es {q0}.
    # Como q0 no es estado final, la cadena vacía siempre se rechaza.
    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estados activos finales: {{{ESTADO_INICIAL}}}  →  RECHAZADA")
        # ID única: el autómata parte con el conjunto inicial y entrada vacía.
        return False, [], [(frozenset({ESTADO_INICIAL}), "")]

    # El AFND comienza con un conjunto de un solo estado: el estado inicial.
    estados_activos = {ESTADO_INICIAL}
    # La traza registra cada paso como (frozenset_origen, símbolo, frozenset_destino).
    # Usamos frozenset para que los conjuntos sean hashables.
    traza: list = []
    # Las IDs del AFND son (frozenset_estados_activos, entrada_restante).
    # A diferencia del AFD (que solo guarda un estado), el AFND debe capturar el
    # conjunto completo de estados activos porque el no determinismo mantiene varias
    # "ramas de cómputo" en paralelo; la ID debe reflejar ese conjunto entero.
    ids: list = [(frozenset({ESTADO_INICIAL}), cadena)]

    for i, simbolo in enumerate(cadena):
        # Validación: si el símbolo no pertenece a Σ, no tiene sentido buscar
        # transiciones; abortamos con el mismo criterio que el AFD.
        if simbolo not in ALFABETO:
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False, traza, ids

        nuevos_estados: set[str] = set()
        for estado in estados_activos:
            nuevos_estados |= TRANSICIONES.get((estado, simbolo), set())

        estados_antes = "{" + ", ".join(sorted(estados_activos)) + "}"
        estados_despues = "{" + ", ".join(sorted(nuevos_estados)) + "}" if nuevos_estados else "∅"
        print(f"  {estados_antes}  --{simbolo}-->  {estados_despues}")

        traza.append((frozenset(estados_activos), simbolo, frozenset(nuevos_estados)))
        estados_activos = nuevos_estados
        # Guardamos la ID post-transición con el nuevo conjunto de estados activos.
        ids.append((frozenset(estados_activos), cadena[i + 1:]))

        if not estados_activos:
            print("  (conjunto de estados activos vacío — ejecución detenida)")
            print("  Estados activos finales: ∅  →  RECHAZADA")
            return False, traza, ids

    estados_finales_alcanzados = estados_activos & ESTADOS_FINALES
    aceptada = bool(estados_finales_alcanzados)
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    estados_str = "{" + ", ".join(sorted(estados_activos)) + "}"
    print(f"  Estados activos finales: {estados_str}  →  {veredicto}")
    return aceptada, traza, ids


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
    import os
    carpeta = "AFND"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, "diagrama_afnd")
    diagrama.render(nombre_archivo, cleanup=True)
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# ---------------------------------------------------------------------------
# Diagrama del recorrido con Graphviz
# ---------------------------------------------------------------------------

def graficar_recorrido(cadena: str, traza: list, ids: list) -> None:
    """
    Genera un PNG compuesto: arriba el diagrama con el recorrido resaltado y
    abajo una tabla con las descripciones instantáneas (IDs) del autómata.

    Una descripción instantánea del AFND es un par (conjunto_estados_activos,
    entrada_restante).  A diferencia del AFD (que solo tiene un estado), el AFND
    mantiene varias "ramas de cómputo" en paralelo, por lo que la ID debe capturar
    el conjunto completo de estados activos en cada instante.

    Usamos Pillow para combinar ambas imágenes verticalmente porque graphviz no
    posiciona bien una tabla como "pie" de un diagrama horizontal.

    La tabla solo aparece en los PNGs individuales y no en el diagrama combinado
    de varias cadenas, para no saturar esa imagen cuando hay muchas entradas.

    Parámetros
    ----------
    cadena : str
        Cadena que se procesó (puede ser la cadena vacía).
    traza : list
        Lista de tuplas (frozenset_origen, símbolo, frozenset_destino).
    ids : list
        Descripciones instantáneas: lista de tuplas (frozenset_estados, entrada_restante).
    """
    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        return

    if traza:
        conjunto_final = traza[-1][2]
    else:
        conjunto_final = frozenset({ESTADO_INICIAL})
    aceptada = bool(conjunto_final & ESTADOS_FINALES)

    estados_visitados: set = set()
    for conj_origen, _, conj_destino in traza:
        estados_visitados |= conj_origen
        estados_visitados |= conj_destino

    aristas_usadas: set = set()
    for conj_origen, simbolo, conj_destino in traza:
        for o in conj_origen:
            destinos_reales = TRANSICIONES.get((o, simbolo), set())
            for d in destinos_reales:
                if d in conj_destino:
                    aristas_usadas.add((o, d))

    sufijo = cadena if cadena else "epsilon"
    sufijo_seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sufijo)

    diagrama = Digraph(name=f"recorrido_AFND_{sufijo_seguro}", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        shape = "doublecircle" if estado in ESTADOS_FINALES else "circle"
        if estado in conjunto_final:
            color_final = "#B8E6B8" if aceptada else "#F4B8B8"
            diagrama.node(estado, shape=shape, style="filled", fillcolor=color_final)
        elif estado in estados_visitados:
            diagrama.node(estado, shape=shape, style="filled", fillcolor="#FFF4B8")
        else:
            diagrama.node(estado, shape=shape)

    diagrama.edge("__inicio__", ESTADO_INICIAL)

    aristas: dict = {}
    for (origen, simbolo), destinos in TRANSICIONES.items():
        for destino in destinos:
            aristas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        if (origen, destino) in aristas_usadas:
            diagrama.edge(origen, destino, label=etiqueta,
                          color="#1F4E79", penwidth="2.5", fontcolor="#1F4E79")
        else:
            diagrama.edge(origen, destino, label=etiqueta,
                          color="#CCCCCC", fontcolor="#CCCCCC")

    import os
    import tempfile

    carpeta = "AFND"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, f"recorrido_afnd_{sufijo_seguro}")

    if _PIL_DISPONIBLE:
        tmp_dir   = tempfile.gettempdir()
        tmp_diag  = os.path.join(tmp_dir, "_diag_afnd_tmp")
        tmp_tabla = os.path.join(tmp_dir, "_tabla_afnd_tmp")

        # Paso 1: renderizamos el diagrama en un archivo temporal.
        diagrama.render(tmp_diag, cleanup=True)

        # Paso 2: construimos la tabla HTML de IDs.
        # Columnas: Paso | Estados activos | Entrada restante | Acción
        encabezado_html = (
            '<TR>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Paso</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Estados activos</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Entrada restante</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Acci&#243;n</FONT></B></TD>'
            '</TR>'
        )
        filas_html = []
        for i, (conj_id, entrada_id) in enumerate(ids):
            es_ultima = (i == len(ids) - 1)
            if es_ultima:
                bg = "#B8E6B8" if aceptada else "#F4B8B8"
            else:
                bg = "#FFFFFF" if i % 2 == 0 else "#F5F5F5"

            if i == 0:
                accion = "inicio"
            else:
                accion = "leer s&#237;mbolo"
            if es_ultima:
                accion += " [ACEPTA]" if aceptada else " [RECHAZA]"

            # Mostramos el conjunto ordenado para que la representación sea
            # determinista entre ejecuciones.  Conjunto vacío → ∅.
            if conj_id:
                estados_str = "{" + ", ".join(sorted(conj_id)) + "}"
            else:
                estados_str = "&#8709;"

            entrada_display = entrada_id if entrada_id else "&#949;"

            filas_html.append(
                f'<TR>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{i}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{estados_str}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{entrada_display}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{accion}</FONT></TD>'
                f'</TR>'
            )

        label_tabla = (
            '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">'
            + encabezado_html
            + "".join(filas_html)
            + '</TABLE>>'
        )

        tabla_dot = Digraph(format="png")
        tabla_dot.attr(bgcolor="white")
        tabla_dot.node("t", label=label_tabla, shape="plaintext")
        tabla_dot.render(tmp_tabla, cleanup=True)

        # Paso 3: combinamos verticalmente diagrama y tabla.
        img_diag  = Image.open(tmp_diag  + ".png").convert("RGB")
        img_tabla = Image.open(tmp_tabla + ".png").convert("RGB")

        padding    = 20
        max_ancho  = max(img_diag.width, img_tabla.width)
        alto_total = img_diag.height + padding + img_tabla.height

        combinada = Image.new("RGB", (max_ancho, alto_total), (255, 255, 255))
        combinada.paste(img_diag,  ((max_ancho - img_diag.width)  // 2, 0))
        combinada.paste(img_tabla, ((max_ancho - img_tabla.width) // 2,
                                    img_diag.height + padding))
        combinada.save(nombre_archivo + ".png")

        # Paso 4: eliminamos los temporales.
        img_diag.close()
        img_tabla.close()
        os.remove(tmp_diag  + ".png")
        os.remove(tmp_tabla + ".png")
    else:
        diagrama.render(nombre_archivo, cleanup=True)
        print("  [!] Instalá Pillow para incluir la tabla de IDs: pip install Pillow")

    print(f"  Recorrido guardado como '{nombre_archivo}.png'")


# ---------------------------------------------------------------------------
# Modo interactivo
# ---------------------------------------------------------------------------

def modo_interactivo() -> None:
    """
    Inicia un loop interactivo donde el usuario ingresa cadenas y el autómata
    las procesa mostrando el resultado paso a paso y generando el diagrama
    del recorrido.
    """
    alfabeto_str = "{" + ", ".join(sorted(ALFABETO)) + "}"
    print("\n" + "=" * 60)
    print("  MODO INTERACTIVO — AFND")
    print(f"  Alfabeto válido: {alfabeto_str}")
    print("  Ingresá cadenas para que el autómata las procese.")
    print("  Escribí 'salir' para terminar.")
    print("=" * 60)

    try:
        while True:
            entrada = input("\n  > Ingresá una cadena (o 'salir'): ")
            if entrada.strip().lower() == "salir":
                print("\n  ¡Hasta luego!")
                break
            # Si el usuario separa varias cadenas con comas, las procesamos
            # todas en orden, igual que si las hubiera ingresado de a una.
            cadenas = [c.strip() for c in entrada.split(",")]
            for cadena in cadenas:
                # Validamos antes de procesar: si la cadena contiene símbolos
                # fuera del alfabeto la ignoramos sin imprimir nada.
                if cadena != "" and not all(c in ALFABETO for c in cadena):
                    continue
                aceptada, traza, ids = procesar_cadena(cadena)
                try:
                    graficar_recorrido(cadena, traza, ids)
                except Exception as e:
                    if "ExecutableNotFound" in type(e).__name__ or "dot" in str(e).lower():
                        print("  (Diagrama omitido: Graphviz no disponible)")
                    else:
                        raise
            print()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Interrupción recibida. ¡Hasta luego!")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  AFND — Cadenas que contienen la subcadena 'ab'")
    print("=" * 60)

    # 1. Mostrar la tabla de transición.
    imprimir_tabla_transicion()

    # 2. Generar el diagrama base del autómata (sin recorrido).
    #    Envuelto en try/except para que un Ctrl+C o la ausencia del ejecutable
    #    'dot' de Graphviz no aborte el script antes de llegar al modo interactivo.
    try:
        generar_diagrama()
    except KeyboardInterrupt:
        print("\n  Generación del diagrama base interrumpida; continuando...")
    except Exception as e:
        if "ExecutableNotFound" in type(e).__name__ or "dot" in str(e).lower():
            print("\n  Graphviz no está instalado o 'dot' no está en el PATH.")
            print("  Descárgalo desde https://graphviz.org/download/ e instálalo.")
            print("  Los diagramas PNG se omitirán; el resto del programa funciona con normalidad.")
        else:
            raise

    # 3. Entrar al modo interactivo para procesar cadenas ingresadas por el usuario.
    modo_interactivo()
