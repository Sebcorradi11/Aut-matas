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

# =====================================================
# IMPORTACIONES
# =====================================================

# Pillow combina el diagrama con la tabla de IDs en graficar_recorrido.
try:
    from PIL import Image
    _PIL_DISPONIBLE = True
except ImportError:
    _PIL_DISPONIBLE = False


# =====================================================
# DEFINICIÓN DEL AUTÓMATA
# =====================================================

ESTADOS = {"q0", "q1", "q2"}
ALFABETO = {"a", "b"}
ESTADO_INICIAL = "q0"
ESTADOS_FINALES = {"q2"}

# (estado, símbolo) → SET de estados destino (set vacío = sin transición)
TRANSICIONES = {
    ("q0", "a"): {"q0", "q1"},   # no determinismo: dos destinos posibles
    ("q0", "b"): {"q0"},
    ("q1", "a"): set(),          # trampa: ningún estado destino definido
    ("q1", "b"): {"q2"},
    ("q2", "a"): {"q2"},
    ("q2", "b"): {"q2"},
}


# =====================================================
# PROCESAMIENTO DE CADENAS
# =====================================================

# Ejecuta el AFND con método de subconjuntos y devuelve si la cadena es aceptada.
def procesar_cadena(cadena: str) -> tuple:
    """
    Simula el AFND con método de subconjuntos: mantiene el conjunto de estados
    activos y lo actualiza en cada símbolo sin backtracking.

    Args:
        cadena (str): Cadena sobre {a, b} a procesar. Puede ser vacía.

    Returns:
        tuple: (aceptada, traza, ids) donde traza es lista de (frozenset_origen,
               símbolo, frozenset_destino) e ids es lista de (frozenset_estados,
               entrada_restante).
    """
    print(f"\nProcesando cadena: '{cadena}'")

    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estados activos finales: {{{ESTADO_INICIAL}}}  →  RECHAZADA")
        return False, [], [(frozenset({ESTADO_INICIAL}), "")]

    estados_activos = {ESTADO_INICIAL}
    traza: list = []
    ids: list = [(frozenset({ESTADO_INICIAL}), cadena)]

    for i, simbolo in enumerate(cadena):
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


# =====================================================
# TABLA DE TRANSICIÓN (consola)
# =====================================================

# Imprime la tabla δ con bordes Unicode; las celdas muestran conjuntos de estados.
def imprimir_tabla_transicion() -> None:
    """
    Imprime la tabla de transición δ con bordes Unicode.

    Convenciones: → estado inicial, * estado final, ∅ sin transición.

    Returns:
        None
    """
    estados_ord = sorted(ESTADOS)
    simbolos_ord = sorted(ALFABETO)

    ancho_estado = max(len(e) + 3 for e in estados_ord)  # +3 para "→ " o "* "
    ancho_simbolo = 10  # "{q0, q1}" tiene 8 caracteres; 10 deja margen

    sep_top = (
        "┌" + "─" * ancho_estado + "┬"
        + ("┬".join("─" * ancho_simbolo for _ in simbolos_ord))
        + "┐"
    )
    sep_mid = (
        "├" + "─" * ancho_estado + "┼"
        + ("┼".join("─" * ancho_simbolo for _ in simbolos_ord))
        + "┤"
    )
    sep_bot = (
        "└" + "─" * ancho_estado + "┴"
        + ("┴".join("─" * ancho_simbolo for _ in simbolos_ord))
        + "┘"
    )

    print("\nTabla de transición δ:")
    print(sep_top)

    encabezado_simbolos = "".join(
        f"│{s:^{ancho_simbolo}}" for s in simbolos_ord
    )
    print(f"│{'δ':^{ancho_estado}}{encabezado_simbolos}│")
    print(sep_mid)

    for estado in estados_ord:
        prefijo = ""
        if estado == ESTADO_INICIAL:
            prefijo += "→ "
        if estado in ESTADOS_FINALES:
            prefijo += "* "
        celda_estado = f"{prefijo}{estado}"

        def formatear_destinos(destinos: set) -> str:
            # Conjunto vacío → ∅ (más legible que "{}" en la tabla)
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


