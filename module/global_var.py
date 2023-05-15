def _init():
    global _global_dict
    _global_dict = {}
    '''
    AsyncSnifferEnable: False
    ProgressBarValue: 0
    iface lst: ' ' (from NetworkCardComboBox)
    src mac address lst: ' ' (from LocalMacComboBox)
    '''

def set_value(key, value):
    _global_dict[key] = value

def get_value(key):
    try:
        return _global_dict[key]
    except:
        return None