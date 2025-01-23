import sys
import os
from PyQt5 import QtCore, QtWidgets, uic, QtGui

from mpi4py import MPI

# MPI 초기화
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

save_dir = "StarterOutputs"

# ui 파일 불러오기
def resource_path(relative_path) :
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

macro_form = resource_path('easyStarter.ui')
form_class = uic.loadUiType(macro_form)[0]

class App(QtWidgets.QMainWindow, form_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.imgLoaded = False

        self.elev_slider.setValue(0)
        self.update_elev()
        self.azim_slider.setValue(0)
        self.update_azim()
        
        self.theta1_slider.setValue(0)
        self.update_theta1()
        self.phi1_slider.setValue(0)
        self.update_phi1()
        
        self.theta2_slider.setValue(0)
        self.update_theta2()
        self.phi2_slider.setValue(0)
        self.update_phi2()

        self.mratio_slider.setValue(20)
        self.update_mratio()
        self.peri_slider.setValue(50)
        self.update_peri()

        self.frame_number_slider.setValue(0)
        self.update_frame_number()


        # Connect sliders to the update functions
        self.elev_slider.valueChanged.connect(self.update_elev)
        self.azim_slider.valueChanged.connect(self.update_azim)
        self.theta1_slider.valueChanged.connect(self.update_theta1)
        self.phi1_slider.valueChanged.connect(self.update_phi1)
        self.theta2_slider.valueChanged.connect(self.update_theta2)
        self.phi2_slider.valueChanged.connect(self.update_phi2)
        self.mratio_slider.valueChanged.connect(self.update_mratio)
        self.peri_slider.valueChanged.connect(self.update_peri)
        self.frame_number_slider.valueChanged.connect(self.update_frame_number)
        self.start_btn.clicked.connect(self.startSim)
        self.main_btn.clicked.connect(self.startMain)
        self.camera_btn.clicked.connect(self.startImg)
        self.movie_btn.clicked.connect(self.startMovie)

    def startMain(self) :
        lastfilename = os.path.join("outputs", f"snapshot_t{1000-1:04d}.npy")
        if os.path.isfile(lastfilename) :
            os.remove(lastfilename)
            print("sak jae")
        os.system(f"mpiexec -np 4 python main_mpi.py --nstep {1000} --save_dir outputs --theta1 {self.theta1} --phi1 {self.phi1} --theta2 {self.theta2} --phi2 {self.phi2} --mratio {self.mratio} --peri {self.peri} ")

        while True :
            filename = os.path.join("outputs", f"snapshot_t{1000-1:04d}.npy")
            if os.path.isfile(filename) :
                break

    def startSim(self) :
        os.system(f"mpiexec -np 4 python main_mpi.py --tot_nstar {100000} --nstep {1000} --save_dir {save_dir} --theta1 {self.theta1} --phi1 {self.phi1} --theta2 {self.theta2} --phi2 {self.phi2} --mratio {self.mratio} --peri {self.peri} --frame_number {self.frame_number}")

        while True :
            filename = os.path.join(save_dir, f"snapshot_t{self.frame_number:04d}.npy")
            if os.path.isfile(filename) :
                break
        self.imgLoaded = True
        
        self.startImg()

    def startImg(self) :
        if os.path.isfile(os.path.join(save_dir, f"snapshot_t{self.frame_number:04d}.npy")) :
            os.system(f"python make_image.py --load_dir {save_dir} --save_dir {save_dir} --frame {self.frame_number} --elev {self.elev} --azim {self.azim} --resol 2")
            while True :
                filename = os.path.join(save_dir, f"snapshot_t{self.frame_number:04d}.png")
                if os.path.isfile(filename) :
                    break  
        else :
            print("이미지 없음, 이미지 불러오고 실행하셈")

        pixmap = QtGui.QPixmap(os.path.join(save_dir, f"snapshot_t{self.frame_number:04d}.png"))
        self.img_label.setPixmap(pixmap)
    def startMovie(self) :
        self.startMain()
        if os.path.isfile(f"outputs/snapshot_t{999:04d}.npy") :
            os.system(f"mpiexec -n 10 python make_movie.py --load_dir outputs --elev {self.elev} --azim {self.azim} --name ezStarter")
            while True :
                filename = "ezStarter_mov.mp4"
                if os.path.isfile(filename) :
                    break  


        
    def update_elev(self):
        self.elev = self.elev_slider.value() / 10
        self.elev_label.setText(f"elev : {self.elev:.1f}")
    def update_azim(self):
        self.azim = self.azim_slider.value() / 10
        self.azim_label.setText(f"azim : {self.azim:.1f}")
    def update_theta1(self):
        self.theta1 = self.theta1_slider.value() / 10 
        self.theta1_label.setText(f"theta1 : {self.theta1:.1f}")
    def update_phi1(self):
        self.phi1 = self.phi1_slider.value() / 10 
        self.phi1_label.setText(f"phi1 : {self.phi1:.01f}")
    def update_theta2(self):
        self.theta2 = self.theta2_slider.value() / 10  
        self.theta2_label.setText(f"theta2 : {self.theta2:.01f}")
    def update_phi2(self):
        self.phi2 = self.phi2_slider.value() / 10  
        self.phi2_label.setText(f"phi2 : {self.phi2:.01f}")
    def update_mratio(self):
        self.mratio = self.mratio_slider.value() / 10  
        self.mratio_label.setText(f"mratio : {self.mratio:.01f}")
    def update_peri(self):
        self.peri = self.peri_slider.value() / 10  
        self.peri_label.setText(f"peri : {self.peri:.01f}")
    def update_frame_number(self):
        self.frame_number = self.frame_number_slider.value()
        self.frame_number_label.setText(f"frame_number : {self.frame_number}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = App()
    myWindow.show()
    app.exec_()