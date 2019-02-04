import os

HEAD_TEXT = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Folder>
\t<name>file-name-here</name>
"""

TAIL_TEXT = """</Folder>
</kml>"""

POINT_TEMPLATE = """\t<Placemark>
\t\t<name>name-here</name>
\t\t<description>description-here</description>
\t\t<LookAt>
\t\t\t<longitude>lon-here</longitude>
\t\t\t<latitude>lat-here</latitude>
\t\t\t<altitude>0</altitude>
\t\t\t<heading>0</heading>
\t\t\t<tilt>0</tilt>
\t\t\t<range>2000</range>
\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
\t\t</LookAt>
\t\t<Point>
\t\t\t<coordinates>lon-here, lat-here</coordinates>
\t\t</Point>
\t</Placemark>
"""


class Point:
    def __init__(self, name, text, lon, lat):
        assert type(name) == str and name != ""
        assert type(text) == str
        assert type(lon) == float
        assert type(lat) == float

        self._name = name
        self._text = text
        self._lon = lon
        self._lat = lat

    def gen_kml_text(self):
        base = POINT_TEMPLATE
        base = base.replace("name-here", self._name)
        base = base.replace("description-here", self._text)
        base = base.replace("lon-here", str(round(self._lon, 10)))
        base = base.replace("lat-here", str(round(self._lat, 10)))
        return base

    def get_name(self):
        return self._name

    def get_text(self):
        return self._text

    def get_lon(self):
        return self._lon

    def get_lat(self):
        return self._lat


class Creator:
    def __init__(self, output_path):
        if not output_path.upper().endswith("KML"):
            output_path += ".kml"

        self._output_path = output_path
        self._points = []

    def get_num_points(self):
        return len(self._points)

    def set_output_path(self, new_path):
        self._output_path = new_path

    def get_output_path(self):
        return self._output_path

    def feed_points(self, points):
        if type(points) in (tuple, list):
            pass
        else:
            points = [points]

        for i, p in enumerate(points):
            if type(p) != Point:
                print("Skipping object at index {}, type {} is not valid.".format(i, type(p)))
            else:
                self._points.append(p)

    def output(self, output_path="DEFAULT"):
        if output_path == "DEFAULT":
            output_path = self._output_path

        if not os.path.exists(os.path.dirname(output_path)):
            os.mkdir(os.path.dirname(output_path))

        with open(output_path, "w") as fh:
            fh.write(HEAD_TEXT.replace("file-name-here", os.path.basename(output_path).replace(".kml", "")))
            for p in self._points:
                fh.write(p.gen_kml_text())
            fh.write(TAIL_TEXT)
