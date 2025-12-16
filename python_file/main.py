import sys

from PyQt6 import *
from PyQt6.QtWidgets import *


class Favorite_pizza(QMainWindow):
    def __int__(self):
        self.setWindowTitle("Favorite pizza")
        self.setGeometry(300, 300, 800, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window = Favorite_pizza()
    Window.show()
    sys.exit(app.exec())