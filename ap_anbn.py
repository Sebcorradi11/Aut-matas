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
ALFABETO_PILA = {"A", "Z"}
SIMBOLO_INICIAL_PILA = "Z"

# (estado, símbolo_entrada, tope_pila) → (nuevo_estado, lista_a_apilar)
# lista vacía [] = desapilar sin reemplazar; None = transición ε (sin consumir entrada)
TRANSICIONES = {
    ("q0", "a", "Z"): ("q0", ["A", "Z"]),   # primera 'a': apila A, deja Z debajo
    ("q0", "a", "A"): ("q0", ["A", "A"]),   # 'a' siguientes: apila otra A
    ("q0", "b", "A"): ("q1", []),           # primera 'b': desapila la A
    ("q1", "b", "A"): ("q1", []),           # 'b' siguientes: sigue desapilando
    ("q1", None,  "Z"): ("q2", ["Z"]),      # ε: pila en fondo → aceptar
}


# =====================================================
# PROCESAMIENTO DE CADENAS
# =====================================================

# Ejecuta el AP sobre una cadena, maneja la pila y aplica transiciones ε al final.
def procesar_cadena(cadena: str) -> tuple:
    """
    Simula el AP símbolo a símbolo, manejando explícitamente la pila en cada paso.
    Al terminar la cadena aplica transiciones ε disponibles para alcanzar q2.

    Args:
        cadena (str): Cadena sobre {a, b} a procesar. Puede ser vacía.

    Returns:
        tuple: (aceptada, traza, ids) donde traza es lista de (origen,
               símbolo_o_None, tope, destino, pila) e ids es lista de
               (estado, entrada_restante, pila).
    """
    print(f"\nProcesando cadena: '{cadena}'")

    # pila[-1] es el tope; append/pop operan en O(1) sobre el final de la lista
    estado = ESTADO_INICIAL
    pila: list[str] = [SIMBOLO_INICIAL_PILA]
    traza: list = []
    # Guardamos list(pila) y no la referencia para que el historial no mute
    ids: list = [(ESTADO_INICIAL, cadena, list(pila))]

    print(f"  Estado inicial: {estado} | Pila: {pila}")

    for i, simbolo in enumerate(cadena):
        if simbolo not in ALFABETO:
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False, traza, ids

        if not pila:
            print(f"  Pila vacía — no hay transición posible para '{simbolo}'")
            return False, traza, ids

        tope = pila[-1]

        if (estado, simbolo, tope) not in TRANSICIONES:
            print(f"  No hay transición para δ({estado}, {simbolo}, {tope}) — RECHAZADA")
            return False, traza, ids

        nuevo_estado, a_apilar = TRANSICIONES[(estado, simbolo, tope)]

        pila.pop()  # desapila el tope antes de poner los nuevos símbolos
        for sym in reversed(a_apilar):  # reversed: el primer elem de a_apilar queda en el tope
            pila.append(sym)

        apilado_str = "".join(a_apilar) if a_apilar else "ε"
        print(f"  δ({estado}, {simbolo}, {tope}) -> ({nuevo_estado}, {apilado_str}) | Pila: {pila}")

        traza.append((estado, simbolo, tope, nuevo_estado, list(pila)))
        estado = nuevo_estado
        ids.append((estado, cadena[i + 1:], list(pila)))

    # --- Transiciones ε (épsilon) ---
    while True:
        if not pila:
            break
        tope = pila[-1]
        if (estado, None, tope) not in TRANSICIONES:
            break

        nuevo_estado, a_apilar = TRANSICIONES[(estado, None, tope)]
        pila.pop()  # desapila el tope antes de poner los nuevos símbolos
        for sym in reversed(a_apilar):  # reversed: el primer elem de a_apilar queda en el tope
            pila.append(sym)

        apilado_str = "".join(a_apilar) if a_apilar else "ε"
        print(f"  δ({estado}, ε, {tope}) -> ({nuevo_estado}, {apilado_str}) | Pila: {pila}")

        traza.append((estado, None, tope, nuevo_estado, list(pila)))
        estado = nuevo_estado
        ids.append((estado, "", list(pila)))

    aceptada = estado in ESTADOS_FINALES
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    print(f"  Estado final: {estado} | Pila: {pila}  →  {veredicto}")
    return aceptada, traza, ids


