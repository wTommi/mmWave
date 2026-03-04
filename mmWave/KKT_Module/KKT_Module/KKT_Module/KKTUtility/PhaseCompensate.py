from typing import Optional, Dict, Tuple


def setRXCompensate(mux:int, rf_config:dict)->Tuple[int, int, int, int]:
    CH1_real_compensate = 1024
    CH1_image_compensate = 0
    CH2_real_compensate = 1024
    CH2_image_compensate = 0
    if mux == 0:
        if rf_config['RX1_real_compansate'] != 'None' and rf_config['RX1_image_compansate'] != 'None':
            CH1_real_compensate = rf_config['RX1_real_compansate']
            CH1_image_compensate = rf_config['RX1_image_compansate']

        if rf_config['RX2_real_compansate'] != 'None' and rf_config['RX2_image_compansate'] != 'None':
            CH2_real_compensate = rf_config['RX2_real_compansate']
            CH2_image_compensate = rf_config['RX2_image_compansate']
        else:
            pass

    elif mux == 1:

        if rf_config['RX2_real_compansate'] != 'None' and rf_config['RX2_image_compansate'] != 'None':
            CH1_real_compensate = rf_config['RX2_real_compansate']
            CH1_image_compensate = rf_config['RX2_image_compansate']
        else:
            pass

    elif mux == 2:

        if rf_config['RX1_real_compansate'] != 'None' and rf_config['RX1_image_compansate'] != 'None':
            CH2_real_compensate = rf_config['RX1_real_compansate']
            CH2_image_compensate = rf_config['RX1_image_compansate']
        else:
            pass

    elif mux == 3:

        if rf_config['RX1_real_compansate'] != 'None' and rf_config['RX1_image_compansate'] != 'None':
            CH1_real_compensate = rf_config['RX1_real_compansate']
            CH1_image_compensate = rf_config['RX1_image_compansate']
            CH2_real_compensate = rf_config['RX1_real_compansate']
            CH2_image_compensate = rf_config['RX1_image_compansate']
        else:
            pass

    elif mux == 4:

        if rf_config['RX2_real_compansate'] != 'None' and rf_config['RX2_image_compansate'] != 'None':
            CH1_real_compensate = rf_config['RX2_real_compansate']
            CH1_image_compensate = rf_config['RX2_image_compansate']
        else:
            pass

        if rf_config['RX1_real_compansate'] != 'None' and rf_config['RX1_image_compansate'] != 'None':
            CH2_real_compensate = rf_config['RX1_real_compansate']
            CH2_image_compensate = rf_config['RX1_image_compansate']
        else:
            pass

    elif mux == 5:

        if rf_config['RX2_real_compansate'] != 'None' and rf_config['RX2_image_compansate'] != 'None':
            CH2_real_compensate = rf_config['RX2_real_compansate']
            CH2_image_compensate = rf_config['RX2_image_compansate']
        else:
            pass

    elif mux == 6:

        if rf_config['RX1_real_compansate'] != 'None' and rf_config['RX1_image_compansate'] != 'None':
            CH1_real_compensate = rf_config['RX1_real_compansate']
            CH1_image_compensate = rf_config['RX1_image_compansate']
        else:
            pass

    elif mux == 7:

        if rf_config['RX2_real_compansate'] != 'None' and rf_config['RX2_image_compansate'] != 'None':
            CH1_real_compensate = rf_config['RX2_real_compansate']
            CH1_image_compensate = rf_config['RX2_image_compansate']
            CH2_real_compensate = rf_config['RX2_real_compansate']
            CH2_image_compensate = rf_config['RX2_image_compansate']
        else:
            pass

    elif mux == 8:

        pass
    return CH1_real_compensate, CH1_image_compensate, CH2_real_compensate, CH2_image_compensate