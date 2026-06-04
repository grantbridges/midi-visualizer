class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # app props
    APP_NAME = "MIDI Visualizer"

    PROJECT_EXT = "mvp" # midi visualizer project

    # animation window constants
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 900

    # visual
    PRIMARY_FONT = 'Arial'