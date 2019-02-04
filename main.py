import excel
import easygui
import OSGridConverter
import kml
import subprocess
import os

__title__ = "Cover Search Converter"


class NoDataFoundError(Exception):
    pass


class Loader:
    def __init__(self, file_path):
        self._path = file_path
        self._handle = None
        self._header_row = None
        self._header_names = None
        self._start_row = None
        self._cols = []
        self._customer_enq_ref = ""
        self._load()
        self._errors = []
        self._creator = kml.Creator(file_path.replace(".xls", ".kml"))

    def _load(self):
        self._handle = excel.OpenExcel(self._path)

    def run(self):
        try:
            self._find_headers()
        except NoDataFoundError:
            easygui.msgbox("Could not find any data!\n\nThe program will now close.")
            exit()

        self._decode_points()

        choices = ["Continue", "Change Output\nLocation", "Cancel"]
        resp = True
        while resp not in (choices[0], choices[2], None):
            msg = "Found headers:"
            msg += "\n" + ("¯" * len(msg))
            for h in self._header_names:
                msg += "\n" + h

            msg += """

Customer Enquiry Reference:
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
{}

{} point loaded.
{} errors.

Output Location:
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
{}""".format(self._customer_enq_ref,
             self._creator.get_num_points(),
             len(self._errors),
             self._creator.get_output_path())
            resp = easygui.buttonbox(msg, __title__, choices)

            if resp == choices[0]:
                self._creator.output()

            elif resp == choices[1]:
                new_path = easygui.filesavebox(default=self._creator.get_output_path(), filetypes=["*.kml"])
                if new_path is None:
                    pass
                else:
                    self._creator.set_output_path(new_path)
            else:
                exit()

            subprocess.Popen(r'explorer /select,"{}"'.format(self._creator.get_output_path()))

    def _find_headers(self):
        found = False
        pos = 0
        while not found and pos < self._handle.getRows():
            row_data = self._handle.read(pos)
            # If the row has at least 1/4 of the cells filled, assume it is the header row.
            if row_data.count("") <= len(row_data) * 0.75:
                found = True
            else:
                pos += 1

            for c in row_data:
                if type(c) == str and "customer enquiry reference" in c.lower():
                    self._customer_enq_ref = c.split(":")[1].strip()

        if found:
            cols = []
            header_names = []
            row_data = self._handle.read(pos)
            for c in range(len(row_data)):
                if row_data[c] != "" and type(row_data[c]) == str:
                    cols.append(c)
                    header_names.append(row_data[c].strip())

            self._header_row = pos
            self._header_names = header_names
            self._start_row = pos + 1
            self._cols = cols

        else:
            raise NoDataFoundError()

    def _decode_points(self):
        choices = list(self._header_names)
        msg = "Choose an attribute to be the name of the new points:"
        name_col = easygui.choicebox(msg, __title__, choices)
        if name_col is None:
            exit()
        else:
            choices.remove(name_col)
            name_col = self._cols[self._header_names.index(name_col)]
        msg = "Choose an attribute to act as the location of the new points:"
        pos_col = easygui.choicebox(msg, __title__, choices)
        if pos_col is None:
            exit()
        else:
            pos_col = self._cols[self._header_names.index(pos_col)]

        print("Starting with column {} as name and {} as pos.".format(name_col, pos_col))

        self._errors = []

        for pos in range(self._start_row, self._handle.getRows()):
            row_data = self._handle.read(pos)
            if row_data[name_col] != "":
                new_point = None
                try:
                    new_point = self._convert_row_to_point(row_data, name_col, pos_col)
                    print("Successfully converted")
                except Exception as e:
                    self._errors.append({"index": pos,
                                         "error_type": e})

                if new_point is not None:
                    self._creator.feed_points(new_point)

    def _convert_row_to_point(self, row_data, name_col, pos_col):
        attributes = {}
        name = ""
        pos_text = ""
        for c in self._cols:
            attributes[self._header_names[self._cols.index(c)]] = row_data[c]
            if c == name_col:
                name = row_data[c]
            if c == pos_col:
                pos_text = row_data[c]
        text = ""
        for h in self._header_names:
            a = attributes[h]
            if not h.endswith(":"):
                h += ":"
            text += h + " " + str(a) + "\n"
        text = text.strip()

        grid_obj = OSGridConverter.grid2latlong(pos_text)

        return kml.Point(name, text, grid_obj.longitude, grid_obj.latitude)


default_path = os.path.join(os.environ["HOMEPATH"], "*.xls")
start_path = easygui.fileopenbox(default=default_path, filetypes=["*.xls", "*.*"])
if start_path is None:
    exit()
xls_loader = Loader(start_path)
xls_loader.run()
