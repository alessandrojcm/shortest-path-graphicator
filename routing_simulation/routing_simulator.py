import sys

from PyQt5.QtWidgets import (QApplication, QDesktopWidget)

from routing_simulation.gui.main_window import RoutingSimulator


def main():
    application = QApplication(sys.argv)
    window = RoutingSimulator()
    desktop = QDesktopWidget().availableGeometry()
    width = (desktop.width() - window.width()) / 2
    height = (desktop.height() - window.height()) / 2
    window.show()
    window.move(width, height)
    sys.exit(application.exec_())
