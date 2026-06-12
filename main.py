import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow
from models import user_settings
from media import audio_provider, video_provider

# create main window and start
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Visualizer")
    
    # initial load of user settings
    user_settings.load()

    # initialize global media providers
    audio_provider.init()
    video_provider.init()

    # start UI
    editor = MainWindow()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()