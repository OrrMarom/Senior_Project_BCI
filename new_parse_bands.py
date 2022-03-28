import argparse
import time
import sys

from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter

import pyautogui

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
    exg_channels = BoardShim.get_exg_channels(args.board_id)
    sampling_rate = BoardShim.get_sampling_rate(args.board_id)
    board.prepare_session()

    # board.start_stream () # use this for default options
    board.start_stream(45000, args.streamer_params)
    time.sleep(5)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    # get all data and remove it from internal buffer
    # board.stop_stream()
    # board.release_session()

    print("\n\n\n\n\n\n\n\n\n")
    refresh_rate=0.5 #in seconds
    for i in range(1000):
        data = board.get_board_data()
        avgBandPowers = DataFilter.get_avg_band_powers(data, exg_channels, sampling_rate, apply_filter=True)
        print_bands(avgBandPowers)
        time.sleep(refresh_rate)

    board.stop_stream()
    board.release_session()

def print_bands(avgBandPowers):
    delta_band = round(avgBandPowers[0][0] * 100, 2)
    theta_band = round(avgBandPowers[0][1] * 100, 2)
    alpha_band = round(avgBandPowers[0][2] * 100, 2)
    beta_band = round(avgBandPowers[0][3] * 100, 2)
    gamma_band = round(avgBandPowers[0][4] * 100, 2)

    jawClench = False
    jawClench = checkJawClenching(gamma_band)
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
        testMoveCursor()
    else:
        result+="                       "

    print(result)
    sys.stdout.flush()

def checkJawClenching(gamma_band):
    if gamma_band > 50:
        return True
    else:
        return False

def testMoveCursor():
    # moves in 1 direction only
    pyautogui.drag(100, 0, duration=0.5)

if __name__ == "__main__":
    main()