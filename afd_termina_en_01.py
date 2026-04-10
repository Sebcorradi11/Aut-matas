"""
AFD — Cadenas binarias que terminan en "01"
Materia   : Teoría de la Computación
Trabajo   : TP1 — Autómata 1 de 3
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

ESTADOS = {"q0", "q1", "q2"}    # Conjunto de estados del AFD
ALFABETO = {"0", "1"}           # Símbolos válidos de entrada
ESTADO_INICIAL = "q0"           # Estado desde el que comienza la lectura
ESTADOS_FINALES = {"q2"}        # Estados de aceptación (la cadena es válida si termina aquí)

# Función de transición δ: mapea (estado_actual, símbolo_leído) → estado_siguiente
TRANSICIONES = {
    ("q0", "0"): "q1",   # En q0 leyendo 0 → vamos a q1 (vimos un 0)
    ("q0", "1"): "q0",   # En q0 leyendo 1 → seguimos en q0 (no avanzamos)
    ("q1", "0"): "q1",   # En q1 leyendo 0 → seguimos en q1 (el 0 más reciente sigue siendo el último)
    ("q1", "1"): "q2",   # En q1 leyendo 1 → vamos a q2 (terminamos en "01" → aceptación)
    ("q2", "0"): "q1",   # En q2 leyendo 0 → volvemos a q1 (el sufijo "01" se rompió, pero hay un nuevo 0)
    ("q2", "1"): "q0",   # En q2 leyendo 1 → volvemos a q0 (el sufijo "01" se rompió completamente)
}


# =====================================================
# PROCESAMIENTO DE CADENAS
# =====================================================

def procesar_cadena(cadena: str) -> tuple:
    """Simula el AFD símbolo a símbolo e imprime cada transición aplicada."""

    print(f"\nProcesando cadena: '{cadena}'")

    # Caso especial: cadena vacía → el AFD no realiza ninguna transición y rechaza
    if cadena == "":
        print("  (cadena vacía — no se aplica ninguna transición)")
        print(f"  Estado final: {ESTADO_INICIAL}  →  RECHAZADA")
        return False, [], [(ESTADO_INICIAL, "")]   # Devuelve rechazo con estado inicial

    estado_actual = ESTADO_INICIAL   # Arranca siempre desde el estado inicial
    traza: list = []                 # Historial de transiciones: [(origen, símbolo, destino), ...]
    ids: list = [(ESTADO_INICIAL, cadena)]   # Tabla de IDs: [(estado, entrada_restante), ...]

    for i, simbolo in enumerate(cadena):          # Recorre la cadena símbolo a símbolo
        if simbolo not in ALFABETO:               # Valida que el símbolo pertenezca al alfabeto
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False, traza, ids              # Aborta y devuelve rechazo

        estado_siguiente = TRANSICIONES[(estado_actual, simbolo)]   # Consulta la función δ
        print(f"  δ({estado_actual}, {simbolo}) = {estado_siguiente}")   # Muestra la transición
        traza.append((estado_actual, simbolo, estado_siguiente))         # Registra el paso en la traza
        estado_actual = estado_siguiente                                  # Avanza al siguiente estado
        ids.append((estado_actual, cadena[i + 1:]))                      # Registra entrada restante

    aceptada = estado_actual in ESTADOS_FINALES             # True si terminamos en un estado final
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"     # Texto del resultado
    print(f"  Estado final: {estado_actual}  →  {veredicto}")
    return aceptada, traza, ids   # Devuelve resultado, traza completa y tabla de IDs


# =====================================================
# TABLA DE TRANSICIÓN (consola)
# =====================================================

def imprimir_tabla_transicion() -> None:
    """Imprime la tabla δ con bordes Unicode en consola. → = estado inicial, * = estado final."""

    estados_ord = sorted(ESTADOS)    # Ordena los estados alfabéticamente para consistencia
    simbolos_ord = sorted(ALFABETO)  # Ordena los símbolos del alfabeto

    ancho_estado = max(len(e) + 3 for e in estados_ord)  # Ancho de columna de estados (+3 para prefijos "→ " o "* ")
    ancho_simbolo = 6                                      # Ancho fijo de columnas de símbolos

    # Construye las líneas separadoras de la tabla con caracteres Unicode
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
        if estado == ESTADO_INICIAL:   # Marca el estado inicial con "→ "
            prefijo += "→ "
        if estado in ESTADOS_FINALES:  # Marca los estados finales con "* "
            prefijo += "* "
        celda_estado = f"{prefijo}{estado}"   # Combina prefijo y nombre del estado

        # Genera las celdas de transición para cada símbolo; "-" si no existe la transición
        celdas_transicion = "".join(
            f"│{TRANSICIONES.get((estado, s), '-'):^{ancho_simbolo}}"
            for s in simbolos_ord
        )
        print(f"│{celda_estado:<{ancho_estado}}{celdas_transicion}│")   # Imprime la fila

    print(sep_bot)   # Borde inferior
    print("  → estado inicial     * estado(s) final(es)")   # Leyenda de convenciones


# =====================================================
# DIAGRAMA BASE (Graphviz)
# =====================================================

def generar_diagrama() -> None:
    """Renderiza el diagrama del AFD con Graphviz y lo guarda en AFD/diagrama_afd.png."""

    try:
        from graphviz import Digraph   # Importa Graphviz para generar grafos dirigidos
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        print("    También necesitás el binario de Graphviz del sistema:")
        print("    https://graphviz.org/download/")
        return

    diagrama = Digraph(name="AFD_termina_en_01", format="png")   # Crea un grafo dirigido en formato PNG
    diagrama.attr(rankdir="LR", fontname="Helvetica")             # Disposición de izquierda a derecha

    diagrama.node("__inicio__", shape="none", width="0", label="")   # Nodo invisible como origen de la flecha de inicio

    for estado in sorted(ESTADOS):
        if estado in ESTADOS_FINALES:
            diagrama.node(estado, shape="doublecircle")   # Doble círculo para estados finales
        else:
            diagrama.node(estado, shape="circle")         # Círculo simple para estados normales

    diagrama.edge("__inicio__", ESTADO_INICIAL)   # Flecha de inicio apuntando al estado inicial

    # Agrupa los símbolos por par (origen, destino) para representarlos en una sola arista
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, simbolo), destino in TRANSICIONES.items():
        aristas.setdefault((origen, destino), []).append(simbolo)   # Acumula símbolos por par de estados

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))            # Une los símbolos con coma
        diagrama.edge(origen, destino, label=etiqueta)    # Dibuja la arista con su etiqueta

    import os
    carpeta = "AFD"
    os.makedirs(carpeta, exist_ok=True)                          # Crea la carpeta AFD si no existe
    nombre_archivo = os.path.join(carpeta, "diagrama_afd")
    diagrama.render(nombre_archivo, cleanup=True)                # Renderiza el PNG y elimina el .gv temporal
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# =====================================================
# DIAGRAMA DEL RECORRIDO (Graphviz + Pillow)
# =====================================================

def graficar_recorrido(cadena: str, traza: list, ids: list) -> None:
    """Genera un PNG con el recorrido del AFD resaltado y la tabla de IDs al pie."""

    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        return

    # Determina el estado final del recorrido y si la cadena fue aceptada
    estado_final = traza[-1][2] if traza else ESTADO_INICIAL
    aceptada = estado_final in ESTADOS_FINALES

    # Recopila los estados visitados durante el recorrido
    estados_visitados: set = set()
    for origen, _, destino in traza:
        estados_visitados.add(origen)
        estados_visitados.add(destino)

    aristas_usadas: set = {(origen, destino) for origen, _, destino in traza}   # Aristas recorridas

    # Genera un sufijo seguro para el nombre de archivo a partir de la cadena procesada
    sufijo = cadena if cadena else "epsilon"
    sufijo_seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sufijo)

    # Construye el diagrama con colores diferenciados según el rol de cada estado
    diagrama = Digraph(name=f"recorrido_AFD_{sufijo_seguro}", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")
    diagrama.node("__inicio__", shape="none", width="0", label="")   # Nodo de inicio invisible

    for estado in sorted(ESTADOS):
        shape = "doublecircle" if estado in ESTADOS_FINALES else "circle"
        if estado == estado_final:
            color_final = "#B8E6B8" if aceptada else "#F4B8B8"   # Verde si acepta, rojo si rechaza
            diagrama.node(estado, shape=shape, style="filled", fillcolor=color_final)
        elif estado in estados_visitados:
            diagrama.node(estado, shape=shape, style="filled", fillcolor="#FFF4B8")   # Amarillo: visitado
        else:
            diagrama.node(estado, shape=shape)   # Sin relleno: no visitado

    diagrama.edge("__inicio__", ESTADO_INICIAL)   # Flecha de inicio

    # Agrupa los símbolos por par (origen, destino) igual que en el diagrama base
    aristas: dict = {}
    for (origen, simbolo), destino in TRANSICIONES.items():
        aristas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        if (origen, destino) in aristas_usadas:
            # Arista resaltada: recorrida durante el procesamiento
            diagrama.edge(origen, destino, label=etiqueta, color="#1F4E79", penwidth="2.5", fontcolor="#1F4E79")
        else:
            # Arista atenuada: no fue usada en este recorrido
            diagrama.edge(origen, destino, label=etiqueta, color="#CCCCCC", fontcolor="#CCCCCC")

    import os
    import tempfile

    carpeta = "AFD"
    os.makedirs(carpeta, exist_ok=True)   # Crea la carpeta AFD si no existe
    nombre_archivo = os.path.join(carpeta, f"recorrido_afd_{sufijo_seguro}")

    if _PIL_DISPONIBLE:
        tmp_dir   = tempfile.gettempdir()                          # Directorio temporal del sistema
        tmp_diag  = os.path.join(tmp_dir, "_diag_afd_tmp")        # Ruta temporal para el diagrama
        tmp_tabla = os.path.join(tmp_dir, "_tabla_afd_tmp")       # Ruta temporal para la tabla de IDs

        diagrama.render(tmp_diag, cleanup=True)   # Renderiza el diagrama en el directorio temporal

        # Construye la cabecera HTML de la tabla de IDs con estilos
        encabezado_html = (
            '<TR>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Paso</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Estado</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Entrada restante</FONT></B></TD>'
            '<TD BGCOLOR="#E0E0E0"><B><FONT FACE="Arial">Acci&#243;n</FONT></B></TD>'
            '</TR>'
        )
        filas_html = []
        for i, (estado_id, entrada_id) in enumerate(ids):   # Itera sobre cada paso del recorrido
            es_ultima = (i == len(ids) - 1)                 # True si es el último paso
            if es_ultima:
                bg = "#B8E6B8" if aceptada else "#F4B8B8"   # Verde o rojo según el resultado final
            else:
                bg = "#FFFFFF" if i % 2 == 0 else "#F5F5F5"   # Filas alternadas blanco/gris

            if i == 0:
                accion = "inicio"   # Primera fila: acción de inicio
            else:
                est_ant = ids[i - 1][0]       # Estado del paso anterior
                sim     = traza[i - 1][1]     # Símbolo leído en el paso anterior
                accion  = f"&#948;({est_ant}, {sim})"   # δ(estado, símbolo) en notación HTML
            if es_ultima:
                accion += " [ACEPTA]" if aceptada else " [RECHAZA]"   # Agrega el veredicto final

            entrada_display = entrada_id if entrada_id else "&#949;"   # ε si ya no queda entrada

            filas_html.append(
                f'<TR>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{i}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{estado_id}</FONT></TD>'
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
        tabla_dot.node("t", label=label_tabla, shape="plaintext")   # Nodo con la tabla HTML
        tabla_dot.render(tmp_tabla, cleanup=True)      # Renderiza la tabla en el directorio temporal

        # Abre ambas imágenes y las convierte a RGB para poder combinarlas
        img_diag  = Image.open(tmp_diag  + ".png").convert("RGB")
        img_tabla = Image.open(tmp_tabla + ".png").convert("RGB")

        padding    = 20                                                   # Separación vertical entre imágenes
        max_ancho  = max(img_diag.width, img_tabla.width)                 # Ancho del canvas final
        alto_total = img_diag.height + padding + img_tabla.height         # Alto total combinado

        combinada = Image.new("RGB", (max_ancho, alto_total), (255, 255, 255))         # Canvas blanco
        combinada.paste(img_diag,  ((max_ancho - img_diag.width)  // 2, 0))           # Diagrama arriba centrado
        combinada.paste(img_tabla, ((max_ancho - img_tabla.width) // 2,
                                    img_diag.height + padding))                        # Tabla abajo centrada
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
    """Inicia un loop donde el usuario ingresa cadenas y el AFD las procesa una a una."""

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
            if entrada.strip().lower() == "salir":   # Condición de salida del loop
                print("\n  ¡Hasta luego!")
                break
            cadenas = [c.strip() for c in entrada.split(",")]   # Permite múltiples cadenas separadas por coma
            for cadena in cadenas:
                if cadena != "" and not all(c in ALFABETO for c in cadena):   # Ignora cadenas con símbolos inválidos
                    continue
                aceptada, traza, ids = procesar_cadena(cadena)   # Procesa la cadena con el AFD
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
    print("  AFD — Cadenas binarias que terminan en '01'")
    print("=" * 60)

    imprimir_tabla_transicion()   # Muestra la tabla de transición δ en consola

    try:
        generar_diagrama()        # Genera y guarda el diagrama base del AFD
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
