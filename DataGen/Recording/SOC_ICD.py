class SOC_EOST_ICD():
    # ICD 14BYTE DATA
    SOURCE_CONSOLE_CONTROL_MSG = b'\x01'
    DEST_CONSOLE_CONTROL_MSG = b'\x01'

    DEST_CONSOLE_SOC_MSG = b'\x03'
    THERMAL_IMAGE_DEBUG_MSG = b'\xC5'
    THERMAL_IMAGE_APP_SETTING_MSG = b'\xD0'


    #UPDATE NEW LIST
    THERMAL_IMAGE_TRSM_GUIDE_MSG = b'\xD6'

    SEND_ICD = {
        '1-REF_NUC': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_APP_SETTING_MSG,
            'data': b'\x00\x00'
        },
        'TRSM_REF_GUIDE_ON': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x00\x01'
        },
        'TRSM_REF_GUIDE_OFF': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x00\x00'
        },
        'TRSM_REF_GUIDE_UP': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x01\x02'
        },
        'TRSM_REF_GUIDE_DOWN': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x01\x03'
        },
        'TRSM_REF_GUIDE_LEFT': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x01\x00'
        },
        'TRSM_REF_GUIDE_RIGHT': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x01\x01'
        },
        'TRSM_REF_GUIDE_SAVE': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x02\x00'
        },
        'TRSM_REF_APPLY': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_TRSM_GUIDE_MSG,
            'data': b'\x03\x01'
        }
    }
    
class SOC_SURV_ICD():
    # ICD 14BYTE DATA
    SOURCE_CONSOLE_CONTROL_MSG = b'\x01'
    DEST_CONSOLE_SOC_MSG = b'\x06'
    THERMAL_IMAGE_APP_SETTING_MSG = b'\xD0'

    SEND_ICD = {
        '1-REF_NUC': {
            'CONSOLE_SOURCE': SOURCE_CONSOLE_CONTROL_MSG,
            'CONSOLE_DESTINATION': DEST_CONSOLE_SOC_MSG,
            'CONSOLE_HEADER': THERMAL_IMAGE_APP_SETTING_MSG,
            'data': b'\x00\x00'
        },       
    }