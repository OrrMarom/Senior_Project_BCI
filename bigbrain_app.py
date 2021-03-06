from cProfile import label
import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations, WindowFunctions, DetrendOperations, NoiseTypes, AggOperations
import argparse
import logging
import numpy as np
import pandas as pd
from datetime import date
import time
import webbrowser 
import pyautogui
from PyQt5.QtGui import QIntValidator
import json

class MainAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('brain.png'))
        self.setWindowTitle("Big Brain - Main Menu")
        self.userName = 'Big Brain'
        today = date.today()
        self.date = today.strftime("%b-%d-%Y")

        #?------------------------------------------------------------
        #?
        #?                 Main GUI Window
        #?
        #?------------------------------------------------------------
        #* init main layout
        self.mainLayout = QHBoxLayout() # layout for the entire app
        #* init left side of main layout (buttons)
        self.menuLayout = QVBoxLayout()
        #* init right side of main layout 
        self.stackedLayout = QVBoxLayout()

        # put sub layouts in main window
        self.mainLayout.addLayout(self.menuLayout)
        self.mainLayout.addLayout(self.stackedLayout)
        # Set the layout on the application's window
        self.setLayout(self.mainLayout)
        #print(self.children())

        #?------------------------------------------------------------
        #?
        #?                 Left GUI Layouts and Widgets
        #?
        #?------------------------------------------------------------
        
        # Create key:value (code name:display name) pair for each button. displays in order of obj
        self.button_name_obj = {
            "connectBtn":"Connect Headset",
            "brainwaveBtn":"Brainwave Visualizer",
            "cursorBtn":"Control Cursor",
            "saveBtn":"Save Data",
            "tutorialBtn":"Tutorial",
            "settingsBtn":"Settings"
        }
        page_counter = 0
        for btn_name in self.button_name_obj:
            # loop through list of names and create QPushButton for each, then assign it to self
            temp_btn = QPushButton(self.button_name_obj[btn_name])
            temp_btn.setFixedSize(QtCore.QSize(200, 100))
            temp_btn.clicked.connect((lambda d: lambda:self._button_router(d))(page_counter))
            page_counter+=1
            # add button variables and widgets to self
            self.__dict__[btn_name] = temp_btn
            self.menuLayout.addWidget(temp_btn)

        # Start application with most buttons disabled until the headset is connected
        self._disable_general_buttons()


        #?------------------------------------------------------------
        #?
        #?                 Right GUI Layouts and Widgets
        #?
        #?------------------------------------------------------------
            
        self.stackedWidget = QStackedWidget()
        # add widgets to the stackedwidget layout
        self.stackedLayout.addWidget(self.stackedWidget)

        #* Connection Page (boardshim)
        self.connectionWidget = QWidget() 
        connectionLayout = QVBoxLayout()
        connectionL1 = QLabel("<--- Begin collecting brainwave data with your OpenBCI headset")
        connectionL2 = QLabel("<--- View your brainwaves in real-time, on each channel")
        connectionL3 = QLabel("<--- Control your mouse cursor by using your brain")
        connectionL4 = QLabel("<--- Save all brainwave data up to this point in time")
        connectionL5 = QLabel("<--- Visit our website to see a tutorial")
        connectionL6 = QLabel("<--- Adjust COM port, cursor control speed, disable channels or switch boards")
        connectionLayout.addWidget(connectionL1)
        connectionLayout.addWidget(connectionL2)
        connectionLayout.addWidget(connectionL3)
        connectionLayout.addWidget(connectionL4)
        connectionLayout.addWidget(connectionL5)
        connectionLayout.addWidget(connectionL6)
        '''
        testlayout1 = QHBoxLayout() 
        testlayout2 = QHBoxLayout()
        connectionLayout.addLayout(testlayout1,2)
        connectionLayout.addLayout(testlayout2,1)

        testText1= QLabel("beep boop")
        testText2= QLabel("bop beep")
        testlayout1.addWidget(testText1,1)
        testlayout2.addWidget(testText2,2)
        '''
        self.connectionWidget.setLayout(connectionLayout)
        # self.connectionTitle = QLabel(self.connectionWidget)
        # self.connectionTitle.setText("Connection Page")
        self.stackedWidget.addWidget(self.connectionWidget)
        
        #* graph?
        self.graphWidget = pg.GraphicsLayoutWidget() # brainwave graph
        self.cursorControlTitle = QLabel(self.graphWidget)
        self.cursorControlTitle.setText("Brainwave Data")
        self.stackedWidget.addWidget(self.graphWidget)

        #* Control Cursor Page
        self.cursorWidget = QWidget() 
        self.cursorControlTitle = QLabel(self.cursorWidget)
        self.cursorControlTitle.setText("Control Cursor Page")
        self.stackedWidget.addWidget(self.cursorWidget)
        
        #* Save Data Page
        self.saveWidget = QWidget() 
        self.saveDataTitle = QLabel(self.saveWidget)
        self.saveDataTitle.setText("Saved Data Page")
        self.stackedWidget.addWidget(self.saveWidget)
        
        #* Tutorial Page
        self.tutorialWidget = QWidget()
        self.tutorialTitle = QLabel(self.tutorialWidget)
        self.tutorialTitle.setText("Tutorial Page")
        self.stackedWidget.addWidget(self.tutorialWidget)
        
        #* Settings Page
        self.settingsWidget = QWidget()
        self.initSettingsWindow()
        self.stackedWidget.addWidget(self.settingsWidget)

    #?------------------------------------------------------------
    #?
    #?                  Start GUI Helper Functions
    #?
    #?------------------------------------------------------------
    
    #*---------------------
    #* General Helpers
    #*---------------------
    # Controls buttons actions after it's pressed
    def _button_router(self, page_index):
        """ 
        Switch to page based off the passed page_index. Current page index are:
            0 = connectBtn
            1 = brainwaveBtn
            2 = cursorBtn
            3 = saveBtn
            4 = tutorialBtn
            5 = settingsBtn
        """
        print(f"Switching to page {page_index}")
        self.stackedWidget.setCurrentIndex(page_index)
        
        # After page is switched, call specific function for each button if it needs one
        if page_index == 0: 
            # connect to headset
            self._connect_to_headset(1)
        elif page_index == 1:
            self.setWindowTitle("Big Brain - Brainwave Graph")
            self._start_brainwave_graph()
        elif page_index == 2:
            # start cursor control
            self.setWindowTitle("Big Brain - Cursor Control")
            self._start_cursor_control()
        elif page_index==3:
            # save brainwave data
            self.saveData()
        elif page_index==4:
            self.openTutorial()

    def _disable_general_buttons(self):
        for btn_name in self.button_name_obj:
            if btn_name not in ["connectBtn","tutorialBtn"]: self.__dict__[btn_name].setDisabled(True)
    def _enable_general_buttons(self):
        for btn_name in self.button_name_obj:
            if btn_name not in ["connectBtn","tutorialBtn"]: self.__dict__[btn_name].setDisabled(False)
    #*---------------------
    #* Start Headset Connection Helper
    #*---------------------
    def _connect_to_headset(self,board_id):
        print("Connecting to headset")
        # Start boardshim and get all required data
        boardshim_init_results = init_boardshim_item()
        boardshim = boardshim_init_results["boardshim"]
        args = boardshim_init_results["args"]

        # initialize blink stuff
        self.blink_count = 0
        self.blink_cooldown_counter = 0
        self.jawClench = False
        self.eyeBlink = False
        self.jaw_stop_counter = 0
        self.jaw_stop_limit = 0
        self.print_file = []
        self.click_safety=False
        #! how long pyautogui pauses between every function
        pyautogui.PAUSE = 0.005

        # initiating time series and fields for ts
        self.board_id = board_id #board_shim.get_board_id()
        self.boardshim = boardshim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate
        
        boardshim.prepare_session()
        boardshim.start_stream(450000, args.streamer_params)

        #* Start the brainwave data streaming in the background
        self._init_timeseries(self.graphWidget)
        self.graphTimer = QtCore.QTimer()

        self.loop_interval = 1 # in milliseconds
        self.graphTimer.setInterval(self.loop_interval)
        self.graphTimer.timeout.connect(self._update_brainwave_data)
        self.graphTimer.start()

        # Enable all the buttons that were previously disabled
        self._enable_general_buttons()
        self.connectBtn.setDisabled(True)

    #*---------------------
    #* Start Graph Helper
    #*---------------------
    def _start_brainwave_graph(self):
        print('beep') # do nothing for now

    # Create Graph for the Graph page
    def _init_timeseries(self, graphWidget):
        self.plots = list()
        self.curves = list()
        for i in range(len(self.exg_channels)):
            graphWidget
            p = graphWidget.addPlot(row=i,col=0)
            p.setYRange(-200,200,padding=0)

            # p.showAxis('left', True)
            # p.setMenuEnabled('left', False)
            # p.showAxis('bottom', False)
            # p.setMenuEnabled('bottom', False)
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
            
    # Updates brainwave data over time
    def _update_brainwave_data(self):
        self.data = self.boardshim.get_current_board_data(self.num_points)
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

            # DataFilter.perform_rolling_filter(self.data[channel], 3, AggOperations.MEDIAN.value)

            DataFilter.remove_environmental_noise (self.data[channel],self.sampling_rate, 1)


            self.curves[count].setData(self.data[channel].tolist())

            # Calculate data for cursor control to use later
            if(channel==1):
                nfft = DataFilter.get_nearest_power_of_two(self.sampling_rate)
                # psd = DataFilter.get_psd_welch(self.data[channel], nfft, nfft // 2, self.sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value)
                psd = DataFilter.get_psd_welch(self.data[channel], nfft, nfft // 2, self.sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value)

                frequency= self.data[channel].tolist().pop()

                delta_band = DataFilter.get_band_power(psd, 1.0, 3.0)
                theta_band = DataFilter.get_band_power(psd, 4.0, 8.0)
                alpha_band = DataFilter.get_band_power(psd, 8.0, 13.0)
                beta_band = DataFilter.get_band_power(psd, 13.0, 30.0)
                gamma_band = DataFilter.get_band_power(psd, 30.0, 45.0)
            

                print_thing = str(["frequency:",int(frequency),"bandstuff:",int(delta_band),int(theta_band),int(alpha_band),int(beta_band),int(gamma_band),"eyeblinkstuff:", self.blink_count,self.blink_cooldown_counter,self.jaw_stop_counter,self.jawClench,self.eyeBlink])
                self.print_file.append(print_thing)
                print(print_thing)

                self.blink_cooldown_counter += self.loop_interval
                self.jaw_stop_counter += self.loop_interval
                self.jawClench = checkJawClenching(gamma_band)
                self.eyeBlink = checkEyeBlinking(frequency)
    
    #*---------------------
    #* Start Cursor Control Helper
    #*---------------------
    def _start_cursor_control(self):
        print("Starting Cursor Control")
        
        # Switch to smaller cursor app
        self.cursorWindow = CursorAppWindow(self)
        self.cursorWindow.show()
        self.hide()

        # Start cursor control
        self.cursorTimer = QtCore.QTimer()
        self.cursorTimer.setInterval(self.loop_interval)
        
        #? self.cursorTimer.timeout.connect(self._update_1d_cursor_movement)
        
        # 2d control
        self.cooldown_rate= 300 # in milliseconds
        self.blink_count = 0 #indicates direction
        self.blink_cooldown_counter = self.cooldown_rate #counts how long it's been since last blink
        self.blink_cooldown_limit = self.blink_cooldown_counter #how long to wait before registering another blink_count in milliseconds

        self.jaw_stop_counter = 100 # Force jaw to be active for this many milliseconds before being able to disable
        self.jaw_stop_limit = 100
        self.jaw_clench_start = False

        self.cursorTimer.timeout.connect(self._update_2d_cursor_movement)

        #! Comment out line below to prevent cursor movement
        self.cursorTimer.start()

    # Directly works on 1d left-right movement
    def _update_1d_cursor_movement(self):
        if self.jawClench:
            testMoveCursorLeft()
        elif self.eyeBlink:  
            testMoveCursorRight()

    # process for 2d cursor movement
    def _update_2d_cursor_movement(self):
        if self.eyeBlink and not self.jaw_clench_start:
            if self.blink_cooldown_counter > self.blink_cooldown_limit:
                self.blink_count += 1
                self.blink_cooldown_counter = 0

            if self.blink_count>4:
                self.blink_count = 0
        elif self.jawClench:  
            self.jaw_clench_start = True
            self.move2DCursor()

        if self.jaw_clench_start and not self.jawClench:
            # if(self.jaw_stop_counter>self.jaw_stop_limit):
            self.jaw_clench_start = False
            self.click_safety = False
            # self.blink_count = 0
            self.jaw_stop_counter = 0

    def move2DCursor(self):
        direction = self.blink_count
        movement_speed = 1
        duration = 0.01

        if direction == 0 and not self.click_safety: #click
            pyautogui.click()
            self.click_safety = True
        elif direction==1: #left
            pyautogui.move(-1 * movement_speed, 0, duration=duration)
        elif direction ==2: #up
            pyautogui.move(0, -1 * movement_speed, duration=duration)
        elif direction ==3: #right
            pyautogui.move(movement_speed,0, duration=duration)
        elif direction ==4: #down
            pyautogui.move(0,movement_speed, duration=duration)

    #*---------------------
    #* Start Save Helper
    #*---------------------
    def saveData(self):
        dataHeader = "{}{}".format(self.userName, self.date)
        # DataFilter.write_file(self.data, '{}'.format(dataHeader), 'a') # 'a' appends to file, 'w' for overwrite

        f = open("test.txt", "w")
        f.write(json.dumps(self.print_file,indent=4))
        f.close()

        print("saved local file")

    #*---------------------
    #* Start Tutorial Helper
    #*---------------------
    def openTutorial(self):
        webbrowser.open('https://tonyvillicana955.wixsite.com/bigbrain/services-1')

    #*---------------------
    #* Start Brainwave console stuff
    #*---------------------

    #*---------------------
    #* Start Settings stuff
    #*---------------------
    #creates the settings page
    def initSettingsWindow(self):
        #define main settings layout
        self.settingsLayout = QVBoxLayout()
        #create slider widget
        self.initSliderWidget()
        #create comport input
        self.initComPortWidget()
        #create board selection input
        self.initBoardSelectWidget()
        #create channel selection
        self.initBoardChannelsWidget()
        #set main settings layout in window
        self.settingsWidget.setLayout(self.settingsLayout)

    #creates slider for settings
    def initSliderWidget(self):
        #create cursor speed slider input
        self.sliderLayout = QHBoxLayout()
        #create desc label
        sld_title = QLabel("Adjust Cursor Speed")
        sld_title.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.sliderLayout.addWidget(sld_title)
        #create speed label
        self.sld_label = QLabel("50")
        self.sld_label.setStyleSheet("font-weight: bold; color: white; background: #007AA5; border-radius: 3px;")
        self.sld_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.sld_label.setGeometry(300,300,350,250)
        self.sliderLayout.addWidget(self.sld_label)
        #create slider
        self.sld = QSlider(Qt.Horizontal)
        self.sld.setMinimum(1)
        self.sld.setMaximum(100)
        self.sld.setMinimumWidth(80)
        self.sld.setValue(50)
        self.sld.setTickPosition(QSlider.TicksBelow)
        self.sld.setTickInterval(1)
        #call func to display slider value
        self.sld.valueChanged.connect(self.sld_value_change)
        #add slider to layout
        self.sliderLayout.addWidget(self.sld)
        self.settingsLayout.addLayout(self.sliderLayout)
    #helper for slider
    def sld_value_change(self, value):
        size = value
        self.sld_label.setText(str(size))

    #creates comport input for settings
    def initComPortWidget(self):
        #create layout for com port input
        self.comPortLayout = QHBoxLayout()
        #create desc label
        comPort_label = QLabel("Com Port")
        self.comPortLayout.addWidget(comPort_label)
        #create input field
        self.comPort = QLineEdit()
        #create int validator (only #'s allowed for input)
        self.intCheck = QIntValidator()
        self.comPort.setValidator(self.intCheck)
        #call func to show comport number
        self.comPort.textChanged.connect(self.com_port_change)
        #add comport to layout
        self.comPortLayout.addWidget(self.comPort)
        self.settingsLayout.addLayout(self.comPortLayout)
    #helper for comport
    def com_port_change(self, text):
        com_port = int(text)
        print(com_port)

    #creates board input for settings
    def initBoardSelectWidget(self):
        #create layout for board selection input
        self.boardLayout = QHBoxLayout()
        #create desc label
        self.board_label = QLabel("Board")
        self.boardLayout.addWidget(self.board_label)
        #create drop down box
        self.board_select = QComboBox()
        self.board_select.addItem("Ganglion")
        self.board_select.addItem("Cyton")
        #add input box to layout
        self.boardLayout.addWidget(self.board_select)
        self.settingsLayout.addLayout(self.boardLayout)

    def initBoardChannelsWidget(self):
        self.boardChannels = QWidget()
        self.boardChannels.setFixedHeight(50)
        self.boardChannels_layout = QVBoxLayout()
        self.boardChannels.setLayout(self.boardChannels_layout)
        self.settingsLayout.addWidget(self.boardChannels)
        self.initGanglionWidget()

    #creates checkboxes for ganglion widget
    def initGanglionWidget(self):
        self.ganglion = QWidget()
        self.ganglion.setFixedHeight(50)
        self.ganglionLayout = QHBoxLayout()
        self.ganglion.setLayout(self.ganglionLayout)
        self.ganglion_label = QLabel("Ganglion Channels")
        self.ganglionLayout.addWidget(self.ganglion_label)
        self.ganglionCheckBox1 = QCheckBox("Channel 1")
        self.ganglionCheckBox2 = QCheckBox("Channel 2")
        self.ganglionCheckBox3 = QCheckBox("Channel 3")
        self.ganglionCheckBox4 = QCheckBox("Channel 4")
        self.ganglionLayout.addWidget(self.ganglionCheckBox1)
        self.ganglionLayout.addWidget(self.ganglionCheckBox2)
        self.ganglionLayout.addWidget(self.ganglionCheckBox3)
        self.ganglionLayout.addWidget(self.ganglionCheckBox4)
        self.settingsLayout.addWidget(self.ganglion)

    #creates checkboxes for cyton widget
    def initCytonWidget(self):
        pass

        

#?------------------------------------------------------------
#?
#?       GUI App for when cursor control is active
#?
#?------------------------------------------------------------
#       
class CursorAppWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('brain.png'))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Big Brain - Cursor Control Menu")
        self.pushButton = QPushButton("QUIT CURSOR CONTROL", self)
        self.pushButton.setFixedSize(QtCore.QSize(500, 50))
        # self.pushButton.setFlat(True)
        self.pushButton.setStyleSheet("font-weight: bold; color: white; background-color: #D20705;")
        self.pushButton.clicked.connect(lambda: self.goback(parent))
        self.directionLabel = QLabel("", self)
        self.directionLabel.setStyleSheet("font-weight: bold; color: white; background-color: #00db33; padding: 3px;")
    
        print('hi')
        self.label_timer = QtCore.QTimer()
        self.loop_interval = parent.loop_interval # in milliseconds
        self.label_timer.setInterval(self.loop_interval)
        self.label_timer.timeout.connect(lambda: self._change_direction_text(parent))
        self.label_timer.start()
        self.center() 

    def _change_direction_text(self,parent):
        blink_count = parent.blink_count
        label_val = ""
        if blink_count == 0:
            label_val= "Click"
        elif blink_count == 1:
            label_val= "Left"
        elif blink_count == 2:
            label_val= "Up"
        elif blink_count == 3:
            label_val= "Right"
        elif blink_count == 4:
            label_val= "Down"

        self.directionLabel.setText(label_val)
        self.directionLabel.adjustSize()


    def goback(self, parent):
        # stop the loop for checking cursor movement
        parent.cursorTimer.stop()
        # return to main app
        parent.show()
        self.hide()

    def center(self):
        screen = QApplication.primaryScreen()
        size = screen.size()
        width = size.width()
        x_center = width / 2;
        self_width = self.pushButton.frameGeometry().size().width()
        center = int(x_center - (self_width/2))
        self.move(center, 0)
        
#?------------------------------------------------------------
#?
#?                  Start General Helper Functions
#?
#?------------------------------------------------------------

        
#*---------------------
#* Start Boardshim connection stuff
#*---------------------
def init_boardshim_item():
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
    
    return {
        "boardshim":BoardShim(args.board_id, params),
        "args":args,
        "params":params
    }

#*---------------------
#* Start Cursor Connection stuff
#*---------------------
def checkJawClenching(gamma_band):
    if gamma_band > 15:
        return True
    else:
        return False
def checkEyeBlinking(frequency):
    if frequency < -140:
        return True
    else:
        return False
def testMoveCursorLeft():
    # moves in 1 direction only
    pyautogui.move(-100, 0, duration=0.5)

def testMoveCursorRight():
    # moves in 1 direction only
    pyautogui.move(100, 0, duration=0.5)

#?------------------------------------------------------------
#?
#?                  Main Function
#?
#?------------------------------------------------------------
if __name__ == "__main__":
    # Start the PyQt window
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    try:
        app = QApplication(sys.argv)
        window = MainAppWindow()
        
        window.show()
        sys.exit(app.exec_())
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        # if board_shim.is_prepared():
        #     logging.info('Releasing session')
        #     board_shim.release_session()