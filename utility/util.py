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
    def swap(arr, first_index: int, second_index: int):
        '''
        Swaps two entries in an array in place
        '''
        arr[first_index], arr[second_index] = arr[second_index], arr[first_index]

    @staticmethod
    def format_ms(ms: int) -> str:
        '''
        Formats time string as mm:ss
        '''
        total_seconds = max(0, ms // 1000)

        minutes = total_seconds // 60
        seconds = total_seconds % 60

        return f"{minutes:02}:{seconds:02}"

    @staticmethod
    def format_elapsed_time(elapsed_sec: float) -> str:
        # Format as MM:SS.milliseconds
        minutes, seconds = divmod(elapsed_sec, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(minutes):02d}:{int(seconds):02d}.{milliseconds:03d}"

    @staticmethod
    def truncate(text: str, max_length: int = 100) -> str:
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text