# =====================================================
# TABLA DE TRANSICIÓN (consola)
# =====================================================

# Imprime la tabla δ del AP (una fila por regla) con bordes Unicode.
def imprimir_tabla_transicion() -> None:
    """
    Imprime la tabla de transición δ con bordes Unicode.

    A diferencia del AFD/AFND, la tabla tiene una fila por regla porque δ
    depende de tres argumentos: estado, símbolo de entrada y tope de pila.
    Convenciones: → estado inicial, * estado final, ε transición/apilado vacío.

    Returns:
        None
    """
    estados_ord = sorted(ESTADOS)

    ancho_estado   = max(len(e) + 3 for e in estados_ord)  # +3 para "→ " o "* "
    ancho_entrada  = 9
    ancho_tope     = 7
    ancho_nuevo    = 14
    ancho_apilar   = 10

    anchos = [ancho_estado, ancho_entrada, ancho_tope, ancho_nuevo, ancho_apilar]

    def linea(izq, sep, der):
        return izq + sep.join("─" * a for a in anchos) + der

    sep_top = linea("┌", "┬", "┐")
    sep_mid = linea("├", "┼", "┤")
    sep_bot = linea("└", "┴", "┘")

    print("\nTabla de transición δ:")
    print(sep_top)

    print(
        f"│{'δ':^{ancho_estado}}"
        f"│{'Entrada':^{ancho_entrada}}"
        f"│{'Tope':^{ancho_tope}}"
        f"│{'Nuevo estado':^{ancho_nuevo}}"
        f"│{'A apilar':^{ancho_apilar}}│"
    )
    print(sep_mid)

    def clave_orden(item):
        (est, ent, tope), _ = item
        # None (ε) va después de los símbolos concretos dentro del mismo estado
        return (est, "" if ent is None else ent, tope)

    for (est, ent, tope), (nuevo_est, a_apilar) in sorted(TRANSICIONES.items(), key=clave_orden):
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


# =====================================================
# DIAGRAMA BASE (Graphviz)
# =====================================================

