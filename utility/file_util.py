import xml.etree.ElementTree as ET

class FileUtil:
    def __new__(cls):
        raise TypeError("FileUtil is static")

    @staticmethod
    def str_to_tuple(s):
        return tuple(map(int, s.split(",")))

    @staticmethod
    def tuple_to_str(t):
        return ",".join(map(str, t))
    
    @staticmethod
    def str_to_bool(value: str, default=False) -> bool:
        if value is None:
            return default
        return value.strip().lower() in ("true", "1", "yes")
    
    @staticmethod
    def bool_to_str(value: bool):
        return str(value).lower()
    
    @staticmethod
    def xml_indent(elem: ET.Element, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for child in elem:
                FileUtil.xml_indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i