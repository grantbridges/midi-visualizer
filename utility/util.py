from common import RGB

class Util:
    def __new__(cls):
        raise TypeError("Util is static")
    
    @staticmethod
    def invert_color(color: RGB) -> RGB:
        r, g, b = color
        return (255 - r, 255 - g, 255 - b)
    
    @staticmethod
    def contrast_color(color: RGB) -> RGB:
        r, g, b = color
        # perceived brightness
        brightness = (0.299 * r) + (0.587 * g) + (0.114 * b)
        return (0, 0, 0) if brightness > 160 else (255, 255, 255)