class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # animation window constants
    FPS = 24
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SCREEN_PADDING = 50
    TITLE = "Midi Visualizer"