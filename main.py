import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow

# create main window and start
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Visualizer")
    app.setApplicationDisplayName("MIDI Visualizer")
    app.setOrganizationName("Grant Bridges")
    editor = MainWindow()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()