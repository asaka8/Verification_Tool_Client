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
from .INS401_Test_Function import Static_Test_Scripts, Dynamic_Test_Script

class Test_Environment:
    '''
    Parameters:
        device: Ethernet device class
    '''
    def __init__(self, device=None):
        '''
        scripts: class of static Test functions 
        dynamic: class of dynamic Test functions
        test_sections: the list of test sections (default: [])
        backup_logf: the file to log some backup information (default: None)
        properties: the properties get from setting josn file 
        paramIds: the list of parameters' ID (default: [])
        values: the list of values of each parameter (default: [])
        '''
        self.scripts = Static_Test_Scripts(device)
        self.dynamic = Dynamic_Test_Script()
        self.test_sections = []
        self.backup_logf = None
        json = Setting_Json_Creat()
        self.properties = json.creat()
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
        section1.add_test_case(Code("Get production test",  self.scripts.get_production_info, case_id=1))
        section1.add_test_case(Code("Check the separator in response of Ping message", self.scripts.info_separator_check, case_id=2))
        section1.add_test_case(Code("Get user configuration parameters test", self.scripts.get_user_configuration_parameters, case_id=3))
        section1.add_test_case(Code("Set user configuration parameters test", self.scripts.set_user_configuration, case_id=4))
        section1.add_test_case(Code("Save user configuration test", self.scripts.save_user_configuration, case_id=5))
        section1.add_test_case(Code("System reset test", self.scripts.send_system_reset_command, case_id=6))
        section1.add_test_case(Code("Get INS/RTK algorithm version test", self.scripts.get_algorithm_version, case_id=7))
        section1.add_test_case(Code("set base rtcm data test", self.scripts.set_base_rtcm_data, case_id=8)) # TODO: update
        section1.add_test_case(Code("set vehicle speed test", self.scripts.set_vehicle_speed_data, case_id=9)) # TODO: update

        section2 = Test_Section("Output packet test", section_id=2)
        self.test_sections.append(section2)
        section2.add_test_case(Code("Output rate of packet-GNSS solution binary packet", self.scripts.output_packet_gnss_solution_test, case_id=1))
        section2.add_test_case(Code("Output rate of packet-INS solution binary packet", self.scripts.output_packet_ins_solution_test, case_id=2))
        section2.add_test_case(Code("Output rate of packet-Diagnostic message binary packet", self.scripts.output_packet_diagnostic_message_test, case_id=3))
        section2.add_test_case(Code("Output rate of packet-IMU solution binary packet", self.scripts.output_packet_raw_imu_data_test, case_id=4))

        section3 = Test_Section("ID setting verification without restart", section_id=3)
        self.test_sections.append(section3)
        section3.add_test_case(Condition_Check("'gnss lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[0], self.values[0], case_id=1))
        section3.add_test_case(Condition_Check("'gnss lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[1], self.values[1], case_id=2))
        section3.add_test_case(Condition_Check("'gnss lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[2], self.values[2], case_id=3))
        section3.add_test_case(Condition_Check("'vrp lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[3], self.values[3], case_id=4))
        section3.add_test_case(Condition_Check("'vrp lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[4], self.values[4], case_id=5))
        section3.add_test_case(Condition_Check("'vrp lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[5], self.values[5], case_id=6))
        section3.add_test_case(Condition_Check("'user lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[6], self.values[6], case_id=7))
        section3.add_test_case(Condition_Check("'user lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[7], self.values[7], case_id=8))
        section3.add_test_case(Condition_Check("'user lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[8], self.values[8], case_id=9))
        section3.add_test_case(Condition_Check("'rotation rbvx' setting verify",  self.scripts.set_parameters_verify, self.paramIds[9], self.values[9], case_id=10))
        section3.add_test_case(Condition_Check("'rotation rbvy' setting verify",  self.scripts.set_parameters_verify, self.paramIds[10], self.values[10], case_id=11))
        section3.add_test_case(Condition_Check("'rotation rbvz' setting verify",  self.scripts.set_parameters_verify, self.paramIds[11], self.values[11], case_id=12))

        section4 = Test_Section("ID setting verification with repower", section_id=4)
        self.test_sections.append(section4)
        section4.add_test_case(Condition_Check_dlc("ID 1-3 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[0], case_id=1))
        section4.add_test_case(Condition_Check_dlc("ID 4-6 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[3], case_id=2))
        section4.add_test_case(Condition_Check_dlc("ID 7-9 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[6], case_id=3))
        section4.add_test_case(Condition_Check_dlc("ID 10-12 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[9], case_id=4))

        section5 = Test_Section("Longterm Test", section_id=5)
        self.test_sections.append(section5)
        section5.add_test_case(Code("time jump in GNSS Solution packets", self.scripts.gnss_solution_gps_time_jump_test, case_id=1))
        section5.add_test_case(Code("time jump in INS Solution packets", self.scripts.ins_solution_gps_time_jump_test, case_id=2))
        section5.add_test_case(Code("time jump in Diagnosis Message packets", self.scripts.dm_solution_gps_time_jump_test, case_id=3))
        section5.add_test_case(Code("time jump in raw IMU packets", self.scripts.imu_solution_gps_time_jump_test, case_id=4))
        section5.add_test_case(Condition_Check_dlc("repeat set cmd for ID 1-12",  self.scripts.parameters_set_loop, self.paramIds, case_id=5))

        section6 = Test_Section("Vehicle code function test", section_id=6)
        self.test_sections.append(section6)
        section6.add_test_case(Condition_Check("VF33 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x33], case_id=1))
        section6.add_test_case(Condition_Check("VF34 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34], case_id=2))
        section6.add_test_case(Condition_Check("VF35 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35], case_id=3))
        section6.add_test_case(Condition_Check("VF36 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36], case_id=4))
        section6.add_test_case(Condition_Check("VF33 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56 ,0x46, 0x33, 0x33], case_id=5))
        section6.add_test_case(Condition_Check("VF34 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34], case_id=6))
        section6.add_test_case(Condition_Check("VF35 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35], case_id=7))
        section6.add_test_case(Condition_Check("VF36 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36], case_id=8))
        section6.add_test_case(Condition_Check("VF33 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x33], case_id=9))
        section6.add_test_case(Condition_Check("VF34 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34], case_id=10))
        section6.add_test_case(Condition_Check("VF35 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35], case_id=11))
        section6.add_test_case(Condition_Check("VF36 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36], case_id=12))
        section6.add_test_case(Condition_Check_dlc("vehicle table version test", self.scripts.vehicle_table_version_test, self.properties["vehicle code"]["vcode version"], case_id=13))
        # ERROR: cannot set parent, new parent is in a different thread

        section7 = Test_Section("GNSS packet reasonable check", section_id=7)
        self.test_sections.append(section7)
        section7.add_test_case(Code("check week", self.scripts.GNSS_packet_reasonable_check_week, case_id=1))
        section7.add_test_case(Code("check time of week", self.scripts.GNSS_packet_reasonable_check_time_ms, case_id=2))
        section7.add_test_case(Code("check position type", self.scripts.GNSS_packet_reasonable_check_position_type, case_id=3))
        section7.add_test_case(Code("check number of satellites", self.scripts.GNSS_packet_reasonable_check_satellites, case_id=4))
        section7.add_test_case(Code("check latitude and longitude", self.scripts.GNSS_packet_reasonable_check_latlongitude, case_id=5))

        section8 = Test_Section("INS packet reasonable check", section_id=8)
        self.test_sections.append(section8)
        section8.add_test_case(Code("check week", self.scripts.INS_packet_reasonable_check_week, case_id=1))
        section8.add_test_case(Code("check gps ms", self.scripts.INS_packet_reasonable_check_time_ms, case_id=2))
        section8.add_test_case(Code("check position type", self.scripts.INS_packet_reasonable_check_position_type, case_id=3))
        section8.add_test_case(Code("check status", self.scripts.INS_packet_reasonable_check_status, case_id=4))
        section8.add_test_case(Code("check continent ID", self.scripts.INS_packet_reasonable_check_continent_ID, case_id=5))

        section9 = Test_Section("DM packet reasonable check", section_id=9)
        self.test_sections.append(section9)
        section9.add_test_case(Code("check gps week", self.scripts.DM_packet_reasonable_check_week, case_id=1))
        section9.add_test_case(Code("check gps ms", self.scripts.DM_packet_reasonable_check_time_ms, case_id=2))
        section9.add_test_case(Code("check temperature of IMU/MCU/ST9100", self.scripts.DM_packet_reasonable_check_temp, case_id=3))
        section9.add_test_case(Code("check GNSS status", self.scripts.DM_packet_reasonable_check_status_gnss, case_id=4))
        section9.add_test_case(Code("check IMU status", self.scripts.DM_packet_reasonable_check_status_imu, case_id=5))
        section9.add_test_case(Code("check Operation status", self.scripts.DM_packet_reasonable_check_status_operation, case_id=6))

        section10 = Test_Section("Raw IMU packet reasonable check", section_id=10)
        self.test_sections.append(section10)
        section10.add_test_case(Code("check gps week", self.scripts.IMU_data_packet_reasonable_check_week, case_id=1))
        section10.add_test_case(Code("check gps ms", self.scripts.IMU_data_packet_reasonable_check_ms, case_id=2))
        section10.add_test_case(Code("check accel", self.scripts.IMU_data_packet_reasonable_check_accel, case_id=3))
        section10.add_test_case(Code("check gyro", self.scripts.IMU_data_packet_reasonable_check_gyro, case_id=4))

        section11 = Test_Section("NMEA-GNGGA check", section_id=11)
        self.test_sections.append(section11)
        section11.add_test_case(Code("check ID GNGGA", self.scripts.NMEA_GNGGA_data_packet_check_ID_GNGGA, case_id=1))
        section11.add_test_case(Code("check UTC time", self.scripts.NMEA_GNGGA_data_packet_check_utc_time, case_id=2))
        section11.add_test_case(Code("check latitude", self.scripts.NMEA_GNGGA_data_packet_check_latitude, case_id=3))
        section11.add_test_case(Code("check longitude", self.scripts.NMEA_GNGGA_data_packet_check_longitude, case_id=4))
        section11.add_test_case(Code("check position type", self.scripts.NMEA_GNGGA_data_packet_check_position_type, case_id=5))

        section12 = Test_Section("NMEA-GNZDA check", section_id=12)
        self.test_sections.append(section12)
        section12.add_test_case(Code("check ID GNZDA", self.scripts.NMEA_GNZDA_data_packet_check_ID_GNZDA, case_id=1))
        section12.add_test_case(Code("check UTC time", self.scripts.NMEA_GNZDA_data_packet_check_utc_time, case_id=2))

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
        section13.add_test_case(Code("check gps week", self.dynamic.GNSS_packet_reasonable_check_week, case_id=1))
        section13.add_test_case(Code("check gps time of week", self.dynamic.GNSS_packet_reasonable_check_time_ms, case_id=2))
        section13.add_test_case(Code("check position type", self.dynamic.GNSS_packet_reasonable_check_position_type, case_id=3))
        section13.add_test_case(Code("check number of satellites", self.dynamic.GNSS_packet_reasonable_check_satellites, case_id=4))
        section13.add_test_case(Code("check latitude and longitude", self.dynamic.GNSS_packet_reasonable_check_latlongitude, case_id=5))

        section14 = Test_Section("INS packet reasonable check", section_id=14)
        self.test_sections.append(section14)
        section14.add_test_case(Code("check week", self.dynamic.INS_packet_reasonable_check_week, case_id=1))
        section14.add_test_case(Code("check gps time of week", self.dynamic.INS_packet_reasonable_check_time_ms, case_id=2))
        section14.add_test_case(Code("check position type", self.dynamic.INS_packet_reasonable_check_position_type, case_id=3))
        section14.add_test_case(Code("check INS status type", self.dynamic.INS_packet_reasonable_check_status, case_id=4))
        section14.add_test_case(Code("check continent ID", self.dynamic.INS_packet_reasonable_check_continent_ID, case_id=5))

        section15 = Test_Section("DM packet reasonable check", section_id=15)
        self.test_sections.append(section15)
        section15.add_test_case(Code("check gps week", self.dynamic.DM_packet_reasonable_check_week, case_id=1))
        section15.add_test_case(Code("check gps time of week", self.dynamic.DM_packet_reasonable_check_time_ms, case_id=2))
        section15.add_test_case(Code("check temperature of IMU/MCU/ST9100", self.dynamic.DM_packet_reasonable_check_temp, case_id=3))
        section15.add_test_case(Code("check GNSS status", self.dynamic.DM_packet_reasonable_check_status_gnss, case_id=4))
        section15.add_test_case(Code("check IMU status", self.dynamic.DM_packet_reasonable_check_status_imu, case_id=5))
        section15.add_test_case(Code("check Operation status", self.dynamic.DM_packet_reasonable_check_status_operation, case_id=6))

        section16 = Test_Section("Raw IMU packet reasonable check", section_id=16)
        self.test_sections.append(section16)
        section16.add_test_case(Code("check gps week", self.dynamic.IMU_data_packet_reasonable_check_week, case_id=1))
        section16.add_test_case(Code("check gps time of week", self.dynamic.IMU_data_packet_reasonable_check_ms, case_id=2))

        section17 = Test_Section("NMEA-GNGGA check", section_id=17)
        self.test_sections.append(section17)
        section17.add_test_case(Code("check ID GNGGA", self.dynamic.NMEA_GNGGA_data_packet_check_ID_GNGGA, case_id=1))
        section17.add_test_case(Code("check UTC time", self.dynamic.NMEA_GNGGA_data_packet_check_utc_time, case_id=2))
        section17.add_test_case(Code("check latitude", self.dynamic.NMEA_GNGGA_data_packet_check_latitude, case_id=3))
        section17.add_test_case(Code("check longitude", self.dynamic.NMEA_GNGGA_data_packet_check_longitude, case_id=4))
        section17.add_test_case(Code("check position type", self.dynamic.NMEA_GNGGA_data_packet_check_position_type, case_id=5))

        section18 = Test_Section("NMEA-GNZDA check", section_id=18)
        self.test_sections.append(section18)
        section18.add_test_case(Code("check ID GNZDA", self.dynamic.NMEA_GNZDA_data_packet_check_ID_GNZDA, case_id=1))
        section18.add_test_case(Code("check UTC time", self.dynamic.NMEA_GNZDA_data_packet_check_utc_time, case_id=2))

    def setup_static_tests_d(self, test_dict):
        '''
        section name & section ID (used in test result output)
        test case load mode:
            Code: no parameter input
            Condition_Check: two parameters input
            Condition_Check_dlc: one parameter input 
        Parameters:
            test_dict: the dict include test cases selected (type: dict; example: {"GNSS packet reasonable check": ["check gps week", "check position type"],
                                                                                   "check position type": ["check week", "check gps time of week"]}) 
        '''
        for section, cases in test_dict.items():
            if section == "User command test":
                section1 = Test_Section("User command test", section_id=1)
                self.test_sections.append(section1)
                for case_name in cases:
                    if case_name == "Get production test":
                        section1.add_test_case(Code("Get production test",  self.scripts.get_production_info, case_id=1))
                    elif case_name == "Check the separator in response of Ping message":
                        section1.add_test_case(Code("Check the separator in response of Ping message", self.scripts.info_separator_check, case_id=2))
                    elif case_name == "Get user configuration parameters test":
                        section1.add_test_case(Code("Get user configuration parameters test", self.scripts.get_user_configuration_parameters, case_id=3))
                    elif case_name == "Set user configuration parameters test":
                        section1.add_test_case(Code("Set user configuration parameters test", self.scripts.set_user_configuration, case_id=4))
                    elif case_name == "Save user configuration test":
                        section1.add_test_case(Code("Save user configuration test", self.scripts.save_user_configuration, case_id=5))
                    elif case_name == "System reset test":
                        section1.add_test_case(Code("System reset test", self.scripts.send_system_reset_command, case_id=6))
                    elif case_name == "Get INS/RTK algorithm version test":
                        section1.add_test_case(Code("Get INS/RTK algorithm version test", self.scripts.get_algorithm_version, case_id=7))
                    elif case_name == "set base rtcm data test":
                        section1.add_test_case(Code("set base rtcm data test", self.scripts.set_base_rtcm_data, case_id=8)) # TODO: update
                    elif case_name == "set vehicle speed test":
                        section1.add_test_case(Code("set vehicle speed test", self.scripts.set_vehicle_speed_data, case_id=9)) # TODO: update

            elif section == "Output packet test":
                section2 = Test_Section("Output packet test", section_id=2)
                self.test_sections.append(section2)
                for case_name in cases:
                    if case_name == "Output rate of packet-GNSS solution binary packet":
                        section2.add_test_case(Code("Output rate of packet-GNSS solution binary packet", self.scripts.output_packet_gnss_solution_test, case_id=1))
                    elif case_name == "Output rate of packet-INS solution binary packet":
                        section2.add_test_case(Code("Output rate of packet-INS solution binary packet", self.scripts.output_packet_ins_solution_test, case_id=2))
                    elif case_name == "Output rate of packet-Diagnostic message binary packet":
                        section2.add_test_case(Code("Output rate of packet-Diagnostic message binary packet", self.scripts.output_packet_diagnostic_message_test, case_id=3))
                    elif case_name == "Output rate of packet-IMU solution binary packet":
                        section2.add_test_case(Code("Output rate of packet-IMU solution binary packet", self.scripts.output_packet_raw_imu_data_test, case_id=4))

            elif section == "ID setting verification without restart":
                section3 = Test_Section("ID setting verification without restart", section_id=3)
                self.test_sections.append(section3)
                for case_name in cases:
                    if case_name == "'gnss lever arm x' setting verify":
                        section3.add_test_case(Condition_Check("'gnss lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[0], self.values[0], case_id=1))
                    elif case_name == "'gnss lever arm y' setting verify":
                        section3.add_test_case(Condition_Check("'gnss lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[1], self.values[1], case_id=2))
                    elif case_name == "'gnss lever arm z' setting verify":
                        section3.add_test_case(Condition_Check("'gnss lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[2], self.values[2], case_id=3))
                    elif case_name == "'vrp lever arm x' setting verify":
                        section3.add_test_case(Condition_Check("'vrp lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[3], self.values[3], case_id=4))
                    elif case_name == "'vrp lever arm y' setting verify":
                        section3.add_test_case(Condition_Check("'vrp lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[4], self.values[4], case_id=5))
                    elif case_name == "'vrp lever arm z' setting verify":
                        section3.add_test_case(Condition_Check("'vrp lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[5], self.values[5], case_id=6))
                    elif case_name == "'user lever arm x' setting verify":
                        section3.add_test_case(Condition_Check("'user lever arm x' setting verify",  self.scripts.set_parameters_verify, self.paramIds[6], self.values[6], case_id=7))
                    elif case_name == "'user lever arm y' setting verify":
                        section3.add_test_case(Condition_Check("'user lever arm y' setting verify",  self.scripts.set_parameters_verify, self.paramIds[7], self.values[7], case_id=8))
                    elif case_name == "'user lever arm z' setting verify":
                        section3.add_test_case(Condition_Check("'user lever arm z' setting verify",  self.scripts.set_parameters_verify, self.paramIds[8], self.values[8], case_id=9))
                    elif case_name == "'rotation rbvx' setting verify":
                        section3.add_test_case(Condition_Check("'rotation rbvx' setting verify",  self.scripts.set_parameters_verify, self.paramIds[9], self.values[9], case_id=10))
                    elif case_name == "'rotation rbvy' setting verify":
                        section3.add_test_case(Condition_Check("'rotation rbvy' setting verify",  self.scripts.set_parameters_verify, self.paramIds[10], self.values[10], case_id=11))
                    elif case_name == "'rotation rbvz' setting verify": 
                        section3.add_test_case(Condition_Check("'rotation rbvz' setting verify",  self.scripts.set_parameters_verify, self.paramIds[11], self.values[11], case_id=12))

            elif section == "ID setting verification with repower":
                section4 = Test_Section("ID setting verification with repower", section_id=4)
                self.test_sections.append(section4)
                for case_name in cases:
                    if case_name == "ID 1-3 setting random params test":
                        section4.add_test_case(Condition_Check_dlc("ID 1-3 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[0], case_id=1))
                    elif case_name == "ID 4-6 setting random params test":
                        section4.add_test_case(Condition_Check_dlc("ID 4-6 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[3], case_id=2))
                    elif case_name == "ID 7-9 setting random params test":
                        section4.add_test_case(Condition_Check_dlc("ID 7-9 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[6], case_id=3))
                    elif case_name == "ID 10-12 setting random params test":
                        section4.add_test_case(Condition_Check_dlc("ID 10-12 setting random params test",  self.scripts.parameters_set_with_reset, self.paramIds[9], case_id=4))

            elif section == "Longterm Test":
                section5 = Test_Section("Longterm Test", section_id=5)
                self.test_sections.append(section5)
                for case_name in cases:
                    if case_name == "time jump in GNSS Solution packets":
                        section5.add_test_case(Code("time jump in GNSS Solution packets", self.scripts.gnss_solution_gps_time_jump_test, case_id=1))
                    elif case_name == "time jump in INS Solution packets":
                        section5.add_test_case(Code("time jump in INS Solution packets", self.scripts.ins_solution_gps_time_jump_test, case_id=2))
                    elif case_name == "time jump in Diagnosis Message packets":
                        section5.add_test_case(Code("time jump in Diagnosis Message packets", self.scripts.dm_solution_gps_time_jump_test, case_id=3))
                    elif case_name == "time jump in raw IMU packets":
                        section5.add_test_case(Code("time jump in raw IMU packets", self.scripts.imu_solution_gps_time_jump_test, case_id=4))
                    elif case_name == "repeat set cmd for ID 1-12":
                        section5.add_test_case(Condition_Check_dlc("repeat set cmd for ID 1-12",  self.scripts.parameters_set_loop, self.paramIds, case_id=5))

            elif section == "Vehicle code function test":
                section6 = Test_Section("Vehicle code function test", section_id=6)
                self.test_sections.append(section6)
                for case_name in cases:
                    if case_name == "VF33 setting test":
                        section6.add_test_case(Condition_Check("VF33 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x33], case_id=1))
                    elif case_name == "VF34 setting test":
                        section6.add_test_case(Condition_Check("VF34 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34], case_id=2))
                    elif case_name == "VF35 setting test":
                        section6.add_test_case(Condition_Check("VF35 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35], case_id=3))
                    elif case_name == "VF36 setting test":
                        section6.add_test_case(Condition_Check("VF36 setting test", self.scripts.vehicle_code_setting_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36], case_id=4))
                    elif case_name == "VF33 vehicle code status test":
                        section6.add_test_case(Condition_Check("VF33 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56 ,0x46, 0x33, 0x33], case_id=5))
                    elif case_name == "VF34 vehicle code status test":
                        section6.add_test_case(Condition_Check("VF34 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34], case_id=6))
                    elif case_name == "VF35 vehicle code status test":
                        section6.add_test_case(Condition_Check("VF35 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35], case_id=7))
                    elif case_name == "VF36 vehicle code status test":
                        section6.add_test_case(Condition_Check("VF36 vehicle code status test", self.scripts.vehicle_code_status_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36], case_id=8))
                    elif case_name == "VF33 vehicle code setting params test":
                        section6.add_test_case(Condition_Check("VF33 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x33], case_id=9))
                    elif case_name == "VF34 vehicle code setting params test":
                        section6.add_test_case(Condition_Check("VF34 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x34], case_id=10))
                    elif case_name == "VF35 vehicle code setting params test":
                        section6.add_test_case(Condition_Check("VF35 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x35], case_id=11))
                    elif case_name == "VF36 vehicle code setting params test":
                        section6.add_test_case(Condition_Check("VF36 vehicle code setting params test", self.scripts.vehicle_code_params_test, self.paramIds[13], [0x56, 0x46, 0x33, 0x36], case_id=12))
                    elif case_name == "vehicle table version test":
                        section6.add_test_case(Condition_Check_dlc("vehicle table version test", self.scripts.vehicle_table_version_test, self.properties["vehicle code"]["vcode version"], case_id=13))

            elif section == "GNSS packet reasonable check":
                section7 = Test_Section("GNSS packet reasonable check", section_id=7)
                self.test_sections.append(section7)
                for case_name in cases:
                    if case_name == "check week":
                        section7.add_test_case(Code("check week", self.scripts.GNSS_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check time of week":
                        section7.add_test_case(Code("check time of week", self.scripts.GNSS_packet_reasonable_check_time_ms, case_id=2))
                    elif case_name == "check position type":
                        section7.add_test_case(Code("check position type", self.scripts.GNSS_packet_reasonable_check_position_type, case_id=3))
                    elif case_name == "check number of satellites":
                        section7.add_test_case(Code("check number of satellites", self.scripts.GNSS_packet_reasonable_check_satellites, case_id=4))
                    elif case_name == "check latitude and longitude":
                        section7.add_test_case(Code("check latitude and longitude", self.scripts.GNSS_packet_reasonable_check_latlongitude, case_id=5))

            elif section == "INS packet reasonable check":
                section8 = Test_Section("INS packet reasonable check", section_id=8)
                self.test_sections.append(section8)
                for case_name in cases:
                    if case_name == "check week":
                        section8.add_test_case(Code("check week", self.scripts.INS_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check gps ms":
                        section8.add_test_case(Code("check gps ms", self.scripts.INS_packet_reasonable_check_time_ms, case_id=2))
                    elif case_name == "check position type":
                        section8.add_test_case(Code("check position type", self.scripts.INS_packet_reasonable_check_position_type, case_id=3))
                    elif case_name == "check status":
                        section8.add_test_case(Code("check status", self.scripts.INS_packet_reasonable_check_status, case_id=4))
                    elif case_name == "check continent ID":
                        section8.add_test_case(Code("check continent ID", self.scripts.INS_packet_reasonable_check_continent_ID, case_id=5))

            elif section == "DM packet reasonable check":
                section9 = Test_Section("DM packet reasonable check", section_id=9)
                self.test_sections.append(section9)
                for case_name in cases:
                    if case_name == "check gps week":
                        section9.add_test_case(Code("check gps week", self.scripts.DM_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check gps ms":
                        section9.add_test_case(Code("check gps ms", self.scripts.DM_packet_reasonable_check_time_ms, case_id=2))
                    elif case_name == "check temperature of IMU/MCU/ST9100":
                        section9.add_test_case(Code("check temperature of IMU/MCU/ST9100", self.scripts.DM_packet_reasonable_check_temp, case_id=3))
                    elif case_name == "check GNSS status":
                        section9.add_test_case(Code("check GNSS status", self.scripts.DM_packet_reasonable_check_status_gnss, case_id=4))
                    elif case_name == "check IMU status":
                        section9.add_test_case(Code("check IMU status", self.scripts.DM_packet_reasonable_check_status_imu, case_id=5))
                    elif case_name == "check Operation status":
                        section9.add_test_case(Code("check Operation status", self.scripts.DM_packet_reasonable_check_status_operation, case_id=6))

            elif section == "Raw IMU packet reasonable check":
                section10 = Test_Section("Raw IMU packet reasonable check", section_id=10)
                self.test_sections.append(section10)
                for case_name in cases:
                    if case_name == "check gps week":
                        section10.add_test_case(Code("check gps week", self.scripts.IMU_data_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check gps ms":
                        section10.add_test_case(Code("check gps ms", self.scripts.IMU_data_packet_reasonable_check_ms, case_id=2))
                    elif case_name == "check accel":
                        section10.add_test_case(Code("check accel", self.scripts.IMU_data_packet_reasonable_check_accel, case_id=3))
                    elif case_name == "check gyro":
                        section10.add_test_case(Code("check gyro", self.scripts.IMU_data_packet_reasonable_check_gyro, case_id=4))

            elif section == "NMEA-GNGGA check":
                section11 = Test_Section("NMEA-GNGGA check", section_id=11)
                self.test_sections.append(section11)
                for case_name in cases:
                    if case_name == "check ID GNGGA":
                        section11.add_test_case(Code("check ID GNGGA", self.scripts.NMEA_GNGGA_data_packet_check_ID_GNGGA, case_id=1))
                    elif case_name == "check UTC time":
                        section11.add_test_case(Code("check UTC time", self.scripts.NMEA_GNGGA_data_packet_check_utc_time, case_id=2))
                    elif case_name == "check latitude":
                        section11.add_test_case(Code("check latitude", self.scripts.NMEA_GNGGA_data_packet_check_latitude, case_id=3))
                    elif case_name == "check longitude":  
                        section11.add_test_case(Code("check longitude", self.scripts.NMEA_GNGGA_data_packet_check_longitude, case_id=4))
                    elif case_name == "check position type":# continue tag
                        section11.add_test_case(Code("check position type", self.scripts.NMEA_GNGGA_data_packet_check_position_type, case_id=5))

            elif section_name == "NMEA-GNZDA check":
                section12 = Test_Section("NMEA-GNZDA check", section_id=12)
                self.test_sections.append(section12)
                for case_name in cases:
                    if case_name == "check ID GNZDA":
                        section12.add_test_case(Code("check ID GNZDA", self.scripts.NMEA_GNZDA_data_packet_check_ID_GNZDA, case_id=1))
                    if case_name == "check UTC time":
                        section12.add_test_case(Code("check UTC time", self.scripts.NMEA_GNZDA_data_packet_check_utc_time, case_id=2))

    def setup_dynamic_tests_d(self, data_path, test_dict):
        '''
        section name & section ID (used in test result output)
        test case load mode:
            Code: no parameter input
            Condition_Check: two parameters input
            Condition_Check_dlc: one parameter input 
        Parameters:
            data_path: the path of dynamic test data (type: string; example: './data/user_2023_06_20_15_55_14.bin')
            test_dict: the dict include test cases selected (type: dict; example: {"GNSS packet reasonable check": ["check gps week", "check position type"],
                                                                                   "check position type": ["check week", "check gps time of week"]})
        '''

        self.dynamic.prepare_data_file(data_path)
        self.dynamic.get_file_time()

        for section, cases in test_dict.items():
            if section == "GNSS packet reasonable check":
                section13 = Test_Section("GNSS packet reasonable check", section_id=13)
                self.test_sections.append(section13)
                for case_name in cases:
                    if case_name == "check gps week":
                        section13.add_test_case(Code("check gps week", self.dynamic.GNSS_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check gps time of week":
                        section13.add_test_case(Code("check gps time of week", self.dynamic.GNSS_packet_reasonable_check_time_ms, case_id=2))
                    elif case_name == "check position type":
                        section13.add_test_case(Code("check position type", self.dynamic.GNSS_packet_reasonable_check_position_type, case_id=3))
                    elif case_name == "check number of satellites":
                        section13.add_test_case(Code("check number of satellites", self.dynamic.GNSS_packet_reasonable_check_satellites, case_id=4))
                    elif case_name == "check latitude and longitude":
                        section13.add_test_case(Code("check latitude and longitude", self.dynamic.GNSS_packet_reasonable_check_latlongitude, case_id=5))

            elif section == "INS packet reasonable check":
                section14 = Test_Section("INS packet reasonable check", section_id=14)
                self.test_sections.append(section14)
                for case_name in cases:
                    if case_name == "check week":
                        section14.add_test_case(Code("check week", self.dynamic.INS_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check gps time of week":
                        section14.add_test_case(Code("check gps time of week", self.dynamic.INS_packet_reasonable_check_time_ms, case_id=2))
                    elif case_name == "check position type":
                        section14.add_test_case(Code("check position type", self.dynamic.INS_packet_reasonable_check_position_type, case_id=3))
                    elif case_name == "check INS status type":
                        section14.add_test_case(Code("check INS status type", self.dynamic.INS_packet_reasonable_check_status, case_id=4))
                    elif case_name == "check continent ID":
                        section14.add_test_case(Code("check continent ID", self.dynamic.INS_packet_reasonable_check_continent_ID, case_id=5))

            if section == "DM packet reasonable check":
                section15 = Test_Section("DM packet reasonable check", section_id=15)
                self.test_sections.append(section15)
                for case_name in cases:
                    if case_name == "check gps week":
                        section15.add_test_case(Code("check gps week", self.dynamic.DM_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check gps time of week":
                        section15.add_test_case(Code("check gps time of week", self.dynamic.DM_packet_reasonable_check_time_ms, case_id=2))
                    elif case_name == "check temperature of IMU/MCU/ST9100":
                        section15.add_test_case(Code("check temperature of IMU/MCU/ST9100", self.dynamic.DM_packet_reasonable_check_temp, case_id=3))
                    elif case_name == "check GNSS status":
                        section15.add_test_case(Code("check GNSS status", self.dynamic.DM_packet_reasonable_check_status_gnss, case_id=4))
                    elif case_name == "check IMU status":
                        section15.add_test_case(Code("check IMU status", self.dynamic.DM_packet_reasonable_check_status_imu, case_id=5))
                    elif case_name == "check Operation status":
                        section15.add_test_case(Code("check Operation status", self.dynamic.DM_packet_reasonable_check_status_operation, case_id=6))

            if section == "Raw IMU packet reasonable check":
                section16 = Test_Section("Raw IMU packet reasonable check", section_id=16)
                self.test_sections.append(section16)
                for case_name in cases:
                    if case_name == "check gps week":
                        section16.add_test_case(Code("check gps week", self.dynamic.IMU_data_packet_reasonable_check_week, case_id=1))
                    elif case_name == "check gps time of week":
                        section16.add_test_case(Code("check gps time of week", self.dynamic.IMU_data_packet_reasonable_check_ms, case_id=2))

            if section == "NMEA-GNGGA check":
                section17 = Test_Section("NMEA-GNGGA check", section_id=17)
                self.test_sections.append(section17)
                for case_name in cases:
                    if case_name == "check ID GNGGA":
                        section17.add_test_case(Code("check ID GNGGA", self.dynamic.NMEA_GNGGA_data_packet_check_ID_GNGGA, case_id=1))
                    elif case_name == "check UTC time":
                        section17.add_test_case(Code("check UTC time", self.dynamic.NMEA_GNGGA_data_packet_check_utc_time, case_id=2))
                    elif case_name == "check latitude":
                        section17.add_test_case(Code("check latitude", self.dynamic.NMEA_GNGGA_data_packet_check_latitude, case_id=3))
                    elif case_name == "check longitude":
                        section17.add_test_case(Code("check longitude", self.dynamic.NMEA_GNGGA_data_packet_check_longitude, case_id=4))
                    elif case_name == "check position type":
                        section17.add_test_case(Code("check position type", self.dynamic.NMEA_GNGGA_data_packet_check_position_type, case_id=5))

            if section == "NMEA-GNZDA check":
                section18 = Test_Section("NMEA-GNZDA check", section_id=18)
                self.test_sections.append(section18)
                for case_name in cases:
                    if case_name == "check ID GNZDA":
                        section18.add_test_case(Code("check ID GNZDA", self.dynamic.NMEA_GNZDA_data_packet_check_ID_GNZDA, case_id=1))
                    elif case_name == "check UTC time":
                        section18.add_test_case(Code("check UTC time", self.dynamic.NMEA_GNZDA_data_packet_check_utc_time, case_id=2))

    def setup_update_tests(self, last_case_id=None):
        '''for update
        '''
        section1 = Test_Section("User command test", section_id=1)
        self.test_sections.append(section1)
        section1.add_test_case(Code("Get INS/RTK algorithm version test", self.scripts.get_algorithm_version))

    def run_tests(self, text_browser=None, debug=False):
        '''
        Parameters:
            text_browser: link to clinet front
            debug: the flag to control debug mode on/off (type: bool; example: False)
        '''
        data_dir = f'./log'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        for i in range(len(self.test_sections)):
            self.test_sections[i].run_test_section(text_browser=text_browser, debug=debug)
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
        '''
        Parameters:
            file_name: the name of the results file (type: string; example: './case/INS401_ETHERNET_INTERFACE_FUNCTION_TEST_CASE_v3.0.xlsx')
            mode: static/dynamic (type: string; example: static)
        '''
        xf = xlsx_factory(file_name, mode)
        test_case_sheet = xf.sheet_ready()
        test_actual_val_column = test_case_sheet[0]
        test_result_column = test_case_sheet[1]
        for section in self.test_sections:
            for test in section.test_cases:
                if len(test.result) == 0:
                    return
                case_id = 'E{}'.format(section.section_id)
                case_num = test.result['id'] - 1
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