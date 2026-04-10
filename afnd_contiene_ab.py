"""
AFND — Cadenas que contienen la subcadena "ab"
Materia   : Teoría de la Computación
Trabajo   : TP1 — Autómata 2 de 3 (AFND)
Institución: Universidad de la Cuenca del Plata
"""

# =====================================================
# IMPORTACIONES
# =====================================================

# Intenta importar Pillow; si no está instalado, se omite la combinación de imágenes
try:
    from PIL import Image        # Pillow: manipulación de imágenes PNG
    _PIL_DISPONIBLE = True       # Bandera: Pillow disponible para combinar diagrama + tabla
except ImportError:
    _PIL_DISPONIBLE = False      # Sin Pillow: solo se guarda el diagrama sin la tabla de IDs


# =====================================================
# DEFINICIÓN DEL AUTÓMATA
# =====================================================

ESTADOS = {"q0", "q1", "q2"}    # Conjunto de estados del AFND
ALFABETO = {"a", "b"}           # Símbolos válidos de entrada
ESTADO_INICIAL = "q0"           # Estado desde el que comienza la lectura
ESTADOS_FINALES = {"q2"}        # Estado de aceptación: ya se encontró la subcadena "ab"

# Función de transición δ: mapea (estado, símbolo) → SET de estados destino
# Un set vacío significa que no hay transición definida para esa combinación (trampa)
TRANSICIONES = {
    ("q0", "a"): {"q0", "q1"},   # No determinismo: al leer 'a' desde q0 se bifurca a q0 y q1
    ("q0", "b"): {"q0"},         # Al leer 'b' desde q0 se permanece en q0
    ("q1", "a"): set(),          # Trampa: no hay transición desde q1 leyendo 'a'
    ("q1", "b"): {"q2"},         # Al leer 'b' desde q1 se llega a q2 (se encontró "ab")
    ("q2", "a"): {"q2"},         # Desde q2 cualquier 'a' mantiene la aceptación
    ("q2", "b"): {"q2"},         # Desde q2 cualquier 'b' mantiene la aceptación
}


# =====================================================
# PROCESAMIENTO DE CADENAS
# =====================================================

def procesar_cadena(cadena: str) -> tuple:
    """Simula el AFND con método de subconjuntos: mantiene el conjunto de estados activos."""

    print(f"\nProcesando cadena: '{cadena}'")

    # Caso especial: cadena vacía → el AFD no realiza ninguna transición y rechaza
    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estados activos finales: {{{ESTADO_INICIAL}}}  →  RECHAZADA")
        return False, [], [(frozenset({ESTADO_INICIAL}), "")]   # Devuelve rechazo con estado inicial

    estados_activos = {ESTADO_INICIAL}                         # Arranca con el conjunto {q0}
    traza: list = []                                           # Historial de pasos: [(conj_origen, símbolo, conj_destino), ...]
    ids: list = [(frozenset({ESTADO_INICIAL}), cadena)]        # Tabla de IDs: [(conj_estados, entrada_restante), ...]

    for i, simbolo in enumerate(cadena):                       # Recorre la cadena símbolo a símbolo
        if simbolo not in ALFABETO:                            # Valida que el símbolo pertenezca al alfabeto
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False, traza, ids

        nuevos_estados: set[str] = set()
        for estado in estados_activos:
            nuevos_estados |= TRANSICIONES.get((estado, simbolo), set())   # Une los destinos de cada estado activo

        # Formatea los conjuntos para mostrarlos en consola
        estados_antes   = "{" + ", ".join(sorted(estados_activos)) + "}"
        estados_despues = "{" + ", ".join(sorted(nuevos_estados)) + "}" if nuevos_estados else "∅"
        print(f"  {estados_antes}  --{simbolo}-->  {estados_despues}")

        traza.append((frozenset(estados_activos), simbolo, frozenset(nuevos_estados)))   # Registra el paso
        estados_activos = nuevos_estados                                                  # Actualiza el conjunto activo
        ids.append((frozenset(estados_activos), cadena[i + 1:]))                         # Registra entrada restante

        if not estados_activos:   # Si el conjunto queda vacío no hay más transiciones posibles
            print("  (conjunto de estados activos vacío — ejecución detenida)")
            print("  Estados activos finales: ∅  →  RECHAZADA")
            return False, traza, ids

    estados_finales_alcanzados = estados_activos & ESTADOS_FINALES   # Intersección con estados de aceptación
    aceptada = bool(estados_finales_alcanzados)                       # True si al menos un estado final está activo
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    estados_str = "{" + ", ".join(sorted(estados_activos)) + "}"
    print(f"  Estados activos finales: {estados_str}  →  {veredicto}")
    return aceptada, traza, ids   # Devuelve resultado, traza completa y tabla de IDs


