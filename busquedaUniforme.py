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
                continue  # Ignoramos la raíz aquí, puedes capturarla si la necesitas

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

def busqueda_costo_uniforme(grafo, nodo_inicio, nodo_meta):
    nodos = [(nodo_inicio, 0)]  # (nodo, costo acumulado)
    padres = {nodo_inicio: None}
    costos = {nodo_inicio: 0}
    visitados = set()

    while nodos:
        nodos.sort(key=lambda x: x[1])
        print("Lista de nodos con costo acumulado:", [(n, c) for n, c in nodos])
        nodo, costo_actual = nodos.pop(0)

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
            nuevo_costo = costo_actual + peso
            if hijo not in costos or nuevo_costo < costos[hijo]:
                costos[hijo] = nuevo_costo
                padres[hijo] = nodo
                if hijo not in visitados:
                    nodos.append((hijo, nuevo_costo))

    return None, None

# Main
grafo, coordenadas = leer_grafo_y_coordenadas("grafo.txt")
print("Grafo:\n", grafo)
print("Coordenadas:\n", coordenadas)

camino, costo = busqueda_costo_uniforme(grafo, 'A', 'F')

if camino:
    print("Camino encontrado:", camino)
    print(f"Costo total del camino: {costo}")
else:
    print("No se encontró un camino.")
