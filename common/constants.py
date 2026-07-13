class Const:
    def __new__(cls):
        raise TypeError("Const is static")
    
    # app props
    ORG_NAME = "Grant Bridges"
    APP_NAME = "Illustri MIDI Studio"
    APP_ALT_NAME = "illustri"
    VERSION = "1.0.0-beta"
    BUILD_DATE = "July 12, 2026"

    PROJECT_EXT = "mvp" # #TODO ipr illustri project

    SCREEN_INITIAL_WIDTH = 1200
    SCREEN_INITIAL_HEIGHT = 900
    SCREEN_MIN_WIDTH = 800
    SCREEN_MIN_HEIGHT = 775

    # visual
    PRIMARY_FONT = 'Arial'