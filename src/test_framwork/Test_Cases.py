import sys
import time

from .Test_Logger import TestLogger
from ..conmunicator.print_center import pass_print, error_print

class Test_Section:
    def __init__(self, section_name, section_id):
        self.section_name = section_name
        self.section_id = section_id
        self.test_cases = []
        self.total_test_cases = 0

    def add_test_case(self, test_case):
        self.test_cases.append(test_case)
        self.total_test_cases += 1
        test_case.test_id = self.total_test_cases

    def run_test_section(self, text_browser=None, debug=False):
        if debug == False:
            counter = 0
            for test in self.test_cases:
                # text_browser.append(f'{self.section_id}. {self.section_name}\r\n')
                counter = counter + 1
                caseID = str(counter)
                if len(caseID) == 1:
                    id = f'E{self.section_id}-00{caseID} '
                elif len(caseID) == 2:
                    id = f'E{self.section_id}-0{caseID} '
                else:
                    id = f'E{self.section_id}-{caseID} '
                test.run_test_case(id, text_browser=text_browser)
        else:
            for case in self.test_cases:
                text_browser.append(f'{self.section_id}. {self.section_name}\r\n')
                text_browser.moveCursor(text_browser.textCursor().End)
                caseID = str(case.case_id)
                # print(caseID)
                if len(caseID) == 1:
                    id = f'E{self.section_id}-00{caseID} '
                elif len(caseID) == 2:
                    id = f'E{self.section_id}-0{caseID} '
                else:
                    id = f'E{self.section_id}-{caseID} '
                case.run_test_case(id ,text_browser=text_browser)

#############################################

class Test_Case:
    def __init__(self, case_name, handle=None, cmd=None, param=None, case_id=None):
        self.test_case_name = case_name
        self.handle = handle
        self.result = []
        self.cmd = cmd
        self.param = param
        self.case_id = case_id

    def _prepare_result(self, response):
        expected_res = ''
        actual_res = ''

        if type(response[1]) is int:
            actual_res = str(response[1])
        elif type(response[1]) is list:
            for i in response[1]:
                if type(i) is int:
                    actual_res += str(i)
                else:
                    actual_res += i
        else:
            actual_res = response[1]

        if type(response[2]) is int:
            expected_res = str(response[2])
        elif type(response[2]) is list:
            for i in response[2]:
                if type(i) is int:
                    expected_res += str(i) + ", "
                else:
                    expected_res += i + ", "
        else:
            expected_res = response[2]

        self.result = { 'id': self.case_id,
                        'test_name': self.test_case_name,
                        'expected': expected_res,
                        'actual': actual_res,
                        'status': response[0]}


    def run_test_case(self, id):
        raise NotImplementedError("Subclass must implement abstract method")
        #print("\t\t" + self.test_case_name + "\r\n")
        #if(self.handle != None):
        #    self.result = self.handle(self.cmd, self.param)

#===========================================#

class Condition_Check(Test_Case):

    def run_test_case(self, id, text_browser=None):
        log = TestLogger()
        self.test_id = id

        text_browser.append(f"{id}{self.test_case_name}")
        text_browser.moveCursor(text_browser.textCursor().End)

        if(self.handle != None):
            response = self.handle(self.cmd, self.param)
            self._prepare_result(response)

            text_browser.append(f"{self.test_case_name} {self.result['expected']} {self.result['actual']}\r\n")
            text_browser.moveCursor(text_browser.textCursor().End)

            test_outcome = id + self.test_case_name + "Expected: "+ self.result['expected'] + " Actual: "+  self.result['actual']  + "\r\n"

            result_str = "Passed --> " + test_outcome if response[0] else "Failed --> " +  test_outcome
            #print(result_str)
            log.backup_log(result_str)

#===========================================#

class Code(Test_Case):

    def run_test_case(self, id, text_browser=None):
        log = TestLogger()
        self.test_id = id

        text_browser.append(f"{id}{self.test_case_name}")
        text_browser.moveCursor(text_browser.textCursor().End)

        if(self.handle != None):

            response = self.handle()
            self._prepare_result(response)
            
            text_browser.append(f"{self.test_case_name} {self.result['expected']} {self.result['actual']}\r\n")
            text_browser.moveCursor(text_browser.textCursor().End)

            test_outcome = id + self.test_case_name + "Expected: "+ self.result['expected'] + " Actual: "+  self.result['actual']  + "\r\n"

            result_str = "Passed --> " + test_outcome if response[0] else "Failed --> " +  test_outcome
            #print(result_str)
            log.backup_log(result_str)

#===========================================#

class Condition_Check_dlc(Test_Case):

    def run_test_case(self, id, text_browser=None):
        log = TestLogger()
        self.test_id = id

        text_browser.append(f"{id}{self.test_case_name}")
        text_browser.moveCursor(text_browser.textCursor().End)

        if(self.handle != None):

            response = self.handle(self.cmd)
            self._prepare_result(response)
            
            text_browser.append(f"{self.test_case_name} {self.result['expected']} {self.result['actual']}\r\n")
            text_browser.moveCursor(text_browser.textCursor().End)

            test_outcome = id + self.test_case_name + "Expected: "+ self.result['expected'] + " Actual: "+  self.result['actual']  + "\r\n"

            result_str = "Passed --> " + test_outcome if response[0] else "Failed --> " +  test_outcome
            #print(result_str)
            log.backup_log(result_str)