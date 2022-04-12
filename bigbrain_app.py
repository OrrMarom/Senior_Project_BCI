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

class Window(QWidget):
    def __init__(self, board_shim):
        super().__init__()
        self.setWindowTitle("Big Brain")
        self.userName = 'johnsmith'
        today = date.today()
        self.date = today.strftime("%b-%d-%Y")

        # layouts
        self.mainLayout = QHBoxLayout() # layout for the entire app
        self.stackedLayout = QVBoxLayout() # layout for the stacked widget on the right
        self.menuLayout = QVBoxLayout() # layout for the menu widget on the left

        # widgets going into the stackedLayout widget
        self.graphWidget = pg.GraphicsLayoutWidget() # brainwave graph
        self.boardshimWidget = QWidget() # headset connection
        self.cursorWidget = QWidget() # control cursor
        self.saveWidget = QWidget() # save data
        self.tutorialWidget = QWidget() # tutorial
        self.settingsWidget = QWidget() # settings

        # stacked widget & adding widgets to it
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.graphWidget)
        self.stackedWidget.addWidget(self.boardshimWidget)
        self.stackedWidget.addWidget(self.cursorWidget)
        self.stackedWidget.addWidget(self.saveWidget)
        self.stackedWidget.addWidget(self.tutorialWidget)
        self.stackedWidget.addWidget(self.settingsWidget)

        # buttons for menu widget (note: index is based on the order above)
        self.button1 = QPushButton("Brainwave Visualizer") # index 0
        self.button2 = QPushButton("*Connect Headset*") # index 1
        self.button3 = QPushButton("*Control Cursor*") # index 2
        self.button4 = QPushButton("Save Data") # index 3
        self.button5 = QPushButton("*Tutorial*") # index 4
        self.button6 = QPushButton("*Settings*") # index 5

        # button colors
        self.button1.resize(100, 32)
        # self.button1.setStyleSheet("color: white; background-color: #127B89; border: 0px")

        # Add buttons to the menu layout
        self.menuLayout.addWidget(self.button1)
        self.menuLayout.addWidget(self.button2)
        self.menuLayout.addWidget(self.button3)
        self.menuLayout.addWidget(self.button4)
        self.menuLayout.addWidget(self.button5)
        self.menuLayout.addWidget(self.button6)

        # creating signals for buttons
        self.button1.clicked.connect(lambda: self.buttonWork(1))
        self.button2.clicked.connect(lambda: self.buttonWork(2))
        self.button3.clicked.connect(lambda: self.buttonWork(3))
        self.button4.clicked.connect(lambda: self.buttonWork(4))
        self.button5.clicked.connect(lambda: self.buttonWork(5))
        self.button6.clicked.connect(lambda: self.buttonWork(6))

        # Brainwave Page is the default index position

        # Connection Page (boardshim)
        self.connectionTitle = QLabel(self.boardshimWidget)
        self.connectionTitle.setText("Boardshim Connection Page")

        # Control Cursor Page
        self.cursorControlTitle = QLabel(self.cursorWidget)
        self.cursorControlTitle.setText("Control Cursor Page")

        # Save Data Page
        self.saveDataTitle = QLabel(self.saveWidget)
        self.saveDataTitle.setText("Saved Data Page")

        # Tutorial Page
        self.tutorialTitle = QLabel(self.tutorialWidget)
        self.tutorialTitle.setText("Tutorial Page")

        # Settings Page
        self.settingsTitle = QLabel(self.settingsWidget)
        self.settingsTitle.setText("Settings Page")

        # add widgets to the stackedwidget layout
        self.stackedLayout.addWidget(self.stackedWidget)

        # put sub layouts in main window
        self.mainLayout.addLayout(self.menuLayout)
        self.mainLayout.addLayout(self.stackedLayout)

        # Set the layout on the application's window
        self.setLayout(self.mainLayout)
        print(self.children())

        # initiating time series and fields for ts
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        self._init_timeseries(self.graphWidget)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def _init_timeseries(self, graphWidget):
        self.plots = list()
        self.curves = list()
        for i in range(len(self.exg_channels)):
            p = graphWidget.addPlot(row=i,col=0)
            p.showAxis('left', True)
            p.setMenuEnabled('left', False)
            p.showAxis('bottom', False)
            p.setMenuEnabled('bottom', False)
            if i == 0:
                p.setTitle('4-Channel EEG TimeSeries Plot')
            self.plots.append(p)
            if i == 0:
                curve = p.plot(pen = {"color":"#2FAED0"})
            elif i == 1:
                curve = p.plot(pen = {"color":"#A12FD0"})
            elif i == 2:
                curve = p.plot(pen = {"color":"#D0512F"})
            elif i == 3:
                curve = p.plot(pen = {"color":"#5ED02F"})
            else:
                curve = p.plot()
            self.curves.append(curve)

    def update(self):
        self.data = self.board_shim.get_current_board_data(self.num_points)
        for count, channel in enumerate(self.exg_channels):
            # plot timeseries
            DataFilter.detrend(self.data[channel], DetrendOperations.CONSTANT.value)
            DataFilter.perform_bandpass(self.data[channel], self.sampling_rate, 51.0, 100.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandpass(self.data[channel], self.sampling_rate, 51.0, 100.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandstop(self.data[channel], self.sampling_rate, 50.0, 4.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandstop(self.data[channel], self.sampling_rate, 60.0, 4.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            self.curves[count].setData(self.data[channel].tolist())

    def saveData(self):
        dataHeader = "{}{}".format(self.userName, self.date)
        DataFilter.write_file(self.data, '{}'.format(dataHeader), 'a') # 'a' appends to file, 'w' for overwrite

    def buttonWork(self, x): # x refers to the button number, which is index + 1 for currentindex on a stacked widget
        if x == 1:
            self.stackedWidget.setCurrentIndex(0)
        elif x == 2:
            self.stackedWidget.setCurrentIndex(1)
        elif x == 3:
            self.stackedWidget.setCurrentIndex(2)
            # self.printBandData() # not working, prints once and won't update again
        elif x == 4:
            self.stackedWidget.setCurrentIndex(3)
            # self.saveData()
        elif x == 5:
            self.stackedWidget.setCurrentIndex(4)
        elif x == 6:
            self.stackedWidget.setCurrentIndex(5)

    def printBandData(self):
        print("\n\n\n\n\n\n\n\n\n")
        refresh_rate=0.5 #in seconds
        for i in range(1000):
            avgBandPowers = DataFilter.get_avg_band_powers(self.data, self.exg_channels, self.sampling_rate, apply_filter=True)
            self.print_bands(avgBandPowers)
            time.sleep(refresh_rate)

    def print_bands(self, avgBandPowers):
        delta_band = round(avgBandPowers[0][0] * 100, 2)
        theta_band = round(avgBandPowers[0][1] * 100, 2)
        alpha_band = round(avgBandPowers[0][2] * 100, 2)
        beta_band = round(avgBandPowers[0][3] * 100, 2)
        gamma_band = round(avgBandPowers[0][4] * 100, 2)

        jawClench = False
        jawClench = self.checkJawClenching(gamma_band)
        if (jawClench):
            goback = "\033[F" * 12
        else:
            goback = "\033[F" * 10

        goback = "\033[F" * 10
        result = f"""{goback}
        Bands
        ----------
        Delta[1-4]: {delta_band}%     
        Theta[4-8]: {theta_band}%     
        Alpha[8-13]: {alpha_band}%     
        Beta[13-30]: {beta_band}%     
        Gamma[30-45]: {gamma_band}%     

        """
        if jawClench:
            result+="*Jaw is being clenched*"
        else:
            result+="                       "

        print(result)
        sys.stdout.flush()

    def checkJawClenching(self, gamma_band):
        if gamma_band > 40:
            return True
        else:
            return False

if __name__ == "__main__":
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.SYNTHETIC_BOARD)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file

    try:
        app = QApplication(sys.argv)
        board_shim = BoardShim(args.board_id, params)
        board_shim.prepare_session()
        board_shim.start_stream(450000, args.streamer_params)

        window = Window(board_shim)
        window.show()
        sys.exit(app.exec_())
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()