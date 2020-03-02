from PyQt5 import QtWidgets, uic

from routing_simulation.utils import real_path


class Log(QtWidgets.QWidget):
    log: QtWidgets.QPlainTextEdit

    def __init__(self):
        super(Log, self).__init__()
        uic.loadUi(real_path('log.ui', __file__), self)
        self.log = self.findChild(QtWidgets.QPlainTextEdit, 'log')
        self.setWindowTitle('Log de mensajes')

    def append(self, text):
        self.log.appendPlainText(text)

    def clear(self):
        self.log.clear()

    def has_text(self):
        return len(self.log.toPlainText().replace(' ', '')) != 0