# =====================================================
# DIAGRAMA BASE (Graphviz)
# =====================================================

# Genera el diagrama del AFND y lo guarda como AFND/diagrama_afnd.png.
def generar_diagrama() -> None:
    """
    Renderiza el diagrama de transición del AFND con Graphviz (formato PNG).

    Expande los sets de destinos para obtener aristas individuales, luego
    agrupa por (origen, destino) para mostrar símbolos en una sola flecha.

    Returns:
        None
    """
    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        print("    También necesitás el binario de Graphviz del sistema:")
        print("    https://graphviz.org/download/")
        return

    diagrama = Digraph(name="AFND_contiene_ab", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")

    # Nodo invisible como origen de la flecha de inicio
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        if estado in ESTADOS_FINALES:
            diagrama.node(estado, shape="doublecircle")
        else:
            diagrama.node(estado, shape="circle")

    diagrama.edge("__inicio__", ESTADO_INICIAL)

    # El AFND tiene sets como destino; los expandemos antes de agrupar por par (origen, destino)
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, simbolo), destinos in TRANSICIONES.items():
        for destino in destinos:
            aristas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        diagrama.edge(origen, destino, label=etiqueta)

    import os
    carpeta = "AFND"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, "diagrama_afnd")
    diagrama.render(nombre_archivo, cleanup=True)  # cleanup=True elimina el .gv temporal
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# =====================================================
# DIAGRAMA DEL RECORRIDO (Graphviz + Pillow)
# =====================================================

# Genera un PNG con el recorrido resaltado y la tabla de IDs al pie.
def graficar_recorrido(cadena: str, traza: list, ids: list) -> None:
    """
    Genera un PNG: diagrama con recorrido resaltado + tabla de IDs al pie.

    Args:
        cadena (str): Cadena procesada (puede ser vacía).
        traza (list): Lista de (frozenset_origen, símbolo, frozenset_destino).
        ids (list): Lista de (frozenset_estados_activos, entrada_restante).

    Returns:
        None
    """
    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        return

    # --- 1. Determinar conjunto final y aceptación ---
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

    # --- 2. Construir el diagrama con recorrido resaltado ---
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

        # --- 3. Generar la tabla HTML de IDs ---
        diagrama.render(tmp_diag, cleanup=True)

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

            # Conjunto vacío → ∅ (&#8709;); ordenamos para salida determinista
            if conj_id:
                estados_str = "{" + ", ".join(sorted(conj_id)) + "}"
            else:
                estados_str = "&#8709;"

            entrada_display = entrada_id if entrada_id else "&#949;"  # ε si vacío

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

        # --- 4. Combinar diagrama y tabla con Pillow ---
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

        img_diag.close()
        img_tabla.close()
        os.remove(tmp_diag  + ".png")
        os.remove(tmp_tabla + ".png")
    else:
        diagrama.render(nombre_archivo, cleanup=True)
        print("  [!] Instalá Pillow para incluir la tabla de IDs: pip install Pillow")

    print(f"  Recorrido guardado como '{nombre_archivo}.png'")


# =====================================================
# MODO INTERACTIVO
# =====================================================

# Loop donde el usuario ingresa cadenas y el autómata las procesa una a una.
def modo_interactivo() -> None:
    """
    Inicia un loop interactivo: el usuario ingresa cadenas, el autómata las
    procesa y genera el diagrama del recorrido.

    Acepta múltiples cadenas separadas por comas. Escribí 'salir' para terminar.

    Returns:
        None
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
            # Permite ingresar varias cadenas separadas por coma
            cadenas = [c.strip() for c in entrada.split(",")]
            for cadena in cadenas:
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


# =====================================================
# PUNTO DE ENTRADA
# =====================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  AFND — Cadenas que contienen la subcadena 'ab'")
    print("=" * 60)

    imprimir_tabla_transicion()

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

    modo_interactivo()
