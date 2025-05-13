#NOTA para correr esta interfaz se necesitan intalar las sig cosas:
# pip install matplotlib
# pip install networkx
# pip install PyQt5

# Falta incluir lo siguiete:
# 1. Al cargar un archivo antes de realizar la busqueda incluir la lógica para asegurarse de que tiene el formato correcto.
# 2. Mostrar la salida del algoritmo en el contenedor de texto, la logica y los pasos, etc, que cada algoritmo realiza para llegar al final.
# 3. Mostrar el grafo correspodiente del algoritmo de búsqueda al dar click en el botón SOLO una vez que se realice la búsqueda.
# 4. Que todo ya sea funcional, que se jalen los archivos correspondienttes a la interfaz principal. 

from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QComboBox, QLabel, QTextEdit,
    QPushButton, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
import sys
import matplotlib.pyplot as plt
import networkx as nx

class BusquedaGrafoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Buscador de Grafos")
        self.setGeometry(200, 200, 700, 600)
        self.setStyleSheet(self.estilos_qss())

        self.archivo_cargado = None
        self.btn_mostrar_grafo = None

        self.initUI()

    def initUI(self):
        self.layout_principal = QVBoxLayout()
        self.layout_principal.setAlignment(Qt.AlignCenter)
        self.layout_principal.setContentsMargins(40, 20, 40, 20)

        self.layout_principal.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.lbl_archivo = QLabel("📂 No se ha cargado ningún archivo")
        self.lbl_archivo.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(self.lbl_archivo)

        self.layout_principal.addSpacing(15)

        self.btn_cargar = QPushButton("Cargar archivo de grafo")
        self.btn_cargar.clicked.connect(self.cargar_archivo)
        self.layout_principal.addWidget(self.btn_cargar, alignment=Qt.AlignCenter)

        self.layout_principal.addSpacing(15)

        self.combo_buscador = QComboBox()
        self.combo_buscador.addItem("Selecciona un algoritmo de búsqueda")
        self.combo_buscador.addItems(["Profundidad", "Amplitud", "A*", "Costo uniforme", "Voraz"])
        self.combo_buscador.currentIndexChanged.connect(self.habilitar_boton)
        self.layout_principal.addWidget(self.combo_buscador, alignment=Qt.AlignCenter)

        self.layout_principal.addSpacing(15)

        self.btn_buscar = QPushButton("🔍 Realizar búsqueda")
        self.btn_buscar.setEnabled(False)
        self.btn_buscar.clicked.connect(self.realizar_busqueda)
        self.layout_principal.addWidget(self.btn_buscar, alignment=Qt.AlignCenter)

        self.layout_principal.addSpacing(25)

        self.salida_texto = QTextEdit()
        self.salida_texto.setReadOnly(True)
        self.salida_texto.setPlaceholderText("Aquí se mostrarán los resultados de la búsqueda o salidas de otros programas...")
        self.layout_principal.addWidget(self.salida_texto)

        self.layout_principal.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(self.layout_principal)

    def cargar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de grafo", "", "Text Files (*.txt)")
        if archivo:
            self.archivo_cargado = archivo
            self.lbl_archivo.setText(f"✅ Archivo cargado: {archivo.split('/')[-1]}")
        else:
            self.lbl_archivo.setText("⚠️ No se ha cargado ningún archivo")

    def habilitar_boton(self):
        self.btn_buscar.setEnabled(self.combo_buscador.currentIndex() != 0)

    def realizar_busqueda(self):
        algoritmo = self.combo_buscador.currentText()
        archivo = self.archivo_cargado

        resultado_simulado = f"""
Algoritmo seleccionado: {algoritmo}
Archivo usado: {archivo if archivo else 'Ninguno'}

Simulación de salida:
Nodo A, Profundidad: 0
Nodo B, Profundidad: 1
Nodo C, Profundidad: 2
...
        """
        self.salida_texto.setText(resultado_simulado)

        # Mostrar botón "Mostrar grafo" después de ejecutar búsqueda
        if not self.btn_mostrar_grafo:
            self.btn_mostrar_grafo = QPushButton("📊 Mostrar grafo")
            self.btn_mostrar_grafo.clicked.connect(self.mostrar_grafo)
            self.layout_principal.addWidget(self.btn_mostrar_grafo, alignment=Qt.AlignCenter)

    def mostrar_grafo(self):
        G = nx.DiGraph()
        G.add_edges_from([
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "E"),
            ("D", "F"),
            ("E", "G")
        ])

        pos = nx.spring_layout(G)
        plt.figure(figsize=(6, 4))
        nx.draw(G, pos, with_labels=True, node_color="#4CAF50", font_weight='bold', edge_color='gray', node_size=700)
        plt.title("Grafo de ejemplo (simulado)")
        plt.show()

    def estilos_qss(self):
        return """
            QWidget {
                background-color: #f7f9fc;
                font-family: Arial;
                font-size: 14px;
            }

            QLabel {
                color: #333;
                font-weight: bold;
            }

            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                min-width: 220px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }

            QComboBox {
                padding: 6px;
                border-radius: 5px;
                border: 1px solid #ccc;
                min-width: 250px;
            }

            QComboBox:focus {
                border-color: #4CAF50;
            }

            QTextEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                padding: 10px;
                min-height: 150px;
                font-family: Consolas, monospace;
            }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = BusquedaGrafoApp()
    ventana.show()
    sys.exit(app.exec_())
