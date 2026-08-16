class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # app props
    ORG_NAME = "Grant Bridges"
    APP_NAME = "Illustri MIDI Studio"
    APP_NAME_SHORT = "Illustri"
    APP_ALT_NAME = "illustri"

    PROJECT_EXT = "ipr" # illustri project

    SCREEN_INITIAL_WIDTH = 1000
    SCREEN_INITIAL_HEIGHT = 800
    SCREEN_MIN_WIDTH = 800
    SCREEN_MIN_HEIGHT = 600

    # visual
    PRIMARY_FONT = 'Arial'