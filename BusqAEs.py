import math

def leer_grafo_y_coordenadas(ruta):
    grafo = {}
    coordenadas = {}
    modo = None

    with open(ruta, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue
            elif linea.startswith("NODE_COORDS:"):
                modo = "coordenadas"
                continue
            elif linea.startswith("EDGES:"):
                modo = "aristas"
                continue
            elif linea.startswith("ROOT:"):
                continue  # puedes capturarlo si lo necesitas

            if modo == "coordenadas" and ':' in linea:
                nodo, coord = linea.split(':')
                x, y = coord.strip().strip('()').split(',')
                coordenadas[nodo.strip()] = (float(x), float(y))

            elif modo == "aristas" and '-' in linea:
                nodos, peso = linea.split(':')
                origen, destino = nodos.strip().split('-')
                peso = float(peso.strip())
                grafo.setdefault(origen, []).append((destino, peso))
                grafo.setdefault(destino, []).append((origen, peso))  # si es no dirigido

    return grafo, coordenadas

def calcular_heuristica(coordenadas, objetivo):
    heuristica = {}
    x_goal, y_goal = coordenadas[objetivo]
    for nodo, (x, y) in coordenadas.items():
        heuristica[nodo] = math.sqrt((x - x_goal)**2 + (y - y_goal)**2)
    return heuristica

def busqueda_a_estrella(grafo, heuristica, nodo_inicio, nodo_meta):
    nodos = [(nodo_inicio, 0)]  # (nodo, costo acumulado g(n))
    padres = {nodo_inicio: None}
    costos = {nodo_inicio: 0}
    visitados = set()

    while nodos:
        nodos.sort(key=lambda x: costos[x[0]] + heuristica[x[0]])
        print("Lista de nodos con f(n):", [(n, round(costos[n] + heuristica[n], 2)) for n, _ in nodos])
        nodo, _ = nodos.pop(0)

        if nodo in visitados:
            continue

        print("Expandimos:", nodo)
        visitados.add(nodo)

        if nodo == nodo_meta:
            camino = []
            actual = nodo
            while actual is not None:
                camino.insert(0, actual)
                actual = padres[actual]
            return camino, costos[nodo]

        for hijo, peso in grafo.get(nodo, []):
            nuevo_costo = costos[nodo] + peso
            if (hijo not in costos or nuevo_costo < costos[hijo]) and hijo not in visitados:
                costos[hijo] = nuevo_costo
                padres[hijo] = nodo
                nodos.append((hijo, nuevo_costo))

    return None, None

# Main
grafo, coordenadas = leer_grafo_y_coordenadas("grafo.txt")
print("Grafo:\n", grafo)
print("Coordenadas:\n", coordenadas)

heuristica = calcular_heuristica(coordenadas, 'F')
print("Heurística (distancia euclidiana a J):\n", heuristica)

camino, costo = busqueda_a_estrella(grafo, heuristica, 'A', 'F')

if camino:
    print("Camino encontrado:", camino)
    print(f"Costo total: {costo}")
else:
    print("No se encontró un camino.")
