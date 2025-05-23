#import subprocess
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import os
import heapq
import tkinter as tk
from tkinter import filedialog
import tkinter as tk
from tkinter import filedialog, messagebox

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"

archivo_seleccionado = None


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# ----------------------------------
# Funciones de lectura y graficación
# ----------------------------------

def leer_grafo_desde_archivo(ruta):
    """
    Lee un archivo de texto con dos posibles secciones:
    1) NODE_COORDS: (opcional)
       Nodo: (x, y)
    2) EDGES:
       - Con peso: NodoA-NodoB: peso
       - Sin peso: NodoA-NodoB

    Devuelve:
    - grafo: dict nodo -> lista de (vecino, peso)
    - coords: dict nodo -> (x, y)
    """
    grafo, coords = {}, {}
    seccion = None

    with open(ruta, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith('#'): 
                continue

            encabezado = linea.rstrip(':').upper()
            if encabezado == 'NODE_COORDS':
                seccion = 'coords'
                continue
            if encabezado == 'EDGES':
                seccion = 'edges'
                continue

            if seccion == 'coords':
                nodo, tup = linea.split(':', 1)
                x, y = tup.strip().lstrip('(').rstrip(')').split(',')
                coords[nodo.strip()] = (float(x), float(y))
            elif seccion == 'edges':
                if ':' in linea:
                    arista, peso = linea.split(':', 1)
                    w = float(peso)
                else:
                    arista, w = linea, 1.0
                a, b = [n.strip() for n in arista.split('-')]
                grafo.setdefault(a, []).append((b, w))
                grafo.setdefault(b, []).append((a, w))
    return grafo, coords


def graficar_grafo(grafo, coords, root=None, meta=None):
    if coords is None:
        raise ValueError("Se requieren coordenadas fijas para graficar el grafo de forma consistente.")

    G = nx.Graph()
    for u, vecinos in grafo.items():
        for v, w in vecinos:
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)

    pos = coords  # Se usan solo las coordenadas dadas

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.clear()

    node_colors = []
    for n in G.nodes():
        if n == root:
            node_colors.append('red')
        elif n == meta:
            node_colors.append('green')
        else:
            node_colors.append('lightblue')

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)

    # Coordenadas en gris bajo cada nodo
    offset = 0.15
    coord_labels = {n: f"({x:.1f}, {y:.1f})" for n, (x, y) in coords.items()}
    pos_coords = {n: (x, y - offset) for n, (x, y) in pos.items()}
    nx.draw_networkx_labels(G, pos_coords, labels=coord_labels, font_size=8, font_color='gray', ax=ax)

    nx.draw_networkx_edges(G, pos, ax=ax)
    pesos = nx.get_edge_attributes(G, 'weight')
    if any(w != 1.0 for w in pesos.values()):
        nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos, ax=ax)

    title = "Grafo con Coordenadas"
    if any(w != 1.0 for w in pesos.values()):
        title += " y Pesos"
    if root:
        title += f" (Raíz: {root})"
    ax.set_title(title)
    ax.axis('off')

    mostrar_imagen_en_tkinter(fig, titulo=title)

def graficar_grafo_con_ruta(grafo, camino, coords, root=None, meta=None):
    if coords is None:
        raise ValueError("Se requieren coordenadas fijas para graficar el grafo de forma consistente.")

    G = nx.Graph()
    for u, vecinos in grafo.items():
        for v, w in vecinos:
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)

    pos = coords  # Solo se usan las coordenadas proporcionadas

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.clear()

    node_colors = []
    for n in G.nodes():
        if n == root:
            node_colors.append('red')
        elif n == meta:
            node_colors.append('green')
        elif camino and n in camino:
            node_colors.append('yellow')
        else:
            node_colors.append('lightblue')

    # Aristas resaltadas para el camino encontrado
    edges_resaltadas = []
    if camino:
        for i in range(len(camino) - 1):
            a, b = camino[i], camino[i + 1]
            if G.has_edge(a, b):
                edges_resaltadas.append((a, b))

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)

    # Coordenadas en gris bajo cada nodo
    offset = 0.15
    coord_labels = {n: f"({x:.1f}, {y:.1f})" for n, (x, y) in coords.items()}
    pos_coords = {n: (x, y - offset) for n, (x, y) in pos.items()}
    nx.draw_networkx_labels(G, pos_coords, labels=coord_labels, font_size=8, font_color='gray', ax=ax)

    # Dibujo de todas las aristas con transparencia, y las del camino resaltadas
    nx.draw_networkx_edges(G, pos, alpha=0.4, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=edges_resaltadas, edge_color='blue', width=2.5, ax=ax)

    # Pesos en aristas si no son todos 1.0
    pesos = nx.get_edge_attributes(G, 'weight')
    if any(w != 1.0 for w in pesos.values()):
        nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos, ax=ax)

    title = "Ruta encontrada sobre el grafo"
    if root:
        title += f" (Raíz: {root})"
    if meta:
        title += f" → Meta: {meta}"
    ax.set_title(title)
    ax.axis('off')

    mostrar_imagen_en_tkinter(fig, titulo=title)



