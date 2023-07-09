import customtkinter
import os
import configparser

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
class App(customtkinter.CTk):
    config = configparser.ConfigParser()
    configFileName = "/tc_parser.ini"
    configFilePath = os.getcwd() + configFileName
    lastDir = r""
    live_template_path = r""
    flag_print = True
    flag_fix = True
    current_file = ""
    WIDTH = 600
    HEIGHT = 700

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
        self.lastDir= self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "last directory")
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
                                                             command=self.select_catalog)

        self.select_catalog_button.grid(row=0, column=0, pady=(10, 10), padx=10, sticky="we")

        self.select_catalog_button = customtkinter.CTkButton(master=self.header,
                                                             text="Select file",
                                                             command=self.select_file)
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
                                                             command=self.select_catalog)
        self.select_catalog_button.grid(row=0, column=0, pady=(10, 10), padx=10, sticky="wesn")

    def check_box_update_event(self):
       pass

    def on_closing(self):
        for key_checkbox, item_checkbox in self.checkbox_dict.items():
            self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option=key_checkbox.lower(), value=str(item_checkbox.get()))
        self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option="last directory", value=str(self.lastDir))
        self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option="template directory", value=str(self.live_template_path))
        self.destroy()

    def select_catalog(self):
        pass

    def select_file(self):
        pass

    def start_parse(self):
        lines_file = []
        if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "verify coding"):
            lines_file = self.validate_verify_coding(lines_file)

        for line_number, current_line in enumerate(lines_file, start=1):
            pass


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

    def validate_verify_coding(self, file_data):
        # VALIDATION OF CODING: EXPECTED UTF-8
        temp_file_data = []
        if r"# -*- coding: utf-8 -*-" not in file_data[0]:
            if self.flag_print:
                print("File:", self.current_file, "\tIn first line coding utf-8 is missing, expected: # -*- coding: utf-8 -*-")
            if self.flag_fix:
                temp_file_data.append("# -*- coding: utf-8 -*-\n")
        return temp_file_data.append(file_data)












if __name__ == '__main__':
    app = App()
    app.mainloop()
