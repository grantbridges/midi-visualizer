import xml.etree.ElementTree as ET
from models import VisConfig, Track

class FileUtil:
    def __new__(cls):
        raise TypeError("FileUtil is static")

    @staticmethod
    def read_vis_config_from_xml(path: str) -> VisConfig:
        tree = ET.parse(path)
        root = tree.getroot()

        bg_color = FileUtil._str_to_tuple(root.get("bgColor"))
        play_audio = FileUtil._str_to_bool(root.get("playAudio"))

        config = VisConfig(bg_color=bg_color, play_audio=play_audio)

        for t_el in root.find("Tracks").findall("Track"):
            track = Track(
                name=t_el.get("name"),
                visible=FileUtil._str_to_bool(t_el.get("visible")),
                color=FileUtil._str_to_tuple(t_el.get("color")),
                bar_height=int(t_el.get("barHeight")),
                bar_pixels_per_second=int(t_el.get("pps")),
            )

            config.tracks.append(track)

        return config

    @staticmethod
    def write_vis_config_to_xml(config: VisConfig, path: str):
        root = ET.Element("VisConfig")
        root.set("bgColor", FileUtil._tuple_to_str(config.bg_color))
        root.set("playAudio", FileUtil._bool_to_str(config.play_audio))

        tracks_el = ET.SubElement(root, "Tracks")

        for track in config.tracks:
            t_el = ET.SubElement(tracks_el, "Track")
            t_el.set("name", track.name)
            t_el.set("visible", FileUtil._bool_to_str(track.visible))
            t_el.set("color", FileUtil._tuple_to_str(track.color))
            t_el.set("barHeight", str(track.bar_height))
            t_el.set("pps", str(track.bar_pixels_per_second))

        FileUtil._indent(root)

        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    # Helpers
    @staticmethod
    def _str_to_tuple(s):
        return tuple(map(int, s.split(",")))

    @staticmethod
    def _tuple_to_str(t):
        return ",".join(map(str, t))
    
    @staticmethod
    def _str_to_bool(value: str, default=False) -> bool:
        if value is None:
            return default
        return value.strip().lower() in ("true", "1", "yes")
    
    @staticmethod
    def _bool_to_str(value: bool):
        return str(value).lower()
    
    @staticmethod
    def _indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for child in elem:
                FileUtil._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i