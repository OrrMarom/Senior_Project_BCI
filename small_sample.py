import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QWidget)
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
import argparse
import logging

class Window(QWidget):
    def __init__(self, board_shim):
        super().__init__()
        self.setWindowTitle("Big Brain")

        # create main layout
        main_win = QHBoxLayout()

        # Create sub layouts
        graph_layout = QHBoxLayout()
        menu_layout = QVBoxLayout()

        # Create the widgets for the graph window
        graph = pg.GraphicsLayoutWidget(title="test")

        # create the widgets for the menu window
        button1 = QPushButton("show graph")
        button2 = QPushButton("start control")
        button3 = QPushButton("save")
        button4 = QPushButton("stop")
        button5 = QPushButton("exit")

        # Add widgets to the menu layout
        menu_layout.addWidget(button1)
        menu_layout.addWidget(button2)
        menu_layout.addWidget(button3)
        menu_layout.addWidget(button4)
        menu_layout.addWidget(button5)

        # add widgets to the graph layout
        graph_layout.addWidget(graph)

        # put sub layouts in main window
        main_win.addLayout(menu_layout)
        main_win.addLayout(graph_layout)

        # Set the layout on the application's window
        self.setLayout(main_win)
        print(self.children())

        # initiating time series and fields for ts
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        # adding lines to the graph
        for i in range(4):
            graph.addPlot(row=i,col=0) # creates the plot


if __name__ == "__main__":
    app = QApplication(sys.argv)

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