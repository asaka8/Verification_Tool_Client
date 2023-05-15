import os
import argparse

from ..conmunicator.INS401_Ethernet import Ethernet_Dev
from .INS401_Test_Center import Test_Environment

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='static', action='store_true')
    parser.add_argument('-d', dest='dynamic', action='store_true')
    parser.add_argument('-t', dest='test', action='store_true')
    parser.add_argument('-config', dest='config', action='store_true')
    args = parser.parse_args()

    if args.static:
        uut = Ethernet_Dev()
        print("\n#######   INS401 ETHERNET Interface Verification V3.0   #######\n")
        
        result = uut.find_device()
        if result != True:
            return
        
        result = uut.ping_device()
        if result != True:
            print('Ethernet ping error.')
            return
        
        model = uut.model_string 
        serial_number = uut.serial_number
        version = uut.app_version
        
        print("\n# UUT Model: ", model)
        print("\n# UUT Serial Number: ", serial_number)
        print("\n# UUT Version: ", version)
        print("")

        env = Test_Environment(uut)
        last_case_id = env.check_backup_logf()
        env.setup_static_tests()
        print("###########  Executing tests...   ##########################\n")
        env.run_tests(last_case_id)
        print("##########  Results   #####################################\n")
        env.print_results()
        if not os.path.exists('./result'):
            os.mkdir('./result')
        file_name = f'./result/test_results_{str(serial_number)}_{str(version)}.xlsx'
        env.log_results(file_name)

    elif args.dynamic:
        env = Test_Environment()
        last_case_id = env.check_backup_logf()
        env.setup_dynamic_tests()
        print("###########  Executing tests...   ##########################\n")
        env.run_tests(last_case_id)
        print("##########  Results   #####################################\n")
        env.print_results()
        if not os.path.exists('./result'):
            os.mkdir('./result')
        file_name = f'./result/test_results.xlsx'
        env.log_results(file_name)

    elif args.test:
        uut = Ethernet_Dev()
        print("\n#######   INS401 ETHERNET Interface Verification V3.0   #######\n")
        
        result = uut.find_device()
        if result != True:
            return
        
        result = uut.ping_device()
        if result != True:
            print('Ethernet ping error.')
            return
        
        model = uut.model_string 
        serial_number = uut.serial_number
        version = uut.app_version
        
        print("\n# UUT Model: ", model)
        print("\n# UUT Serial Number: ", serial_number)
        print("\n# UUT Version: ", version)
        print("")

        env = Test_Environment(uut)
        env.setup_update_tests()
        print("###########  Executing tests...   ##########################\n")
        env.run_tests()
        print("##########  Results   #####################################\n")
        env.print_results()

    elif args.config:
        env = Test_Environment()
        env.json_generator()

class Verification:
    def __init__(self):
        pass

    def static_test(self, text_browser):
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
        env.setup_static_tests()
        text_browser.append("###########  Executing tests...   ##########################\n")
        text_browser.moveCursor(text_browser.textCursor().End)
        env.run_tests(text_browser=text_browser)
        text_browser.append("Test finished")
        text_browser.moveCursor(text_browser.textCursor().End)
        if not os.path.exists('./result'):
            os.mkdir('./result')
        file_name = f'./result/test_results_{str(serial_number)}_{str(version)}.xlsx'
        env.log_results(file_name)

    def dynamic_test(self, text_browser, data_path, result_file_path):
        env = Test_Environment()
        last_case_id = env.check_backup_logf()
        env.setup_dynamic_tests(data_path)
        text_browser.append("###########  Executing tests...   ##########################\n")
        text_browser.moveCursor(text_browser.textCursor().End)
        env.run_tests(text_browser=text_browser)
        text_browser.append("##########  Results   #####################################\n")
        text_browser.moveCursor(text_browser.textCursor().End)
        if not os.path.exists('./result'):
            os.mkdir('./result')
        file_name = result_file_path
        env.log_results(file_name)