from common import RGB, Color

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
    def mix_colors(a: RGB, b: RGB, amount: float) -> RGB:
        """
        amount: 0.0 = all a
                1.0 = all b
        """
        amount = max(0.0, min(1.0, amount))

        return (
            Util.clamp(int(a[0] + (b[0] - a[0]) * amount), 0, 255),
            Util.clamp(int(a[1] + (b[1] - a[1]) * amount), 0, 255),
            Util.clamp(int(a[2] + (b[2] - a[2]) * amount), 0, 255),
        )

    @staticmethod
    def lighten_color(color: RGB, amount: float) -> RGB:
        return Util.mix_colors(color, Color.WHITE, amount)

    @staticmethod
    def darken_color(color: RGB, amount: float) -> RGB:
        return Util.mix_colors(color, Color.BLACK, amount)
    
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
    
    @staticmethod
    def swap(arr, first_index: int, second_index: int):
        '''
        Swaps two entries in an array in place
        '''
        arr[first_index], arr[second_index] = arr[second_index], arr[first_index]