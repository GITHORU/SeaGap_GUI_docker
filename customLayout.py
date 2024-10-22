from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import QLocale
import os



class IntSelector(QVBoxLayout):
    def __init__(self, min, max, label, req, backText="", *args, **kwargs):
        super(IntSelector, self).__init__(*args, **kwargs)

        self.min = min
        self.max = max

        self.line_edit = QLineEdit("")
        if req :
            self.line_edit.setPlaceholderText(backText + " *required")
        else :
            self.line_edit.setPlaceholderText(backText)
        validator = QIntValidator(self.min, self.max)

        self.line_edit.setValidator(validator)

        self.line_edit.textChanged.connect(self.check_int)

        self.addWidget(QLabel(label + " :"))
        self.addWidget(self.line_edit)

    def check_int(self):
        try :
            if int(self.line_edit.text()) > self.max :
                self.line_edit.setText(int(self.max))
            elif int(self.line_edit.text()) < self.min :
                self.line_edit.setText(int(self.min))
        except :
            return



class DoubleSelector(QVBoxLayout):
    def __init__(self, min, max, label, req, backText="", dec=16, *args, **kwargs):
        super(DoubleSelector, self).__init__(*args, **kwargs)

        self.min = min
        self.max = max

        self.line_edit = QLineEdit("")
        if req :
            self.line_edit.setPlaceholderText(backText + " *required")
        else :
            self.line_edit.setPlaceholderText(backText)
        validator = QDoubleValidator(self.min, self.max, dec)
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        validator.setLocale(locale)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.line_edit.setValidator(validator)

        self.line_edit.textChanged.connect(self.check_double)

        self.addWidget(QLabel(label + " :"))
        self.addWidget(self.line_edit)

    def check_double(self):
        try :
            if float(self.line_edit.text()) > self.max :
                self.line_edit.setText(str(self.max))
            elif float(self.line_edit.text()) < self.min :
                self.line_edit.setText(str(self.min))
        except :
            return

class FileExplorerLayout(QVBoxLayout):
    def __init__(self, label, req=True, default_text="", *args, **kwargs): #default_path="",
        super(FileExplorerLayout, self).__init__(*args, **kwargs)
        self.label = label
        # self.default_path = default_path

        self.addWidget(QLabel(self.label+" :"))

        selector = QHBoxLayout()
        self.button = QPushButton("Select file")
        self.button.clicked.connect(self.open_file_dialog)
        selector.addWidget(self.button)

        self.line_edit = QLineEdit(default_text)
        self.line_edit.setDisabled(True)
        if req :
            self.line_edit.setPlaceholderText("*required")
        selector.addWidget(self.line_edit)

        self.addLayout(selector)

    def open_file_dialog(self):
        dlg = QFileDialog()
        dlg.setWindowTitle("Select " + self.label + " File")
        # if self.default_path != "" :
        dlg.setDirectory(os.curdir) #self.default_path)
        self.line_edit.setText(dlg.getOpenFileName()[0])

class FolderExplorerLayout(QVBoxLayout):
    def __init__(self, label, req=True, default_text="", *args, **kwargs): #, default_path=""
        super(FolderExplorerLayout, self).__init__(*args, **kwargs)
        self.label = label
        # self.default_path = default_path

        self.addWidget(QLabel(self.label+" :"))

        selector = QHBoxLayout()
        self.button = QPushButton("Select folder")
        self.button.clicked.connect(self.open_folder_dialog)
        selector.addWidget(self.button)

        self.line_edit = QLineEdit(default_text)
        self.line_edit.setDisabled(True)
        if req :
            self.line_edit.setPlaceholderText("*required")
        selector.addWidget(self.line_edit)

        self.addLayout(selector)

    def open_folder_dialog(self):
        dlg = QFileDialog()
        dlg.setWindowTitle("Select " + self.label + " Folder")
        # if self.default_path != "" :
        dlg.setDirectory(os.curdir) #self.default_path)
        self.line_edit.setText(dlg.getExistingDirectory())