def mostrar_imagen_en_tkinter(fig, titulo="Visualización del grafo"):
    ventana = tk.Toplevel()
    ventana.title(titulo)
    canvas = FigureCanvasTkAgg(fig, master=ventana)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)



# ----------------------------------
# Búsquedas
# ----------------------------------

def busquedaAmplitud(grafo, inicio, meta):
    cola = [inicio]
    padres = {inicio: None}
    print("BFS pasos:")
    
    while cola:
        actual = cola.pop(0)

        camino_p = []
        node = actual
        while node is not None:
            camino_p.insert(0, node)
            node = padres[node]
        print(" -> ".join(camino_p))

        if actual == meta:
            costo = len(camino_p) - 1  # Cada arista cuesta 1
            return camino_p, costo, padres

        for v, _ in grafo.get(actual, []):
            if v not in padres:
                padres[v] = actual
                cola.append(v)
    
    return None, None, None




def dfs_limitado(grafo, nodo_actual, objetivo, profundidad_max, visitados=None, camino=None, padres=None):
    """
    DFS limitada para IDDFS, retorna camino, padres y costo (# aristas).
    """
    if padres is None:
        padres = {}
    if visitados is None:
        visitados = set()
    if camino is None:
        camino = []

    # Marcamos y agregamos al camino
    visitados.add(nodo_actual)
    camino.append(nodo_actual)

    # Verificar objetivo
    if nodo_actual == objetivo:
        costo = len(camino) - 1
        return list(camino), padres, costo

    # Si alcanzamos profundidad máxima
    if profundidad_max <= 0:
        camino.pop()
        visitados.remove(nodo_actual)
        return None, padres, None

    # Explorar vecinos
    for vecino, _ in grafo.get(nodo_actual, []):
        if vecino not in visitados:
            padres[vecino] = nodo_actual
            resultado, padres, costo = dfs_limitado(
                grafo, vecino, objetivo, profundidad_max - 1,
                visitados, camino, padres
            )
            if resultado:
                return resultado, padres, costo

    # Backtrack
    camino.pop()
    visitados.remove(nodo_actual)
    return None, padres, None

def busquedaProfundidad(grafo, nodo_inicio, nodo_meta):
    nodos = [nodo_inicio]  # Pila (modo LIFO)
    padres = {nodo_inicio: None} 

    while nodos:
        print("Nodos: ", nodos)
        nodo = nodos.pop(0)
        print("Nodo: ", nodo)

        if nodo == nodo_meta:
            # Construir camino
            camino = []
            actual = nodo_meta
            while actual is not None:
                camino.insert(0, actual)
                actual = padres[actual]
            costo = len(camino) - 1  
            return camino, costo, padres

        # Expandir
        for hijo in reversed([h for h, _ in grafo.get(nodo, [])]):
            print("hijo:", hijo)
            if padres[nodo] is not None and hijo == padres[nodo]:
                continue  
            if hijo not in padres:
                padres[hijo] = nodo
                nodos.insert(0, hijo)

    return None, None, None 



def busquedaProfundidadIterativa(grafo, inicio, meta, maxima_profundidad=10):
    """Búsqueda por profundización iterativa (IDDFS).
    Retorna camino, costo (# aristas) y padres, o (None, None, {}) si no se encuentra."""
    for limite in range(maxima_profundidad + 1):
        print(f"Intentando IDDFS con límite={limite}")
        resultado, padres, costo = dfs_limitado(
            grafo, inicio, meta, limite
        )
        if resultado:
            print(f"Meta encontrada con costo {costo}")
            return resultado, costo, padres
    print("No se encontró la meta dentro del límite dado.")
    return None, None, {}



