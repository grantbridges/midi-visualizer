import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow

# create main window and start
def main():
    q_app = QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
    sys.exit(q_app.exec())

if __name__ == "__main__":
    main()