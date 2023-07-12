import customtkinter
import os
import configparser
from tkinter import filedialog
import re

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"


class App(customtkinter.CTk):
    config = configparser.ConfigParser()
    configFileName = "/tc_parser.ini"
    configFilePath = os.getcwd() + configFileName
    lastDir = r""
    file_to_parse = []
    temporary_file = []
    live_template_path = r""
    flag_print = True
    flag_fix = True
    current_file = ""
    WIDTH = 600
    HEIGHT = 700
    current_line = ""
    old_template = False

    options = ["Verify Coding",
               "Verify ASCII chars range",
               "Validation of headers",
               "Use of single quotes",
               "Not closed quotes",
               "Indentation of Steps",
               "Variables in Steps",
               "Excessive Spacebards",
               "Step finished with dot",
               "Not closed backets",
               "Binary operators correctness",
               "Semicolor termination",
               "Check imports",
               "Line length < 200",
               "While loop",
               "Bad practise naming",
               "Tabs not spaces",
               "General indentation",
               "Template updater"]

    def __init__(self):
        self.lastDir = self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "last directory")
        self.live_template_path = self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "template directory")
        super().__init__()
        # self.minsize(width=self.WIDTH, height=self.HEIGHT)
        self.title("TC Parser")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1, 2), weight=1)
        # ====================== header settings ======================
        self.header = customtkinter.CTkFrame(master=self)
        self.header.grid(row=0, column=0, sticky="we", padx=10, pady=(10, 0))

        self.header.grid_columnconfigure((0, 1), weight=1)
        self.select_catalog_button = customtkinter.CTkButton(master=self.header,
                                                             text="Select catalog",
                                                             command=self.select_catalog_event)

        self.select_catalog_button.grid(row=0, column=0, pady=(10, 10), padx=10, sticky="we")

        self.select_catalog_button = customtkinter.CTkButton(master=self.header,
                                                             text="Select file",
                                                             command=self.select_file_event)
        self.select_catalog_button.grid(row=0, column=1, pady=(10, 10), padx=10, sticky="we")

        # ====================== header settings ======================

        self.text_grid = customtkinter.CTkFrame(master=self)
        self.text_grid.grid(row=1, column=0, sticky="wesn", padx=10, pady=(10, 0))
        self.text_grid.grid_rowconfigure(0, weight=1)
        self.text_grid.grid_columnconfigure(0, weight=1)
        self.textbox = customtkinter.CTkTextbox(self.text_grid)
        self.textbox.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="wesn")

        # ====================== select section settings ======================

        self.select_grid = customtkinter.CTkFrame(master=self)
        self.select_grid.grid(row=2, column=0, sticky="wesn", padx=10, pady=(10, 0))
        self.checkbox_dict = {}
        for index, option_name in enumerate(self.options):
            checkbox = customtkinter.CTkCheckBox(master=self.select_grid, text=f"{option_name}", command=self.check_box_update_event)
            checkbox.grid(row=index // 3, column=index % 3, pady=10, padx=10, sticky="nwe")
            checkbox.select() if int(self.GetOptionFromCfg(self.configFilePath, section="DEFAULT", option=option_name)) else checkbox.deselect()
            self.checkbox_dict.update({option_name: checkbox})

        # ====================== footer section settings ======================

        self.footer_grid = customtkinter.CTkFrame(master=self)
        self.footer_grid.grid(row=3, column=0, sticky="swe", padx=10, pady=(10, 0))
        self.footer_grid.grid_columnconfigure(0, weight=1)
        self.select_catalog_button = customtkinter.CTkButton(master=self.footer_grid,
                                                             text="PARSE TEST CASE",
                                                             command=self.start_parse)
        self.select_catalog_button.grid(row=0, column=0, pady=(10, 10), padx=10, sticky="wesn")

    def check_box_update_event(self):
        pass


    def on_closing(self):
        for key_checkbox, item_checkbox in self.checkbox_dict.items():
            self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option=key_checkbox.lower(), value=str(item_checkbox.get()))
        self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option="last directory", value=str(self.lastDir))
        self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option="template directory", value=str(self.live_template_path))
        self.destroy()

    def select_catalog_event(self):
        self.file_to_parse = []
        self.lastDir = filedialog.askdirectory()
        self.file_to_parse = [f"{self.lastDir}/{each.name}" for each in os.scandir(self.lastDir)]

    def select_file_event(self):
        self.file_to_parse = []
        list_files_path = filedialog.askopenfilenames(
            title="Select file",
            filetypes=(("python file", "*.py"), ("text file", "*.txt"), ("All files", "*.*"),)
        )
        self.lastDir = os.path.split(list_files_path[0])[0]
        self.file_to_parse = list_files_path

    def start_parse(self):
        for file_open_path in self.file_to_parse:
            temp_data_line = []
            with open(file_open_path, "r") as open_file:
                self.temporary_file = open_file.readlines()


            if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "verify coding"):
                self.validate_verify_coding()

            for each_line in self.temporary_file:
                self.current_line = each_line

                if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "excessive spacebards"):
                    self.validate_spacebars_in_step()
                    self.validate_indentation_level()

                temp_data_line.append(self.current_line)

            self.temporary_file = temp_data_line
            with open(file_open_path, "w") as open_file:
                open_file.writelines(self.temporary_file)

            # for line_number, current_line in enumerate(temporary_file, start=1):
            #     pass

    def GetOptionFromCfg(self, cfg_path, section, option):
        if os.path.isfile(cfg_path):
            with open(cfg_path) as opened_file:
                self.config.read_file(opened_file)
                if self.config.has_option(section, option):
                    return self.config.get(section, option)
                else:
                    print(f"option: {option} in section {section} doesn't exist")
                    return None
        else:
            print(f"{self.configFilePath} doesn't exist.")

    def SaveOptToCfg(self, cfg_path, section, option, value):
        self.config.set(section, option, value)
        with open(cfg_path, "w") as opened_file:
            self.config.write(opened_file)

    def validate_spacebars_in_step(self):
        if self.old_template:
            temporary_file = re.search("( *Step\()([\"\'].*[\"\'])(\))", self.current_line)
        else:
            temporary_file = re.search("( *with Step\()([\"\'].*[\"\'])(, ?\d\)\:|\):)", self.current_line)
        temporary_string = ""
        if temporary_file is not None and len(temporary_file.groups()) > 1:
            for each_index, each_group in enumerate(temporary_file.groups()):
                temporary_string += each_group if each_index != 1 else re.sub(" {2,}", " ", each_group)
            self.current_line = temporary_string + "\n"

    def validate_indentation_level(self):
        temporary_file = re.search("( *)(with Step\([\"\'].*[\"\'])(, ?\d\)\:|\):)", self.current_line)
        temporary_string = ""
        if temporary_file is not None and len(temporary_file.groups()) == 3:
            indentation_no = (len(temporary_file.groups()[0]) // 4) + 1
            for each_index, each_group in enumerate(temporary_file.groups()[:-1]):
                temporary_string += (" " * ((indentation_no - 1) * 4)) if each_index == 0 else each_group
            self.current_line = temporary_string + (f", {indentation_no}):" if indentation_no > 1 else "):") + "\n"

    def validate_verify_coding(self):
        # VALIDATION OF CODING: EXPECTED UTF-8

        temp_file_data = []
        if len(self.temporary_file) > 0:
            if r"# -*- coding: utf-8 -*-" not in self.temporary_file[0]:
                if self.flag_print:
                    print("File:", self.current_file, "\tIn first line coding utf-8 is missing, expected: # -*- coding: utf-8 -*-")
                if self.flag_fix:
                    temp_file_data.append("# -*- coding: utf-8 -*-\n")
                    self.temporary_file = temp_file_data + self.temporary_file


if __name__ == '__main__':
    app = App()
    app.mainloop()
