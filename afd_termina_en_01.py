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
ALFABETO = {"0", "1"}
ESTADO_INICIAL = "q0"
ESTADOS_FINALES = {"q2"}

# (estado, símbolo) → estado destino
TRANSICIONES = {
    ("q0", "0"): "q1",
    ("q0", "1"): "q0",
    ("q1", "0"): "q1",
    ("q1", "1"): "q2",
    ("q2", "0"): "q1",
    ("q2", "1"): "q0",
}


# =====================================================
# PROCESAMIENTO DE CADENAS
# =====================================================

# Ejecuta el autómata sobre una cadena y devuelve si es aceptada.
def procesar_cadena(cadena: str) -> tuple:
    """
    Simula el AFD símbolo a símbolo e imprime cada transición aplicada.

    Args:
        cadena (str): Cadena binaria a procesar. Puede ser vacía.

    Returns:
        tuple: (aceptada, traza, ids) donde traza es lista de (origen, símbolo,
               destino) e ids es lista de (estado, entrada_restante).
    """
    print(f"\nProcesando cadena: '{cadena}'")

    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estado final: {ESTADO_INICIAL}  →  RECHAZADA")
        return False, [], [(ESTADO_INICIAL, "")]

    estado_actual = ESTADO_INICIAL
    traza: list = []
    ids: list = [(ESTADO_INICIAL, cadena)]

    for i, simbolo in enumerate(cadena):
        if simbolo not in ALFABETO:
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False, traza, ids

        estado_siguiente = TRANSICIONES[(estado_actual, simbolo)]
        print(f"  δ({estado_actual}, {simbolo}) = {estado_siguiente}")
        traza.append((estado_actual, simbolo, estado_siguiente))
        estado_actual = estado_siguiente
        ids.append((estado_actual, cadena[i + 1:]))

    aceptada = estado_actual in ESTADOS_FINALES
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    print(f"  Estado final: {estado_actual}  →  {veredicto}")
    return aceptada, traza, ids


# =====================================================
# TABLA DE TRANSICIÓN (consola)
# =====================================================

# Imprime la tabla δ con bordes Unicode en la consola.
def imprimir_tabla_transicion() -> None:
    """
    Imprime la tabla de transición δ con bordes Unicode.

    Convenciones: → estado inicial, * estado final.

    Returns:
        None
    """
    estados_ord = sorted(ESTADOS)
    simbolos_ord = sorted(ALFABETO)

    ancho_estado = max(len(e) + 3 for e in estados_ord)  # +3 para "→ " o "* "
    ancho_simbolo = 6

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

        celdas_transicion = "".join(
            f"│{TRANSICIONES.get((estado, s), '-'):^{ancho_simbolo}}"
            for s in simbolos_ord
        )
        print(f"│{celda_estado:<{ancho_estado}}{celdas_transicion}│")

    print(sep_bot)
    print("  → estado inicial     * estado(s) final(es)")


# =====================================================
# DIAGRAMA BASE (Graphviz)
# =====================================================

# Genera el diagrama del AFD y lo guarda como AFD/diagrama_afd.png.
def generar_diagrama() -> None:
    """
    Renderiza el diagrama de transición del AFD con Graphviz (formato PNG).

    Usa rankdir="LR" y un nodo invisible "__inicio__" para la flecha de inicio.
    Agrupa símbolos con el mismo par (origen, destino) en una sola arista.

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

    diagrama = Digraph(name="AFD_termina_en_01", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")

    # Nodo invisible como origen de la flecha de inicio
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        if estado in ESTADOS_FINALES:
            diagrama.node(estado, shape="doublecircle")
        else:
            diagrama.node(estado, shape="circle")

    diagrama.edge("__inicio__", ESTADO_INICIAL)

    # Agrupamos por (origen, destino) para unir símbolos en una sola arista
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, simbolo), destino in TRANSICIONES.items():
        aristas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        diagrama.edge(origen, destino, label=etiqueta)

    import os
    carpeta = "AFD"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, "diagrama_afd")
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
        traza (list): Lista de (estado_origen, símbolo, estado_destino).
        ids (list): Lista de (estado, entrada_restante).

    Returns:
        None
    """
    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        return

    # --- 1. Determinar estado final y aceptación ---
    if traza:
        estado_final = traza[-1][2]
    else:
        estado_final = ESTADO_INICIAL
    aceptada = estado_final in ESTADOS_FINALES

    estados_visitados: set = set()
    for origen, _, destino in traza:
        estados_visitados.add(origen)
        estados_visitados.add(destino)

    aristas_usadas: set = {(origen, destino) for origen, _, destino in traza}

    sufijo = cadena if cadena else "epsilon"
    sufijo_seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sufijo)

    # --- 2. Construir el diagrama con recorrido resaltado ---
    diagrama = Digraph(name=f"recorrido_AFD_{sufijo_seguro}", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        shape = "doublecircle" if estado in ESTADOS_FINALES else "circle"
        if estado == estado_final:
            color_final = "#B8E6B8" if aceptada else "#F4B8B8"
            diagrama.node(estado, shape=shape, style="filled", fillcolor=color_final)
        elif estado in estados_visitados:
            diagrama.node(estado, shape=shape, style="filled", fillcolor="#FFF4B8")
        else:
            diagrama.node(estado, shape=shape)

    diagrama.edge("__inicio__", ESTADO_INICIAL)

    aristas: dict = {}
    for (origen, simbolo), destino in TRANSICIONES.items():
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

    carpeta = "AFD"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, f"recorrido_afd_{sufijo_seguro}")

    if _PIL_DISPONIBLE:
        tmp_dir   = tempfile.gettempdir()
        tmp_diag  = os.path.join(tmp_dir, "_diag_afd_tmp")
        tmp_tabla = os.path.join(tmp_dir, "_tabla_afd_tmp")

        # --- 3. Generar la tabla HTML de IDs ---
        diagrama.render(tmp_diag, cleanup=True)

        encabezado_html = (
            '<TR>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Paso</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Estado</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Entrada restante</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Acci&#243;n</FONT></B></TD>'
            '</TR>'
        )
        filas_html = []
        for i, (estado_id, entrada_id) in enumerate(ids):
            es_ultima = (i == len(ids) - 1)
            if es_ultima:
                bg = "#B8E6B8" if aceptada else "#F4B8B8"
            else:
                bg = "#FFFFFF" if i % 2 == 0 else "#F5F5F5"

            if i == 0:
                accion = "inicio"
            else:
                est_ant = ids[i - 1][0]
                sim     = traza[i - 1][1]
                accion  = f"&#948;({est_ant}, {sim})"
            if es_ultima:
                accion += " [ACEPTA]" if aceptada else " [RECHAZA]"

            entrada_display = entrada_id if entrada_id else "&#949;"  # ε si vacío

            filas_html.append(
                f'<TR>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{i}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{estado_id}</FONT></TD>'
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
    print("  MODO INTERACTIVO — AFD")
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
    print("  AFD — Cadenas binarias que terminan en '01'")
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
