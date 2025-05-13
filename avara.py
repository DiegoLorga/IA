import networkx as nx
import matplotlib.pyplot as plt
import math
import os

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# ----------------------------------
# Funciones de lectura y graficación
# ----------------------------------

def leer_grafo_desde_archivo(ruta):
    """
    Lee un archivo de texto con tres posibles secciones:
    1) ROOT: NodoRaiz
    2) NODE_COORDS: (opcional)
       Nodo: (x, y)
    3) EDGES:
       - Con peso: NodoA-NodoB: peso
       - Sin peso: NodoA-NodoB

    Devuelve:
    - grafo: dict nodo -> lista de (vecino, peso)
    - coords: dict nodo -> (x, y)
    - root: nodo raíz
    """
    grafo, coords = {}, {}
    root, seccion = None, None

    with open(ruta, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith('#'): continue

            if linea.upper().startswith('ROOT:'):
                root = linea.split(':',1)[1].strip()
                continue
            encabezado = linea.rstrip(':').upper()
            if encabezado == 'NODE_COORDS': seccion = 'coords'; continue
            if encabezado == 'EDGES': seccion = 'edges'; continue

            if seccion == 'coords':
                nodo, tup = linea.split(':',1)
                x,y = tup.strip().lstrip('(').rstrip(')').split(',')
                coords[nodo.strip()] = (float(x), float(y))
            elif seccion == 'edges':
                if ':' in linea:
                    arista, peso = linea.split(':',1)
                    w = float(peso)
                else:
                    arista, w = linea, 1.0
                a,b = [n.strip() for n in arista.split('-')]
                grafo.setdefault(a,[]).append((b,w))
                grafo.setdefault(b,[]).append((a,w))

    if root is None:
        raise ValueError("Debe especificar ROOT: <Nodo>")
    return grafo, coords, root


def graficar_grafo(grafo, coords=None, root=None, meta=None):

    """
    Dibuja el grafo con:
    - Nodo raíz resaltado.
    - Pesos si existen.
    - Coordenadas si existen (mostradas debajo del nodo).
    """

    G = nx.Graph()
    for u, vecinos in grafo.items():
        for v, w in vecinos:
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)

    # Usar coordenadas si existen, si no usar spring layout
    pos = coords if coords else nx.spring_layout(G)

    plt.clf()
    colors = []
    for n in G.nodes():
        if n == root:
            colors.append('red')
        elif n == meta:
            colors.append('green')
        else:
            colors.append('lightblue')

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=600)

    # Mostrar solo nombre del nodo en su centro
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Mostrar coordenadas debajo del nodo
    if coords:
        offset = 0.15  # separación vertical hacia abajo
        coord_labels = {
            n: f"({x:.1f}, {y:.1f})"
            for n, (x, y) in coords.items()
        }
        pos_coords = {
            n: (x, y - offset)
            for n, (x, y) in pos.items()
        }
        nx.draw_networkx_labels(G, pos_coords, labels=coord_labels, font_size=8, font_color='gray')

    # Dibujar aristas y pesos si los hay
    nx.draw_networkx_edges(G, pos)
    peso = nx.get_edge_attributes(G, 'weight')
    if any(w != 1.0 for w in peso.values()):
        nx.draw_networkx_edge_labels(G, pos, edge_labels=peso)

    # Título dinámico
    title = "Grafo"
    if coords:
        title += " con Coordenadas"
    if any(w != 1.0 for w in peso.values()):
        title += " y Pesos"
    title += f" (Raíz: {root})"

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def graficar_arbol_exploracion(padres, coords=None, root=None, meta=None):
    """
    Dibuja el árbol de exploración generado por un algoritmo de búsqueda.
    - Usa colores distintos para la raíz y el nodo meta.
    - Muestra coordenadas si están disponibles.
    - Muestra pesos si los padres fueron derivados de un grafo con pesos.
    """
    G = nx.DiGraph()
    for hijo, padre in padres.items():
        if padre is not None:
            G.add_edge(padre, hijo)

    # Posiciones
    pos = coords if coords else nx.spring_layout(G)

    # Colores de nodos
    colors = []
    for n in G.nodes():
        if n == root:
            colors.append('red')
        elif n == meta:
            colors.append('green')
        else:
            colors.append('lightblue')

    # Dibujar nodos y etiquetas
    plt.figure()
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=600)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Coordenadas debajo del nodo
    if coords:
        offset = 0.15
        coord_labels = {n: f"({x:.1f}, {y:.1f})" for n, (x, y) in coords.items()}
        pos_coords = {n: (x, y - offset) for n, (x, y) in pos.items()}
        nx.draw_networkx_labels(G, pos_coords, labels=coord_labels, font_size=8, font_color='gray')

    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, arrows=True)

    plt.title("Árbol de exploración (Raíz en rojo, Meta en verde)")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def graficar_grafo_con_ruta(grafo, camino, coords=None, root=None, meta=None):
    """
    Dibuja el grafo y resalta la ruta encontrada.
    """
    G = nx.Graph()
    for u, vecinos in grafo.items():
        for v, w in vecinos:
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)

    pos = coords if coords else nx.spring_layout(G)

    # Preparar colores para nodos
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

    # Aristas en la ruta
    edges_resaltadas = []
    if camino:
        for i in range(len(camino) - 1):
            a, b = camino[i], camino[i + 1]
            if G.has_edge(a, b):
                edges_resaltadas.append((a, b))

    plt.figure()
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Coordenadas debajo del nodo si hay
    if coords:
        offset = 0.15
        coord_labels = {n: f"({x:.1f}, {y:.1f})" for n, (x, y) in coords.items()}
        pos_coords = {n: (x, y - offset) for n, (x, y) in pos.items()}
        nx.draw_networkx_labels(G, pos_coords, labels=coord_labels, font_size=8, font_color='gray')

    # Dibujar aristas normales
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    
    # Dibujar la ruta resaltada
    nx.draw_networkx_edges(G, pos, edgelist=edges_resaltadas, edge_color='blue', width=2.5)

    # Mostrar pesos si hay
    pesos = nx.get_edge_attributes(G, 'weight')
    if any(w != 1.0 for w in pesos.values()):
        nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos)

    plt.title("Ruta encontrada sobre el grafo")
    plt.axis('off')
    plt.tight_layout()
    plt.show()