def busquedaAvara(grafo, coords, inicio, meta):
    def heuristica(n):
        if n in coords and meta in coords:
            x1, y1 = coords[n]
            x2, y2 = coords[meta]
            return math.hypot(x2 - x1, y2 - y1)
        return 0

    nodos = [inicio]
    padres = {inicio: None}
    visitados = set()
    costo_total = {inicio: 0} 

    print("Avara pasos:")
    while nodos:
        print("Lista de nodos:", nodos)
        nodo = nodos.pop(0) 
        print("Expandimos:", nodo)

        if nodo == meta:
            camino = []
            actual = meta
            while actual is not None:
                camino.insert(0, actual)
                actual = padres[actual]
            return camino, costo_total[meta], padres

        visitados.add(nodo)

        hijos = []
        for hijo, peso in grafo.get(nodo, []):
            if hijo not in visitados and hijo not in nodos:
                padres[hijo] = nodo
                costo_total[hijo] = costo_total[nodo] + peso
                hijos.append(hijo)

        hijos.sort(key=lambda x: heuristica(x))
        print("Frontera:", hijos)

        for hijo in hijos:
            i = 0
            while i < len(nodos) and heuristica(hijo) >= heuristica(nodos[i]):
                i += 1
            nodos.insert(i, hijo)

    return None, None, None

def busquedaCostoUniforme(grafo, inicio, meta):
    frontera = [(0, inicio)]
    padres = {inicio: None}
    costos = {inicio: 0}
    visitados = set()

    while frontera:
        frontera.sort(key=lambda x: x[0])
        costo_actual, nodo = frontera.pop(0)

        if nodo in visitados:
            continue

        if nodo == meta:
            camino = []
            while nodo:
                camino.insert(0, nodo)
                nodo = padres[nodo]
            print("\nCosto total del camino:", costo_actual)
            return camino, costo_actual, padres  # ✅ aquí se retorna costo_actual también

        visitados.add(nodo)
        for vecino, peso in grafo.get(nodo, []):
            nuevo_costo = costo_actual + peso
            if vecino not in costos or nuevo_costo < costos[vecino]:
                costos[vecino] = nuevo_costo
                padres[vecino] = nodo
                if vecino not in visitados:
                    frontera.append((nuevo_costo, vecino))

    return None, None, padres  # si no se encontró camino



def busquedaAEstrella(grafo, coords, inicio, meta):
    def h(n):
        if n not in coords or meta not in coords:
            raise ValueError(f"No hay coordenadas para {n} o {meta}")
        x1, y1 = coords[n]; x2, y2 = coords[meta]
        return math.hypot(x2 - x1, y2 - y1)

    frontera = [(0, inicio)]
    padres = {inicio: None}
    costos = {inicio: 0}
    visitados = set()

    tabla = []

    while frontera:
        frontera.sort(key=lambda x: costos[x[1]] + h(x[1]))
        _, nodo = frontera.pop(0)

        if nodo in visitados:
            continue

        f_n = round(costos[nodo] + h(nodo), 2)
        tabla.append((nodo, round(costos[nodo], 2), round(h(nodo), 2), f_n))

        if nodo == meta:
            camino = []
            while nodo:
                camino.insert(0, nodo)
                nodo = padres[nodo]

            # Imprimir tabla
            print("\nTabla de nodos expandido en A*:")
            print(f"{'Nodo':<8}{'g(n)':<8}{'h(n)':<8}{'f(n)':<8}")
            for fila in tabla:
                print(f"{fila[0]:<8}{fila[1]:<8}{fila[2]:<8}{fila[3]:<8}")
            print("Costo total del camino:", costos[meta])
            return camino, costos[meta], padres  # ✅ devuelve costo

        visitados.add(nodo)

        for vecino, peso in grafo.get(nodo, []):
            nuevo_costo = costos[nodo] + peso
            if vecino not in costos or nuevo_costo < costos[vecino]:
                costos[vecino] = nuevo_costo
                padres[vecino] = nodo
                if vecino not in visitados:
                    frontera.append((nuevo_costo, vecino))

    return None, None, padres


def validar_para(algoritmo, grafo, coords, meta):
    if meta not in grafo:
        print(f"❌ El nodo meta '{meta}' no existe en el grafo.")
        return False

    if algoritmo in ("A*", "Ávara"):
        if not coords or meta not in coords:
            print(f"❌ El grafo no tiene coordenadas suficientes para {algoritmo}.")
            return False

    if algoritmo in ("A*", "Costo Uniforme"):
        tiene_pesos = any(w != 1.0 for vecinos in grafo.values() for _, w in vecinos)
        if not tiene_pesos:
            print(f"⚠️ El grafo no tiene pesos definidos. {algoritmo} tratará todos como 1.")
    return True

# ----------------------------------
# Menú interactivo
# ----------------------------------

