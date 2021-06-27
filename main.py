from PyQt5 import QtCore, QtWidgets, QtGui,QtNetwork
import sys
from downlaod_tab import DownloadTabWidget
from activity_tab import ActivityTabWidget
from video_info import VideoInfo
import ffmpeg

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow,self).__init__()
        self.setWindowTitle('YouTube Downloader')
        #self.setGeometry(500,200,600,500)
        self.move(400,100)
    
    def create_tabWidget(self):
        self.tab = QtWidgets.QTabWidget()
        self.tab1 = DownloadTabWidget()

        self.tab2 = ActivityTabWidget()

        self.tab.addTab(self.tab1,'Download')
        self.tab.addTab(self.tab2, 'Activity')
        self.tab1.setupUI()
        self.tab2.setupUI()
        
        self.setCentralWidget(self.tab)

        self.tab1.download_button.clicked.connect(lambda : self.addVideo(url = self.tab1.url, \
            res = self.tab1.res, fps = self.tab1.fps, save_path=self.tab1.savePath))

    def addVideo(self, url, res, fps, save_path):
        
        video = VideoInfo(url, res,fps, save_path)
        video.setupUI()
        self.tab2.Vbox1.addWidget(video)
        self.tab2.Vbox1.update()

if __name__== "__main__":
    application = QtWidgets.QApplication(sys.argv)
    mainWindow = MyWindow()
    mainWindow.create_tabWidget()
    
    style ="./MacOS.qss"
    with open(style,"r") as fh:
        application.setStyleSheet(fh.read())
    
    mainWindow.adjustSize()
    mainWindow.setFixedSize(mainWindow.frameSize())
    mainWindow.show()
    sys.exit(application.exec_())