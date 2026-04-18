class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # animation window constants
    FPS = 60
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SCREEN_PADDING = 50
    TITLE = "Midi Visualizer"

    # visual
    PRIMARY_FONT = 'freesansbold.ttf'