# =====================================================
# TABLA DE TRANSICIÓN (consola)
# =====================================================

def imprimir_tabla_transicion() -> None:
    """Imprime la tabla δ con bordes Unicode. Las celdas muestran conjuntos de estados destino."""

    estados_ord  = sorted(ESTADOS)    # Ordena los estados alfabéticamente
    simbolos_ord = sorted(ALFABETO)   # Ordena los símbolos del alfabeto

    ancho_estado  = max(len(e) + 3 for e in estados_ord)   # +3 para prefijos "→ " o "* "
    ancho_simbolo = 10                                       # "{q0, q1}" tiene 8 caracteres; 10 deja margen

    # Construye las líneas separadoras con caracteres Unicode de tabla
    sep_top = "┌" + "─" * ancho_estado + "┬" + ("┬".join("─" * ancho_simbolo for _ in simbolos_ord)) + "┐"
    sep_mid = "├" + "─" * ancho_estado + "┼" + ("┼".join("─" * ancho_simbolo for _ in simbolos_ord)) + "┤"
    sep_bot = "└" + "─" * ancho_estado + "┴" + ("┴".join("─" * ancho_simbolo for _ in simbolos_ord)) + "┘"

    print("\nTabla de transición δ:")
    print(sep_top)   # Borde superior

    # Fila de encabezado con los símbolos del alfabeto
    encabezado_simbolos = "".join(f"│{s:^{ancho_simbolo}}" for s in simbolos_ord)
    print(f"│{'δ':^{ancho_estado}}{encabezado_simbolos}│")
    print(sep_mid)   # Separador tras el encabezado

    for estado in estados_ord:
        prefijo = ""
        if estado == ESTADO_INICIAL:    # Marca el estado inicial con "→ "
            prefijo += "→ "
        if estado in ESTADOS_FINALES:   # Marca los estados finales con "* "
            prefijo += "* "
        celda_estado = f"{prefijo}{estado}"

        def formatear_destinos(destinos: set) -> str:
            if not destinos:
                return "∅"                                  # Conjunto vacío → ∅ (más legible que "{}")
            return "{" + ", ".join(sorted(destinos)) + "}"

        # Genera cada celda con el conjunto de destinos; ∅ si no hay transición
        celdas_transicion = "".join(
            f"│{formatear_destinos(TRANSICIONES.get((estado, s), set())):^{ancho_simbolo}}"
            for s in simbolos_ord
        )
        print(f"│{celda_estado:<{ancho_estado}}{celdas_transicion}│")   # Imprime la fila

    print(sep_bot)   # Borde inferior
    print("  → estado inicial     * estado(s) final(es)     ∅ sin transición")


# =====================================================
# DIAGRAMA BASE (Graphviz)
# =====================================================

def generar_diagrama() -> None:
    """Renderiza el diagrama del AFND con Graphviz y lo guarda en AFND/diagrama_afnd.png."""

    try:
        from graphviz import Digraph   # Importa Graphviz para generar grafos dirigidos
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        print("    También necesitás el binario de Graphviz del sistema:")
        print("    https://graphviz.org/download/")
        return

    diagrama = Digraph(name="AFND_contiene_ab", format="png")   # Grafo dirigido en formato PNG
    diagrama.attr(rankdir="LR", fontname="Helvetica")            # Disposición de izquierda a derecha

    diagrama.node("__inicio__", shape="none", width="0", label="")   # Nodo invisible para la flecha de inicio

    for estado in sorted(ESTADOS):
        if estado in ESTADOS_FINALES:
            diagrama.node(estado, shape="doublecircle")   # Doble círculo para estados finales
        else:
            diagrama.node(estado, shape="circle")         # Círculo simple para estados normales

    diagrama.edge("__inicio__", ESTADO_INICIAL)   # Flecha de inicio apuntando al estado inicial

    # El AFND tiene sets como destino; los expandemos para obtener aristas individuales
    # y luego agrupamos por par (origen, destino) para unir símbolos en una sola flecha
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, simbolo), destinos in TRANSICIONES.items():
        for destino in destinos:
            aristas.setdefault((origen, destino), []).append(simbolo)   # Acumula símbolos por par

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))            # Une los símbolos con coma
        diagrama.edge(origen, destino, label=etiqueta)    # Dibuja la arista con su etiqueta

    import os
    carpeta = "AFND"
    os.makedirs(carpeta, exist_ok=True)                          # Crea la carpeta AFND si no existe
    nombre_archivo = os.path.join(carpeta, "diagrama_afnd")
    diagrama.render(nombre_archivo, cleanup=True)                # Renderiza el PNG y elimina el .gv temporal
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# =====================================================
# DIAGRAMA DEL RECORRIDO (Graphviz + Pillow)
# =====================================================

