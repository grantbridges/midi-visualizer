class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # animation window constants
    FPS = 24
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 900
    SCREEN_PADDING = 50
    TITLE = "Midi Visualizer"