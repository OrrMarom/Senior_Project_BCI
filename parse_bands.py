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
    # get all data and remove it from internal buffer
    # board.stop_stream()
    # board.release_session()

    print("\n\n\n\n\n\n\n\n\n")
    refresh_rate=1 #in seconds
    for i in range(1000):
        data = board.get_board_data()
        frequencies = data.tolist()[2]
        band_counts = _average_waves_over_time(frequencies)
        _get_wave_sections(band_counts)
        time.sleep(refresh_rate)


    board.stop_stream()
    board.release_session()

def _average_waves_over_time(frequencies):
    alpha,beta,delta,theta,gamma,other,total=0,0,0,0,0,0,0
    
    for num in frequencies:
        total+=1

        if(num>1 and num<=4):
            delta+=1
        elif(num>4 and num<=8):
            theta+=1
        elif(num>8 and num<=13):
            alpha+=1
        elif(num>13 and num<=30):
            beta+=1
        elif(num>30 and num<=45):
            gamma+=1
        else:
            other+=1
            

    final_obj = {
        "alpha":alpha,
        "beta":beta,
        "delta":delta,
        "theta":theta,
        "gamma":gamma,
        "other":other,
        "total":total
    }
    return final_obj

def _get_wave_sections(band_counts):
    # Determine ratios of frequencies
    delta=band_counts["delta"]
    theta=band_counts["theta"]
    alpha=band_counts["alpha"]
    beta=band_counts["beta"]
    gamma=band_counts["gamma"]
    other=band_counts["other"]


    # Convert to percentages
    total_num_waves = band_counts["total"]
    adjusted_num = total_num_waves - other if not other==total_num_waves else 1

    delta_band=round(delta/adjusted_num*100,2)
    theta_band=round(theta/adjusted_num*100,2)
    alpha_band=round(alpha/adjusted_num*100,2)
    beta_band=round(beta/adjusted_num*100,2)
    gamma_band=round(gamma/adjusted_num*100,2)

    # Print the bands table
    blink = False
    blink = _check_for_closed_eyes(alpha_band,beta_band,delta_band,theta_band,gamma_band)
    if(blink):
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
    if(blink):
        result+="*Eyes are closed*"
    else:
        result+="                  "



    print(result)
    sys.stdout.flush()
    
def _get_percentage(band,total_num):
    return round(band*100/total_num,2)
    

def _check_for_closed_eyes(alpha,beta,delta,theta,gamma):
    if(
        alpha>=15
    ):
        return True
    else:
        return False

if __name__ == "__main__":
    main()