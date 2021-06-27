from PyQt5 import QtCore, QtWidgets, QtGui
from pytube import YouTube
import pytube
import ffmpeg
import os

class DownloadTabWidget(QtWidgets.QWidget):
    enteredLink = QtCore.pyqtSignal(str)
    
    def __init__(self):
        super(DownloadTabWidget, self).__init__()
        self.thread = QtCore.QThread()
        self.worker = LinkCheck()
        self.worker.moveToThread(self.thread)
        self.enteredLink.connect(self.worker.processLink)
        self.worker.linkFail.connect(self.updateLinkFailed)
        self.worker.linkSuccess.connect(self.updateLinkSuccessfull)
        self.thread.start()

    def setupUI(self):
        self.urlLabel = QtWidgets.QLabel('Enter the URL of the video you want to download')
        self.urlLabel.setContentsMargins(0,0,0,10)
        
        self.urlLineEdit = QtWidgets.QLineEdit()
        self.urlLineEdit.setPlaceholderText('paste link here')
        self.urlLineEdit.textChanged.connect(lambda : self.enteredLink.emit(str(self.urlLineEdit.text())))


        self.hline = QtWidgets.QFrame()
        self.hline.setFrameShape(QtWidgets.QFrame.HLine)
        self.hline.setFrameShadow(QtWidgets.QFrame.Plain)
        self.hline.setMidLineWidth(3)
        self.hline.setLineWidth(0)

        self.qualityLabel = QtWidgets.QLabel('Download quality:')
        self.qualityList= QtWidgets.QComboBox()
        self.qualityList.setEnabled(False)
        

        self.pathLabel = QtWidgets.QLabel('Save path:')
        self.pathLabel.setAlignment(QtCore.Qt.AlignRight)

        self.pathLineEdit = QtWidgets.QLineEdit()
        self.pathLineEdit.setFrame(False)
        self.pathLineEdit.setAlignment(QtCore.Qt.AlignLeft)
        self.pathLineEdit.setAlignment(QtCore.Qt.AlignTop)

        self.browse_pic = QtGui.QPixmap('./Icons/browse-folder.png')
        self.browse_icon = QtGui.QIcon(self.browse_pic)
        self.browse_button = QtWidgets.QPushButton(self.browse_icon, ' Browse...')
        self.browse_button.clicked.connect(self.openFolder)

        file_list = QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.DownloadLocation)
        self.savePath = QtCore.QDir.currentPath() if not file_list else file_list[-1]
        self.pathLineEdit.setText(self.savePath)

        self.fileDialog = QtWidgets.QFileDialog(caption='Select Directory')
        self.fileDialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory) 
        self.fileDialog.setDirectory(self.savePath)
        self.fileDialog.setOption(QtWidgets.QFileDialog.Option.ShowDirsOnly)
        self.firstDialog = True
        
        self.hline1 = QtWidgets.QFrame()
        self.hline1.setFrameShape(QtWidgets.QFrame.HLine)
        self.hline1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.hline1.setMidLineWidth(3)
        self.hline1.setLineWidth(0)
        
        self.grid_parent = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.grid_parent)
        self.grid.setColumnMinimumWidth(0,60)
        self.grid.setColumnMinimumWidth(2,200)
        self.grid.setColumnMinimumWidth(4,60)
        self.grid.setRowMinimumHeight(0,30)
        self.grid.setRowMinimumHeight(3,30)
        self.grid.addWidget(self.qualityLabel,1,1)
        self.grid.addWidget(self.qualityList,1,2)
        self.grid.addWidget(self.pathLabel,2,1)
        self.grid.addWidget(self.pathLineEdit,2,2)
        self.grid.addWidget(self.browse_button,2,3)

        self.download_pic = QtGui.QPixmap('./Icons/download-solid.svg')
        self.download_icon = QtGui.QIcon(self.download_pic)
        self.download_button = QtWidgets.QPushButton(self.download_icon,'  Download')
        self.download_button.setMinimumWidth(120)
        self.download_button.setMinimumHeight(30)
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.downloadClicked)

        self.Vbox = QtWidgets.QVBoxLayout(self)
        self.Vbox.addWidget(self.urlLabel)
        self.Vbox.addWidget(self.urlLineEdit)
        self.Vbox.insertSpacing(2,20)
        self.Vbox.addWidget(self.hline)
        self.Vbox.addWidget(self.grid_parent)
        self.Vbox.addWidget(self.hline1)
        self.Vbox.insertSpacing(6,20)
        self.Vbox.addWidget(self.download_button,0,QtCore.Qt.AlignRight)
        self.Vbox.insertSpacing(7,10)

    @QtCore.pyqtSlot()
    def updateLinkFailed(self):
        self.qualityList.clear()
        self.qualityList.setEnabled(False)
        self.download_button.setEnabled(False)
    
    @QtCore.pyqtSlot(dict)
    def updateLinkSuccessfull(self, resolution_dict):
        self.resolution_dict = resolution_dict
        self.qualityList.setEnabled(True)
        self.download_button.setEnabled(True)
        self.qualityList.clear()

        self.qualityList.addItems(self.resolution_dict.keys())
   
    @QtCore.pyqtSlot()
    def downloadClicked(self):
        self.url = self.urlLineEdit.text()
        self.res = self.qualityList.currentText()
        self.fps = self.resolution_dict[self.res]
        

    @QtCore.pyqtSlot()
    def openFolder(self):
        if (self.fileDialog.exec()):
            self.savePath = self.fileDialog.selectedFiles()[-1]
            self.pathLineEdit.setText(self.savePath)
            self.fileDialog.setDirectory(self.savePath)

class LinkCheck(QtCore.QObject):
    linkFail = QtCore.pyqtSignal()
    linkSuccess = QtCore.pyqtSignal(dict)

    @QtCore.pyqtSlot(str)
    def processLink(self, url):
        try:
            self.url = url
            self.yt = pytube.YouTube(self.url)
            self.streams = self.yt.streams.filter(adaptive=True, file_extension='mp4')

        except:
            self.linkFail.emit()
        else:
            
            
            self.resolution_dict = {}
            for stream in self.streams:
                if stream.resolution not in self.resolution_dict:
                    self.resolution_dict[stream.resolution] = stream.fps
                elif stream.resolution in self.resolution_dict and stream.fps > self.resolution_dict[stream.resolution]:
                    del self.resolution_dict[stream.resolution]
                    self.resolution_dict[stream.resolution] = stream.fps
            self.resolution_dict.pop(None) if None in self.resolution_dict.keys() else None

            self.linkSuccess.emit(self.resolution_dict)