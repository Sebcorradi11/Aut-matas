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
# Importaciones
# ---------------------------------------------------------------------------

# Pillow se usa en graficar_recorrido para combinar verticalmente la imagen del
# diagrama (generada con graphviz) con la tabla de descripciones instantáneas
# (también generada con graphviz como nodo HTML).  Usamos Pillow porque graphviz
# no posiciona bien una tabla como "pie" de un diagrama horizontal; combinar dos
# PNGs con Pillow permite controlar el layout con precisión.
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

def procesar_cadena(cadena: str) -> tuple:
    """
    Simula la ejecución del AFD sobre `cadena` símbolo a símbolo.

    Por cada símbolo imprime la transición aplicada con notación formal:
        δ(estado_actual, símbolo) = estado_siguiente

    Retorna una tupla (aceptada, traza) donde aceptada es True si la cadena
    es aceptada (el estado final pertenece a F) y traza es la lista de pasos
    (estado_origen, símbolo, estado_destino) registrados durante la ejecución.
    Devolver la traza desde aquí (en lugar de reconstruirla después) garantiza
    que coincida exactamente con lo que se imprimió por consola, sin riesgo
    de inconsistencias si la cadena contiene símbolos inválidos.

    Parámetros
    ----------
    cadena : str
        Cadena binaria a procesar.  Puede ser la cadena vacía.

    Retorna
    -------
    tuple
        (True, traza) → aceptada, (False, traza) → rechazada.
    """
    print(f"\nProcesando cadena: '{cadena}'")

    # Caso especial: cadena vacía.  El AFD permanece en q0, que no es estado
    # final, por lo que la cadena vacía siempre se rechaza.
    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estado final: {ESTADO_INICIAL}  →  RECHAZADA")
        # ID única: el autómata parte y permanece en el estado inicial con entrada vacía.
        return False, [], [(ESTADO_INICIAL, "")]

    estado_actual = ESTADO_INICIAL
    # La traza registra cada paso como (origen, símbolo, destino) para que
    # graficar_recorrido pueda resaltar exactamente las aristas recorridas.
    traza: list = []
    # Las IDs (descripciones instantáneas) registran la "foto" del autómata en cada
    # instante.  Para el AFD la ID es (estado, entrada_restante), ya que la única
    # memoria del modelo es el estado actual.  El formato difiere entre autómatas:
    # el AFND usa (conjunto_estados, entrada) y el AP usa (estado, entrada, pila).
    ids: list = [(ESTADO_INICIAL, cadena)]

    for i, simbolo in enumerate(cadena):
        # Validación: rechazamos de inmediato si el símbolo no es del alfabeto,
        # porque consultar TRANSICIONES con una clave inexistente lanzaría KeyError
        # y daría un error confuso al usuario.
        if simbolo not in ALFABETO:
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False, traza, ids

        estado_siguiente = TRANSICIONES[(estado_actual, simbolo)]
        # Notación formal de transición: δ(estado, símbolo) = nuevo_estado
        print(f"  δ({estado_actual}, {simbolo}) = {estado_siguiente}")
        traza.append((estado_actual, simbolo, estado_siguiente))
        estado_actual = estado_siguiente
        # Guardamos la ID post-transición: nuevo estado + lo que queda por leer.
        # cadena[i+1:] es "" cuando i es el último índice, que es correcto.
        ids.append((estado_actual, cadena[i + 1:]))

    # La cadena es aceptada si y solo si el estado en el que detuvimos la
    # lectura pertenece al conjunto de estados finales F.
    aceptada = estado_actual in ESTADOS_FINALES
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    print(f"  Estado final: {estado_actual}  →  {veredicto}")
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
    import os
    carpeta = "AFD"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = os.path.join(carpeta, "diagrama_afd")
    diagrama.render(nombre_archivo, cleanup=True)
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# ---------------------------------------------------------------------------
# Diagrama del recorrido con Graphviz
# ---------------------------------------------------------------------------

def graficar_recorrido(cadena: str, traza: list, ids: list) -> None:
    """
    Genera un PNG compuesto: arriba el diagrama con el recorrido resaltado y
    abajo una tabla con las descripciones instantáneas (IDs) del autómata.

    Una descripción instantánea del AFD es un par (estado, entrada_restante).
    La única memoria del modelo es el estado actual; no hay pila ni subconjunto
    de estados activos.  Esto contrasta con el AFND —que necesita un conjunto de
    estados— y el AP —que necesita estado más pila—, reflejando las diferencias
    en el poder de memoria de cada modelo (Hopcroft et al., 2007; Sipser, 2013).

    Usamos Pillow para combinar ambas imágenes verticalmente porque graphviz no
    posiciona bien una tabla como "pie" de un diagrama horizontal.  Combinar PNGs
    con Pillow permite controlar el layout con precisión sin depender del motor DOT.

    La tabla solo aparece en los PNGs individuales y no en el diagrama combinado
    de varias cadenas, para no saturar esa imagen cuando hay muchas entradas.

    Parámetros
    ----------
    cadena : str
        Cadena que se procesó (puede ser la cadena vacía).
    traza : list
        Lista de tuplas (estado_origen, símbolo, estado_destino).
    ids : list
        Descripciones instantáneas: lista de tuplas (estado, entrada_restante).
    """
    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        return

    # Determinamos el estado final alcanzado y si la cadena fue aceptada.
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
        # --- Combinamos diagrama + tabla de IDs con Pillow ---
        tmp_dir   = tempfile.gettempdir()
        tmp_diag  = os.path.join(tmp_dir, "_diag_afd_tmp")
        tmp_tabla = os.path.join(tmp_dir, "_tabla_afd_tmp")

        # Paso 1: renderizamos el diagrama en un archivo temporal.
        diagrama.render(tmp_diag, cleanup=True)

        # Paso 2: construimos la tabla HTML de IDs y la renderizamos.
        # Columnas: Paso | Estado | Entrada restante | Acción
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

            # La entrada restante vacía se muestra como ε en la tabla.
            entrada_display = entrada_id if entrada_id else "&#949;"

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

        # Paso 3: combinamos verticalmente las dos imágenes con Pillow.
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

        # Paso 4: eliminamos los temporales para no ensuciar el directorio.
        img_diag.close()
        img_tabla.close()
        os.remove(tmp_diag  + ".png")
        os.remove(tmp_tabla + ".png")
    else:
        # Sin Pillow generamos solo el diagrama (sin la tabla de IDs).
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
    print("  AFD — Cadenas binarias que terminan en '01'")
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
