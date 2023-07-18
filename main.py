import sys

from PySide2.QtWidgets import QApplication
from src.front.client import MainWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle('Fusion')
    w = MainWidget()
    w.main_ui.show()
    sys.exit(app.exec_())