# ----------------------------------
# Búsquedas
# ----------------------------------

def busquedaAmplitud(grafo, nodo_inicio, nodo_meta):
    """Búsqueda en anchura (BFS)."""
    cola = [nodo_inicio]
    padres = {nodo_inicio: None}
    while cola:
        actual = cola.pop(0)
        if actual == nodo_meta:
            camino=[]
            while actual:
                camino.insert(0,actual)
                actual = padres[actual]
            return camino, padres
        for vecino,_ in grafo.get(actual,[]):
            if vecino not in padres:
                padres[vecino]=actual
                cola.append(vecino)
    return None, padres


def dfs_limitado(grafo, nodo_actual, objetivo, profundidad_max, visitados=None, camino=None, padres=None):
    """
    DFS limitada para IDDFS.
    """
    if padres is None:
        padres = {}

    if visitados is None:
        visitados = set()
    if camino is None:
        camino = []
    visitados.add(nodo_actual)
    camino.append(nodo_actual)
    if nodo_actual == objetivo:
        return list(camino), padres
    if profundidad_max <= 0:
        camino.pop()
        visitados.remove(nodo_actual)
        return None, padres
    for vecino,_ in grafo.get(nodo_actual, []):
        if vecino not in visitados:
            padres[vecino] = nodo_actual
            resultado, padres = dfs_limitado(grafo, vecino, objetivo, profundidad_max-1, visitados, camino, padres)
            if resultado:
                return resultado, padres
    camino.pop()
    visitados.remove(nodo_actual)
    return None, padres


def busquedaProfundidadIterativa(grafo, inicio, meta, maxima_profundidad=10):
    """Búsqueda por profundización iterativa (IDDFS)."""
    for limite in range(maxima_profundidad+1):
        print(f"Intentando IDDFS con límite={limite}")
        resultado, padres = dfs_limitado(grafo, inicio, meta, limite)
        if resultado:
            return resultado, padres
    return None, {}


def busquedaAvara(grafo, coords, inicio, meta):
    """Búsqueda ávara (Greedy Best-First Search)."""
    def h(n):
        x1,y1 = coords[n]; x2,y2 = coords[meta]
        return math.hypot(x2-x1, y2-y1)
    abiertos = [(h(inicio), inicio)]
    padres = {inicio: None}
    visitados = set()
    while abiertos:
        abiertos.sort(key=lambda x: x[0])
        _, actual = abiertos.pop(0)
        if actual == meta:
            camino=[]
            while actual:
                camino.insert(0,actual)
                actual = padres[actual]
            return camino, padres
        visitados.add(actual)
        for vecino,_ in grafo.get(actual,[]):
            if vecino in visitados or any(vecino==n for _,n in abiertos):
                continue
            padres[vecino]=actual
            abiertos.append((h(vecino), vecino))
    return None, padres

def busquedaProfundidad(grafo, inicio, meta):
    """Búsqueda en profundidad normal (DFS recursiva)."""
    visitados = set()
    camino = []
    padres = {inicio: None}

    def dfs(u):
        visitados.add(u)
        camino.append(u)
        if u == meta:
            return True
        for v,_ in grafo.get(u, []):
            if v not in visitados:
                padres[v] = u
                if dfs(v):
                    return True
        camino.pop()
        return False
    if dfs(inicio):
        return camino, padres
    return None, padres

