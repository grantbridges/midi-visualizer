import xml.etree.ElementTree as ET

from models.vis_config import VisConfig

class FileUtil:
    @staticmethod
    def read_vis_config_from_xml(filepath: str):
        tree = ET.parse("config.xml")
        root = tree.getroot()

        display = root.find("Display")
        show_playhead = display.get("ShowPlayhead") == "true"
        bg_color = tuple(map(int, display.get("BackgroundColor").split(",")))

        # Tracks
        tracks = []
        for t in root.find("Tracks").findall("Track"):
            name = t.get("name")
            color = tuple(map(int, t.get("color").split(",")))
            alpha = int(t.get("alpha"))
            bar_height = int(t.get("barHeight"))

            tracks.append({
                "name": name,
                "color": color,
                "alpha": alpha,
                "bar_height": bar_height
            })
    
    @staticmethod
    def write_vis_config_to_xml(visConfig: VisConfig):
        import xml.etree.ElementTree as ET

    @staticmethod
    def _tuple_to_str(t):
        return ",".join(map(str, t))
    
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

    @staticmethod
    def write_vis_config_to_xml(config: VisConfig, path: str):
        root = ET.Element("VisConfig")
        root.set("bgColor", FileUtil._tuple_to_str(config.bg_color))

        tracks_el = ET.SubElement(root, "Tracks")

        for track in config.tracks:
            t_el = ET.SubElement(tracks_el, "Track")
            t_el.set("name", track.name)
            t_el.set("color", FileUtil._tuple_to_str(track.color))
            t_el.set("barHeight", str(track.bar_height))
            t_el.set("pps", str(track.bar_pixels_per_second))

        FileUtil._indent(root)

        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)