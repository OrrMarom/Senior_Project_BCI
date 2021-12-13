import argparse
import time
import sys
import numpy as np

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


def main():
    BoardShim.enable_dev_board_logger()

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
                        required=True)
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

    board = BoardShim(args.board_id, params)
    board.prepare_session()

    # board.start_stream () # use this for default options
    board.start_stream(45000, args.streamer_params)
    time.sleep(5)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    data = board.get_board_data()  # get all data and remove it from internal buffer
    # board.stop_stream()
    # board.release_session()

    print("\n\n\n\n\n\n")
    for i in range(10):
        list_data = data.tolist()
        _get_wave_sections(list_data[0])
        time.sleep(1)

    board.stop_stream()
    board.release_session()

def _get_wave_sections(frequencies):
    alpha,beta,delta,theta,other=0,0,0,0,0
    total_num = len(frequencies)
    for num in frequencies:
        if(num>=1 and num<=5):
            delta+=1
        elif(num>=4 and num<=8):
            theta+=1
        elif(num>=8 and num<=13):
            alpha+=1
        elif(num>=13 and num<=30):
            beta+=1
        else:
            other+=1

    goback = "\033[F" * 8
    result = f"""{goback}
    Bands
    ----------
    Alpha: {alpha/total_num*100}
    Beta: {beta/total_num*100}
    Delta: {delta/total_num*100}
    Theta: {theta/total_num*100}
    Other: {other/total_num*100}"""
    print(result)
    sys.stdout.flush()

if __name__ == "__main__":
    main()