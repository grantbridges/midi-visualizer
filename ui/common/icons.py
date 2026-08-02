import qtawesome as qta

class Icons:
    '''
    Utility class for instantiating new icon objects (prefer mdi6)
    Run `qta-browser` in terminal to browse options
    '''
    def __new__(cls):
        raise TypeError("Icons is static")
    
    @staticmethod
    def play():
        return Icons._get_icon("mdi6.play")
    
    @staticmethod
    def pause():
        return Icons._get_icon("mdi6.pause")
    
    @staticmethod
    def stop():
        return Icons._get_icon("mdi6.stop")
    
    @staticmethod
    def audio():
        return Icons._get_icon("mdi6.volume-medium")
    
    @staticmethod
    def muted():
        return Icons._get_icon("mdi6.volume-variant-off")
        
    @staticmethod
    def rewind():
        return Icons._get_icon("mdi6.rewind")
    
    @staticmethod
    def fast_fwd():
        return Icons._get_icon("mdi6.fast-forward")
    
    @staticmethod
    def skip_back():
        return Icons._get_icon("mdi6.skip-previous")
    
    @staticmethod
    def skip_fwd():
        return Icons._get_icon("mdi6.skip-next")
    
    @staticmethod
    def gear():
        return Icons._get_icon("mdi6.cog")
    
    @staticmethod
    def loop():
        return Icons._get_icon("mdi6.arrow-u-left-top")
    
    @staticmethod
    def arrow_right_thin():
        return Icons._get_icon("mdi6.arrow-right-thin")
    
    @staticmethod
    def arrow_up_bold():
        return Icons._get_icon("mdi6.arrow-up-bold")
    
    @staticmethod
    def arrow_down_bold():
        return Icons._get_icon("mdi6.arrow-down-bold")
    
    @staticmethod
    def trash_can():
        return Icons._get_icon("mdi6.trash-can")
    
    @staticmethod
    def ellipsis():
        return Icons._get_icon("mdi6.dots-horizontal")
    
    @staticmethod
    def image_outline():
        return Icons._get_icon("mdi6.image-outline")
    
    @staticmethod
    def music_note():
        return Icons._get_icon("mdi6.music-note")
    
    @staticmethod
    def music():
        return Icons._get_icon("mdi6.music")
    
    @staticmethod
    def magic():
        return Icons._get_icon("mdi6.magic-staff")
    
    @staticmethod
    def group():
        return Icons._get_icon("mdi6.group")
    
    @staticmethod
    def menu():
        return Icons._get_icon("mdi6.menu")
    
    @staticmethod
    def _get_icon(name: str):
        return qta.icon(
            name,
            color="#dddddd",
            color_active="#ffffff",
            color_disabled="#777777"
        )