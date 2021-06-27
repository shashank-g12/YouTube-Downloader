from PyQt5 import QtCore, QtWidgets, QtGui, QtNetwork
import os
import ffmpeg
import time
import pytube

class VideoInfo(QtWidgets.QWidget):
    downloadSignal = QtCore.pyqtSignal(str, str, int, str)
    stopSignal = QtCore.pyqtSignal()
    def __init__(self, url, res , fps, save_path):
        super(VideoInfo, self).__init__()
        self.url = url
        self.res = res
        self.fps = fps
        self.savePath = save_path
    
        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.setTerminationEnabled(True)
        self.downloadSignal.connect(self.worker.getDetails)
        self.worker.thumbnailUpdate.connect(self.updateThumbnail)
        self.worker.progressValue.connect(self.updateProgress)
        self.worker.titleName.connect(self.updateTitle)
        self.worker.failedThread.connect(self.thread.quit)
        self.worker.finished.connect(self.thread.quit)
        
        self.stopSignal.connect(self.stop)
        
        self.thread.start()

    def setupUI(self):
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setScaledContents(True)

        self.textLabel = QtWidgets.QLabel()
        self.textLabel.setWordWrap(True)
        
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        
        self.delete = QtWidgets.QToolButton()
        self.trash_can = QtGui.QIcon(QtGui.QPixmap('./Icons/bin.png'))
        self.delete.setIcon(self.trash_can)
        self.delete.clicked.connect(self.remove, type = QtCore.Qt.DirectConnection)

        self.hline = QtWidgets.QFrame()
        self.hline.setFrameShape(QtWidgets.QFrame.HLine)
        self.hline.setFrameShadow(QtWidgets.QFrame.Plain)
        self.hline.setMidLineWidth(3)
        self.hline.setLineWidth(0)

        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setColumnStretch(3,4)
        self.grid_layout.setRowMinimumHeight(3,15)
        self.grid_layout.setHorizontalSpacing(15)

        self.grid_layout.addWidget(self.imageLabel,1,1 , 2,1)
        self.grid_layout.addWidget(self.textLabel,1,3)
        self.grid_layout.addWidget(self.progressBar,2,3,1,2)
        self.grid_layout.addWidget(self.delete, 1,4)
        self.grid_layout.addWidget(self.hline,4,1,1,4)


        self.downloadSignal.emit(self.url, self.res, self.fps, self.savePath)
    
    def updateTitle(self, title):
        self.textLabel.setText(title)
    
    def updateThumbnail(self, pic):
        self.imageLabel.setPixmap(pic)

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def remove(self):
        self.stopSignal.emit()
        self.thread.terminate()
        self.thread.quit()
        self.thread.finished.connect(lambda:self.worker.deleteLater)
        self.deleteLater()
    
    def stop(self):
        if os.path.exists(os.path.join(self.savePath, self.worker.video_name)):
            os.remove(os.path.join(self.savePath, self.worker.video_name))
        if os.path.exists(os.path.join(self.savePath, self.worker.audio_name)):
            os.remove(os.path.join(self.savePath, self.worker.audio_name))
    
    

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    thumbnailUpdate = QtCore.pyqtSignal('PyQt_PyObject')
    thumbnailrecieved = QtCore.pyqtSignal()
    progressValue = QtCore.pyqtSignal(float)
    titleName = QtCore.pyqtSignal(str)
    failedThread = QtCore.pyqtSignal()

    def getDetails(self, url, res, fps, save_path):
        self.url = url
        self.res = res
        self.fps = fps
        self.savePath = save_path
        try:
            self.yt = pytube.YouTube(self.url, on_progress_callback=self.progress)
        
        except:
            self.failedThread.emit()
        
        else:
            self.title = self.yt.title + ' (' + self.res + ')'
            self.titleName.emit(self.title)
            self.video_stream = self.yt.streams.filter(adaptive = True, file_extension = 'mp4', res=self.res, fps=self.fps)
            self.audio_stream = self.yt.streams.filter(adaptive = True, file_extension = 'mp4', type = 'audio')

            self.filesize = self.video_stream.first().filesize  + self.audio_stream.first().filesize
            self.total_recieved = 0

            self.manager = QtNetwork.QNetworkAccessManager() 
            self.request = QtNetwork.QNetworkRequest(QtCore.QUrl(self.yt.thumbnail_url))
            self.manager.finished.connect(self.thumbnailDownload)
            self.manager.get(self.request)

            self.thumbnailrecieved.connect(self.startDownload)
 
    def thumbnailDownload(self,reply):
        self.pix = QtGui.QPixmap()
        self.pix.loadFromData(reply.readAll())
        self.pix = self.pix.scaled(70,70,aspectRatioMode=2, transformMode=1)
        self.thumbnailUpdate.emit(self.pix)
        self.thumbnailrecieved.emit()

    def progress(self, stream, chunk, bytes_remaining):
        value = self.total_recieved + stream.filesize - bytes_remaining
        self.progressValue.emit((value/self.filesize)*100)
        if bytes_remaining == float(0):
            self.total_recieved += stream.filesize
    
    def startDownload(self):
        self.video_name = 'video_' + self.video_stream.first().default_filename
        self.audio_name = 'audio_' + self.audio_stream.first().default_filename

        video = self.video_stream.first().download(output_path=self.savePath,filename_prefix='video_')
        audio = self.audio_stream.first().download(output_path=self.savePath,filename_prefix='audio_')
        merge_video = ffmpeg.input(video)
        merge_audio = ffmpeg.input(audio)

        list_captions = self.yt.captions.keys()
        language = 'en' if 'en' in list_captions else 'a.en' if 'a.en' in list_captions else None
        title = video.split('/')[-1][6:]
        file_path = os.path.join(self.savePath,title)
            
        if language is not None:
            sub_file = self.yt.captions[language].download('sub', output_path=self.savePath)
            print(sub_file)
            merge_sub = ffmpeg.input(sub_file)
            merged = ffmpeg.output(merge_video, merge_audio, merge_sub, file_path, format = 'mp4', vcodec = 'copy',\
                            acodec = 'copy', scodec = 'mov_text')
        else:
            merged = ffmpeg.output(merge_video, merge_audio, file_path, format = 'mp4', vcodec = 'copy',\
                            acodec = 'copy')
        merged.run()
        os.remove(video)
        os.remove(audio)
        os.remove(sub_file) if language is not None else None
        self.finished.emit()