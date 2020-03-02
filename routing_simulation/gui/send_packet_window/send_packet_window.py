import numpy as np
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QLineEdit, QSpinBox, QDialog
from pubsub import pub

from routing_simulation.utils import real_path, check_binary

# Simulation data window
class SendPacketWindow(QDialog):
    origin: QSpinBox
    destination: QSpinBox
    packet: QLineEdit
    buttons: QtWidgets.QDialogButtonBox

    def __init__(self, max_node: int):
        super(SendPacketWindow, self).__init__()
        uic.loadUi(real_path('send_packet_window.ui', __file__), self)
        self.setWindowTitle('Data configuration')
        self.__init_widgets(max_node)

    def __init_widgets(self, max_node):
        self.origin = self.findChild(QSpinBox, 'origin')
        self.origin.setMinimum(0)

        self.destination = self.findChild(QSpinBox, 'destination')
        self.destination.setMinimum(0)

        self.packet = self.findChild(QLineEdit, 'packet')
        self.packet.setMaxLength(8)

        self.buttons = self.findChild(QtWidgets.QDialogButtonBox, 'options')
        self.buttons.accepted.connect(self.__check_validity)
        self.buttons.rejected.connect(lambda: self.close())

    def __check_validity(self):
        payload = np.array([int(bit) for bit in list(self.packet.text())])

        if payload.size == 0:
            return self.span_warning('You must enter the payload')

        if self.origin.value() >= self.origin.maximum() or self.destination.value() >= self.destination.maximum():
            return self.span_warning('Invalid node')

        if not check_binary(payload):
            return self.span_warning('Payload not in binary')

        if payload.size > self.packet.maxLength():
            return self.span_warning('Payload must be 8 bit tops')

        if self.origin.value() == self.destination.value():
            return self.span_warning('Origin can\'t be the same as the destination')

        pub.sendMessage('send_package', data=(self.origin.value(), self.destination.value(), payload))
        self.close()

    def span_warning(self, message: str):
        message_box = QtWidgets.QMessageBox()
        message_box.setText(message)
        message_box.setWindowTitle('Warning')
        message_box.setIcon(QtWidgets.QMessageBox.Warning)
        message_box.setStandardButtons(QtWidgets.QMessageBox.Close)
        message_box.exec_()
