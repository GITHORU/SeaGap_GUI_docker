import sys
from os.path import exists, join

import yaml, os

from juliacall import Main as jl
from juliacall import Pkg as jlPkg

jlPkg.add(url="https://github.com/f-tommy/SeaGapR")
jl.seval("using SeaGapR")
jl.seval('const SeaGap = SeaGapR')

from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QTabWidget, QVBoxLayout, QPushButton, QToolBar, QStatusBar, QFileDialog
from PySide6.QtGui import QIcon, QAction
from customDialogs import DenoiseDialog, StaticArrayDialog, StaticArrayGradDialog, StaticArrayMCMCGradVDialog, \
    StaticIndividualDialog, NewProjectDialog, TtresDialog, MCMCGradVPlotDialog, NTDMCMCGradVPlotDialog, FromGARPOSDialog, TrackPlotDialog, TimeTrackPlotDialog, GradmapDialog, Histogram2DGradVPlotDialog
from customLayout import FileExplorerLayout



def is_path_list_valid(path_list):
    for path in path_list :
        if not exists(path):
            return False
    return True


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
    ### ATTRIBUTES ###

        self.base_path = ""
        self.ANT_path = ""
        self.PXP_path = ""
        self.SSP_path = ""
        self.OBS_path = ""
        self.proj_file_path = ""

    ### TOOLBAR ###

        toolbar = QToolBar("My main toolbar")

        self.new_project_action = QAction("New")
        self.new_project_action.setStatusTip("Create a new project file")
        self.new_project_action.triggered.connect(self.create_new_project)

        self.load_proj_action = QAction("Load")
        self.load_proj_action.setStatusTip("Load existing folder")
        self.load_proj_action.triggered.connect(self.load_proj)

        self.save_project_action = QAction("Save")
        self.save_project_action.setStatusTip("Save current project")
        self.save_project_action.triggered.connect(self.save_project)

        toolbar.addAction(self.new_project_action)
        toolbar.addAction(self.load_proj_action)
        toolbar.addAction(self.save_project_action)

        self.addToolBar(toolbar)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # self.status_bar.showMessage("COUCOU !!!", 2000)

        self.maintab = QTabWidget()


    ### FILE TAB ###

        self.file_tab = QWidget()
        self.file_tab_layout = QVBoxLayout()

        self.ANT_file_explorer = FileExplorerLayout("ANT")
        self.file_tab_layout.addLayout(self.ANT_file_explorer)

        self.PXP_file_explorer = FileExplorerLayout("PXP")
        self.file_tab_layout.addLayout(self.PXP_file_explorer)

        self.SSP_file_explorer = FileExplorerLayout("SSP")
        self.file_tab_layout.addLayout(self.SSP_file_explorer)

        self.OBS_file_explorer = FileExplorerLayout("OBS")
        self.file_tab_layout.addLayout(self.OBS_file_explorer)



        self.file_tab.setLayout(self.file_tab_layout)

    ### PREPROC TAB ###

        self.preproc_tab = QWidget()
        self.preproc_tab_layout = QVBoxLayout()

        self.denoise_Button = QPushButton("Denoise")
        self.denoise_Button.clicked.connect(self.run_denoise_dlg)
        self.preproc_tab_layout.addWidget(self.denoise_Button)

        self.from_GARPOS_Button = QPushButton("From GARPOS ...")
        self.from_GARPOS_Button.clicked.connect(self.run_from_GARPOS_dlg)
        self.preproc_tab_layout.addWidget(self.from_GARPOS_Button)

        self.preproc_tab.setLayout(self.preproc_tab_layout)

    ### CALC TAB ###

        self.calc_tab = QWidget()
        self.calc_tab_layout = QVBoxLayout()

        self.static_array_Button = QPushButton("Static array")
        self.static_array_Button.clicked.connect(self.run_static_array_dlg)
        self.calc_tab_layout.addWidget(self.static_array_Button)

        self.static_array_grad_Button = QPushButton("Static array grad")
        self.static_array_grad_Button.clicked.connect(self.run_static_array_grad_dlg)
        self.calc_tab_layout.addWidget(self.static_array_grad_Button)

        self.static_array_mcmcgradv_Button = QPushButton("Static array mcmcgradv")
        self.static_array_mcmcgradv_Button.clicked.connect(self.run_static_array_mcmcgradv_dlg)
        self.calc_tab_layout.addWidget(self.static_array_mcmcgradv_Button)

        self.static_individual_Button = QPushButton("Static individual")
        self.static_individual_Button.clicked.connect(self.run_static_individual_dlg)
        self.calc_tab_layout.addWidget(self.static_individual_Button)

        self.calc_tab.setLayout(self.calc_tab_layout)

    ### PLOTTING TAB ###

        self.plotting_tab = QWidget()
        self.plotting_tab_layout = QVBoxLayout()

        self.ttres_Button = QPushButton("TT residuals")
        self.ttres_Button.clicked.connect(self.run_ttres_dlg)
        self.plotting_tab_layout.addWidget(self.ttres_Button)

        self.track_Button = QPushButton("Track")
        self.track_Button.clicked.connect(self.show_track_window)
        self.plotting_tab_layout.addWidget(self.track_Button)

        self.timetrack_Button = QPushButton("Time track")
        self.timetrack_Button.clicked.connect(self.show_timetrack_window)
        self.plotting_tab_layout.addWidget(self.timetrack_Button)

        self.mcmcgradvplot_Button = QPushButton("MCMC Grad V plot")
        self.mcmcgradvplot_Button.clicked.connect(self.run_mcmcgradvplot_dlg)
        self.plotting_tab_layout.addWidget(self.mcmcgradvplot_Button)

        self.ntdmcmcgradvplot_Button = QPushButton("NTD MCMC Grad V plot")
        self.ntdmcmcgradvplot_Button.clicked.connect(self.run_ntdmcmcgradvplot_dlg)
        self.plotting_tab_layout.addWidget(self.ntdmcmcgradvplot_Button)

        self.gradmap_Button = QPushButton("Gradmap")
        self.gradmap_Button.clicked.connect(self.show_gradmap_window)
        self.plotting_tab_layout.addWidget(self.gradmap_Button)

        self.histogram2D_Button = QPushButton("Histogram 2D Grad V")
        self.histogram2D_Button.clicked.connect(self.show_histogram2D_window)
        self.plotting_tab_layout.addWidget(self.histogram2D_Button)



        self.plotting_tab.setLayout(self.plotting_tab_layout)

    ### ASSIGNING TABS

        self.maintab.addTab(self.file_tab, "Files")
        self.maintab.addTab(self.preproc_tab, "Pre-processing")
        self.maintab.addTab(self.calc_tab, "Calculs")
        self.maintab.addTab(self.plotting_tab, "Plotting")

    ### FINAL DETAILS ###

        # Définition du titre de la fenêtre
        self.setWindowTitle("SeaGap - GUI")

        my_icon = QIcon("./img/logo.png")

        self.setWindowIcon(my_icon)

        # self.ANT_file_explorer.button.clicked.connect(self.get_path_list)
        # self.PXP_file_explorer.button.clicked.connect(self.get_path_list)
        # self.SSP_file_explorer.button.clicked.connect(self.get_path_list)
        # self.OBS_file_explorer.button.clicked.connect(self.get_path_list)

        self.setCentralWidget(self.maintab)

    def create_new_project(self):
        dlg = NewProjectDialog()
        dlg.setWindowTitle("Select new project folder")
        dlg.exec()
        if dlg.proj_file_path != "" :
            self.load_proj(None, proj_file_path=dlg.proj_file_path)
        else :
            self.proj_file_path = ""
        print("New project '" + os.path.basename(dlg.proj_file_path) + "' created")
        self.status_bar.showMessage("New project '" + os.path.basename(dlg.proj_file_path) + "' created")

    def load_proj(self, _, proj_file_path=""):
        if proj_file_path == "" :
            dlg = QFileDialog()
            dlg.setWindowTitle("Select project file")
            proj_file_path = dlg.getOpenFileName(filter="project(*.prj)")[0]
        
        if not exists(proj_file_path) :
            self.proj_file_path = ""
            print("Wrong project file")
            self.status_bar.showMessage("Wrong project file")
            return
        with open(proj_file_path) as f:
            dict_prj = yaml.full_load(f)

            self.base_path = dict_prj["base_path"]
            if self.base_path != "" :
                os.chdir(self.base_path)
                print("OK !")
                # self.ANT_file_explorer.default_path = self.base_path
                # self.PXP_file_explorer.default_path = self.base_path
                # self.SSP_file_explorer.default_path = self.base_path
                # self.OBS_file_explorer.default_path = self.base_path

            self.ANT_path = dict_prj["ANT_path"]
            self.ANT_file_explorer.line_edit.setText(self.ANT_path)

            self.PXP_path = dict_prj["PXP_path"]
            self.PXP_file_explorer.line_edit.setText(self.PXP_path)

            self.SSP_path = dict_prj["SSP_path"]
            self.SSP_file_explorer.line_edit.setText(self.SSP_path)

            self.OBS_path = dict_prj["OBS_path"]
            self.OBS_file_explorer.line_edit.setText(self.OBS_path)


            self.proj_file_path = proj_file_path

        print("Successfully loaded '"+ os.path.basename(self.proj_file_path) +"' project file")
        self.status_bar.showMessage("Successfully loaded '"+ os.path.basename(self.proj_file_path) +"' project file")

    def save_project(self):
        if self.proj_file_path == "" :
            print("No project selected")
            self.status_bar.showMessage("No project selected")
            return
        with open(self.proj_file_path, "w") as proj_file_path :
            proj_file_path.write('---\n')
            proj_file_path.write('base_path : "'+os.path.dirname(self.proj_file_path)+'"\n')
            proj_file_path.write('proj_name : "'+os.path.splitext(os.path.basename(self.proj_file_path))[0]+'"\n')
            proj_file_path.write('ANT_path : "'+self.ANT_file_explorer.line_edit.text()+'"\n')
            proj_file_path.write('PXP_path : "'+self.PXP_file_explorer.line_edit.text()+'"\n')
            proj_file_path.write('SSP_path : "'+self.SSP_file_explorer.line_edit.text()+'"\n')
            proj_file_path.write('OBS_path : "'+self.OBS_file_explorer.line_edit.text()+'"\n')
        print("Successfully saved '"+ os.path.basename(self.proj_file_path))
        self.status_bar.showMessage("Successfully saved '"+ os.path.basename(self.proj_file_path))

    def get_path_list(self):
        return [self.ANT_file_explorer.line_edit.text(), self.PXP_file_explorer.line_edit.text(), self.SSP_file_explorer.line_edit.text(), self.OBS_file_explorer.line_edit.text()]



    def run_denoise_dlg(self):

        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        denoise_dlg = DenoiseDialog(l_path, jl)
        denoise_dlg.exec()



    def run_from_GARPOS_dlg(self):

        from_GARPOS_dlg = FromGARPOSDialog()
        from_GARPOS_dlg.exec()




    def run_static_array_dlg(self):

        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        static_array_dlg = StaticArrayDialog(l_path, jl)
        static_array_dlg.exec()


    def run_ttres_dlg(self):
        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        ttres_dlg = TtresDialog(l_path, jl)
        ttres_dlg.exec()


    def run_mcmcgradvplot_dlg(self):
        l_path = self.get_path_list()
        mcmcgradvplot_dlg = MCMCGradVPlotDialog(l_path, jl)
        mcmcgradvplot_dlg.exec()


    def run_ntdmcmcgradvplot_dlg(self):
        l_path = self.get_path_list()
        ntdmcmcgradvplot_dlg = NTDMCMCGradVPlotDialog(l_path, jl)
        ntdmcmcgradvplot_dlg.exec()

    def show_track_window(self):
        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        path_ANT, path_PXP, path_SSP, path_OBS = l_path
        jl.SeaGap.plot_track(fn1=path_PXP, fn2=path_OBS, fno="gui_tmp/track.png")

        track_plot_dlg = TrackPlotDialog()
        track_plot_dlg.exec()



    def show_gradmap_window(self):
        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        gradmap_dlg = GradmapDialog(l_path, jl)
        gradmap_dlg.exec()

    def show_timetrack_window(self):
        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        path_ANT, path_PXP, path_SSP, path_OBS = l_path
        jl.SeaGap.plot_timetrack(fn=path_OBS, fno="gui_tmp/time_track.png")

        track_plot_dlg = TimeTrackPlotDialog()
        track_plot_dlg.exec()


    def run_static_array_grad_dlg(self):

        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        static_array_grad_dlg = StaticArrayGradDialog(l_path, jl)
        static_array_grad_dlg.exec()


    def run_static_array_mcmcgradv_dlg(self):

        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        static_array_mcmcgradv_dlg = StaticArrayMCMCGradVDialog(l_path, jl)
        static_array_mcmcgradv_dlg.exec()


    def run_static_individual_dlg(self):
        l_path = self.get_path_list()
        if not is_path_list_valid(l_path):
            self.status_bar.showMessage("Paths not valid")
            print("Paths not valid")
            return
        static_array_individual_dlg = StaticIndividualDialog(l_path, jl)
        static_array_individual_dlg.exec()


    def show_histogram2D_window(self):

        l_path = self.get_path_list()
        # if not is_path_list_valid(l_path):
        #     self.status_bar.showMessage("Paths not valid")
        #     print("Paths not valid")
        #     return
        histogram2d_dlg = Histogram2DGradVPlotDialog(l_path, jl)
        histogram2d_dlg.exec()





if __name__ == '__main__':
    # jl.println("Hello from Julia!")

    # z, v, nz_st, numz = jl.SeaGap.read_prof("../data/ss_prof.inp",3.0)
    # print(z)
    # Create the Qt Application
    app = QApplication()

    # Create and show the form
    window = MainWindow()
    window.show()
    # Run the main Qt loop
    sys.exit(app.exec())