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
    
    @staticmethod
    def clamp(val, min_val, max_val):
        return max(min_val, min(val, max_val))
    
    @staticmethod
    def is_equal(val, check_val, precision = 0.0001):
        return abs(val - check_val) <= precision

    @staticmethod
    def internal_to_display(
        value: float,
        internal_min: float,
        internal_max: float,
        display_min: float,
        display_max: float,
    ) -> float:
        if internal_max == internal_min:
            raise ValueError("internal_max and internal_min cannot be equal")

        t = (value - internal_min) / (internal_max - internal_min)
        return display_min + t * (display_max - display_min)

    @staticmethod
    def display_to_internal(
        value: float,
        display_min: float,
        display_max: float,
        internal_min: float,
        internal_max: float,
    ) -> float:
        if display_max == display_min:
            raise ValueError("display_max and display_min cannot be equal")

        t = (value - display_min) / (display_max - display_min)
        return internal_min + t * (internal_max - internal_min)