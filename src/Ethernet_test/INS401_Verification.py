import os
import argparse

from ..conmunicator.INS401_Ethernet import Ethernet_Dev
from .INS401_Test_Center import Test_Environment

class Verification:
    def __init__(self):
        pass

    def static_test(self, text_browser, debug=False, test_dict=None):
        '''Static
        '''
        uut = Ethernet_Dev()
        text_browser.append("\n#######   INS401 ETHERNET Interface Verification V3.0   #######\n")
        text_browser.moveCursor(text_browser.textCursor().End)

        
        result = uut.find_device()
        if result != True:
            text_browser.append('Can not connect device')
            text_browser.moveCursor(text_browser.textCursor().End)
            return
        
        result = uut.ping_device()
        if result != True:
            text_browser.append('Ethernet ping error.')
            text_browser.moveCursor(text_browser.textCursor().End)
            return
        
        model = uut.model_string 
        serial_number = uut.serial_number
        version = uut.app_version
        
        text_browser.append(f"\n# UUT Model: {model}")
        text_browser.moveCursor(text_browser.textCursor().End)
        text_browser.append(f"\n# UUT Serial Number: {serial_number}")
        text_browser.moveCursor(text_browser.textCursor().End)
        text_browser.append(f"\n# UUT Version: {version}")
        text_browser.moveCursor(text_browser.textCursor().End)
        text_browser.append("")
        text_browser.moveCursor(text_browser.textCursor().End)

        env = Test_Environment(uut)
        # switch debug mode
        if debug == False:
            env.setup_static_tests()
            text_browser.append("###########  Executing tests...   ##########################\n")
            text_browser.moveCursor(text_browser.textCursor().End)
            env.run_tests(text_browser=text_browser, debug=debug)
        else:
            env.setup_static_tests_d(test_dict=test_dict)
            text_browser.append("###########  Executing tests...   ##########################\n")
            text_browser.moveCursor(text_browser.textCursor().End)
            env.run_tests(text_browser=text_browser, debug=debug)
        text_browser.append("Test finished")
        text_browser.moveCursor(text_browser.textCursor().End)
        if not os.path.exists('./result'):
            os.mkdir('./result')
        file_name = f'./result/test_results_{str(serial_number)}_{str(version)}.xlsx'
        env.log_results(file_name, mode='static')

    def dynamic_test(self, text_browser, data_path, result_file_path, debug=False, test_dict=None):
        '''Dynamic
        '''
        env = Test_Environment()
        last_case_id = env.check_backup_logf()
        # switch debug mode
        if debug == False:
            env.setup_dynamic_tests(data_path)
            text_browser.append("###########  Executing tests...   ##########################\n")
            text_browser.moveCursor(text_browser.textCursor().End)
            env.run_tests(text_browser=text_browser, debug=debug)
        else:
            env.setup_dynamic_tests_d(data_path,test_dict=test_dict)
            text_browser.append("###########  Executing tests...   ##########################\n")
            text_browser.moveCursor(text_browser.textCursor().End)
            env.run_tests(text_browser=text_browser, debug=debug)
        text_browser.append("##########  Results   #####################################\n")
        text_browser.moveCursor(text_browser.textCursor().End)
        if not os.path.exists('./result'):
            os.mkdir('./result')
        file_name = result_file_path
        env.log_results(file_name, mode='dynamic')