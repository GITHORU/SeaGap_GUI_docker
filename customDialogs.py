from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialogButtonBox, QLineEdit, \
    QStatusBar, QRadioButton
from customLayout import DoubleSelector, IntSelector, FolderExplorerLayout, FileExplorerLayout
from PySide6.QtGui import QIcon, QPixmap
import shutil, os
from PySide6.QtCore import Qt
import docker


from os.path import exists, join

from GARPOS2SeaGap import GARPOS2SeaGap

from multiprocessing import Process

from customProcs import ttres_proc, static_array_proc, static_individual_proc, static_array_grad_proc, static_array_mcmcgradv_proc

from time import time, sleep

# jl.seval('using SeaGap')



class NewProjectDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.statusbar = QStatusBar(self)

        self.proj_file_path = ""

        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.main_layout = QVBoxLayout()

        name_label = QLabel("New project name")
        self.proj_name_line_edit = QLineEdit()
        self.proj_name_line_edit.setPlaceholderText("*required")
        self.folder_layout = FolderExplorerLayout("New project folder", req=True)

        QBtn = (
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.main_layout.addWidget(name_label)
        self.main_layout.addWidget(self.proj_name_line_edit)
        self.main_layout.addLayout(self.folder_layout)
        self.main_layout.addWidget(self.buttonBox)

        self.main_layout.addWidget(self.statusbar)

        self.setLayout(self.main_layout)

    def accept(self):
        if self.proj_name_line_edit.text() == "" and self.folder_layout.line_edit.text() == "" :
            print("Lacking necessary parameters")
            self.statusbar.showMessage("Lacking necessary parameters")
            super().reject()
        proj_folder_path = self.folder_layout.line_edit.text()
        proj_name = self.proj_name_line_edit.text()
        proj_path = os.path.normpath(join(proj_folder_path, proj_name)).replace("\\", "/")
        os.makedirs(proj_path)

        with open(join(proj_path, proj_name+".prj"), "w") as prj_file :
            prj_file.write('---\n')
            prj_file.write('base_path : "'+proj_path+'"\n')
            prj_file.write('proj_name : "'+proj_name+'"\n')
            prj_file.write('ANT_path : "'+'"\n')
            prj_file.write('PXP_path : "'+'"\n')
            prj_file.write('SSP_path : "'+'"\n')
            prj_file.write('OBS_path : "'+'"\n')
        os.makedirs(join(proj_path, "gui_tmp"))
        self.proj_file_path = join(proj_path, proj_name+".prj")


        super().accept()

class TrackPlotDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track plot")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.layout = QVBoxLayout()

        label = QLabel(self)
        pixmap = QPixmap("gui_tmp/track.png")
        label.setPixmap(pixmap)
        self.layout.addWidget(label)

        self.setLayout(self.layout)

class GradmapDialog(QDialog):
    def __init__(self, l_path, jl):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("Grad map plot")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path
        self.jl = jl

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.fig_layout = QHBoxLayout()

        self.folder_selector = FolderExplorerLayout("MCMC Grad V results folder", req=True)
        self.input_layout.addLayout(self.folder_selector)


        self.layout.addLayout(self.input_layout)

        self.graph_img1 = QLabel()
        self.fig_layout.addWidget(self.graph_img1)

        self.layout.addLayout(self.fig_layout)

        self.run_gradmap_plot_button = QPushButton("Run NTD MCMC Grad V plot")
        self.run_gradmap_plot_button.clicked.connect(self.run_gradmap_plot)
        self.input_layout.addWidget(self.run_gradmap_plot_button)

        self.input_layout.addWidget(self.statusbar)

        QBtn = (
                QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setDisabled(True)
        self.buttonBox.accepted.connect(self.accept)

        self.setLayout(self.layout)

    def run_gradmap_plot(self):
        self.graph_img1.clear()
        self.graph_img1.repaint()
        if self.folder_selector.line_edit.text() == "" :
            print("Lacking folder")
            self.statusbar.showMessage("Lacking folder")
            return

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path
        mcmcgradv_folder = self.folder_selector.line_edit.text()

        self.jl.SeaGap.plot_gradmap_gradv(fn1=path_PXP, fn2=join(mcmcgradv_folder, "static_array_mcmcgradv_residual.out"), show=False, fno=join(mcmcgradv_folder, "static_array_mcmcgradv_gradmap.png"))

        pixmap1 = QPixmap(join(mcmcgradv_folder, "static_array_mcmcgradv_gradmap.png"))
        self.graph_img1.setPixmap(
            pixmap1.scaled(pixmap1.width() // 1, pixmap1.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        self.graph_img1.repaint()

class TimeTrackPlotDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time track plot")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.layout = QVBoxLayout()

        label = QLabel(self)
        pixmap = QPixmap("gui_tmp/time_track.png")
        label.setPixmap(pixmap)
        self.layout.addWidget(label)

        self.setLayout(self.layout)




class DenoiseDialog(QDialog):
    
    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("Denoise")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.first_denoise = True

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()

        self.lat_selector = DoubleSelector(-89.99, 89.99, "Latitude", True)
        self.input_layout.addLayout(self.lat_selector)

        self.TR_DEPTH_selector = DoubleSelector(0, 99999.0, "Surface transducer depth", True)
        self.input_layout.addLayout(self.TR_DEPTH_selector)

        self.n_selector = IntSelector(3, 99999, "Window size for the running filter", False, backText="Must be odd (def : 15)")
        self.input_layout.addLayout(self.n_selector)

        self.k_selector = IntSelector(0, 99999, "Which Transpounder", False, backText="(def : 0 = all)")
        self.input_layout.addLayout(self.k_selector)

        self.sigma_selector = DoubleSelector(0.1, 99999.0, "Number of Sigmas", False, backText="(def : 4.0)")
        self.input_layout.addLayout(self.sigma_selector)

        self.run_denoise_button = QPushButton("Run denoise")
        self.run_denoise_button.clicked.connect(self.run_denoise)
        self.input_layout.addWidget(self.run_denoise_button)

        self.input_layout.addWidget(self.statusbar)

        self.graph_img = QLabel()
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.graph_img)

        QBtn = (
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setDisabled(True)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.input_layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

        client = docker.from_env()
        self.cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(self.l_path[4]) + ":/app"])

#TAG

    def run_denoise(self):
        self.graph_img.clear()
        self.graph_img.repaint()
        if self.lat_selector.line_edit.text() == "" or self.TR_DEPTH_selector.line_edit.text() == "" :
            print("Lacking denoise parameters")
            self.statusbar.showMessage("Lacking denoise parameters")
            return

        path_ANT, path_PXP, path_SSP, self.path_OBS_ori, proj_fold = self.l_path
        if self.first_denoise :
            shutil.copyfile(self.path_OBS_ori, "gui_tmp/tmp_denoise_obs.inp")
            self.first_denoise = False

        path_OBS = "gui_tmp/tmp_denoise_obs.inp"
        lat = float(self.lat_selector.line_edit.text())
        TR_DEPTH = float(self.TR_DEPTH_selector.line_edit.text())
        if self.n_selector.line_edit.text() != "":
            n = int(self.n_selector.line_edit.text())
        else :
            n = 15
        if self.k_selector.line_edit.text() != "":
            k = int(self.k_selector.line_edit.text())
        else :
            k = 0
        if self.sigma_selector.line_edit.text() != "":
            sigma = float(self.sigma_selector.line_edit.text())
        else :
            sigma = 4.0

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")


        l_params = [lat, TR_DEPTH, path_ANT, path_PXP, path_SSP, path_OBS, "gui_tmp/tmp_denoise.out", "gui_tmp/tmp_denoise.png", n, sigma, k]
        _, stream = self.cont.exec_run('''julia -e 'using SeaGap;SeaGap.denoise({0}, [{1}], fn1=\"{2}\", fn2=\"{3}\", fn3=\"{4}\", fn4=\"{5}\", fno1=\"{6}\", fno2=\"{7}\", n={8}, sigma={9}, k={10}, save=false, show=false, prompt=false)' '''.format(*l_params), stream=True)
        for data in stream:
            print(data.decode(), end='')

        # self.jl.SeaGap.denoise(lat,juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), fn1=path_ANT , fn2=path_PXP , fn3=path_SSP , fn4=path_OBS, fno1="gui_tmp/tmp_denoise.out", fno2="gui_tmp/tmp_denoise.png", save=False, show=False, prompt=False, n=n, sigma=sigma, k=k)
        pixmap = QPixmap('gui_tmp/tmp_denoise.png')
        self.graph_img.setPixmap(pixmap.scaled(pixmap.width()//2, pixmap.height()//2, Qt.AspectRatioMode.KeepAspectRatio ))
        self.graph_img.repaint()

        self.buttonBox.setDisabled(False)


    def accept(self):
        try :
            shutil.copyfile("gui_tmp/tmp_denoise_obs.inp", self.path_OBS_ori)
            os.remove("gui_tmp/tmp_denoise_obs.inp")
            os.remove("gui_tmp/tmp_denoise.out")
            os.remove("gui_tmp/tmp_denoise.png")
        except :
            pass

        self.cont.stop(timeout=0)
        super().accept()

    def reject(self):
        try :
            os.remove("gui_tmp/tmp_denoise_obs.inp")
            os.remove("gui_tmp/tmp_denoise.out")
            os.remove("gui_tmp/tmp_denoise.png")
        except :
            pass

        self.cont.stop(timeout=0)
        super().reject()

class FromGARPOSDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("From GARPOS ...")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()

        self.OBS_selector = FileExplorerLayout("GARPOS OBS file", req=True)
        self.input_layout.addLayout(self.OBS_selector)

        self.SVP_selector = FileExplorerLayout("GARPOS SVP file", req=True)
        self.input_layout.addLayout(self.SVP_selector)

        self.INI_selector = FileExplorerLayout("GARPOS INI file", req=True)
        self.input_layout.addLayout(self.INI_selector)

        self.SeaGap_folder_selector = FolderExplorerLayout("output SeaGap files folder", req=True)
        self.input_layout.addLayout(self.SeaGap_folder_selector)

        self.prefix = QLineEdit("fromGARPOS_")
        self.input_layout.addWidget(self.prefix)

        self.split_radio = QRadioButton("Split sets into multiple files")
        self.input_layout.addWidget(self.split_radio)

        self.run_convert_button = QPushButton("Convert")
        self.run_convert_button.clicked.connect(self.run_convert)
        self.input_layout.addWidget(self.run_convert_button)
        self.layout.addLayout(self.input_layout)
        # self.layout.addWidget(self.graph_img)

        QBtn = (
                QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setDisabled(True)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.input_layout.addWidget(self.buttonBox)
        self.input_layout.addWidget(self.statusbar)

        self.setLayout(self.layout)


    def run_convert(self):
        if self.OBS_selector.line_edit.text() == "" or self.SVP_selector.line_edit.text() == "" or self.INI_selector.line_edit.text() == "" or self.SeaGap_folder_selector.line_edit.text() == "":
            print("Lacking converter parameters")
            self.statusbar.showMessage("Lacking converter parameters")
            return

        path_OBS = self.OBS_selector.line_edit.text()
        path_SVP = self.SVP_selector.line_edit.text()
        path_INI = self.INI_selector.line_edit.text()
        SG_folder = self.SeaGap_folder_selector.line_edit.text()
        prefix = self.prefix.text()

        path_SG_PXP = join(SG_folder, prefix+"pxp-ini.inp")
        path_SG_OBS = join(SG_folder, prefix+"obsdata.inp")
        path_SG_SSP = join(SG_folder, prefix+"ss_prof.inp")
        path_SG_ANT = join(SG_folder, prefix+"tr-ant.inp")

        GARPOS2SeaGap(path_OBS, path_SVP, path_INI, path_SG_PXP, path_SG_OBS, path_SG_SSP, path_SG_ANT, split_sets=self.split_radio.isChecked())
        self.buttonBox.setDisabled(False)


class TtresDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("ttres")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.lat_selector = DoubleSelector(-89.99, 89.99, "Latitude", True)
        self.input_layout.addLayout(self.lat_selector)

        self.TR_DEPTH_selector = DoubleSelector(0, 99999.0, "Surface transducer depth", True)
        self.input_layout.addLayout(self.TR_DEPTH_selector)

        self.run_ttres_button = QPushButton("Plot")
        self.run_ttres_button.clicked.connect(self.run_ttres)
        self.input_layout.addWidget(self.run_ttres_button)

        self.actualize_graph_button = QPushButton("Actualize Graph")
        self.actualize_graph_button.clicked.connect(self.actualize_graph)
        self.input_layout.addWidget(self.actualize_graph_button)

        self.input_layout.addWidget(self.statusbar)

        self.graph_img = QLabel()
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.graph_img)

        self.setLayout(self.layout)

        self.actualize_graph()

    def actualize_graph(self):
        if 'tmp_ttres_ttres.png' in os.listdir("gui_tmp") :
            pixmap = QPixmap("gui_tmp/tmp_ttres_ttres.png")
            self.graph_img.setPixmap(
                pixmap.scaled(pixmap.width() // 1.5, pixmap.height() // 1.5, Qt.AspectRatioMode.KeepAspectRatio))
            self.graph_img.repaint()
        else :
            self.graph_img.clear()
            self.graph_img.repaint()

# TAG1

    def run_ttres(self):
        print("Running Ttres...")
        self.graph_img.clear()
        self.graph_img.repaint()
        if self.lat_selector.line_edit.text() == "" or self.TR_DEPTH_selector.line_edit.text() == "":
            print("Lacking denoise parameters")
            self.statusbar.showMessage("Lacking denoise parameters")
            return

        lat = float(self.lat_selector.line_edit.text())
        TR_DEPTH = float(self.TR_DEPTH_selector.line_edit.text())
        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")


        proc = Process(target=ttres_proc, args=(lat, TR_DEPTH, path_ANT, path_PXP, path_SSP, path_OBS, "gui_tmp/tmp_ttres_ttres.out", "gui_tmp/tmp_ttres_log.txt"), kwargs={"proj_fold":proj_fold})
        proc.start()



    def accept(self):
        try :
            # os.remove("gui_tmp/tmp_ttres_ttres.png")
            os.remove("gui_tmp/tmp_ttres_ttres.out")
            os.remove("gui_tmp/tmp_ttres_log.txt")
        except :
            pass
        super().accept()

    def reject(self):
        # try :
        #     os.remove("gui_tmp/tmp_ttres_ttres.png")
        # except :
        #     pass
        try :
            os.remove("gui_tmp/tmp_ttres_ttres.out")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_ttres_log.txt")
        except :
            pass
        super().reject()








class MCMCGradVPlotDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("MCMC Grad V plot")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.fig_layout = QHBoxLayout()

        self.folder_selector = FolderExplorerLayout("MCMC Grad V results folder", req=True)
        self.input_layout.addLayout(self.folder_selector)

        self.nshuffle_selector = IntSelector(1, 999999999, "number of plots for each parameter", req=True, backText="0 < nshuffle < nb iteration/NA")
        self.input_layout.addLayout(self.nshuffle_selector)

        self.NA_selector = IntSelector(1, 9999999, "Sampling interval of the MCMC prcessing", req=False, backText="(def : 5)")
        self.input_layout.addLayout(self.NA_selector)


        self.layout.addLayout(self.input_layout)

        self.graph_img1 = QLabel()
        self.fig_layout.addWidget(self.graph_img1)

        self.graph_img2 = QLabel()
        self.fig_layout.addWidget(self.graph_img2)

        self.layout.addLayout(self.fig_layout)

        self.run_mcmcgradv_plot_button = QPushButton("Run MCMC Grad V plot")
        self.run_mcmcgradv_plot_button.clicked.connect(self.run_mcmcgradv_plot)
        self.input_layout.addWidget(self.run_mcmcgradv_plot_button)

        self.input_layout.addWidget(self.statusbar)

        QBtn = (
                QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setDisabled(True)
        self.buttonBox.accepted.connect(self.accept)

        self.setLayout(self.layout)

        client = docker.from_env()
        self.cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(self.l_path[4]) + ":/app"])



    def run_mcmcgradv_plot(self):
        # self.graph_img1.clear()
        # self.graph_img1.repaint()
        # self.graph_img2.clear()
        # self.graph_img2.repaint()
        if self.folder_selector.line_edit.text() == "" and self.nshuffle_selector.line_edit.text() == "":
            print("Lacking folder")
            self.statusbar.showMessage("Lacking folder")
            return
        nshuffle = int(self.nshuffle_selector.line_edit.text())
        if self.NA_selector.line_edit.text() != "":
            NA = int(self.NA_selector.line_edit.text())
        else:
            NA = 5

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path

        mcmcgradv_folder = os.path.relpath(self.folder_selector.line_edit.text(), proj_fold).replace("\\", "/")

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")

        l_params1 = [nshuffle, join(mcmcgradv_folder, "static_array_mcmcgradv_mcmc.out").replace("\\", "/"), join(mcmcgradv_folder, "static_array_mcmcgradv_resfig.png").replace("\\", "/")]
        l_params2 = [NA, nshuffle, join(mcmcgradv_folder, "static_array_mcmcgradv_sample.out").replace("\\", "/"), join(mcmcgradv_folder, "static_array_mcmcgradv_paramfig.png").replace("\\", "/")]
        _, stream = self.cont.exec_run('''julia -e 'using SeaGap;
        SeaGap.plot_mcmcres_gradv(nshuffle={0}, fn=\"{1}\", show=false, fno=\"{2}\"); '''.format(*l_params1)+
        ''' SeaGap.plot_mcmcparam_gradv({0}, nshuffle={1}, fn=\"{2}\", show=false, fno=\"{3}\")' '''.format(*l_params2), stream=True)
        for data in stream:
            print(data.decode(), end='')

        # self.jl.SeaGap.plot_mcmcres_gradv(nshuffle=nshuffle, fn=join(mcmcgradv_folder, "static_array_mcmcgradv_mcmc.out"), show=False, fno=join(mcmcgradv_folder, "static_array_mcmcgradv_resfig.png")) #, fno="gui_tmp/test.png"
        #
        # self.jl.SeaGap.plot_mcmcparam_gradv(NA, nshuffle=nshuffle, fn=join(mcmcgradv_folder, "static_array_mcmcgradv_sample.out"), show=False, fno=join(mcmcgradv_folder, "static_array_mcmcgradv_paramfig.png")) #, fno="gui_tmp/test.png"

        pixmap1 = QPixmap(join(mcmcgradv_folder, "static_array_mcmcgradv_resfig.png"))
        self.graph_img1.setPixmap(
            pixmap1.scaled(pixmap1.width() // 1, pixmap1.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        self.graph_img1.repaint()
        #
        pixmap2 = QPixmap(join(mcmcgradv_folder, "static_array_mcmcgradv_paramfig.png"))
        self.graph_img2.setPixmap(
            pixmap2.scaled(pixmap2.width() // 1, pixmap2.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        self.graph_img2.repaint()

    def accept(self):
        self.cont.stop(timeout=0)
        super().accept()

    def reject(self):
        self.cont.stop(timeout=0)
        super().reject()


class Histogram2DGradVPlotDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("Histogram 2D Grad V plot")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.fig_layout = QHBoxLayout()

        self.folder_selector = FolderExplorerLayout("MCMC Grad V results folder", req=True)
        self.input_layout.addLayout(self.folder_selector)

        self.nshuffle_selector = IntSelector(1, 999999999, "number of plots for each parameter", req=True, backText="0 < nshuffle < nb of samples")
        self.input_layout.addLayout(self.nshuffle_selector)


        self.layout.addLayout(self.input_layout)

        self.graph_img1 = QLabel()
        self.fig_layout.addWidget(self.graph_img1)

        self.graph_img2 = QLabel()
        self.fig_layout.addWidget(self.graph_img2)

        self.layout.addLayout(self.fig_layout)

        self.run_histogram2dgradv_plot_button = QPushButton("Run Histogram 2D Grad V plot")
        self.run_histogram2dgradv_plot_button.clicked.connect(self.run_histogram2dgradv_plot)
        self.input_layout.addWidget(self.run_histogram2dgradv_plot_button)

        self.input_layout.addWidget(self.statusbar)

        QBtn = (
                QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setDisabled(True)
        self.buttonBox.accepted.connect(self.accept)

        self.setLayout(self.layout)

        client = docker.from_env()
        self.cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(self.l_path[4]) + ":/app"])

    def run_histogram2dgradv_plot(self):
        # self.graph_img1.clear()
        # self.graph_img1.repaint()
        # self.graph_img2.clear()
        # self.graph_img2.repaint()
        if self.folder_selector.line_edit.text() == "" and self.nshuffle_selector.line_edit.text() == "":
            print("Lacking parameters")
            self.statusbar.showMessage("Lacking parameters")
            return
        nshuffle = int(self.nshuffle_selector.line_edit.text())

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path

        mcmcgradv_folder = os.path.relpath(self.folder_selector.line_edit.text(), proj_fold).replace("\\", "/")

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")

        l_params1 = [nshuffle, join(mcmcgradv_folder, "static_array_mcmcgradv_sample.out").replace("\\", "/"), join(mcmcgradv_folder, "static_array_mcmcgradv_hist2dfig.png").replace("\\", "/")]
        l_params2 = [join(mcmcgradv_folder, "static_array_mcmcgradv_sample.out").replace("\\", "/"), join(mcmcgradv_folder, "static_array_mcmcgradv_corrfig.png").replace("\\", "/")]

        _, stream = self.cont.exec_run(
            '''julia -e 'using SeaGap; SeaGap.plot_histogram2d_gradv(nshuffle={0}, fn=\"{1}\", show=false, fno=\"{2}\");'''.format(*l_params1) +
            '''SeaGap.plot_cormap_gradv(fn=\"{0}\", show=false, fno=\"{1}\")' '''.format(*l_params2)
            , stream=True)
        for data in stream:
            print(data.decode(), end='')

        pixmap1 = QPixmap(join(mcmcgradv_folder, "static_array_mcmcgradv_hist2dfig.png"))
        self.graph_img1.setPixmap(
            pixmap1.scaled(pixmap1.width() // 1, pixmap1.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        self.graph_img1.repaint()

        pixmap2 = QPixmap(join(mcmcgradv_folder, "static_array_mcmcgradv_corrfig.png"))
        self.graph_img2.setPixmap(
            pixmap2.scaled(pixmap2.width() // 1, pixmap2.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        self.graph_img2.repaint()


        # self.jl.SeaGap.plot_histogram2d_gradv(nshuffle=nshuffle, fn=join(mcmcgradv_folder, "static_array_mcmcgradv_sample.out"), show=False, fno=join(mcmcgradv_folder, "static_array_mcmcgradv_hist2dfig.png"))
        #
        #
        #
        # self.jl.SeaGap.plot_cormap_gradv(fn=join(mcmcgradv_folder, "static_array_mcmcgradv_sample.out"), show=False, fno=join(mcmcgradv_folder, "static_array_mcmcgradv_corrfig.png"))
        #
        # pixmap2 = QPixmap(join(mcmcgradv_folder, "static_array_mcmcgradv_corrfig.png"))
        # self.graph_img2.setPixmap(
        #     pixmap2.scaled(pixmap2.width() // 1, pixmap2.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        # self.graph_img2.repaint()

    def accept(self):
        self.cont.stop(timeout=0)
        super().accept()

    def reject(self):
        self.cont.stop(timeout=0)
        super().reject()


class NTDMCMCGradVPlotDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("NTD MCMC Grad V plot")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.fig_layout = QHBoxLayout()

        self.folder_selector = FolderExplorerLayout("MCMC Grad V results folder", req=True)
        self.input_layout.addLayout(self.folder_selector)


        self.layout.addLayout(self.input_layout)

        self.graph_img1 = QLabel()
        self.fig_layout.addWidget(self.graph_img1)

        self.layout.addLayout(self.fig_layout)

        self.run_ntdmcmcgradv_plot_button = QPushButton("Run NTD MCMC Grad V plot")
        self.run_ntdmcmcgradv_plot_button.clicked.connect(self.run_ntdmcmcgradv_plot)
        self.input_layout.addWidget(self.run_ntdmcmcgradv_plot_button)

        self.input_layout.addWidget(self.statusbar)

        QBtn = (
                QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setDisabled(True)
        self.buttonBox.accepted.connect(self.accept)

        self.setLayout(self.layout)

        client = docker.from_env()
        self.cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(self.l_path[4]) + ":/app"])

    def run_ntdmcmcgradv_plot(self):
        # self.graph_img1.clear()
        # self.graph_img1.repaint()
        if self.folder_selector.line_edit.text() == "" :
            print("Lacking folder")
            self.statusbar.showMessage("Lacking folder")
            return

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path

        mcmcgradv_folder = os.path.relpath(self.folder_selector.line_edit.text(), proj_fold).replace("\\", "/")

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")


        l_params = [join(mcmcgradv_folder, "static_array_mcmcgradv_residual.out").replace("\\", "/"), join(mcmcgradv_folder, "static_array_mcmcgradv_ntdfig.png").replace("\\", "/")]

        _, stream = self.cont.exec_run('''julia -e 'using SeaGap; SeaGap.plot_ntd_gradv(fn=\"{0}\", show=false, fno=\"{1}\")' '''.format(*l_params), stream=True)
        for data in stream:
            print(data.decode(), end='')

        # self.jl.SeaGap.plot_ntd_gradv(fn=join(mcmcgradv_folder, "static_array_mcmcgradv_residual.out"), show=False, fno=join(mcmcgradv_folder, "static_array_mcmcgradv_ntdfig.png"))

        pixmap1 = QPixmap(join(mcmcgradv_folder, "static_array_mcmcgradv_ntdfig.png"))
        self.graph_img1.setPixmap(
            pixmap1.scaled(pixmap1.width() // 1, pixmap1.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        self.graph_img1.repaint()

    def accept(self):
        self.cont.stop(timeout=0)
        super().accept()

    def reject(self):
        self.cont.stop(timeout=0)
        super().reject()

class StaticArrayDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("Static array")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.lat_selector = DoubleSelector(-89.99, 89.99, "Latitude", True)
        self.input_layout.addLayout(self.lat_selector)

        self.TR_DEPTH_selector = DoubleSelector(0.0, 99999.0, "Surface transducer depth", True)
        self.input_layout.addLayout(self.TR_DEPTH_selector)

        self.NPB_selector = IntSelector(3, 99999, "Number of temporal B-spline bases", False, backText="(def : 100)")
        self.input_layout.addLayout(self.NPB_selector)

        self.eps_selector = DoubleSelector(0.0, 99999.0, "Convergence threshold", False, backText="(def : 1.e-4)")
        self.input_layout.addLayout(self.eps_selector)

        self.ITMAX_selector = IntSelector(1, 99999, "Max. number of iterations", False, backText="(def : 50)")
        self.input_layout.addLayout(self.ITMAX_selector)

        self.delta_pos_selector = DoubleSelector(0, 99999.0, "Infinitesimal distance value for Jacobian matrix", False, backText="(def : 1.e-4)")
        self.input_layout.addLayout(self.delta_pos_selector)

        self.folder_selector = FolderExplorerLayout("Static array folder")
        self.input_layout.addLayout(self.folder_selector)

        self.run_static_array_button = QPushButton("Run static array")
        self.run_static_array_button.clicked.connect(self.run_static_array)
        self.input_layout.addWidget(self.run_static_array_button)

        self.input_layout.addWidget(self.statusbar)

        self.graph_img = QLabel()
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.graph_img)

        QBtn = (
                QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setDisabled(True)
        self.buttonBox.accepted.connect(self.accept)

        self.input_layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    #TAG2

    def run_static_array(self):
        print("Running static_array...")
        if self.lat_selector.line_edit.text() == "" or self.TR_DEPTH_selector.line_edit.text() == "" or self.folder_selector.line_edit.text() == "":
            print("lacking static array parameters")
            self.statusbar.showMessage("Lacking static array parameters")
            return

        if not exists(self.folder_selector.line_edit.text()):
            print("Wrong path entered")
            self.statusbar.showMessage("Wrong path entered")
            return

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path
        lat = float(self.lat_selector.line_edit.text())
        folder_path = self.folder_selector.line_edit.text()
        TR_DEPTH = float(self.TR_DEPTH_selector.line_edit.text())
        if self.NPB_selector.line_edit.text() != "":
            NPB = int(self.NPB_selector.line_edit.text())
        else:
            NPB = 100
        if self.eps_selector.line_edit.text() != "":
            eps = float(self.eps_selector.line_edit.text())
        else:
            eps = 0.0001
        if self.ITMAX_selector.line_edit.text() != "":
            ITMAX = int(self.ITMAX_selector.line_edit.text())
        else:
            ITMAX = 50
        if self.delta_pos_selector.line_edit.text() != "":
            delta_pos = float(self.delta_pos_selector.line_edit.text())
        else:
            delta_pos = 0.0001

        log_path =  os.path.relpath(os.path.join(folder_path, "static_array_log.out"), proj_fold).replace("\\", "/")
        solve_path =  os.path.relpath(os.path.join(folder_path, "static_array_solve.out"), proj_fold).replace("\\", "/")
        position_path =  os.path.relpath(os.path.join(folder_path, "static_array_position.out"), proj_fold).replace("\\", "/")
        residual_path =  os.path.relpath(os.path.join(folder_path, "static_array_residual.out"), proj_fold).replace("\\", "/")
        bspline_path =  os.path.relpath(os.path.join(folder_path, "static_array_bspline.out"), proj_fold).replace("\\", "/")
        AICBIC_path =  os.path.relpath(os.path.join(folder_path, "static_array_AICBIC.out"), proj_fold).replace("\\", "/")

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")

        proc = Process(target=static_array_proc, args=(lat, TR_DEPTH, NPB, path_ANT, path_PXP, path_SSP, path_OBS, eps, ITMAX, delta_pos, log_path, solve_path, position_path, residual_path, bspline_path, AICBIC_path), kwargs={"proj_fold": proj_fold})
        proc.start()



        # bspline_path = os.path.relpath(os.path.join(folder_path, "static_array_individual_bspline.out"), proj_fold).replace("\\", "/")

        # self.jl.SeaGap.static_array(lat, juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), NPB, fn1=path_ANT, fn2=path_PXP, fn3=path_SSP, fn4=path_OBS, eps=eps, ITMAX=ITMAX, delta_pos=delta_pos, fno0=log_path, fno1=solve_path, fno2=position_path, fno3=residual_path, fno4=bspline_path, fno5=AICBIC_path)

        self.buttonBox.setDisabled(False)


        
        
class StaticArrayGradDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("Static array grad")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.lat_selector = DoubleSelector(-89.99, 89.99, "Latitude", True)
        self.input_layout.addLayout(self.lat_selector)

        self.TR_DEPTH_selector = DoubleSelector(0.0, 99999.0, "Surface transducer depth", True)
        self.input_layout.addLayout(self.TR_DEPTH_selector)

        self.NPB_selector = IntSelector(3, 99999, "Number of temporal B-spline bases", False, backText="(def : 100)")
        self.input_layout.addLayout(self.NPB_selector)

        self.ITMAX_selector = IntSelector(1, 99999, "Max. number of iterations", False, backText="(def : 50)")
        self.input_layout.addLayout(self.ITMAX_selector)

        self.delta_pos_selector = DoubleSelector(0, 99999.0, "Infinitesimal distance value for Jacobian matrix", False, backText="(def : 1.e-4)")
        self.input_layout.addLayout(self.delta_pos_selector)

        self.folder_selector = FolderExplorerLayout("Static array grad folder")
        self.input_layout.addLayout(self.folder_selector)

        self.run_static_array_grad_button = QPushButton("Run static array grad")
        self.run_static_array_grad_button.clicked.connect(self.run_static_array_grad)
        self.input_layout.addWidget(self.run_static_array_grad_button)

        self.input_layout.addWidget(self.statusbar)

        self.graph_img = QLabel()
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.graph_img)

        # QBtn = (
        #         QDialogButtonBox.Ok
        # )
        #
        # self.buttonBox = QDialogButtonBox(QBtn)
        # self.buttonBox.setDisabled(True)
        # self.buttonBox.accepted.connect(self.accept)
        #
        # self.input_layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

# TAG3

    def run_static_array_grad(self):
        print("Running static_array_grad...")
        if self.lat_selector.line_edit.text() == "" or self.TR_DEPTH_selector.line_edit.text() == "" or self.folder_selector.line_edit.text() == "":
            print("lacking static array parameters")
            self.statusbar.showMessage("lacking static array parameters")
            return

        if not exists(self.folder_selector.line_edit.text()):
            print("Wrong path entered")
            self.statusbar.showMessage("Wrong path entered")
            return

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path
        lat = float(self.lat_selector.line_edit.text())
        folder_path = self.folder_selector.line_edit.text()
        TR_DEPTH = float(self.TR_DEPTH_selector.line_edit.text())
        if self.NPB_selector.line_edit.text() != "":
            NPB = int(self.NPB_selector.line_edit.text())
        else:
            NPB = 100
        if self.ITMAX_selector.line_edit.text() != "":
            ITMAX = int(self.ITMAX_selector.line_edit.text())
        else:
            ITMAX = 50
        if self.delta_pos_selector.line_edit.text() != "":
            delta_pos = float(self.delta_pos_selector.line_edit.text())
        else:
            delta_pos = 0.0001
        log_path = os.path.relpath(os.path.join(folder_path, "static_array_grad_log.out"), proj_fold).replace("\\", "/")
        solve_path = os.path.relpath(os.path.join(folder_path, "static_array_grad_solve.out"), proj_fold).replace("\\", "/")
        position_path = os.path.relpath(os.path.join(folder_path, "static_array_grad_position.out"), proj_fold).replace("\\", "/")
        residual_path = os.path.relpath(os.path.join(folder_path, "static_array_grad_residual.out"), proj_fold).replace("\\", "/")
        bspline_path = os.path.relpath(os.path.join(folder_path, "static_array_grad_bspline.out"), proj_fold).replace("\\", "/")

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")


        proc = Process(target=static_array_grad_proc, args=(lat, TR_DEPTH, NPB, path_ANT, path_PXP, path_SSP, path_OBS, ITMAX, delta_pos, log_path, solve_path, position_path, residual_path, bspline_path), kwargs={"proj_fold": proj_fold})
        proc.start()

        # lat, TR_DEPTH, NPB, path_ANT, path_PXP, path_SSP, path_OBS, ITMAX, delta_pos, log_path, solve_path, position_path, residual_path, bspline_path

        # self.jl.SeaGap.static_array_grad(lat, juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), NPB, fn1=path_ANT, fn2=path_PXP, fn3=path_SSP, fn4=path_OBS, ITMAX=ITMAX, delta_pos=delta_pos, fno0=log_path, fno1=solve_path, fno2=position_path, fno3=residual_path, fno4=bspline_path)

        # self.buttonBox.setDisabled(False)


class StaticArrayMCMCGradVDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()

        self.statusbar = QStatusBar(self)
        self.setWindowTitle("Static array MCMC grad V")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.fig_layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.lat_selector = DoubleSelector(-89.99, 89.99, "Latitude", True)
        self.input_layout.addLayout(self.lat_selector)

        self.dep_selector = DoubleSelector(0.0, 99999.0, "Water depth of the site (km)", True)
        self.input_layout.addLayout(self.dep_selector)

        self.TR_DEPTH_selector = DoubleSelector(0.0, 99999.0, "Surface transducer depth", True)
        self.input_layout.addLayout(self.TR_DEPTH_selector)

        self.NPB1_selector = IntSelector(3, 99999, "Number of L-NTD B-spline bases", False, backText="(def : 5)")
        self.input_layout.addLayout(self.NPB1_selector)

        self.NPB2_selector = IntSelector(3, 99999, "Number of S-NTD B-spline bases", False, backText="(def : 100)")
        self.input_layout.addLayout(self.NPB2_selector)

        self.NPB3_selector = IntSelector(3, 99999, "Number of shallow gradient B-spline bases", False, backText="(def : 5)")
        self.input_layout.addLayout(self.NPB3_selector)

        self.NPB4_selector = IntSelector(3, 99999, "Number of gradient depth B-spline bases", False, backText="(def : 1)")
        self.input_layout.addLayout(self.NPB4_selector)

        self.NSB_selector = IntSelector(3, 99999, "Number of the perturbated bases for each iteration", False, backText="(def : 100)")
        self.input_layout.addLayout(self.NSB_selector)

        self.gm_selector = DoubleSelector(0.0, 999999999.0, "Mean value for shallow gradient constraint", False, backText="(def : 0.0)")
        self.input_layout.addLayout(self.gm_selector)

        self.gs_selector = DoubleSelector(0.0, 999999999.0, "Std value for shallow gradient constraint", False, backText="(def : 0.00005)")
        self.input_layout.addLayout(self.gs_selector)

        self.dm_selector = DoubleSelector(0.0, 999999999.0, "Mean value for gradient depth constraint", False, backText="(def : 0.65)")
        self.input_layout.addLayout(self.dm_selector)

        self.ds_selector = DoubleSelector(0.0, 999999999.0, "Std value for gradient depth constraint", False, backText="(def : 0.15)")
        self.input_layout.addLayout(self.ds_selector)

        self.rm_selector = DoubleSelector(0.0, 999999999.0, "Mean value for relative gradient depth constraint", False, backText="(def : 0.0)")
        self.input_layout.addLayout(self.rm_selector)

        self.rs_selector = DoubleSelector(0.0, 999999999.0, "Std value for relative gradient depth constraint", False, backText="(def : 0.1)")
        self.input_layout.addLayout(self.rs_selector)

        self.nloop_selector = IntSelector(3, 999999999, "Total number of the MCMC iterations", False, backText="(def : 600000)")
        self.input_layout.addLayout(self.nloop_selector)

        self.nburn_selector = IntSelector(3, 999999999, "Burn-in period of the MCMC iterations", False, backText="(def : 100000)")
        self.input_layout.addLayout(self.nburn_selector)

        self.folder_selector = FolderExplorerLayout("Static array MCMC grad folder")
        self.input_layout.addLayout(self.folder_selector)

        self.run_static_array_mcmcgradv_button = QPushButton("Run static array MCMC grad V")
        self.run_static_array_mcmcgradv_button.clicked.connect(self.run_static_array_mcmcgradv)
        self.input_layout.addWidget(self.run_static_array_mcmcgradv_button)

        self.actualize_graph_button = QPushButton("Actualize Graph")
        self.actualize_graph_button.clicked.connect(self.actualize_graph)
        self.input_layout.addWidget(self.actualize_graph_button)

        self.input_layout.addWidget(self.statusbar)

        self.layout.addLayout(self.input_layout)

        self.graph_img1 = QLabel()
        self.fig_layout.addWidget(self.graph_img1)
        self.graph_img2 = QLabel()
        self.fig_layout.addWidget(self.graph_img2)

        self.layout.addLayout(self.fig_layout)

        # QBtn = (
        #         QDialogButtonBox.Ok
        # )
        #
        # self.buttonBox = QDialogButtonBox(QBtn)
        # self.buttonBox.setDisabled(True)
        # self.buttonBox.accepted.connect(self.accept)

        # self.input_layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def actualize_graph(self):
        folder_path = self.folder_selector.line_edit.text()
        if folder_path != "" :
            if 'static_array_mcmcgradv_resfig.png' in os.listdir(folder_path) :
                pixmap1 = QPixmap(os.path.join(folder_path, "static_array_mcmcgradv_resfig.png"))
                self.graph_img1.setPixmap(
                    pixmap1.scaled(pixmap1.width() // 1.5, pixmap1.height() // 1.5, Qt.AspectRatioMode.KeepAspectRatio))
                self.graph_img1.repaint()
            else :
                self.graph_img1.clear()
                self.graph_img1.repaint()


            if 'static_array_mcmcgradv_paramfig.png' in os.listdir(folder_path) :
                pixmap2 = QPixmap(os.path.join(folder_path, "static_array_mcmcgradv_paramfig.png"))
                self.graph_img2.setPixmap(
                    pixmap2.scaled(pixmap2.width() // 1.5, pixmap2.height() // 1.5, Qt.AspectRatioMode.KeepAspectRatio))
                self.graph_img2.repaint()
            else :
                self.graph_img2.clear()
                self.graph_img2.repaint()

#TAG4

    def run_static_array_mcmcgradv(self):
        print("running static_array_mcmcgradv ...")
        # self.graph_img1.clear()
        # self.graph_img1.repaint()
        # self.graph_img2.clear()
        # self.graph_img2.repaint()
        if self.lat_selector.line_edit.text() == "" or self.TR_DEPTH_selector.line_edit.text() == "" or self.folder_selector.line_edit.text() == "" or self.dep_selector.line_edit.text() == "":
            print("Lacking static array MCMC grad V parameters")
            self.statusbar.showMessage("Lacking static array MCMC grad V parameters")
            return

        if not exists(self.folder_selector.line_edit.text()):
            print("Wrong path entered")
            self.statusbar.showMessage("Wrong path entered")
            return

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path
        lat = float(self.lat_selector.line_edit.text())
        folder_path = self.folder_selector.line_edit.text()
        TR_DEPTH = float(self.TR_DEPTH_selector.line_edit.text())
        dep = float(self.dep_selector.line_edit.text())
        if self.NPB1_selector.line_edit.text() != "":
            NPB1 = int(self.NPB1_selector.line_edit.text())
        else:
            NPB1 = 5
        if self.NPB2_selector.line_edit.text() != "":
            NPB2 = int(self.NPB2_selector.line_edit.text())
        else:
            NPB2 = 100
        if self.NPB3_selector.line_edit.text() != "":
            NPB3 = int(self.NPB3_selector.line_edit.text())
        else:
            NPB3 = 5
        if self.NPB4_selector.line_edit.text() != "":
            NPB4 = int(self.NPB4_selector.line_edit.text())
        else:
            NPB4 = 1
        if self.gm_selector.line_edit.text() != "":
            gm = float(self.gm_selector.line_edit.text())
        else:
            gm = 0.0
        if self.gs_selector.line_edit.text() != "":
            gs = float(self.gs_selector.line_edit.text())
        else:
            gs = 0.00005

        if self.dm_selector.line_edit.text() != "":
            dm = float(self.dm_selector.line_edit.text())
        else:
            dm = 0.65
        if self.ds_selector.line_edit.text() != "":
            ds = float(self.ds_selector.line_edit.text())
        else:
            ds = 0.15

        if self.rm_selector.line_edit.text() != "":
            rm = float(self.rm_selector.line_edit.text())
        else:
            rm = 0.0
        if self.rs_selector.line_edit.text() != "":
            rs = float(self.rs_selector.line_edit.text())
        else:
            rs = 0.1


        if self.nloop_selector.line_edit.text() != "":
            nloop = int(self.nloop_selector.line_edit.text())
        else:
            nloop = 600000
        if self.nburn_selector.line_edit.text() != "":
            nburn = int(self.nburn_selector.line_edit.text())
        else:
            nburn = 100000

        # if self.lscale_selector.line_edit.text() != "":
        #     lscale = float(self.lscale_selector.line_edit.text())
        # else:
        #     lscale = 1.0

        nshuffle = (nloop-nburn)//5-1


        log_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_log.out"), proj_fold).replace("\\", "/")
        sample_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_sample.out"), proj_fold).replace("\\", "/")
        mcmc_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_mcmc.out"), proj_fold).replace("\\", "/")
        position_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_position.out"), proj_fold).replace("\\", "/")
        statistics_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_statistics.out"), proj_fold).replace("\\", "/")
        acceptance_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_acceptance.out"), proj_fold).replace("\\", "/")
        residual_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_residual.out"), proj_fold).replace("\\", "/")
        bspline_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_bspline.out"), proj_fold).replace("\\", "/")
        gradient_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_gradient.out"), proj_fold).replace("\\", "/")
        initial_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_initial.out"), proj_fold).replace("\\", "/")
        resfig_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_resfig.png"), proj_fold).replace("\\", "/")
        paramfig_path = os.path.relpath(os.path.join(folder_path, "static_array_mcmcgradv_paramfig.png"), proj_fold).replace("\\", "/")

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")

        proc = Process(target=static_array_mcmcgradv_proc, args=(lat, dep, TR_DEPTH, 0.0, NPB1, NPB2, NPB3, NPB4, path_ANT, path_PXP, path_SSP, path_OBS, "gui_tmp/tmp_static_array_s_log.txt", "gui_tmp/tmp_static_array_s_solve.out", "gui_tmp/tmp_static_array_s_position.out", "gui_tmp/tmp_static_array_s_residual_sdls.out", "gui_tmp/tmp_static_array_s_S-NTD.out", "gui_tmp/tmp_static_array_s_ABIC.out", "gui_tmp/tmp_static_array_s_gradient.out", gm, dm, ds, rm, rs, nloop, nburn, log_path, sample_path, mcmc_path, position_path, statistics_path, acceptance_path, residual_path, bspline_path, gradient_path, initial_path, nshuffle, resfig_path, paramfig_path), kwargs={"proj_fold": proj_fold})
        proc.start()

        # lat, TR_DEPTH, 0.0, NPB1, NPB2, path_ANT, path_PXP, path_SSP, path_OBS, "gui_tmp/tmp_static_array_s_log.txt", "gui_tmp/tmp_static_array_s_solve.out", "gui_tmp/tmp_static_array_s_position.out", "gui_tmp/tmp_static_array_s_residual_sdls.out", "gui_tmp/tmp_static_array_s_S-NTD.out", "gui_tmp/tmp_static_array_s_ABIC.out", "gui_tmp/tmp_static_array_s_gradient.out"

        # self.jl.SeaGap.static_array_s(lat, juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), 0.0, NPB1, NPB2, fn1=path_ANT, fn2=path_PXP, fn3=path_SSP, fn4=path_OBS, fno0="gui_tmp/tmp_static_array_s_log.txt",fno1="gui_tmp/tmp_static_array_s_solve.out",fno2="gui_tmp/tmp_static_array_s_position.out",fno3="gui_tmp/tmp_static_array_s_residual_sdls.out",fno4="gui_tmp/tmp_static_array_s_S-NTD.out",fno5="gui_tmp/tmp_static_array_s_ABIC.out",fno6="gui_tmp/tmp_static_array_s_gradient.out")
        # self.jl.SeaGap.make_initial_gradv(NPB1, NPB2, fn="gui_tmp/tmp_static_array_s_solve.out", fno="gui_tmp/tmp_static_array_s_initial.inp")
        # self.jl.SeaGap.static_array_mcmcgradv(lat, dep, juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), NPB1, NPB2, NPB3, NPB4, gm=gm, gs=gs, dm=dm, ds=ds, rm=rm, rs=rs, nloop=nloop, nburn=nburn, fn1=path_ANT, fn2=path_PXP, fn3=path_SSP, fn4=path_OBS, fn5="gui_tmp/tmp_static_array_s_initial.inp", fno0=log_path, fno1=sample_path, fno2=mcmc_path, fno3=position_path, fno4=statistics_path, fno5=acceptance_path, fno6=residual_path, fno7=bspline_path, fno8=gradient_path, fno9=initial_path)
        #
        # self.jl.SeaGap.plot_mcmcres_gradv(nshuffle=nshuffle, fn=mcmc_path, show=False, fno=resfig_path) #, fno="gui_tmp/test.png"
        #
        # self.jl.SeaGap.plot_mcmcparam_gradv(5, nshuffle=nshuffle, fn=sample_path, show=False, fno=paramfig_path) #, fno="gui_tmp/test.png"

        # pixmap1 = QPixmap(resfig_path)
        # self.graph_img1.setPixmap(
        #     pixmap1.scaled(pixmap1.width() // 1, pixmap1.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        # self.graph_img1.repaint()
        # #
        # pixmap2 = QPixmap(paramfig_path)
        # self.graph_img2.setPixmap(
        #     pixmap2.scaled(pixmap2.width() // 1, pixmap2.height() // 1, Qt.AspectRatioMode.KeepAspectRatio))
        # self.graph_img2.repaint()
        #
        # self.buttonBox.setDisabled(False)

    def accept(self):
        try :
            os.remove("gui_tmp/tmp_static_array_s_log.txt")
            os.remove("gui_tmp/tmp_static_array_s_solve.out")
            os.remove("gui_tmp/tmp_static_array_s_position.out")
            os.remove("gui_tmp/tmp_static_array_s_residual_sdls.out")
            os.remove("gui_tmp/tmp_static_array_s_S-NTD.out")
            os.remove("gui_tmp/tmp_static_array_s_ABIC.out")
            os.remove("gui_tmp/tmp_static_array_s_gradient.out")
            os.remove("gui_tmp/tmp_static_array_s_initial.inp")
        except :
            pass
        super().accept()

    def reject(self):
        try :
            os.remove("gui_tmp/tmp_static_array_s_log.txt")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_static_array_s_solve.out")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_static_array_s_position.out")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_static_array_s_residual_sdls.out")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_static_array_s_S-NTD.out")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_static_array_s_ABIC.out")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_static_array_s_gradient.out")
        except :
            pass
        try :
            os.remove("gui_tmp/tmp_static_array_s_initial.inp")
        except :
            pass
        super().reject()


class StaticIndividualDialog(QDialog):

    def __init__(self, l_path):
        super().__init__()
        self.statusbar = QStatusBar(self)
        self.setWindowTitle("Static individual")
        my_icon = QIcon("./img/logo.png")
        self.setWindowIcon(my_icon)

        self.l_path = l_path

        self.layout = QHBoxLayout()

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignTop)

        self.lat_selector = DoubleSelector(-89.99, 89.99, "Latitude", True)
        self.input_layout.addLayout(self.lat_selector)

        self.TR_DEPTH_selector = DoubleSelector(0.0, 99999.0, "Surface transducer depth", True)
        self.input_layout.addLayout(self.TR_DEPTH_selector)

        self.NPB_selector = IntSelector(3, 99999, "Number of temporal B-spline bases", False, backText="(def : 100)")
        self.input_layout.addLayout(self.NPB_selector)

        self.eps_selector = DoubleSelector(0.0, 99999.0, "Convergence threshold", False, backText="(def : 1.e-4)")
        self.input_layout.addLayout(self.eps_selector)

        self.ITMAX_selector = IntSelector(1, 99999, "Max. number of iterations", False, backText="(def : 50)")
        self.input_layout.addLayout(self.ITMAX_selector)

        self.delta_pos_selector = DoubleSelector(0, 99999.0, "Infinitesimal distance value for Jacobian matrix", False, backText="(def : 1.e-4)")
        self.input_layout.addLayout(self.delta_pos_selector)

        self.folder_selector = FolderExplorerLayout("Static array individual folder")
        self.input_layout.addLayout(self.folder_selector)

        self.run_static_array_button = QPushButton("Run static array individual")
        self.run_static_array_button.clicked.connect(self.run_static_individual)
        self.input_layout.addWidget(self.run_static_array_button)

        self.input_layout.addWidget(self.statusbar)

        self.graph_img = QLabel()
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.graph_img)

        # QBtn = (
        #         QDialogButtonBox.Ok
        # )
        #
        # self.buttonBox = QDialogButtonBox(QBtn)
        # self.buttonBox.setDisabled(True)
        # self.buttonBox.accepted.connect(self.accept)
        #
        # self.input_layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

# TAG5

    def run_static_individual(self):
        if self.lat_selector.line_edit.text() == "" or self.TR_DEPTH_selector.line_edit.text() == "" or self.folder_selector.line_edit.text() == "":
            print("Lacking static individual parameters")
            self.statusbar.showMessage("Lacking static individual parameters")
            return

        if not exists(self.folder_selector.line_edit.text()):
            print("wrong path entered")
            self.statusbar.showMessage("Wrong path entered")
            return

        path_ANT, path_PXP, path_SSP, path_OBS, proj_fold = self.l_path
        lat = float(self.lat_selector.line_edit.text())
        folder_path = self.folder_selector.line_edit.text()
        TR_DEPTH = float(self.TR_DEPTH_selector.line_edit.text())
        if self.NPB_selector.line_edit.text() != "":
            NPB = int(self.NPB_selector.line_edit.text())
        else:
            NPB = 100
        if self.eps_selector.line_edit.text() != "":
            eps = float(self.eps_selector.line_edit.text())
        else:
            eps = 0.0001
        if self.ITMAX_selector.line_edit.text() != "":
            ITMAX = int(self.ITMAX_selector.line_edit.text())
        else:
            ITMAX = 50
        if self.delta_pos_selector.line_edit.text() != "":
            delta_pos = float(self.delta_pos_selector.line_edit.text())
        else:
            delta_pos = 0.0001
        log_path = os.path.relpath(os.path.join(folder_path, "static_array_individual_log.out"), proj_fold).replace("\\", "/")
        solve_path = os.path.relpath(os.path.join(folder_path, "static_array_individual_solve.out"), proj_fold).replace("\\", "/")
        position_path = os.path.relpath(os.path.join(folder_path, "static_array_individual_position.out"), proj_fold).replace("\\", "/")
        residual_path = os.path.relpath(os.path.join(folder_path, "static_array_individual_residual.out"), proj_fold).replace("\\", "/")
        bspline_path = os.path.relpath(os.path.join(folder_path, "static_array_individual_bspline.out"), proj_fold).replace("\\", "/")

        path_ANT, path_PXP, path_SSP, path_OBS = os.path.relpath(path_ANT).replace("\\", "/"), os.path.relpath(path_PXP).replace("\\", "/"), os.path.relpath(path_SSP).replace("\\", "/"), os.path.relpath(path_OBS).replace("\\", "/")

        proc = Process(target=static_individual_proc, args=(lat, TR_DEPTH, NPB, path_ANT, path_PXP, path_SSP, path_OBS, eps, ITMAX, delta_pos, log_path, solve_path, position_path, residual_path, bspline_path), kwargs={"proj_fold":proj_fold})
        proc.start()



