class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # app props
    APP_NAME = "MIDI Visualizer"

    PROJECT_EXT = "mvp" # midi visualizer project

    SCREEN_MIN_WIDTH = 800
    SCREEN_MIN_HEIGHT = 775

    # visual
    PRIMARY_FONT = 'Arial'