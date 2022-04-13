from sqlite3 import Cursor
import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import *
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations, WindowFunctions, DetrendOperations
import argparse
import logging
import numpy as np
import pandas as pd
from datetime import date
import time

class Window2(QWidget):                           # <===
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Window22222")
        self.pushButton = QPushButton("back", self)
        self.pushButton.clicked.connect(lambda: self.goback(parent))  

    def goback(self, parent):
        #parent.setVisible(True)
        parent.show()
        self.hide()
        

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window22222")

        self.pushButton = QPushButton("Start", self)
        self.pushButton.clicked.connect(self.window2)              # <===
        self.show()

    def window2(self):                                             # <===
        self.w = Window2(self)
        self.w.show()
        #self.setVisible(False)
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


