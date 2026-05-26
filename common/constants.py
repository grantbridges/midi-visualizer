class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # app props
    APP_NAME = "MIDI Visualizer"

    # animation window constants
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 900

    # visual
    PRIMARY_FONT = 'Arial'