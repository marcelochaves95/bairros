from PyQt6.QtWidgets import QApplication
from bairros.view import Bairros
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Bairros()
    window.show()
    sys.exit(app.exec())