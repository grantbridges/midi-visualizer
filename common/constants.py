class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # app props
    APP_NAME = "MIDI Visualizer"
    APP_ALT_NAME = "midi-vis"

    PROJECT_EXT = "mvp" # midi visualizer project

    SCREEN_INITIAL_WIDTH = 1200
    SCREEN_INITIAL_HEIGHT = 900
    SCREEN_MIN_WIDTH = 800
    SCREEN_MIN_HEIGHT = 775

    # visual
    PRIMARY_FONT = 'Arial'