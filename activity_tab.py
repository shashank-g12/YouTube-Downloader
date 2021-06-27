from PyQt5 import QtCore, QtWidgets, QtGui
import sys

class ActivityTabWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ActivityTabWidget, self).__init__()
    
    def setupUI(self):
        """ Create widget holder to go into the scroll area
        which is the child of the ActivityTabWidgetClass
        """
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
 
        self.Vbox = QtWidgets.QVBoxLayout(self)
        self.Vbox.addWidget(self.scroll)
    
        self.widgetHolder = QtWidgets.QWidget()
        self.scroll.setWidget(self.widgetHolder)
        self.Vbox1 = QtWidgets.QVBoxLayout(self.widgetHolder)
        self.Vbox1.setAlignment(QtCore.Qt.AlignTop)