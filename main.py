import customtkinter
import traceback
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
               "Remove unnecessary lines",
               "Excessive Spacebards",
               "Indentation step level",
               "Step finished with dot",

               "Verify ASCII chars range",
               "Validation of headers",
               "Use of single quotes",
               "Not closed quotes",
               "Indentation of Steps",
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
        self.textbox.delete("0.0", "end")
        self.file_to_parse = []
        self.lastDir = filedialog.askdirectory()
        self.file_to_parse = [f"{self.lastDir}/{each.name}" for each in os.scandir(self.lastDir)]
        temp_text = ""
        list_files_path = self.file_to_parse
        for each_name in list_files_path:
            temp_text += os.path.split(each_name)[1] + "\n"
        self.textbox.insert("0.0", temp_text)

    def select_file_event(self):
        self.textbox.delete("0.0", "end")
        self.file_to_parse = []
        list_files_path = filedialog.askopenfilenames(
            title="Select file",
            filetypes=(("python file", "*.py"), ("text file", "*.txt"), ("All files", "*.*"),)
        )
        self.lastDir = os.path.split(list_files_path[0])[0]
        self.file_to_parse = list_files_path
        temp_text = ""
        for each_name in list_files_path:
            temp_text += os.path.split(each_name)[1] + "\n"
        self.textbox.insert("0.0", temp_text)

    def start_parse(self):
        for file_open_path in self.file_to_parse:
            temp_data_line = []
            with open(file_open_path, "r") as open_file:
                self.temporary_file = open_file.readlines()

            if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "verify coding"):
                self.validate_verify_coding()
            if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "remove unnecessary lines"):
                self.remove_unnecessary_empty_lines()

            for each_line in self.temporary_file:
                self.current_line = each_line

                if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "excessive spacebards"):
                    self.validate_spacebars_in_step()

                if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "Indentation step level"):
                    self.validate_indentation_level()

                if self.GetOptionFromCfg(self.configFilePath, "DEFAULT", "Step finished with dot"):
                    self.validate_dot_on_the_end()

                temp_data_line.append(self.current_line)
            self.temporary_file = temp_data_line

            self.ParseFile()
            with open(file_open_path, "w") as open_file:
                open_file.writelines(self.temporary_file)

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
            temporary_file = re.search("( *with Step\()([\"\'].*[\"\'])(, ?\d\):|\):)", self.current_line)
        temporary_string = ""
        if temporary_file is not None and len(temporary_file.groups()) > 1:
            for each_index, each_group in enumerate(temporary_file.groups()):
                temporary_string += each_group if each_index != 1 else re.sub(" {2,}", " ", each_group)
            self.current_line = temporary_string + "\n"

    def validate_indentation_level(self):
        temporary_file = re.search("( *)(with Step\([\"\'].*[\"\'])(, ?\d\):|\):)", self.current_line)
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

    def validate_dot_on_the_end(self):
        temporary_file = re.search("( *.*Step\([\"\'].*\n*.*)(\.)(\".*\))", self.current_line)
        if temporary_file is not None and len(temporary_file.groups()) == 3:
            temporary_string = ""
            for each_index, each_line in enumerate(temporary_file.groups()):
                if each_index != 1:
                    temporary_string += each_line
            self.current_line = temporary_string + "\n"

    def remove_unnecessary_empty_lines(self):
        if len(self.temporary_file) > 0:
            temporary_file = ""
            for each_line in self.temporary_file:
                temporary_file += each_line
            temporary_file = re.sub("\n{2,}", "\n\n", temporary_file)
            self.temporary_file = [each_line + "\n" for each_line in temporary_file.split("\n")]

    def ParseFile(self, ):
        #     status = 'OK'
        MAX_STEP_LEVEL = 3
        tcLines = self.temporary_file

        stepNumber = MAX_STEP_LEVEL * [0]  # counter for steps numerating
        logsNumber = 0
        procedure = '\n##    PROCEDURE:\n'  # procedure string
        procedureFlag = False  # True during procedure lines parsing, False when parsing complete
        reqirementFlag = False  # True when requrements are parsed
        parsedLines = []
        headerEndLineNumber = 0
        errorList = []  # line number, error description
        lineNumberOffset = 0

        for lineNumber, line in enumerate(tcLines, 1):
            if not headerEndLineNumber:
                if line.startswith('""")'):
                    headerEndLineNumber = lineNumber
                elif line.startswith('header.Log()'):
                    headerEndLineNumber = lineNumber + 1

            if not line.startswith('#') and line.count("'") and (not line.count('"') or line.find("'") < line.find('"')):
                errorList.append(
                    [lineNumber, ' - single quote(s) instead of double quote(s): strings shall be in double quotes ["].'])
                status = 'NOK'

            elif not line.startswith('#') and line.count('"') % 2 and not line.count('"""'):
                errorList.append([lineNumber, ' - lack quotation mark(s): strings shall be in quotation marks ["].'])
                status = 'NOK'

            elif re.search(r'^#* *Req *\(', line):
                reqirementFlag = True
                if not line.startswith('#'):  # process only not hashed lines
                    line = re.sub(r'Req *\( *\[ *" *', 'Req(["', line,
                                  1)  # delete needless space chars in `Req ( [ " ` string
                    line = re.sub(r' *" *\] *\) *$', '"])', line, 1)  # delete needless space chars in ` " ] ) ` string
                    line = re.sub(r' *" *, *" *', '", "', line)  # delete needless space chars in ` " , " ` string

                    if not re.search(r'Req\(\[.*\]\)', line):
                        errorList.append([lineNumber, ' - lack bracket: requirements shall be list of strings.'])
                        status = 'NOK'
                    else:
                        requirements = re.search(r'(?<=\[).*(?=\])', line).group()
                        bordersCheck = re.search(r'(^[^"])|([^"]$)', requirements)  # check if starts and ends with "
                        oneQuotationMarkCheck = re.search(r'(^"$)',
                                                          requirements)  # check if only one " (quotation mark) is used
                        internalCheck = re.search(r'([^"], )|(, [^"])',
                                                  requirements)  # check if , (comma) is rounded by " (quotation marks)
                        if bordersCheck or oneQuotationMarkCheck or internalCheck:
                            errorList.append(
                                [lineNumber, ' - lack quotation mark(s): requirements shall be list of strings.'])
                            status = 'NOK'

            elif re.search(r'^[ \t]*Step *\(', line) or re.search(r'^[ \t]*with Step *\(', line):
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
                        errorList.append(
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
                        # if OldTestCaseStyle == 0:
                        #     if line.startswith("Step("):
                        #         print(f"You have selected New TC's ABC model, line: {lineNumber} "
                        #               "Incorrect naming, use 'with Step(' in your TC's instead")
                        #     else:
                        #         line = indent + 'with Step("' + stepText + text + '"' + levelStr + '):\n'
                        # else:
                        #     if OldTestCaseStyle == 1:
                        #         if line.startswith("with Step(") or line.startswith("    "):
                        #             print(f"You have selected OLD TC's model, line: {lineNumber} "
                        #                   "Incorrect naming, use 'Step(' in your TC's instead")
                        #         else:
                        #             line = indent + 'Step("' + stepText + text + '"' + levelStr + ')\n'
                        procedure += '##    ' + stepText + text + '\n'
                except:
                    errorList.append([lineNumber, ' exception - ' + traceback.format_exc()])
                    status = 'NOK'

            elif re.search(r'^[ \t]*Logs *\(', line):
                try:
                    line = re.sub(r'Logs *\( *" *', 'Logs("', line, 1)  # delete needless space chars in "Logs ( " string
                    line = re.sub(r' *" *\) *$', '")', line, 1)  # delete needless space chars in " ) " string
                    logsNumber += 1
                    line = re.sub(r'(?<=[\'"]) *\d*\.* *', str(logsNumber) + '. ', line, 1)  # update test logs number
                    procedure += '##    ' + re.search(r'(?<=[\'"]).*(?=[\'"])', line).group() + '\n'
                except:
                    errorList.append([lineNumber, ' exception - ' + traceback.format_exc()])
                    status = 'NOK'

            if line == '##    PROCEDURE:\n':
                procedureFlag = True

            if procedureFlag and not (line.isspace() or line.startswith('##    ')):
                procedureFlag = False

            if procedureFlag:  # delete procedure lines
                lineNumberOffset -= 1
            else:
                parsedLines.append(line)

        if not reqirementFlag:
            procedure += '#Req([])\n'

        lineNumberOffset += procedure.count('\n')
        for lineNumber, errorDescription in errorList:
            if lineNumber > headerEndLineNumber:
                lineNumber = lineNumber + lineNumberOffset
            # print(("Error: " + fileName + ", line: " + str(lineNumber) + errorDescription))

        # parsedLines.insert(headerEndLineNumber, procedure)


if __name__ == '__main__':
    app = App()
    app.mainloop()