def busquedaCostoUniforme(grafo, inicio, meta):
    import heapq

    frontera = [(0, inicio)]  # (costo acumulado, nodo)
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
            return camino, padres

        visitados.add(nodo)
        for vecino, peso in grafo.get(nodo, []):
            nuevo_costo = costo_actual + peso
            if vecino not in costos or nuevo_costo < costos[vecino]:
                costos[vecino] = nuevo_costo
                padres[vecino] = nodo
                if vecino not in visitados:
                    frontera.append((nuevo_costo, vecino))

    return None, padres

def busquedaAEstrella(grafo, coords, inicio, meta):
    """Búsqueda A* (A estrella) con heurística euclidiana."""
    def h(n):
        if n not in coords or meta not in coords:
            raise ValueError(f"No hay coordenadas para {n} o {meta}")
        x1, y1 = coords[n]; x2, y2 = coords[meta]
        return math.hypot(x2 - x1, y2 - y1)

    frontera = [(0, inicio)]  # (costo acumulado, nodo)
    padres = {inicio: None}
    costos = {inicio: 0}
    visitados = set()

    while frontera:
        frontera.sort(key=lambda x: costos[x[1]] + h(x[1]))
        _, nodo = frontera.pop(0)

        if nodo in visitados:
            continue

        if nodo == meta:
            camino = []
            while nodo:
                camino.insert(0, nodo)
                nodo = padres[nodo]
            return camino, padres

        visitados.add(nodo)

        for vecino, peso in grafo.get(nodo, []):
            nuevo_costo = costos[nodo] + peso
            if vecino not in costos or nuevo_costo < costos[vecino]:
                costos[vecino] = nuevo_costo
                padres[vecino] = nodo
                if vecino not in visitados:
                    frontera.append((nuevo_costo, vecino))

    return None, padres

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

def menu():
    ruta = r'grafo.txt'
    grafo, coords, root = leer_grafo_desde_archivo(ruta)

    print(f"\n{BOLD}{CYAN}=== MENÚ DE BÚSQUEDAS ==={RESET}")
    print(f"{YELLOW}1.{RESET} {GREEN}Búsqueda en Anchura (BFS){RESET}")
    print(f"{YELLOW}2.{RESET} {GREEN}Profundización Iterativa (IDDFS){RESET}")
    print(f"{YELLOW}3.{RESET} {GREEN}Búsqueda Ávara{RESET}")
    print(f"{YELLOW}4.{RESET} {GREEN}Búsqueda en Profundidad{RESET}")
    print(f"{YELLOW}5.{RESET} {GREEN}Búsqueda de Costo Uniforme{RESET}")
    print(f"{YELLOW}6.{RESET} {GREEN}Búsqueda A*{RESET}")
    print(f"{YELLOW}0.{RESET} {RED}Salir{RESET}")
    opcion = input(f"{BOLD}Elige una opción: {RESET}")



    camino, padres = None, None

    if opcion == '1':
        meta = input("Nodo meta: ")
        if not validar_para("BFS", grafo, coords, meta):
            return menu()
        graficar_grafo(grafo, coords, root, meta)
        camino, padres = busquedaAmplitud(grafo, root, meta)

    elif opcion == '2':
        meta = input("Nodo meta: ")
        if not validar_para("IDDFS", grafo, coords, meta):
            return menu()
        profundidad = int(input("Profundidad máxima [10]: ") or 10)
        graficar_grafo(grafo, coords, root, meta)
        camino, padres = busquedaProfundidadIterativa(grafo, root, meta, profundidad)

    elif opcion == '3':
        meta = input("Nodo meta: ")
        if not validar_para("Ávara", grafo, coords, meta):
            return menu()
        graficar_grafo(grafo, coords, root, meta)
        camino, padres = busquedaAvara(grafo, coords, root, meta)

    elif opcion == '4':
        meta = input("Nodo meta: ")
        if not validar_para("DFS", grafo, coords, meta):
            return menu()
        graficar_grafo(grafo, coords, root, meta)
        camino, padres = busquedaProfundidad(grafo, root, meta)

    elif opcion == '5':
        meta = input("Nodo meta: ")
        if not validar_para("Costo Uniforme", grafo, coords, meta):
            return menu()
        graficar_grafo(grafo, coords, root, meta)
        camino, padres = busquedaCostoUniforme(grafo, root, meta)

    elif opcion == '6':
        meta = input("Nodo meta: ")
        if not validar_para("A*", grafo, coords, meta):
            return menu()
        graficar_grafo(grafo, coords, root, meta)
        camino, padres = busquedaAEstrella(grafo, coords, root, meta)

    else:
        print("Saliendo...")
        return

    if camino:
        graficar_arbol_exploracion(padres, coords, root, meta)
        graficar_grafo_con_ruta(grafo, camino, coords, root, meta)
        print("Camino encontrado: " + " -> ".join(camino))
    else:
        print("No se encontró camino.")

    input("\nPresiona Enter para continuar...")
    limpiar_pantalla()
    menu()


if __name__ == '__main__':
    menu()