#funciones para mostrar ventana para seleccionar archivo
def seleccionar_archivo():
    global archivo_seleccionado
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de grafo",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if ruta:
        archivo_seleccionado = ruta
        label_archivo.config(text=f"Archivo seleccionado:\n{ruta}")

def confirmar_y_cerrar(ventana):
    if archivo_seleccionado:
        ventana.destroy()
    else:
        messagebox.showwarning("Advertencia", "Por favor selecciona un archivo antes de confirmar.")

def ventana_seleccion():
    ventana = tk.Tk()
    ventana.title("Cargar archivo de grafo")

    ancho = 500
    alto = 200
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    global label_archivo
    label_archivo = tk.Label(ventana, text="Ningún archivo seleccionado", wraplength=480)
    label_archivo.pack(pady=10)

    btn_seleccionar = tk.Button(ventana, text="Seleccionar archivo", command=seleccionar_archivo)
    btn_seleccionar.pack(pady=5)

    btn_confirmar = tk.Button(ventana, text="Confirmar", command=lambda: confirmar_y_cerrar(ventana))
    btn_confirmar.pack(pady=5)

    ventana.mainloop()

def menu():
    global archivo_seleccionado

    while True:
        # Si no se ha seleccionado archivo aún, pedirlo
        if not archivo_seleccionado:
            ventana_seleccion()
            if not archivo_seleccionado:
                print("No se seleccionó ningún archivo. Saliendo.")
                return

            grafo, coords = leer_grafo_desde_archivo(archivo_seleccionado)
            graficar_grafo(grafo, coords)

        # Pedir nodo raíz y nodo meta
        root = input("Nodo raíz: ")
        meta = input("Nodo meta: ")

        # Mostrar opciones
        print(f"\n{BOLD}{CYAN}=== MENÚ DE BÚSQUEDAS ==={RESET}")
        print(f"{YELLOW}1.{RESET} {GREEN}Búsqueda en Anchura (BFS){RESET}")
        print(f"{YELLOW}2.{RESET} {GREEN}Profundización Iterativa (IDDFS){RESET}")
        print(f"{YELLOW}3.{RESET} {GREEN}Búsqueda Ávara{RESET}")
        print(f"{YELLOW}4.{RESET} {GREEN}Búsqueda en Profundidad{RESET}")
        print(f"{YELLOW}5.{RESET} {GREEN}Búsqueda de Costo Uniforme{RESET}")
        print(f"{YELLOW}6.{RESET} {GREEN}Búsqueda A*{RESET}")
        print(f"{YELLOW}0.{RESET} {RED}Salir{RESET}")
        opcion = input(f"{BOLD}Elige una opción: {RESET}")

        # Salir si se elige 0
        if opcion == '0':
            print("Saliendo...")
            break

        camino, padres, costo = None, None, None

        # Ejecutar la búsqueda elegida
        if opcion == '1':
            if not validar_para("BFS", grafo, coords, meta):
                continue
            camino, costo, padres = busquedaAmplitud(grafo, root, meta)

        elif opcion == '2':
            if not validar_para("IDDFS", grafo, coords, meta):
                continue
            profundidad = int(input("Profundidad máxima [10]: ") or 10)
            camino, padres, costo = busquedaProfundidadIterativa(grafo, root, meta, profundidad)
            costo = len(costo) - 2

        elif opcion == '3':
            if not validar_para("Ávara", grafo, coords, meta):
                continue
            camino, costo, padres = busquedaAvara(grafo, coords, root, meta)

        elif opcion == '4':
            if not validar_para("DFS", grafo, coords, meta):
                continue
            camino, costo, padres = busquedaProfundidad(grafo, root, meta)

        elif opcion == '5':
            if not validar_para("Costo Uniforme", grafo, coords, meta):
                continue
            camino, costo, padres = busquedaCostoUniforme(grafo, root, meta)

        elif opcion == '6':
            if not validar_para("A*", grafo, coords, meta):
                continue
            camino, costo, padres = busquedaAEstrella(grafo, coords, root, meta)

        else:
            print("Opción inválida.")
            continue

        # Mostrar resultados
        if camino:
            graficar_grafo_con_ruta(grafo, camino, coords, root, meta)
            print("Camino encontrado: " + " -> ".join(camino))
            if costo:
                print(f"Costo: {costo:.2f}")
            else:
                print("No se encontró costo.")
        else:
            print("No se encontró camino.")

        input("\nPresiona Enter para continuar...")
        limpiar_pantalla()



if __name__ == '__main__':
    menu()
