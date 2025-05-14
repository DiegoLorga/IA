import networkx as nx
import matplotlib.pyplot as plt
import math
import heapq

# ----------------------------------
# Funciones de lectura y graficación
# ----------------------------------

def leer_grafo_desde_archivo(ruta):
    grafo, coords = {}, {}
    seccion = None
    with open(ruta, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith('#'): continue
            encabezado = linea.rstrip(':').upper()
            if encabezado == 'NODE_COORDS': seccion = 'coords'; continue
            if encabezado == 'EDGES': seccion = 'edges'; continue
            if seccion == 'coords':
                nodo, tup = linea.split(':', 1)
                x, y = tup.strip().lstrip('(').rstrip(')').split(',')
                coords[nodo.strip()] = (float(x), float(y))
            elif seccion == 'edges':
                if ':' in linea:
                    arista, peso = linea.split(':', 1)
                    peso = peso.strip().rstrip(',')
                    try: w = float(peso)
                    except: w = 1.0
                else:
                    arista, w = linea, 1.0
                a, b = [n.strip() for n in arista.split('-')]
                grafo.setdefault(a, []).append((b, w))
                grafo.setdefault(b, []).append((a, w))
    return grafo, coords


def graficar_grafo(grafo, coords=None, root=None):
    G = nx.Graph()
    for u, vecinos in grafo.items():
        for v, w in vecinos:
            if not G.has_edge(u, v): G.add_edge(u, v, weight=w)
    pos = coords if coords else nx.spring_layout(G)
    plt.clf()
    colors = ['red' if n == root else 'lightblue' for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=600)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    title = "Grafo" + (" con Coordenadas" if coords else "") + (f" (Raíz: {root})" if root else "")
    plt.title(title)
    plt.axis('off')
    plt.show()

# ----------------------------------
# Búsquedas completas con pasos y costo
# ----------------------------------

def busquedaAmplitud(grafo, inicio, meta):
    cola = [inicio]
    padres = {inicio: None}
    print("BFS pasos:")
    while cola:
        actual = cola.pop(0)
        # reconstruir camino parcial
        camino_p = []
        node = actual
        while node:
            camino_p.insert(0, node)
            node = padres[node]
        print(" -> ".join(camino_p))
        if actual == meta:
            costo = len(camino_p) - 1
            return camino_p, costo
        for v, _ in grafo.get(actual, []):
            if v not in padres:
                padres[v] = actual
                cola.append(v)
    return None, None


def dfs_limitado(grafo, u, meta, prof, visitados=None, camino=None):
    if visitados is None: visitados = set()
    if camino is None:   camino = []
    visitados.add(u)
    camino.append(u)
    print(f"Prof {prof} DFS paso: {' -> '.join(camino)}")
    if u == meta: return list(camino)
    if prof == 0:
        camino.pop(); visitados.remove(u)
        return None
    for v, _ in grafo.get(u, []):
        if v not in visitados:
            res = dfs_limitado(grafo, v, meta, prof-1, visitados, camino)
            if res: return res
    camino.pop(); visitados.remove(u)
    return None


def busquedaProfundidadIterativa(grafo, inicio, meta, maxp=10):
    print("IDDFS pasos:")
    for limite in range(maxp+1):
        print(f"Limite={limite}")
        res = dfs_limitado(grafo, inicio, meta, limite)
        if res:
            costo = len(res)-1
            return res, costo
    return None, None


def busquedaProfundidad(grafo, inicio, meta):
    visitados = set(); camino = []
    def dfs(u):
        visitados.add(u); camino.append(u)
        print(f"DFS paso: {' -> '.join(camino)}")
        if u == meta: return True
        for v, _ in grafo.get(u, []):
            if v not in visitados and dfs(v): return True
        camino.pop(); return False
    print("DFS pasos:")
    found = dfs(inicio)
    if found:
        return camino, len(camino)-1
    return None, None


def busquedaAvara(grafo, coords, inicio, meta):
    def h(n):
        if n in coords and meta in coords:
            x1,y1=coords[n]; x2,y2=coords[meta]
            return math.hypot(x2-x1,y2-y1)
        return 0
    abiertos=[(h(inicio), inicio)]; padres={inicio:None}; visitados=set()
    print("Greedy pasos:")
    while abiertos:
        abiertos.sort(key=lambda x:x[0]); _, u = abiertos.pop(0)
        camino_u=[]
        node=u
        while node:
            camino_u.insert(0,node)
            node=padres[node]
        print(" -> ".join(camino_u))
        if u==meta:
            return camino_u, len(camino_u)-1
        visitados.add(u)
        for v,_ in grafo.get(u,[]):
            if v in visitados or any(v==n for _,n in abiertos): continue
            padres[v]=u; abiertos.append((h(v),v))
    return None, None


def busquedaCostoUniforme(grafo, inicio, meta):
    heap=[(0,inicio)]; padres={inicio:None}; costos={inicio:0}
    print("UCS pasos:")
    while heap:
        cost,u=heapq.heappop(heap)
        camino_u=[]; node=u
        while node:
            camino_u.insert(0,node); node=padres[node]
        print(f"{' -> '.join(camino_u)} (costo={cost})")
        if u==meta: return camino_u, cost
        for v,w in grafo.get(u,[]):
            nc=cost+w
            if v not in costos or nc<costos[v]:
                costos[v]=nc; padres[v]=u; heapq.heappush(heap,(nc,v))
    return None, None

# ----------------------------------
# Menú interactivo
# ----------------------------------

def print_resultado(res):
    if res and res[0]:
        path,c=res; print(f"Resultado: {' -> '.join(path)} | Costo={c}")
    else: print("No se encontró camino.")


def menu():
    ruta=r'C:\Users\Jose Guadalupe\OneDrive\Documentos\Octavo-semestre\IA\Proyecto+1\grafo.txt'
    grafo,coords=leer_grafo_desde_archivo(ruta)
    graficar_grafo(grafo,coords)
    root=input("Nodo raíz: ")
    graficar_grafo(grafo,coords,root)
    while True:
        print("\n=== MENÚ ===")
        for i,opt in enumerate(["Búsqueda en Anchura (BFS)",
            "Profundización Iterativa (IDDFS)",
            "Búsqueda Ávara (Greedy)",
            "Búsqueda en Profundidad (DFS)",
            "Costo Uniforme (UCS)"]): print(f"{i+1}. {opt}")
        print("0. Salir")
        op=input("Opción: ")
        if op=='0': break
        meta=input("Nodo meta: ")
        if op=='1': res=busquedaAmplitud(grafo,root,meta)
        elif op=='2': res=busquedaProfundidadIterativa(grafo,root,meta)
        elif op=='3': res=busquedaAvara(grafo,coords,root,meta)
        elif op=='4': res=busquedaProfundidad(grafo,root,meta)
        elif op=='5': res=busquedaCostoUniforme(grafo,root,meta)
        else: print("Inválido"); continue
        print_resultado(res);
        input("Enter para continuar")
    print("Adiós")

if __name__=='__main__': menu()
