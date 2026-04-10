"""
AP (Autómata con Pila) — Lenguaje L = { aⁿbⁿ | n ≥ 1 }
Materia   : Teoría de la Computación
Trabajo   : TP1 — Autómata 3 de 3 (AP)
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

ESTADOS = {"q0", "q1", "q2"}    # Conjunto de estados del AP
ALFABETO = {"a", "b"}           # Símbolos válidos de entrada
ESTADO_INICIAL = "q0"           # Estado desde el que comienza la lectura
ESTADOS_FINALES = {"q2"}        # Estado de aceptación: cantidades de 'a' y 'b' coincidieron
ALFABETO_PILA = {"A", "Z"}      # Símbolos de la pila: A = marca de conteo, Z = fondo de pila
SIMBOLO_INICIAL_PILA = "Z"      # La pila arranca con Z (símbolo de fondo)

# Función de transición δ: (estado, símbolo_entrada, tope_pila) → (nuevo_estado, lista_a_apilar)
# lista_a_apilar vacía [] = desapilar sin reemplazar
# símbolo_entrada None = transición ε (no consume símbolo de la entrada)
# El PRIMER elemento de lista_a_apilar queda en el TOPE (se apila en orden reverso)
TRANSICIONES = {
    ("q0", "a", "Z"): ("q0", ["A", "Z"]),   # Primera 'a': apila A dejando Z debajo
    ("q0", "a", "A"): ("q0", ["A", "A"]),   # 'a' siguientes: apila otra A sobre la existente
    ("q0", "b", "A"): ("q1", []),           # Primera 'b': desapila la A correspondiente
    ("q1", "b", "A"): ("q1", []),           # 'b' siguientes: sigue desapilando A por cada 'b'
    ("q1", None,  "Z"): ("q2", ["Z"]),      # ε: si solo queda Z en la pila → aceptar
}


# =====================================================
# PROCESAMIENTO DE CADENAS
# =====================================================

def procesar_cadena(cadena: str) -> tuple:
    """Simula el AP símbolo a símbolo manejando la pila; aplica transiciones ε al terminar."""

    print(f"\nProcesando cadena: '{cadena}'")

    # pila[-1] es el tope; append/pop operan en O(1) sobre el final de la lista
    estado = ESTADO_INICIAL
    pila: list[str] = [SIMBOLO_INICIAL_PILA]   # Pila inicial: solo el símbolo de fondo Z
    traza: list = []
    ids: list = [(ESTADO_INICIAL, cadena, list(pila))]   # Copia de la pila para no mutar el historial

    print(f"  Estado inicial: {estado} | Pila: {pila}")

    for i, simbolo in enumerate(cadena):
        if simbolo not in ALFABETO:   # Valida que el símbolo pertenezca al alfabeto
            print(f"  ERROR: el símbolo '{simbolo}' no pertenece al alfabeto Σ = {ALFABETO}")
            return False, traza, ids

        if not pila:   # Pila vacía: no hay transición posible
            print(f"  Pila vacía — no hay transición posible para '{simbolo}'")
            return False, traza, ids

        tope = pila[-1]   # Consulta el tope sin desapilar

        if (estado, simbolo, tope) not in TRANSICIONES:   # Sin transición definida → rechazo inmediato
            print(f"  No hay transición para δ({estado}, {simbolo}, {tope}) — RECHAZADA")
            return False, traza, ids

        nuevo_estado, a_apilar = TRANSICIONES[(estado, simbolo, tope)]   # Obtiene la regla aplicable

        pila.pop()                        # Desapila el tope actual
        for sym in reversed(a_apilar):    # Apila los nuevos símbolos; reversed asegura que el primero quede arriba
            pila.append(sym)

        apilado_str = "".join(a_apilar) if a_apilar else "ε"
        print(f"  δ({estado}, {simbolo}, {tope}) -> ({nuevo_estado}, {apilado_str}) | Pila: {pila}")

        traza.append((estado, simbolo, tope, nuevo_estado, list(pila)))   # Registra el paso en la traza
        estado = nuevo_estado
        ids.append((estado, cadena[i + 1:], list(pila)))   # Registra estado, entrada restante y pila actual

    # --- Transiciones ε (épsilon): se aplican tras consumir toda la entrada ---
    while True:
        if not pila:   # Pila vacía: no hay transición ε posible
            break
        tope = pila[-1]
        if (estado, None, tope) not in TRANSICIONES:   # Sin transición ε definida: termina el ciclo
            break

        nuevo_estado, a_apilar = TRANSICIONES[(estado, None, tope)]   # Obtiene la regla ε aplicable
        pila.pop()                        # Desapila el tope
        for sym in reversed(a_apilar):    # Apila los nuevos símbolos en orden correcto
            pila.append(sym)

        apilado_str = "".join(a_apilar) if a_apilar else "ε"
        print(f"  δ({estado}, ε, {tope}) -> ({nuevo_estado}, {apilado_str}) | Pila: {pila}")

        traza.append((estado, None, tope, nuevo_estado, list(pila)))   # Registra el paso ε
        estado = nuevo_estado
        ids.append((estado, "", list(pila)))   # Entrada restante vacía tras las transiciones ε

    aceptada = estado in ESTADOS_FINALES   # True si terminamos en el estado de aceptación
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    print(f"  Estado final: {estado} | Pila: {pila}  →  {veredicto}")
    return aceptada, traza, ids   # Devuelve resultado, traza completa y tabla de IDs


# =====================================================
# TABLA DE TRANSICIÓN (consola)
# =====================================================

def imprimir_tabla_transicion() -> None:
    """Imprime la tabla δ del AP con bordes Unicode; una fila por regla de transición."""

    estados_ord = sorted(ESTADOS)

    # Anchos de columna para cada campo de la tabla
    ancho_estado   = max(len(e) + 3 for e in estados_ord)   # +3 para prefijos "→ " o "* "
    ancho_entrada  = 9    # Columna de símbolo de entrada (o ε)
    ancho_tope     = 7    # Columna de tope de pila
    ancho_nuevo    = 14   # Columna de nuevo estado
    ancho_apilar   = 10   # Columna de símbolos a apilar

    anchos = [ancho_estado, ancho_entrada, ancho_tope, ancho_nuevo, ancho_apilar]

    def linea(izq, sep, der):
        return izq + sep.join("─" * a for a in anchos) + der   # Genera una línea separadora Unicode

    sep_top = linea("┌", "┬", "┐")
    sep_mid = linea("├", "┼", "┤")
    sep_bot = linea("└", "┴", "┘")

    print("\nTabla de transición δ:")
    print(sep_top)   # Borde superior

    # Fila de encabezado con los nombres de las columnas
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
        return (est, "" if ent is None else ent, tope)   # None (ε) ordena al final dentro del estado

    for (est, ent, tope), (nuevo_est, a_apilar) in sorted(TRANSICIONES.items(), key=clave_orden):
        prefijo = ""
        if est == ESTADO_INICIAL:    # Marca el estado inicial con "→ "
            prefijo += "→ "
        if est in ESTADOS_FINALES:   # Marca los estados finales con "* "
            prefijo += "* "
        celda_estado = f"{prefijo}{est}"

        entrada_str = "ε" if ent is None else ent               # ε para transiciones sin consumo de entrada
        apilar_str  = "ε" if not a_apilar else "".join(a_apilar)   # ε si no se apila nada (desapilar)

        print(
            f"│{celda_estado:<{ancho_estado}}"
            f"│{entrada_str:^{ancho_entrada}}"
            f"│{tope:^{ancho_tope}}"
            f"│{nuevo_est:^{ancho_nuevo}}"
            f"│{apilar_str:^{ancho_apilar}}│"
        )

    print(sep_bot)   # Borde inferior
    print("  → estado inicial     * estado(s) final(es)     ε transición/apilado vacío")


# =====================================================
# DIAGRAMA BASE (Graphviz)
# =====================================================

def generar_diagrama() -> None:
    """Renderiza el diagrama del AP con Graphviz y lo guarda en AP/diagrama_ap.png."""

    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        print("    También necesitás el binario de Graphviz del sistema:")
        print("    https://graphviz.org/download/")
        return

    diagrama = Digraph(name="AP_anbn", format="png")    # Grafo dirigido en formato PNG
    diagrama.attr(rankdir="LR", fontname="Helvetica")   # Disposición de izquierda a derecha

    diagrama.node("__inicio__", shape="none", width="0", label="")   # Nodo invisible para la flecha de inicio

    for estado in sorted(ESTADOS):
        if estado in ESTADOS_FINALES:
            diagrama.node(estado, shape="doublecircle")   # Doble círculo para estados finales
        else:
            diagrama.node(estado, shape="circle")         # Círculo simple para estados normales

    diagrama.edge("__inicio__", ESTADO_INICIAL)   # Flecha de inicio apuntando al estado inicial

    # Etiqueta estándar de AP: "entrada, tope / apilar" (ej. "a, Z / AZ")
    aristas: dict[tuple[str, str], list[str]] = {}
    for (origen, ent, tope), (destino, a_apilar) in TRANSICIONES.items():
        entrada_str = "ε" if ent is None else ent
        apilar_str  = "ε" if not a_apilar else "".join(a_apilar)
        etiqueta    = f"{entrada_str}, {tope} / {apilar_str}"
        aristas.setdefault((origen, destino), []).append(etiqueta)   # Agrupa etiquetas por par de estados

    for (origen, destino), etiquetas in aristas.items():
        etiqueta_final = "\n".join(sorted(etiquetas))      # Múltiples reglas → una flecha con varias líneas
        diagrama.edge(origen, destino, label=etiqueta_final)

    import os
    carpeta = "AP"
    os.makedirs(carpeta, exist_ok=True)                          # Crea la carpeta AP si no existe
    nombre_archivo = os.path.join(carpeta, "diagrama_ap")
    diagrama.render(nombre_archivo, cleanup=True)                # Renderiza el PNG y elimina el .gv temporal
    print(f"\nDiagrama guardado como '{nombre_archivo}.png'")


# =====================================================
# DIAGRAMA DEL RECORRIDO (Graphviz + Pillow)
# =====================================================

def graficar_recorrido(cadena: str, traza: list, ids: list) -> None:
    """Genera un PNG con el recorrido del AP resaltado y la tabla de IDs (con pila) al pie."""

    try:
        from graphviz import Digraph
    except ImportError:
        print("\n[!] La librería 'graphviz' no está instalada.")
        print("    Instalala con:  pip install graphviz")
        return

    # Determina el estado final y si la cadena fue aceptada
    estado_final = traza[-1][3] if traza else ESTADO_INICIAL   # índice 3 = estado destino en la traza del AP
    aceptada = estado_final in ESTADOS_FINALES

    # Recopila los estados visitados (origen e destino de cada paso)
    estados_visitados: set = set()
    for paso in traza:
        estados_visitados.add(paso[0])   # Estado origen
        estados_visitados.add(paso[3])   # Estado destino

    aristas_usadas: set = {(paso[0], paso[3]) for paso in traza}   # Pares (origen, destino) recorridos

    # Genera un sufijo seguro para el nombre de archivo
    sufijo = cadena if cadena else "epsilon"
    sufijo_seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sufijo)

    # Construye el diagrama con colores según el rol de cada estado
    diagrama = Digraph(name=f"recorrido_AP_{sufijo_seguro}", format="png")
    diagrama.attr(rankdir="LR", fontname="Helvetica")
    diagrama.node("__inicio__", shape="none", width="0", label="")

    for estado in sorted(ESTADOS):
        shape = "doublecircle" if estado in ESTADOS_FINALES else "circle"
        if estado == estado_final:
            color_final = "#B8E6B8" if aceptada else "#F4B8B8"   # Verde si acepta, rojo si rechaza
            diagrama.node(estado, shape=shape, style="filled", fillcolor=color_final)
        elif estado in estados_visitados:
            diagrama.node(estado, shape=shape, style="filled", fillcolor="#FFF4B8")   # Amarillo: visitado
        else:
            diagrama.node(estado, shape=shape)   # Sin relleno: no visitado

    diagrama.edge("__inicio__", ESTADO_INICIAL)

    # Construye el mapa de aristas con etiquetas en formato "entrada, tope / apilar"
    aristas: dict = {}
    for (origen, ent, tope), (destino, a_apilar) in TRANSICIONES.items():
        entrada_str = "ε" if ent is None else ent
        apilar_str  = "ε" if not a_apilar else "".join(a_apilar)
        etiqueta    = f"{entrada_str}, {tope} / {apilar_str}"
        aristas.setdefault((origen, destino), []).append(etiqueta)

    for (origen, destino), etiquetas in aristas.items():
        etiqueta_final = "\n".join(sorted(etiquetas))
        if (origen, destino) in aristas_usadas:
            # Arista resaltada: fue recorrida durante el procesamiento
            diagrama.edge(origen, destino, label=etiqueta_final, color="#1F4E79", penwidth="2.5", fontcolor="#1F4E79")
        else:
            # Arista atenuada: no fue usada en este recorrido
            diagrama.edge(origen, destino, label=etiqueta_final, color="#CCCCCC", fontcolor="#CCCCCC")

    import os
    import tempfile

    carpeta = "AP"
    os.makedirs(carpeta, exist_ok=True)   # Crea la carpeta AP si no existe
    nombre_archivo = os.path.join(carpeta, f"recorrido_ap_{sufijo_seguro}")

    if _PIL_DISPONIBLE:
        tmp_dir   = tempfile.gettempdir()                         # Directorio temporal del sistema
        tmp_diag  = os.path.join(tmp_dir, "_diag_ap_tmp")        # Ruta temporal para el diagrama
        tmp_tabla = os.path.join(tmp_dir, "_tabla_ap_tmp")       # Ruta temporal para la tabla de IDs

        diagrama.render(tmp_diag, cleanup=True)   # Renderiza el diagrama en el directorio temporal

        # Construye la cabecera HTML de la tabla de IDs (incluye columna Pila)
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
        for i, (est_id, entrada_id, pila_id) in enumerate(ids):   # Itera sobre cada paso del recorrido
            es_ultima = (i == len(ids) - 1)                        # True si es el último paso
            if es_ultima:
                bg = "#B8E6B8" if aceptada else "#F4B8B8"      # Verde o rojo según el resultado
            else:
                bg = "#FFFFFF" if i % 2 == 0 else "#F5F5F5"   # Filas alternadas blanco/gris

            if i == 0:
                accion = "inicio"   # Primera fila: arranque del autómata
            else:
                est_ant  = ids[i - 1][0]      # Estado del paso anterior
                sim      = traza[i - 1][1]    # Símbolo leído (None para ε-transiciones)
                tope_ant = traza[i - 1][2]    # Tope de pila en el paso anterior
                if sim is None:
                    accion = f"&#948;({est_ant}, &#949;, {tope_ant})"   # Muestra ε en notación HTML
                else:
                    accion = f"&#948;({est_ant}, {sim}, {tope_ant})"
            if es_ultima:
                accion += " [ACEPTA]" if aceptada else " [RECHAZA]"   # Agrega el veredicto final

            entrada_display = entrada_id if entrada_id else "&#949;"          # ε si ya no queda entrada
            pila_display    = "".join(pila_id) if pila_id else "&#949;"       # ε si la pila está vacía

            filas_html.append(
                f'<TR>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{i}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{est_id}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{entrada_display}</FONT></TD>'
                f'<TD BGCOLOR="{bg}"><FONT FACE="Arial">{pila_display}</FONT></TD>'
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
        tabla_dot.node("t", label=label_tabla, shape="plaintext")   # Nodo con la tabla HTML sin borde
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
    """Inicia un loop donde el usuario ingresa cadenas y el AP las procesa una a una."""

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
            if entrada.strip().lower() == "salir":   # Condición de salida del loop
                print("\n  ¡Hasta luego!")
                break
            cadenas = [c.strip() for c in entrada.split(",")]   # Permite múltiples cadenas separadas por coma
            for cadena in cadenas:
                if cadena != "" and not all(c in ALFABETO for c in cadena):   # Ignora cadenas con símbolos inválidos
                    continue
                aceptada, traza, ids = procesar_cadena(cadena)   # Procesa la cadena con el AP
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
    print("  AP — Lenguaje L = { aⁿbⁿ | n ≥ 1 }")
    print("=" * 60)

    imprimir_tabla_transicion()   # Muestra la tabla de transición δ en consola

    try:
        generar_diagrama()        # Genera y guarda el diagrama base del AP
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
