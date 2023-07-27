import customtkinter
import traceback
import os
import configparser
from tkinter import filedialog
import re
import json
from xml.dom import minidom
from pprint import pprint as pp
import logging
import time

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_widget_scaling(0.90)
customtkinter.set_window_scaling(0.90)


class App(customtkinter.CTk):
    # logging.basicConfig(level=logging.DEBUG,
    #                     format="%(asctime)s %(levelname)s %(meassage)s",
    #                     datefmt="%Y-%m-%d %H:%M:%S")
    logging.basicConfig(level=logging.WARNING,
                        format="%(asctime)s - %(funcName)20s() - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

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
    WIDTH = 1400
    HEIGHT = 900
    current_line = ""
    current_line_no = 1
    current_file_name = ""
    old_template = False
    errorList = []  # line number, error description
    procedure_line = ""
    checkbox_dict = {}
    options = [
        "Update Step level",
        "Verify Coding",
        "Remove unnecessary lines",
        "Excessive Spacebars",
        "Indentation step level",
        "Indentation log level",
        "Step finished with dot",
        "Validate requirements",
        "Remove spacebars template",

        "Verify ASCII chars range",
        "Validation of headers",
        "Use of single quotes",
        "Not closed quotes",
        "Variables in Steps",

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
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.bottom_grid_level = customtkinter.CTkFrame(master=self)
        self.bottom_grid_level.grid(sticky="wesn", padx=10, pady=10)
        self.bottom_grid_level.grid_columnconfigure(0, weight=1)
        self.bottom_grid_level.grid_columnconfigure(1, weight=3)
        self.bottom_grid_level.grid_rowconfigure(0, weight=1)

        # =========================== EMPTY LINE ======================

        self.left_column = customtkinter.CTkFrame(master=self.bottom_grid_level)
        self.left_column.grid(row=0, column=0, sticky="wesn", padx=10, pady=10)
        self.left_column.grid_columnconfigure(0, weight=1)
        self.left_column.grid_rowconfigure((1, 2, 3, 4, 5, 6, 7), weight=1)

        # =========================== EMPTY LINE ======================
        left_row_index = 0
        self.top_left_empty_line = customtkinter.CTkFrame(master=self.left_column, height=1)
        self.top_left_empty_line.grid(row=left_row_index, column=0)
        #
        # # ====================== header settings ======================
        left_row_index += 1
        self.header = customtkinter.CTkFrame(master=self.left_column, height=50)
        self.header.grid(row=left_row_index, column=0, sticky="we", padx=10, pady=(10, 0))
        self.header.grid_columnconfigure((0, 1), weight=1)
        self.select_catalog_button = customtkinter.CTkButton(master=self.header,
                                                             text="Select catalog",
                                                             command=self.select_catalog_event)

        self.select_catalog_button.grid(row=0, column=0, pady=(10, 10), padx=10, sticky="wesn")

        self.select_catalog_button = customtkinter.CTkButton(master=self.header,
                                                             text="Select file",
                                                             command=self.select_file_event)
        self.select_catalog_button.grid(row=0, column=1, pady=(10, 10), padx=10, sticky="wesn")

        # ====================== header settings ======================
        left_row_index += 1
        self.text_grid = customtkinter.CTkFrame(master=self.left_column, height=200)
        self.text_grid.grid(row=left_row_index, column=0, sticky="wesn", padx=10, pady=(10, 0))
        self.text_grid.grid_rowconfigure(0, weight=1)
        self.text_grid.grid_columnconfigure(0, weight=1)
        self.textbox = customtkinter.CTkTextbox(self.text_grid)
        self.textbox.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="wesn")

        # ====================== header settings ======================

        left_row_index += 1
        self.template_grid = customtkinter.CTkFrame(master=self.left_column, height=100)
        self.template_grid.grid(row=left_row_index, column=0, sticky="we", padx=10, pady=(10, 0))
        self.template_grid.grid_columnconfigure((0, 1), weight=1)

        self.template_label = customtkinter.CTkLabel(master=self.template_grid, text="Live Template", compound="left")
        self.template_label.grid(row=0, column=0, sticky="w", padx=30, pady=10)

        self.template_button = customtkinter.CTkButton(master=self.template_grid, text="Select template path", command=self.select_template_file_event)
        self.template_button.grid(row=0, column=1, sticky="we", padx=10, pady=10)

        self.template_textbox = customtkinter.CTkTextbox(self.template_grid, height=20, width=100, state="disabled")
        self.template_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="we")
        self.template_textbox.grid_configure(columnspan=2)

        # ====================== select section settings ======================

        left_row_index += 1
        self.select_grid = customtkinter.CTkFrame(master=self.left_column, height=300)
        self.select_grid.grid(row=left_row_index, column=0, sticky="wesn", padx=10, pady=(10, 0))

        for index, option_name in enumerate(self.options):
            checkbox = customtkinter.CTkCheckBox(master=self.select_grid, text=f"{option_name}", command=self.check_box_update_event)
            checkbox.grid(row=index // 3, column=index % 3, pady=8, padx=10, sticky="nwe")
            checkbox.select() if int(self.GetOptionFromCfg(self.configFilePath, section="DEFAULT", option=option_name)) else checkbox.deselect()
            self.checkbox_dict.update({option_name: checkbox})

        # ====================== select section settings ======================

        left_row_index += 1
        self.select_version_grid = customtkinter.CTkFrame(master=self.left_column, height=50)
        self.select_version_grid.grid(row=left_row_index, column=0, sticky="wesn", padx=10, pady=(10, 0))
        self.checkbox_version = customtkinter.CTkCheckBox(master=self.select_version_grid, text=f"New tc version", command=self.check_box_update_event)
        self.checkbox_version.grid(row=1, column=1, pady=10, padx=10, sticky="nwe")
        self.checkbox_version.select() if int(self.GetOptionFromCfg(self.configFilePath, section="DEFAULT", option="tc version")) else self.checkbox_version.deselect()

        # ====================== footer section settings ======================

        left_row_index += 1
        self.footer_grid = customtkinter.CTkFrame(master=self.left_column, height=50)
        self.footer_grid.grid(row=left_row_index, column=0, sticky="swe", padx=10, pady=(10, 0))
        self.footer_grid.grid_columnconfigure(0, weight=1)
        self.select_catalog_button = customtkinter.CTkButton(master=self.footer_grid,
                                                             text="PARSE TEST CASE",
                                                             command=self.start_parse)
        self.select_catalog_button.grid(row=0, column=0, pady=(10, 10), padx=10, sticky="wesn")

        # =========================== EMPTY LINE ======================
        left_row_index += 1
        self.bottom_left_empty_line = customtkinter.CTkFrame(master=self.left_column, height=1)
        self.bottom_left_empty_line.grid(row=left_row_index, column=0)

        # ============================= right column ============================ #
        self.second_column = customtkinter.CTkFrame(master=self.bottom_grid_level)
        self.second_column.grid(row=0, column=1, sticky="snwe", padx=(0, 10), pady=(10, 10))
        self.second_column.grid_columnconfigure(0, weight=1)
        self.second_column.grid_rowconfigure(0, weight=1)

        # ============================ Text box ================================= #
        # self.error_grid = customtkinter.CTkFrame(master=self.second_column)
        # self.text_grid.grid(row=1, column=0, sticky="wesn", padx=10, pady=(10, 0))
        # self.text_grid.grid_rowconfigure(0, weight=1)
        # self.text_grid.grid_columnconfigure(0, weight=1)
        self.error_textbox = customtkinter.CTkTextbox(self.second_column, width=700)
        self.error_textbox.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="wesn")

    def check_box_update_event(self):
        pass

    def on_closing(self):
        self._update_init_file()
        self.destroy()

    def _update_init_file(self):
        logging.info("Entry")
        time_start = time.time()
        for key_checkbox, item_checkbox in self.checkbox_dict.items():
            self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option=key_checkbox.lower(), value=str(item_checkbox.get()))
        self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option="last directory", value=str(self.lastDir))
        self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option="tc version", value=str(self.checkbox_version.get()))
        self.SaveOptToCfg(self.configFilePath, section="DEFAULT", option="template directory", value=str(self.live_template_path))
        logging.info(f"Exit in {time.time() - time_start}")

    def select_catalog_event(self):
        logging.info("Entry")
        time_start = time.time()
        self.textbox.delete("0.0", "end")
        self.file_to_parse = []
        self.lastDir = filedialog.askdirectory()
        self.file_to_parse = [f"{self.lastDir}/{each.name}" for each in os.scandir(self.lastDir)]
        temp_text = ""
        logging.debug(f"Selected folder: {self.lastDir}")
        logging.debug(f"Selected files: {self.file_to_parse}")
        list_files_path = self.file_to_parse
        for each_name in list_files_path:
            temp_text += os.path.split(each_name)[1] + "\n"
        self.textbox.insert("0.0", temp_text)
        logging.info(f"Exit in {time.time() - time_start}")

    def select_file_event(self):
        logging.info("Entry")
        time_start = time.time()
        self.textbox.delete("0.0", "end")
        self.file_to_parse = []
        list_files_path = filedialog.askopenfilenames(
            title="Select file",
            filetypes=(("python file", "*.py"), ("text file", "*.txt"), ("All files", "*.*"),)
        )
        self.lastDir = os.path.split(list_files_path[0])[0]
        self.file_to_parse = list_files_path
        logging.debug(f"Selected folder: {self.lastDir}")
        logging.debug(f"Selected files: {self.file_to_parse}")
        temp_text = ""
        for each_name in list_files_path:
            temp_text += os.path.split(each_name)[1] + "\n"
        self.textbox.insert("0.0", temp_text)
        logging.info(f"Exit in {time.time() - time_start}")

    def select_template_file_event(self):
        logging.info("Entry")
        time_start = time.time()
        self.template_textbox.delete("0.0", "end")
        list_files_path = filedialog.askopenfilenames(
            title="Select file",
            filetypes=(("python file", "*.py"), ("text file", "*.txt"), ("All files", "*.*"),)
        )
        self.live_template_path = os.path.split(list_files_path[0])[0]
        logging.debug(f"Selected folder: {list_files_path[0]}")
        self.template_textbox.configure(state="normal")
        self.template_textbox.insert("0.0", f"{list_files_path[0]}")
        self.template_textbox.configure(state="disabled")
        logging.info(f"Exit in {time.time() - time_start}")

    def start_parse(self):
        logging.info("Entry")
        time_start = time.time()
        self.errorList = []
        self._update_init_file()
        for file_open_path in self.file_to_parse:
            self.current_file_name = os.path.split(file_open_path)[1]

            if self.checkbox_dict.get('Template updater').get():
                self.update_templates(file_open_path)

            temp_data_line = []
            with open(file_open_path, "r") as open_file:
                self.temporary_file = open_file.readlines()

            if self.checkbox_dict.get('Verify Coding').get():
                self.validate_verify_coding()
            if self.checkbox_dict.get('Remove unnecessary lines').get():
                self.remove_unnecessary_empty_lines()

            for each_line_no, each_line in enumerate(self.temporary_file, start=1):
                self.current_line = each_line
                self.current_line_no = each_line_no

                if self.checkbox_dict.get('Remove spacebars template').get():
                    self.remove_unnecessary_white_signs_before_editor()

                if self.checkbox_dict.get('Excessive Spacebars').get():
                    self.validate_spacebars_in_step()

                if self.checkbox_dict.get('Indentation step level').get():
                    self.validate_indentation_level()

                if self.checkbox_dict.get('Indentation log level').get():
                    self.validate_level_log_indentation()
                    self.validate_whitespaces_in_log()

                if self.checkbox_dict.get('Step finished with dot').get():
                    self.validate_dot_on_the_end()

                if self.checkbox_dict.get('Validate requirements').get():
                    self.validate_requirement()

                temp_data_line.append(self.current_line)
            self.temporary_file = temp_data_line

            # Parse testcase and update steps number
            if self.checkbox_dict.get('Update Step level').get():
                self.parse_step_level_file()

            self.append_step_procedure()

            with open(file_open_path, "w") as open_file:
                open_file.writelines(self.temporary_file)

            self._PrintErrorList()
            logging.info(f"Exit in {time.time() - time_start}")
            self.error_textbox.insert("end", f"\n\nParsing finished in {time.time() - time_start:.02f}s, world will better now!")

    def GetOptionFromCfg(self, cfg_path, section, option, int_return=False):
        logging.info("Entry")
        time_start = time.time()
        if os.path.isfile(cfg_path):
            with open(cfg_path) as opened_file:
                self.config.read_file(opened_file)
                if self.config.has_option(section, option):
                    if int_return:
                        return int(self.config.get(section, option))
                    else:
                        return self.config.get(section, option)
                else:
                    print(f"option: {option} in section {section} doesn't exist")
                    return None
        else:
            print(f"{self.configFilePath} doesn't exist.")
        logging.info(f"Exit in {time.time() - time_start}")

    def SaveOptToCfg(self, cfg_path, section, option, value):
        logging.info("Entry")
        time_start = time.time()
        self.config.set(section, option, value)
        with open(cfg_path, "w") as opened_file:
            self.config.write(opened_file)
        logging.info(f"Exit in {time.time() - time_start}")

    def validate_requirement(self):
        logging.info("Entry")
        time_start = time.time()
        line = self.current_line
        if re.search(r'^#* *Req *\(', line):
            if not line.startswith('#'):  # process only not hashed lines
                line = re.sub(r'Req *\( *\[ *" *', 'Req(["', line,
                              1)  # delete needless space chars in `Req ( [ " ` string
                line = re.sub(r' *" *\] *\) *$', '"])', line, 1)  # delete needless space chars in ` " ] ) ` string
                line = re.sub(r' *" *, *" *', '", "', line)  # delete needless space chars in ` " , " ` string

                if not re.search(r'Req\([\[].*[\]]\)', line):
                    self.errorList.append([self.current_file_name,
                                           self.current_line_no,
                                           'Lack bracket: requirements shall be list of strings.'])
                else:
                    requirements = re.search(r'(?<=\[).*(?=])', line).group()
                    bordersCheck = re.search(r'(^[^"])|([^"]$)', requirements)  # check if starts and ends with "
                    oneQuotationMarkCheck = re.search(r'(^"$)',
                                                      requirements)  # check if only one " (quotation mark) is used
                    internalCheck = re.search(r'([^"], )|(, [^"])',
                                              requirements)  # check if , (comma) is rounded by " (quotation marks)
                    if bordersCheck or oneQuotationMarkCheck or internalCheck:
                        self.errorList.append(
                            [self.current_file_name,
                             self.current_line_no,
                             'Lack quotation mark(s): requirements shall be list of strings.'])
        logging.info(f"Exit in {time.time() - time_start}")

    def validate_spacebars_in_step(self):
        logging.info("Entry")
        time_start = time.time()
        if "#" not in self.current_line:
            if self.old_template:
                temporary_file = re.search("( *Step\()([\"\'].*[\"\'])(\))", self.current_line)
            else:
                temporary_file = re.search("( *with Step\()([\"\'].*[\"\'])(, ?\d\):|\):)", self.current_line)
            temporary_string = ""
            if temporary_file is not None and len(temporary_file.groups()) > 1:
                for each_index, each_group in enumerate(temporary_file.groups()):
                    temporary_string += each_group if each_index != 1 else re.sub(" {2,}", " ", each_group)
                self.current_line = temporary_string + "\n"
        logging.info(f"Exit in {time.time() - time_start}")

    def _PrintErrorList(self):
        self.error_textbox.delete("0.0", "end")
        self.error_textbox.insert("end", "Detected issues in testcases:")

        if len(self.errorList) > 0:
            for each_error in self.errorList:
                self.error_textbox.insert("end", f"\n File: {each_error[0]},\t line: {each_error[1]},\t fault detected: {each_error[2]}")
        else:
            self.error_textbox.insert("end", "\nAny problem with testcases")

    def validate_level_log_indentation(self):
        logging.info("Entry")
        time_start = time.time()
        temp_line = self.current_line
        allowed_level_list = [1, 2, 3]
        indentation_log_level = re.match("(\s*Log\([\"\'].*[\"\'],? ?)(\d?)\)", temp_line)
        if indentation_log_level is not None:
            indentation_log_level = indentation_log_level.groups()
            if len(indentation_log_level[1]) > 0:
                indentation_log_level = int(indentation_log_level[1])
            else:
                indentation_log_level = 1
            if indentation_log_level not in allowed_level_list:
                self.errorList.append([self.current_file_name,
                                       self.current_line_no,
                                       f"Incorrect Log level, current level: {indentation_log_level}, allowed levels: {allowed_level_list}"])
        logging.info(f"Exit in {time.time() - time_start}")

    def validate_whitespaces_in_log(self):
        logging.info("Entry")
        time_start = time.time()
        line = self.current_line
        try:
            line = re.sub(r'Log *\( *" *', 'Log("', line, 1)  # delete needless space chars in "Logs ( " string
            line = re.sub(r' *" *\) *$', '")', line, 1)  # delete needless space chars in " ) " string
            self.current_line = line
        except:
            self.errorList.append([self.current_file_name,
                                   self.current_line_no,
                                   ' exception - ' + traceback.format_exc()])
            status = 'NOK'
        logging.info(f"Exit in {time.time() - time_start}")

    def validate_indentation_level(self):
        logging.info("Entry")
        time_start = time.time()
        if "#" not in self.current_line:
            temporary_file = re.search("( *)(with Step\([\"\'].*[\"\'])(, ?\d\):|\):)", self.current_line)
            temporary_string = ""
            if temporary_file is not None and len(temporary_file.groups()) == 3:
                indentation_no = (len(temporary_file.groups()[0]) // 4) + 1
                for each_index, each_group in enumerate(temporary_file.groups()[:-1]):
                    temporary_string += (" " * ((indentation_no - 1) * 4)) if each_index == 0 else each_group
                self.current_line = temporary_string + (f", {indentation_no}):" if indentation_no > 1 else "):") + "\n"
        logging.info(f"Exit in {time.time() - time_start}")

    def validate_verify_coding(self):
        logging.info("Entry")
        time_start = time.time()
        # VALIDATION OF CODING: EXPECTED UTF-8
        temp_file_data = []
        if len(self.temporary_file) > 0:
            if r"# -*- coding: utf-8 -*-" not in self.temporary_file[0]:
                if self.flag_print:
                    print("File:", self.current_file, "\tIn first line coding utf-8 is missing, expected: # -*- coding: utf-8 -*-")
                if self.flag_fix:
                    temp_file_data.append("# -*- coding: utf-8 -*-\n")
                    self.temporary_file = temp_file_data + self.temporary_file
        logging.info(f"Exit in {time.time() - time_start}")

    def validate_dot_on_the_end(self):
        logging.info("Entry")
        time_start = time.time()
        if "#" not in self.current_line:
            temporary_file = re.search("( *.*Step\([\"\'].*\n*.*)(\.)(\".*\))", self.current_line)
            if temporary_file is not None and len(temporary_file.groups()) == 3:
                temporary_string = ""
                for each_index, each_line in enumerate(temporary_file.groups()):
                    if each_index != 1:
                        temporary_string += each_line
                self.current_line = temporary_string + "\n"
        logging.info(f"Exit in {time.time() - time_start}")

    def remove_unnecessary_empty_lines(self):
        logging.info("Entry")
        time_start = time.time()
        if len(self.temporary_file) > 0:
            temporary_file = ""
            for each_line in self.temporary_file:
                temporary_file += each_line
            temporary_file = re.sub("\n\s*\n", "\n\n", temporary_file)
            self.temporary_file = [each_line + "\n" for each_line in temporary_file.split("\n")]
        logging.info(f"Exit in {time.time() - time_start}")

    def parse_step_level_file(self, ):
        logging.info("Entry")
        time_start = time.time()
        MAX_STEP_LEVEL = 3
        tcLines = self.temporary_file

        stepNumber = MAX_STEP_LEVEL * [0]  # counter for steps numerating
        self.procedure_line = ['\n##    PROCEDURE:\n']  # procedure string
        parsedLines = []

        OldTestCaseStyle = self.checkbox_version.get()
        for lineNumber, line in enumerate(tcLines, 1):
            if re.search(r'^[ \t]*Step *\(', line) or re.search(r'^[ \t]*with Step *\(', line):
                try:
                    indent = re.search(r'^[ \t]*', line).group()
                    level = re.search(r'" *, *(\d+) *\)', line)
                    if level:
                        level = int(level.groups()[0])
                        levelStr = ', ' + str(level)
                    else:
                        level = 1
                        levelStr = ''
                    if level > MAX_STEP_LEVEL:
                        self.errorList.append(
                            [lineNumber, ' - wrong level value: level parameter shall be one of integers 1, 2 or 3.'])
                        status = 'NOK'
                    else:
                        text = ' ' + re.search(r'"[ \d.]*(.*?) *"', line).groups()[0]
                        stepText = ''
                        stepNumber[level - 1] += 1
                        for i in range(MAX_STEP_LEVEL):
                            if i < level:
                                if stepNumber[i] == 0:
                                    stepNumber[i] += 1
                                stepText += str(stepNumber[i]) + '.'
                            else:
                                stepNumber[i] = 0
                        if OldTestCaseStyle:
                            if line.startswith("Step("):
                                print(f"You have selected New TC's ABC model, line: {lineNumber} "
                                      "Incorrect naming, use 'with Step(' in your TC's instead")
                            else:
                                line = indent + 'with Step("' + stepText + text + '"' + levelStr + '):\n'
                        else:
                            if line.startswith("with Step(") or line.startswith("    "):
                                print(f"You have selected OLD TC's model, line: {lineNumber} "
                                      "Incorrect naming, use 'Step(' in your TC's instead")
                            else:
                                line = indent + 'Step("' + stepText + text + '"' + levelStr + ')\n'
                        self.procedure_line.append('##    ' + stepText + text + '\n')
                        parsedLines.append(line)
                except:
                    self.errorList.append([lineNumber, ' exception - ' + traceback.format_exc()])
                    status = 'NOK'
            else:
                parsedLines.append(line)
        self.temporary_file = parsedLines
        logging.info(f"Exit in {time.time() - time_start}")

    def remove_unnecessary_white_signs_before_editor(self):
        logging.info("Entry")
        time_start = time.time()
        temporary_file = re.search("[ ]+#[\s]?(<[/]?editor)(.*)", self.current_line)
        if temporary_file is not None:
            temporary_string = "# "
            for each_index, each_line in enumerate(temporary_file.groups()):
                temporary_string += each_line
            self.current_line = temporary_string + "\n"
        logging.info(f"Exit in {time.time() - time_start}")

    def append_step_procedure(self):
        logging.info("Entry")
        time_start = time.time()
        temp_file_lines = self.temporary_file[:]
        start_procedure_list = None
        procedure_flag = False
        procedure_start = None
        procedure_stop = None
        log_end = None

        for each_index, each_line in enumerate(temp_file_lines):
            each_line: str
            if "##    PROCEDURE:" in each_line:
                procedure_flag = True
                procedure_start = each_index

            if "header.Log()" in each_line:
                log_end = each_index

            if procedure_flag and not each_line.startswith("## "):
                procedure_flag = False
                procedure_stop = each_index
        if procedure_start is not None:
            del temp_file_lines[procedure_start:procedure_stop]
            copy_temp_file = temp_file_lines[:procedure_start] + self.procedure_line + temp_file_lines[procedure_start:] + ["\n"]
        else:
            if log_end is not None:
                procedure_start = log_end + 1
                copy_temp_file = temp_file_lines[:procedure_start] + ["\n"] + self.procedure_line + temp_file_lines[procedure_start:] + ["\n"]
            else:
                copy_temp_file = temp_file_lines[:]
        self.temporary_file = copy_temp_file[:]
        logging.info(f"Exit in {time.time() - time_start}")

    def update_templates(self, tc_path):
        logging.info("Entry")
        time_start = time.time()
        xml_path = self.GetOptionFromCfg(cfg_path=self.configFilePath, section="DEFAULT", option="template directory")

        file = open(tc_path, "r")
        script = file.read()

        parsedFile = minidom.parse(xml_path)
        tags_dict = {}
        for tag in parsedFile.getElementsByTagName("template"):
            name = tag.attributes.get("name").value
            value = tag.attributes.get("value").value
            tags_dict.update({name: value})

        start_tags_no = script.count("# <editor-fold")
        end_tags_no = script.count("# </editor-fold")

        if start_tags_no != end_tags_no:
            print("Open and closed <editor-fold> tags doesn't match!")
            print(tc_path)
            exit(1)
        if not start_tags_no:
            print("No tags: skip")
            # continue
            # exit(0)

        start_tags = []
        end_tags = []
        for start_tag in re.finditer("# <editor-fold.+?>", script):
            start_tags.append(start_tag)
        for end_tag in re.finditer("# </editor-fold>", script):
            end_tags.append(end_tag)

        if start_tags_no != len(start_tags) != len(end_tags):
            print("Error: Likely internal script issue!")
            exit(1)

        for start_tag, end_tag in zip(reversed(start_tags), reversed(end_tags)):
            to_update = script[start_tag.start():end_tag.end()]
            desc = re.search(r'desc="(.*?)"', start_tag.group()).group(1)
            if desc not in tags_dict.keys():
                print("Warning: tag was not found and wasn't replaced: %s" % (desc,))
                continue
            update_counts = script.count(to_update)
            if update_counts != 1:
                print("Warning: %d occurrences of same tag" % (update_counts,))
            update = tags_dict[desc].strip()  # strip to remove excessive new lines

            # Get string with values as dict from <editor-fold> tag
            var = re.search(r"var={(.*?)}", start_tag.group())
            var_dict = {}
            if var:
                var = var.group()[4:]
                try:
                    var_dict = json.loads(var)
                except json.decoder.JSONDecodeError:
                    print("Error: json tag issue!")
                    print(var)
                except:
                    print("Error: likely json tag issue!")

            for key, value in var_dict.items():
                _key = key.join(["$", "$"])  # add $ to variable name
                update = update.replace(_key, str(value))  # replace variables with value from <editor-fold> tag

            script = update.join(script.rsplit(to_update, 1))  # Replace last occurrence

        file.close()

        file = open(tc_path, "w")
        file.write(script)
        file.close()
        logging.info(f"Exit in {time.time() - time_start}")


if __name__ == '__main__':
    app = App()
    app.mainloop()
