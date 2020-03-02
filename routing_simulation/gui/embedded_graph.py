from functools import partial

import matplotlib.pyplot as plt
import networkx as nx
from pubsub import pub
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from routing_simulation.models.network import network_setup
from routing_simulation.gui.log.log import Log
from routing_simulation.gui.send_packet_window.send_packet_window import SendPacketWindow
from routing_simulation.utils import patch_resource, items_spy


# From: https://stackoverflow.com/questions/35328916/embedding-a-networkx-graph-into-pyqt-widget


class EmbeddedGraph(QWidget):
    NumButtons = {
        'random_network': 'Red aleatoria',
        'send_package': 'Enviar paquete',
        'start_simulation': 'Iniciar simulación'
    }
    IDLE = 'blue'
    SELECTED = 'red'
    DISABLED = 'gray'

    def __init__(self):
        super(EmbeddedGraph, self).__init__()
        font = QFont()
        self.network = None
        self.log = Log()
        self.data = None
        self.pos = None

        font.setPointSize(16)
        pub.subscribe(self.__paint_path, 'links')
        pub.subscribe(self.set_package, 'send_package')
        pub.subscribe(self.from_dotfile, 'load_dotfile')
        pub.subscribe(self.load_csv, 'load_csv')

        self.initUI()
        self.__setup_network()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)
        self.createVerticalGroupBox()
        self.pos = None

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.verticalGroupBox)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        grid.addWidget(self.canvas, 0, 1, 9, 9)
        grid.addLayout(buttonLayout, 0, 0)

        self.show()

    def createVerticalGroupBox(self):
        self.verticalGroupBox = QGroupBox()

        layout = QVBoxLayout()
        for k, v in self.NumButtons.items():
            button = QPushButton(v)
            button.setObjectName(k)
            layout.addWidget(button)
            layout.setSpacing(10)
            self.verticalGroupBox.setLayout(layout)
            button.clicked.connect(self.submitCommand)
        self.verticalGroupBox.findChild(QPushButton, 'start_simulation').setEnabled(False)
        self.verticalGroupBox.findChild(QPushButton, 'send_package').setEnabled(False)

    def submitCommand(self):
        eval('self.' + str(self.sender().objectName()) + '()')

    def random_network(self):
        self.network.init_random_graph()
        self.pos = nx.spring_layout(self.network.topology)
        self.__draw_network()
        self.verticalGroupBox.findChild(QPushButton, 'send_package').setEnabled(True)

    def from_dotfile(self, file):
        try:
            self.network.from_pydot(file)
        except Exception as err:
            print(err)
            self.__error_message(
                'Error cargando archivo DOT, por favor verifique que cada arista tenga peso (con la propiedad label)')
            return
        self.pos = nx.random_layout(self.network.topology)
        self.__draw_network()
        self.verticalGroupBox.findChild(QPushButton, 'send_package').setEnabled(True)

    def load_csv(self, file):
        try:
            self.network.from_csv(file)
        except Exception as err:
            print(err)
            self.__error_message(
                'Error cargando archivo csv, por favor verifique que está de la forma origen,destino,peso')
            return
        self.pos = nx.random_layout(self.network.topology)
        self.__draw_network()
        self.verticalGroupBox.findChild(QPushButton, 'send_package').setEnabled(True)

    def send_package(self):
        SendPacketWindow(self.network.topology.number_of_nodes()).show()

    def set_package(self, data):
        from networkx import bellman_ford_path, NetworkXNoPath, NodeNotFound
        self.data = data
        origin, destination, _ = data
        try:
            bellman_ford_path(self.network.topology, origin, destination)
        except NetworkXNoPath:
            self.__error_message('No hay ruta entre nodo {o} y nodo {d}'.format(o=origin, d=destination))
            return
        except NodeNotFound:
            self.__error_message('Nodo de origen o destino no está en el grafo.')
            return

        self.verticalGroupBox.findChild(QPushButton, 'start_simulation').setEnabled(True)
        self.paint_nodes()

    def paint_nodes(self):
        origin, destination, payload = self.data
        node_cols = [self.IDLE if i != origin and i != destination else self.SELECTED for i in
                     self.network.topology.nodes()]
        self.__draw_network(node_cols)
        self.log.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_simulation(self):
        self.paint_nodes()
        origin, destination, payload = self.data

        self.log.clear()
        self.network.set_frame(payload, origin, destination)
        self.network.start()

    def __draw_network(self, node_colors=None):
        self.figure.clf()
        labels = {k: str(v) for k, v in nx.get_edge_attributes(self.network.topology, 'weight').items()}
        if not node_colors:
            nx.draw(self.network.topology, pos=self.pos, with_labels=True)
        else:
            nx.draw(self.network.topology, pos=self.pos, node_color=node_colors, with_labels=True)
        nx.draw_networkx_edge_labels(self.network.topology, pos=self.pos, edge_labels=labels)
        self.canvas.draw_idle()

    def __patch_resource(self):
        monitor = partial(items_spy, lambda d: pub.sendMessage('links', data=d))

        patch_resource(self.network.available_links, post=monitor)

    def __paint_path(self, data):
        nx.draw_networkx_edges(self.network.topology, self.pos, data, edge_color=self.SELECTED)
        nx.draw_networkx_nodes(self.network.topology, self.pos, list(set([node for edge in data for node in edge])),
                               node_color=self.SELECTED)
        self.canvas.draw_idle()

    def __print_messages(self):
        while True:
            with self.network.log.get() as rq:
                message = yield rq
                if message is not None:
                    self.log.append(message)

    def __setup_network(self):
        graph = None
        if self.network is not None and self.network.topology is not None:
            graph = self.network.topology
        self.network = network_setup(True)
        self.network.env.process(self.__print_messages())
        if graph:
            self.network.topology = graph
        self.__patch_resource()

    def __error_message(self, message):
        message_box = QMessageBox()
        message_box.setText(message)
        message_box.setWindowTitle('Error')
        message_box.setIcon(QMessageBox.Warning)
        message_box.setStandardButtons(QMessageBox.Close)
        message_box.exec_()