def graficar_recorrido(cadena: str, traza: list, ids: list) -> None:
    """Genera un PNG con el recorrido del AFND resaltado y la tabla de IDs al pie."""

    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        return

    # Determina el conjunto de estados final y si la cadena fue aceptada
    conjunto_final = traza[-1][2] if traza else frozenset({ESTADO_INICIAL})
    aceptada = bool(conjunto_final & ESTADOS_FINALES)   # True si algún estado final está en el conjunto

    # Recopila todos los estados individuales visitados durante el recorrido
    estados_visitados: set = set()
    for conj_origen, _, conj_destino in traza:
        estados_visitados |= conj_origen
        estados_visitados |= conj_destino

    # Determina las aristas realmente usadas: solo las que pertenecen a la transición activa
    aristas_usadas: set = set()
    for conj_origen, simbolo, conj_destino in traza:
        for o in conj_origen:
            destinos_reales = TRANSICIONES.get((o, simbolo), set())
            for d in destinos_reales:
                if d in conj_destino:
                    aristas_usadas.add((o, d))   # Solo cuenta si el destino quedó activo

    # Genera un sufijo seguro para el nombre de archivo (reemplaza caracteres no válidos)
    sufijo = cadena if cadena else "epsilon"
    sufijo_seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sufijo)

    # Construye el diagrama con colores según el rol de cada estado en el recorrido
    diagrama = Digraph(name=f"recorrido_AFND_{sufijo_seguro}", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        shape = "doublecircle" if estado in ESTADOS_FINALES else "circle"
        if estado in conjunto_final:
            color_final = "#B8E6B8" if aceptada else "#F4B8B8"   # Verde si acepta, rojo si rechaza
            diagrama.node(estado, shape=shape, style="filled", fillcolor=color_final)
        elif estado in estados_visitados:
            diagrama.node(estado, shape=shape, style="filled", fillcolor="#FFF4B8")   # Amarillo: visitado
        else:
            diagrama.node(estado, shape=shape)   # Sin relleno: no visitado

    diagrama.edge("__inicio__", ESTADO_INICIAL)

    # Construye el mapa de aristas expandiendo los sets de destino
    aristas: dict = {}
    for (origen, simbolo), destinos in TRANSICIONES.items():
        for destino in destinos:
            aristas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        if (origen, destino) in aristas_usadas:
            # Arista resaltada: fue usada durante el recorrido
            diagrama.edge(origen, destino, label=etiqueta, color="#1F4E79", penwidth="2.5", fontcolor="#1F4E79")
        else:
            # Arista atenuada: no fue usada en este recorrido
            diagrama.edge(origen, destino, label=etiqueta, color="#CCCCCC", fontcolor="#CCCCCC")

    import os
    import tempfile

    carpeta = "AFND"
    os.makedirs(carpeta, exist_ok=True)   # Crea la carpeta AFND si no existe
    nombre_archivo = os.path.join(carpeta, f"recorrido_afnd_{sufijo_seguro}")

    if _PIL_DISPONIBLE:
        tmp_dir   = tempfile.gettempdir()                           # Directorio temporal del sistema
        tmp_diag  = os.path.join(tmp_dir, "_diag_afnd_tmp")        # Ruta temporal para el diagrama
        tmp_tabla = os.path.join(tmp_dir, "_tabla_afnd_tmp")       # Ruta temporal para la tabla de IDs

        diagrama.render(tmp_diag, cleanup=True)   # Renderiza el diagrama en el directorio temporal

        # Construye la cabecera HTML de la tabla de IDs
        encabezado_html = (
            '<TR>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Paso</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Estados activos</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Entrada restante</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Acci&#243;n</FONT></B></TD>'
            '</TR>'
        )
        filas_html = []
        for i, (conj_id, entrada_id) in enumerate(ids):   # Itera sobre cada paso del recorrido
            es_ultima = (i == len(ids) - 1)               # True si es el último paso
            if es_ultima:
                bg = "#B8E6B8" if aceptada else "#F4B8B8"      # Verde o rojo según el resultado
            else:
                bg = "#FFFFFF" if i % 2 == 0 else "#F5F5F5"   # Filas alternadas blanco/gris

            if i == 0:
                accion = "inicio"        # Primera fila: acción de inicio
            else:
                accion = "leer s&#237;mbolo"   # Pasos siguientes: lectura de símbolo
            if es_ultima:
                accion += " [ACEPTA]" if aceptada else " [RECHAZA]"   # Agrega el veredicto

            # Conjunto vacío → ∅ (&#8709;); ordena para salida determinista
            if conj_id:
                estados_str = "{" + ", ".join(sorted(conj_id)) + "}"
            else:
                estados_str = "&#8709;"

            entrada_display = entrada_id if entrada_id else "&#949;"   # ε si ya no queda entrada

            filas_html.append(
                f'<TR>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{i}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{estados_str}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{entrada_display}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{accion}</FONT></TD>'
                f'</TR>'
            )

        # Arma el label HTML completo con encabezado y todas las filas
        label_tabla = (
            '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">'
            + encabezado_html
            + "".join(filas_html)
            + '</TABLE>>'
        )

        tabla_dot = Digraph(format="png")              # Grafo auxiliar solo para renderizar la tabla
        tabla_dot.attr(bgcolor="white")
        tabla_dot.node("t", label=label_tabla, shape="plaintext")   # Nodo con tabla HTML sin borde
        tabla_dot.render(tmp_tabla, cleanup=True)      # Renderiza la tabla en el directorio temporal

        # Abre ambas imágenes y las convierte a RGB para poder combinarlas
        img_diag  = Image.open(tmp_diag  + ".png").convert("RGB")
        img_tabla = Image.open(tmp_tabla + ".png").convert("RGB")

        padding    = 20                                                    # Separación vertical entre imágenes
        max_ancho  = max(img_diag.width, img_tabla.width)                  # Ancho del canvas final
        alto_total = img_diag.height + padding + img_tabla.height          # Alto total combinado

        combinada = Image.new("RGB", (max_ancho, alto_total), (255, 255, 255))          # Canvas blanco
        combinada.paste(img_diag,  ((max_ancho - img_diag.width)  // 2, 0))            # Diagrama arriba centrado
        combinada.paste(img_tabla, ((max_ancho - img_tabla.width) // 2,
                                    img_diag.height + padding))                         # Tabla abajo centrada
        combinada.save(nombre_archivo + ".png")   # Guarda la imagen combinada final

        # Libera memoria y elimina los archivos temporales
        img_diag.close()
        img_tabla.close()
        os.remove(tmp_diag  + ".png")
        os.remove(tmp_tabla + ".png")
    else:
        diagrama.render(nombre_archivo, cleanup=True)   # Sin Pillow: guarda solo el diagrama
        print("  [!] Instalá Pillow para incluir la tabla de IDs: pip install Pillow")

    print(f"  Recorrido guardado como '{nombre_archivo}.png'")


# =====================================================
# MODO INTERACTIVO
# =====================================================

def modo_interactivo() -> None:
    """Inicia un loop donde el usuario ingresa cadenas y el AFND las procesa una a una."""

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
            if entrada.strip().lower() == "salir":   # Condición de salida del loop
                print("\n  ¡Hasta luego!")
                break
            cadenas = [c.strip() for c in entrada.split(",")]   # Permite múltiples cadenas separadas por coma
            for cadena in cadenas:
                if cadena != "" and not all(c in ALFABETO for c in cadena):   # Ignora cadenas con símbolos inválidos
                    continue
                aceptada, traza, ids = procesar_cadena(cadena)   # Procesa la cadena con el AFND
                try:
                    graficar_recorrido(cadena, traza, ids)        # Intenta generar el diagrama del recorrido
                except Exception as e:
                    if "ExecutableNotFound" in type(e).__name__ or "dot" in str(e).lower():
                        print("  (Diagrama omitido: Graphviz no disponible)")   # Graphviz no instalado
                    else:
                        raise   # Relanza cualquier otro error inesperado
            print()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Interrupción recibida. ¡Hasta luego!")   # Manejo de Ctrl+C o fin de entrada


# =====================================================
# PUNTO DE ENTRADA
# =====================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  AFND — Cadenas que contienen la subcadena 'ab'")
    print("=" * 60)

    imprimir_tabla_transicion()   # Muestra la tabla de transición δ en consola

    try:
        generar_diagrama()        # Genera y guarda el diagrama base del AFND
    except KeyboardInterrupt:
        print("\n  Generación del diagrama base interrumpida; continuando...")
    except Exception as e:
        if "ExecutableNotFound" in type(e).__name__ or "dot" in str(e).lower():
            print("\n  Graphviz no está instalado o 'dot' no está en el PATH.")
            print("  Descárgalo desde https://graphviz.org/download/ e instálalo.")
            print("  Los diagramas PNG se omitirán; el resto del programa funciona con normalidad.")
        else:
            raise

    modo_interactivo()   # Inicia el modo interactivo para procesar cadenas
