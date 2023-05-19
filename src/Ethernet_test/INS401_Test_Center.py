import os
import time
import module.global_var as global_var

from ..conmunicator.print_center import pass_print, error_print

from ..test_framwork.Test_Logger import xlsx_factory
from ..test_framwork.Test_Cases import Test_Section
from ..test_framwork.Test_Cases import Code
from ..test_framwork.Test_Cases import Condition_Check
from ..test_framwork.Test_Cases import Condition_Check_dlc
from ..test_framwork.Jsonf_Creater import Setting_Json_Creat
from .INS401_Test_Function import Test_Scripts, Dynamic_Test_Script

class Test_Environment:

    def __init__(self, device=None):
        self.scripts = Test_Scripts(device)
        self.dynamic = Dynamic_Test_Script()
        self.test_sections = []
        self.backup_logf = None
        self.json = Setting_Json_Creat()
        self.properties = self.json.creat()
        self.paramIds = []
        self.values = []
        for i in self.properties["userId"]:
            paramsId = i["ID"]
            value = i["value"]
            self.paramIds.append(paramsId)
            self.values.append(value) 

    # Add test scetions
    def setup_static_tests(self):
        '''
        section name & section ID (used in test result output)
        test case load mode:
        Code: no parameter input
        Condition_Check: two parameters input
        Condition_Check_dlc: one parameter input 
        '''
        section1 = Test_Section("User command test", section_id=1)
        self.test_sections.append(section1)
        section1.add_test_case(Code("Get production test",  self.scripts.get_production_info))
        section1.add_test_case(Code("Check the separator in response of Ping message", self.scripts.info_separator_check))
        section1.add_test_case(Code("Get user configuration parameters test", self.scripts.get_user_configuration_parameters))
        section1.add_test_case(Code("Set user configuration parameters test", self.scripts.set_user_configuration))
        section1.add_test_case(Code("Save user configuration test", self.scripts.save_user_configuration))
        section1.add_test_case(Code("System reset test", self.scripts.send_system_reset_command))
        section1.add_test_case(Code("Get INS/RTK algorithm version test", self.scripts.get_algorithm_version))
        section1.add_test_case(Code("set base rtcm data test", self.scripts.set_base_rtcm_data)) # TODO: update
        section1.add_test_case(Code("set vehicle speed test", self.scripts.set_vehicle_speed_data)) # TODO: update

        section2 = Test_Section("Output packet test", section_id=2)
        self.test_sections.append(section2)
        section2.add_test_case(Code("Output rate of packet-GNSS solution binary packet", self.scripts.output_packet_gnss_solution_test))
        section2.add_test_case(Code("Output rate of packet-INS solution binary packet", self.scripts.output_packet_ins_solution_test))
        section2.add_test_case(Code("Output rate of packet-Diagnostic message binary packet", self.scripts.output_packet_diagnostic_message_test))
        section2.add_test_case(Code("Output rate of packet-IMU solution binary packet", self.scripts.output_packet_raw_imu_data_test))

        section3 = Test_Section("ID setting verification without restart", section_id=3)
        self.test_sections.append(section3)
        section3.add_test_case(Condition_Check("'gnss lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[0], self.values[0]))
        section3.add_test_case(Condition_Check("'gnss lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[1], self.values[1]))
        section3.add_test_case(Condition_Check("'gnss lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[2], self.values[2]))
        section3.add_test_case(Condition_Check("'vrp lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[3], self.values[3]))
        section3.add_test_case(Condition_Check("'vrp lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[4], self.values[4]))
        section3.add_test_case(Condition_Check("'vrp lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[5], self.values[5]))
        section3.add_test_case(Condition_Check("'user lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[6], self.values[6]))
        section3.add_test_case(Condition_Check("'user lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[7], self.values[7]))
        section3.add_test_case(Condition_Check("'user lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[8], self.values[8]))
        section3.add_test_case(Condition_Check("'rotation rbvx' setting verify",  self.scripts.set_parameters_verify, self.paramIds[9], self.values[9]))
        section3.add_test_case(Condition_Check("'rotation rbvy' setting verify",  self.scripts.set_parameters_verify, self.paramIds[10], self.values[10]))
        section3.add_test_case(Condition_Check("'rotation rbvz' setting verify",  self.scripts.set_parameters_verify, self.paramIds[11], self.values[11]))

        section4 = Test_Section("ID setting verification with repower", section_id=4)
        self.test_sections.append(section4)
        section4.add_test_case(Condition_Check_dlc("ID 1-3 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[0]))
        section4.add_test_case(Condition_Check_dlc("ID 4-6 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[3]))
        section4.add_test_case(Condition_Check_dlc("ID 7-9 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[6]))
        section4.add_test_case(Condition_Check_dlc("ID 10-12 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[9]))

        section5 = Test_Section("Longterm Test", section_id=5)
        self.test_sections.append(section5)
        section5.add_test_case(Code("time jump in GNSS Solution packets", self.scripts.gnss_solution_gps_time_jump_test))
        section5.add_test_case(Code("time jump in INS Solution packets", self.scripts.ins_solution_gps_time_jump_test))
        section5.add_test_case(Code("time jump in Diagnosis Message packets", self.scripts.dm_solution_gps_time_jump_test))
        section5.add_test_case(Code("time jump in raw IMU packets", self.scripts.imu_solution_gps_time_jump_test))
        section5.add_test_case(Condition_Check_dlc("repeat set cmd for ID 1-12",  self.scripts.parameters_set_loop, self.paramIds))

        section6 = Test_Section("Vehicle code function test", section_id=6)
        self.test_sections.append(section6)
        section6.add_test_case(Condition_Check("VF33 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x33]))
        section6.add_test_case(Condition_Check("VF34 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34]))
        section6.add_test_case(Condition_Check("VF35 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35]))
        section6.add_test_case(Condition_Check("VF36 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36]))
        section6.add_test_case(Condition_Check("VF33 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56 ,0x46, 0x33, 0x33]))
        section6.add_test_case(Condition_Check("VF34 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34]))
        section6.add_test_case(Condition_Check("VF35 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35]))
        section6.add_test_case(Condition_Check("VF36 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36]))
        section6.add_test_case(Condition_Check("VF33 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x33]))
        section6.add_test_case(Condition_Check("VF34 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34]))
        section6.add_test_case(Condition_Check("VF35 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35]))
        section6.add_test_case(Condition_Check("VF36 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36]))
        section6.add_test_case(Condition_Check_dlc("vehicle table version test", self.scripts.vehicle_table_version_test, self.properties["vehicle code"]["vcode version"]))
        # ERROR: cannot set parent, new parent is in a different thread

        section7 = Test_Section("GNSS packet reasonable check", section_id=7)
        self.test_sections.append(section7)
        section7.add_test_case(Code("check week", self.scripts.GNSS_packet_reasonable_check_week))
        section7.add_test_case(Code("check time of week", self.scripts.GNSS_packet_reasonable_check_time_ms))
        section7.add_test_case(Code("check position type", self.scripts.GNSS_packet_reasonable_check_position_type))
        section7.add_test_case(Code("check number of satellites", self.scripts.GNSS_packet_reasonable_check_satellites))
        section7.add_test_case(Code("check latitude and longitude", self.scripts.GNSS_packet_reasonable_check_latlongitude))

        section8 = Test_Section("INS packet reasonable check", section_id=8)
        self.test_sections.append(section8)
        section8.add_test_case(Code("check week", self.scripts.INS_packet_reasonable_check_week))
        section8.add_test_case(Code("check gps ms", self.scripts.INS_packet_reasonable_check_time_ms))
        section8.add_test_case(Code("check position type", self.scripts.INS_packet_reasonable_check_position_type))
        section8.add_test_case(Code("check status", self.scripts.INS_packet_reasonable_check_status))
        section8.add_test_case(Code("check continent ID", self.scripts.INS_packet_reasonable_check_continent_ID))

        section9 = Test_Section("DM packet reasonable check", section_id=9)
        self.test_sections.append(section9)
        section9.add_test_case(Code("check gps week", self.scripts.DM_packet_reasonable_check_week))
        section9.add_test_case(Code("check gps ms", self.scripts.DM_packet_reasonable_check_time_ms))
        section9.add_test_case(Code("check temperature of IMU/MCU/ST9100", self.scripts.DM_packet_reasonable_check_temp))
        section9.add_test_case(Code("check GNSS status", self.scripts.DM_packet_reasonable_check_status_gnss))
        section9.add_test_case(Code("check IMU status", self.scripts.DM_packet_reasonable_check_status_imu))
        section9.add_test_case(Code("check Operation status", self.scripts.DM_packet_reasonable_check_status_operation))

        section10 = Test_Section("Raw IMU packet reasonable check", section_id=10)
        self.test_sections.append(section10)
        section10.add_test_case(Code("check gps week", self.scripts.IMU_data_packet_reasonable_check_week))
        section10.add_test_case(Code("check gps ms", self.scripts.IMU_data_packet_reasonable_check_ms))
        section10.add_test_case(Code("check accel", self.scripts.IMU_data_packet_reasonable_check_accel))
        section10.add_test_case(Code("check gyro", self.scripts.IMU_data_packet_reasonable_check_gyro))

        section11 = Test_Section("NMEA-GNGGA check", section_id=11)
        self.test_sections.append(section11)
        section11.add_test_case(Code("check ID GNGGA", self.scripts.NMEA_GNGGA_data_packet_check_ID_GNGGA))
        section11.add_test_case(Code("check UTC time", self.scripts.NMEA_GNGGA_data_packet_check_utc_time))
        section11.add_test_case(Code("check latitude", self.scripts.NMEA_GNGGA_data_packet_check_latitude))
        section11.add_test_case(Code("check longitude", self.scripts.NMEA_GNGGA_data_packet_check_longitude))
        section11.add_test_case(Code("check position type", self.scripts.NMEA_GNGGA_data_packet_check_position_type))

        section12 = Test_Section("NMEA-GNZDA check", section_id=12)
        self.test_sections.append(section12)
        section12.add_test_case(Code("check ID GNZDA", self.scripts.NMEA_GNZDA_data_packet_check_ID_GNZDA))
        section12.add_test_case(Code("check UTC time", self.scripts.NMEA_GNZDA_data_packet_check_utc_time))

    def setup_dynamic_tests(self, data_path):
        '''
        section name & section ID (used in test result output)
        test case load mode:
        Code: no parameter input
        Condition_Check: two parameters input
        Condition_Check_dlc: one parameter input 
        '''

        self.dynamic.prepare_data_file(data_path)
        self.dynamic.get_file_time()

        section13 = Test_Section("GNSS packet reasonable check", section_id=13)
        self.test_sections.append(section13)
        section13.add_test_case(Code("check gps week", self.dynamic.GNSS_packet_reasonable_check_week))
        section13.add_test_case(Code("check gps time of week", self.dynamic.GNSS_packet_reasonable_check_time_ms))
        section13.add_test_case(Code("check position type", self.dynamic.GNSS_packet_reasonable_check_position_type))
        section13.add_test_case(Code("check number of satellites", self.dynamic.GNSS_packet_reasonable_check_satellites))
        section13.add_test_case(Code("check latitude and longitude", self.dynamic.GNSS_packet_reasonable_check_latlongitude))

        section14 = Test_Section("INS packet reasonable check", section_id=14)
        self.test_sections.append(section14)
        section14.add_test_case(Code("check week", self.dynamic.INS_packet_reasonable_check_week))
        section14.add_test_case(Code("check gps time of week", self.dynamic.INS_packet_reasonable_check_time_ms))
        section14.add_test_case(Code("check position type", self.dynamic.INS_packet_reasonable_check_position_type))
        section14.add_test_case(Code("check INS status type", self.dynamic.INS_packet_reasonable_check_status))
        section14.add_test_case(Code("check continent ID", self.dynamic.INS_packet_reasonable_check_continent_ID))

        section15 = Test_Section("DM packet reasonable check", section_id=15)
        self.test_sections.append(section15)
        section15.add_test_case(Code("check gps week", self.dynamic.DM_packet_reasonable_check_week))
        section15.add_test_case(Code("check gps time of week", self.dynamic.DM_packet_reasonable_check_time_ms))
        section15.add_test_case(Code("check temperature of IMU/MCU/ST9100", self.dynamic.DM_packet_reasonable_check_temp))
        section15.add_test_case(Code("check GNSS status", self.dynamic.DM_packet_reasonable_check_status_gnss))
        section15.add_test_case(Code("check IMU status", self.dynamic.DM_packet_reasonable_check_status_imu))
        section15.add_test_case(Code("check Operation status", self.dynamic.DM_packet_reasonable_check_status_operation))

        section16 = Test_Section("Raw IMU packet reasonable check", section_id=16)
        self.test_sections.append(section16)
        section16.add_test_case(Code("check gps week", self.dynamic.IMU_data_packet_reasonable_check_week))
        section16.add_test_case(Code("check gps time of week", self.dynamic.IMU_data_packet_reasonable_check_ms))

        section17 = Test_Section("NMEA-GNGGA check", section_id=17)
        self.test_sections.append(section17)
        section17.add_test_case(Code("check ID GNGGA", self.dynamic.NMEA_GNGGA_data_packet_check_ID_GNGGA))
        section17.add_test_case(Code("check UTC time", self.dynamic.NMEA_GNGGA_data_packet_check_utc_time))
        section17.add_test_case(Code("check latitude", self.dynamic.NMEA_GNGGA_data_packet_check_latitude))
        section17.add_test_case(Code("check longitude", self.dynamic.NMEA_GNGGA_data_packet_check_longitude))
        section17.add_test_case(Code("check position type", self.dynamic.NMEA_GNGGA_data_packet_check_position_type))

        section18 = Test_Section("NMEA-GNZDA check", section_id=18)
        self.test_sections.append(section18)
        section18.add_test_case(Code("check ID GNZDA", self.dynamic.NMEA_GNZDA_data_packet_check_ID_GNZDA))
        section18.add_test_case(Code("check UTC time", self.dynamic.NMEA_GNZDA_data_packet_check_utc_time))


    def setup_update_tests(self, last_case_id=None):
        '''for update
        '''
        section1 = Test_Section("User command test", section_id=1)
        self.test_sections.append(section1)
        section1.add_test_case(Code("Get INS/RTK algorithm version test", self.scripts.get_algorithm_version))

    def run_tests(self, text_browser=None, last_case_id=None):
        data_dir = f'./log'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        for i in range(len(self.test_sections)):
                self.test_sections[i].run_test_section(text_browser=text_browser)
                val = (i+1) * (100 / len(self.test_sections))
                global_var.set_value('ProgressBarValue', val)
                time.sleep(0.1)
                    
    def check_backup_logf(self):
        backup_logf_name = f'./log/backup_log.txt'
        data_dir = f'./log'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(backup_logf_name):
            logf = open(backup_logf_name, 'w+')
            logf.close()
        backup_logf = open(backup_logf_name, 'r')
        lines = backup_logf.readlines()
        lines_len = len(lines)
        for i in range(lines_len):
            last_line = lines[lines_len - (i+1)]
            if '-->' in last_line:
                last_case_id = last_line.split(' ')[2]
                backup_logf.close()
                return last_case_id
        backup_logf.close()
        return None
    
    def json_generator(self):
        jsonf = self.json.creat()
        if jsonf is not None:
            pass_print("json file is created")
        else:
            error_print("json file is not created")

    def print_results(self):
        print("Test Results:")
        for section in self.test_sections:
            section_str = "Section " + str(section.section_id) + ": " + section.section_name + "\r\n"
            print(section_str)
            for test in section.test_cases:
                # id = str(section.section_id) + "-" + str(test.test_id)
                id = f'{test.test_id}'
                result = "Passed --> " if test.result['status'] else "Failed --x "
                result_str = result + id + " " + test.test_case_name + " Expected: "+ test.result['expected'] + " Actual: "+  test.result['actual'] + "\r\n"
                print(result_str)

    def log_results(self, file_name, mode):
        xf = xlsx_factory(file_name, mode)
        test_case_sheet = xf.sheet_ready()
        test_actual_val_column = test_case_sheet[0]
        test_result_column = test_case_sheet[1]
        for section in self.test_sections:
            for test in section.test_cases:
                if len(test.result) == 0:
                    return
                if len(test.result['id']) == 7:
                    case_id = test.result['id'][0:2]
                    case_num = int(test.result['id'][3:6]) - 1
                elif len(test.result['id']) == 8:
                    case_id = test.result['id'][0:3]
                    case_num = int(test.result['id'][4:7]) - 1
                status = test.result['status']
                actual_val = test.result['actual']
                if status == False:
                    result_field = test_result_column[case_id]
                    actual_val_field = test_actual_val_column[case_id]
                    xf.change_val(result_field, case_num, 'failed')
                    xf.change_val(actual_val_field, case_num, actual_val)
                    xf.set_cell_color(result_field, case_num)
                    xf.set_cell_color(actual_val_field, case_num)
        xf.savef(file_name)
                    