# Genera el diagrama del AP y lo guarda como AP/diagrama_ap.png.
def generar_diagrama() -> None:
    """
    Renderiza el diagrama de transición del AP con Graphviz (formato PNG).

    Etiqueta de arista: "entrada, tope / apilar" (ej. "a, Z / AZ").
    Agrupa reglas con el mismo par (origen, destino) en una sola flecha.

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

    diagrama = Digraph(name="AP_anbn", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")

    # Nodo invisible como origen de la flecha de inicio
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        if estado in ESTADOS_FINALES:
            diagrama.node(estado, shape="doublecircle")
        else:
            diagrama.node(estado, shape="circle")

    diagrama.edge("__inicio__", ESTADO_INICIAL)

    # Formato de etiqueta estándar para AP: "entrada, tope / apilar"
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, ent, tope), (destino, a_apilar) in TRANSICIONES.items():
        entrada_str = "ε" if ent is None else ent
        apilar_str  = "ε" if not a_apilar else "".join(a_apilar)
        etiqueta    = f"{entrada_str}, {tope} / {apilar_str}"
        aristas.setdefault((origen, destino), []).append(etiqueta)

    for (origen, destino), etiquetas in aristas.items():
        etiqueta_final = "\n".join(sorted(etiquetas))
        diagrama.edge(origen, destino, label=etiqueta_final)

    import os
    carpeta = "AP"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, "diagrama_ap")
    diagrama.render(nombre_archivo, cleanup=True)  # cleanup=True elimina el .gv temporal
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# =====================================================
# DIAGRAMA DEL RECORRIDO (Graphviz + Pillow)
# =====================================================

# Genera un PNG con el recorrido resaltado y la tabla de IDs (con columna de pila) al pie.
def graficar_recorrido(cadena: str, traza: list, ids: list) -> None:
    """
    Genera un PNG: diagrama con recorrido resaltado + tabla de IDs al pie.

    La tabla incluye la columna Pila (tope a la derecha), que es el dato clave
    para distinguir cadenas como "ab", "aabb" y "aaabbb" en el mismo diagrama.

    Args:
        cadena (str): Cadena procesada (puede ser vacía).
        traza (list): Lista de (estado_origen, símbolo_o_None, tope, estado_destino, pila).
        ids (list): Lista de (estado, entrada_restante, pila).

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
        estado_final = traza[-1][3]
    else:
        estado_final = ESTADO_INICIAL
    aceptada = estado_final in ESTADOS_FINALES

    estados_visitados: set = set()
    for paso in traza:
        estados_visitados.add(paso[0])
        estados_visitados.add(paso[3])

    aristas_usadas: set = {(paso[0], paso[3]) for paso in traza}

    sufijo = cadena if cadena else "epsilon"
    sufijo_seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sufijo)

    # --- 2. Construir el diagrama con recorrido resaltado ---
    diagrama = Digraph(name=f"recorrido_AP_{sufijo_seguro}", format="png")
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
    for (origen, ent, tope), (destino, a_apilar) in TRANSICIONES.items():
        entrada_str = "ε" if ent is None else ent
        apilar_str  = "ε" if not a_apilar else "".join(a_apilar)
        etiqueta    = f"{entrada_str}, {tope} / {apilar_str}"
        aristas.setdefault((origen, destino), []).append(etiqueta)

    for (origen, destino), etiquetas in aristas.items():
        etiqueta_final = "\n".join(sorted(etiquetas))
        if (origen, destino) in aristas_usadas:
            diagrama.edge(origen, destino, label=etiqueta_final,
                          color="#1F4E79", penwidth="2.5", fontcolor="#1F4E79")
        else:
            diagrama.edge(origen, destino, label=etiqueta_final,
                          color="#CCCCCC", fontcolor="#CCCCCC")

    import os
    import tempfile

    carpeta = "AP"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, f"recorrido_ap_{sufijo_seguro}")

    if _PIL_DISPONIBLE:
        tmp_dir   = tempfile.gettempdir()
        tmp_diag  = os.path.join(tmp_dir, "_diag_ap_tmp")
        tmp_tabla = os.path.join(tmp_dir, "_tabla_ap_tmp")

        # --- 3. Generar la tabla HTML de IDs ---
        diagrama.render(tmp_diag, cleanup=True)

        encabezado_html = (
            '<TR>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Paso</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Estado</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Entrada restante</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Pila</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Acci&#243;n</FONT></B></TD>'
            '</TR>'
        )
        filas_html = []
        for i, (est_id, entrada_id, pila_id) in enumerate(ids):
            es_ultima = (i == len(ids) - 1)
            if es_ultima:
                bg = "#B8E6B8" if aceptada else "#F4B8B8"
            else:
                bg = "#FFFFFF" if i % 2 == 0 else "#F5F5F5"

            if i == 0:
                accion = "inicio"
            else:
                est_ant  = ids[i - 1][0]
                sim      = traza[i - 1][1]   # None para ε-transiciones
                tope_ant = traza[i - 1][2]
                if sim is None:
                    accion = f"&#948;({est_ant}, &#949;, {tope_ant})"
                else:
                    accion = f"&#948;({est_ant}, {sim}, {tope_ant})"
            if es_ultima:
                accion += " [ACEPTA]" if aceptada else " [RECHAZA]"

            entrada_display = entrada_id if entrada_id else "&#949;"
            # pila[-1] es el tope; "".join muestra la pila con el tope a la derecha
            pila_display = "".join(pila_id) if pila_id else "&#949;"

            filas_html.append(
                f'<TR>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{i}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{est_id}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{entrada_display}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{pila_display}</FONT></TD>'
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
    print("  MODO INTERACTIVO — AP")
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
    print("  AP — Lenguaje L = { aⁿbⁿ | n ≥ 1 }")
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
