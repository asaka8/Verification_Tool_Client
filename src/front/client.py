import sys
import time
import threading
import concurrent.futures

from PySide2.QtWidgets import QDialog, QMainWindow, QMessageBox, QFileDialog, QApplication, QWidget, QTreeWidget, \
    QVBoxLayout, QTreeWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QTreeWidgetItemIterator
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QThread, QMimeData, Signal, Qt
from PySide2.QtGui import QFont, QIcon, QDrag

# from .debug_ui import StaticDebugSettingWidget, DynamicDebugSettingWidget

from ..conmunicator.INS401_Ethernet import Ethernet_Dev
from ..Ethernet_test.INS401_Verification import Verification
from ..test_framwork.Jsonf_Creater import Setting_Json_Creat
from ..Ethernet_test.INS401_Test_Center import Test_Environment

from module.myThread import MyThread as thread
from module.myUiLoader import myUiLoader as UiLoader
import module.global_var as global_var

class SettingDialog(QDialog):
    def __init__(self, mode=None):
        super(SettingDialog, self).__init__()
        # load setting dialog ui file
        setting_qfile = QFile("ui/setting_dialog.ui")
        setting_qfile.open(QFile.ReadOnly)
        setting_qfile.close()
        self.setting_ui = UiLoader().loadUi(setting_qfile, self)
        if mode  == 'static':
            self.setting_ui.setWindowTitle("Static Setting")
        elif mode == 'dynamic':
            self.setting_ui.setWindowTitle("Dynamic Setting")
        elif mode == 'debug':
            self.setting_ui.setWindowTitle("Debug Setting")

        # LineEdit initialization
        self.linedit_initial_value_dict = {
            "ins sn": self.setting_ui.InsSnLineEdit.text(),
            "hardware": self.setting_ui.HardwareLineEdit.text(),
            "imu sn": self.setting_ui.ImuSnLineEdit.text(),
            "rtk ins app": self.setting_ui.RtkInsAppLineEdit.text(),
            "bootloader": self.setting_ui.BootloaderLineEdit.text(),
            "imu330nl fw": self.setting_ui.ImuFwLineEdit.text(),
            "sta9100 fw": self.setting_ui.StaFwLineEdit.text(),

            "ins": self.setting_ui.INSLineEdit.text(),
            "rtk": self.setting_ui.RTKLineEdit.text(),

            "longterm run time": self.setting_ui.LongtermRunTimeLineEdit.text(),
            "static run time": self.setting_ui.StaticRunTimeLineEdit.text(),
            "static postion type": self.setting_ui.StaticPosComboBox.currentText(),
            "dynamic postion type": self.setting_ui.DynamicPosComboBox.currentText(),

            "enable": self.setting_ui.EnableComboBox.currentText(),
            "ip": self.setting_ui.IpLineEdit.text(),
            "port": self.setting_ui.PortLineEdit.text(),
            "mount point": self.setting_ui.MountPointLineEdit.text(),
            "user name": self.setting_ui.UserNameLineEdit.text(),
            "password": self.setting_ui.PasswordLineEdit.text()
        }

        # thread initialization
        self.check_ntrip_enable_thread = thread(target=self.check_ntrip_enable)
        self.check_ntrip_enable_thread.start()

        # button function initialization
        self.setting_ui.SaveButton.clicked.connect(self.save_setting)
        self.setting_ui.ResetButton.clicked.connect(self.reset_setting)

        # comboBox function initialization
        if mode != 'dynamic':
            self.setting_ui.DynamicPosComboBox.setEnabled(False)
        elif mode != 'static':
            self.setting_ui.StaticPosComboBox.setEnabled(False)
        
        # add icon
        icon = QIcon("./aceinna.ico")
        self.setting_ui.setWindowIcon(icon)

    def save_setting(self):
        json = Setting_Json_Creat()
        properties = json.creat()
        # get product information
        product_info = properties['productINFO']
        product_info['INS401_SN'] = self.setting_ui.InsSnLineEdit.text()
        product_info['Hardware'] = self.setting_ui.HardwareLineEdit.text()
        product_info['IMU_SN'] = self.setting_ui.ImuSnLineEdit.text()
        product_info['RTK_INS_APP'] = self.setting_ui.RtkInsAppLineEdit.text()
        product_info['Bootloader'] = self.setting_ui.BootloaderLineEdit.text()
        product_info['IMU330NL FW'] = self.setting_ui.ImuFwLineEdit.text() 
        product_info['STA9100 FW'] = self.setting_ui.StaFwLineEdit.text()

        # algorithm version
        algorithm_ver = properties['algorithmVER']
        algorithm_ver['INS'] = self.setting_ui.INSLineEdit.text()
        algorithm_ver['RTK'] = self.setting_ui.RTKLineEdit.text()

        # test parameters
        properties['long term test']['LONGTERM_RUNNING_TIME'] = self.setting_ui.LongtermRunTimeLineEdit.text()
        properties['static test']['STATIC_RUNNING_TIME'] = self.setting_ui.StaticRunTimeLineEdit.text()
        properties['static test']['position type'] = int(self.setting_ui.StaticPosComboBox.currentText()[0])
        properties['dynamic test']['position type'] = int(self.setting_ui.DynamicPosComboBox.currentText()[0])

        # ntrip account
        if self.setting_ui.EnableComboBox.currentText() == 'ON':
            properties['ntrip account']['Enable'] = self.setting_ui.EnableComboBox.currentText()
            properties['ntrip account']['ip'] = self.setting_ui.IpLineEdit.text()
            properties['ntrip account']['port'] = self.setting_ui.PortLineEdit.text()
            properties['ntrip account']['mountPoint'] = self.setting_ui.MountPointLineEdit.text()
            properties['ntrip account']['username'] = self.setting_ui.UserNameLineEdit.text()
            properties['ntrip account']['password'] = self.setting_ui.PasswordLineEdit.text()
        else:
            properties['ntrip account']['Enable'] = self.setting_ui.EnableComboBox.currentText()
        reply = QMessageBox.question(self, 'Save Setting', 'Do you want to save?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            json.save(properties)
            self.setting_ui.close()
        else:
            return
        
    def reset_setting(self):
        self.setting_ui.InsSnLineEdit.setText(self.linedit_initial_value_dict['ins sn'])
        self.setting_ui.HardwareLineEdit.setText(self.linedit_initial_value_dict['hardware'])
        self.setting_ui.ImuSnLineEdit.setText(self.linedit_initial_value_dict['imu sn'])
        self.setting_ui.RtkInsAppLineEdit.setText(self.linedit_initial_value_dict['rtk ins app'])
        self.setting_ui.BootloaderLineEdit.setText(self.linedit_initial_value_dict['bootloader'])
        self.setting_ui.ImuFwLineEdit.setText(self.linedit_initial_value_dict['imu330nl fw'])
        self.setting_ui.StaFwLineEdit.setText(self.linedit_initial_value_dict['sta9100 fw'])

        self.setting_ui.INSLineEdit.setText(self.linedit_initial_value_dict['ins'])
        self.setting_ui.RTKLineEdit.setText(self.linedit_initial_value_dict['rtk'])

        self.setting_ui.LongtermRunTimeLineEdit.setText(self.linedit_initial_value_dict['longterm run time'])
        self.setting_ui.StaticRunTimeLineEdit.setText(self.linedit_initial_value_dict['static run time'])
        self.setting_ui.StaticPosComboBox.setCurrentText(self.linedit_initial_value_dict['static postion type'])
        self.setting_ui.DynamicPosComboBox.setCurrentText(self.linedit_initial_value_dict['dynamic postion type'])
        
        self.setting_ui.EnableComboBox.setCurrentText(self.linedit_initial_value_dict['enable'])
        self.setting_ui.IpLineEdit.setText(self.linedit_initial_value_dict['ip'])
        self.setting_ui.PortLineEdit.setText(self.linedit_initial_value_dict['port'])
        self.setting_ui.MountPointLineEdit.setText(self.linedit_initial_value_dict['mount point'])
        self.setting_ui.UserNameLineEdit.setText(self.linedit_initial_value_dict['user name'])
        self.setting_ui.PasswordLineEdit.setText(self.linedit_initial_value_dict['password'])

    def open(self):
        self.setting_ui.show()
        self.setting_ui.exec_()

    # ----------------------------------------------------------------
    # thread function
    def check_ntrip_enable(self):
        while True:
            if self.setting_ui.EnableComboBox.currentText() == 'OFF':
                self.setting_ui.IpLineEdit.setEnabled(False)
                self.setting_ui.PortLineEdit.setEnabled(False)
                self.setting_ui.MountPointLineEdit.setEnabled(False)
                self.setting_ui.UserNameLineEdit.setEnabled(False)
                self.setting_ui.PasswordLineEdit.setEnabled(False)
            elif self.setting_ui.EnableComboBox.currentText() == 'ON':
                self.setting_ui.IpLineEdit.setEnabled(True)
                self.setting_ui.PortLineEdit.setEnabled(True)
                self.setting_ui.MountPointLineEdit.setEnabled(True)
                self.setting_ui.UserNameLineEdit.setEnabled(True)
                self.setting_ui.PasswordLineEdit.setEnabled(True)

    # ----------------------------------------------------------------
    # thread management
    # ...

    # ----------------------------------------------------------------
    # events
    def closeEvent(self, event):
        if self.check_ntrip_enable_thread is None:
            return
        if self.check_ntrip_enable_thread.is_alive() == True:
            self.check_ntrip_enable_thread.stop()

class StaticDialog(QDialog):
    def __init__(self, debug=False, test_dict=None):
        super(StaticDialog, self).__init__()
        self.debug = debug
        self.test_dict = test_dict
        # load static dialog ui file
        static_qfile = QFile('ui/static_test_dialog.ui')
        static_qfile.open(QFile.ReadOnly)
        static_qfile.close()
        self.static_ui = UiLoader().loadUi(static_qfile, self)

        # button function initialization
        self.static_ui.runButton.clicked.connect(self.start_test)
        self.static_ui.runButton.clicked.connect(self.progressBar_update)
        self.static_ui.cancelButton.clicked.connect(self.cancel_test)
        self.static_ui.settingButton.clicked.connect(self.open_setting_dialog)
        self.static_ui.clearButton.clicked.connect(self.clear_textbrowser)

        # progress bar function initialization
        self.static_ui.progressBar.hide()
        global_var.set_value("ProgressBarValue", 0)

        # textbrowser initialization
        self.static_ui.textBrowser.moveCursor(self.static_ui.textBrowser.textCursor().End)

        # thread initialization
        self.static_test_thread = None
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        # add icon
        icon = QIcon("./aceinna.ico")
        self.static_ui.setWindowIcon(icon)

    # --------------------------------------------------------------------------------------------
    # Static test function
    def start_test(self):
        ver = Verification()
        self.static_ui.progressBar.show()
        
        # self.static_test_thread = thread(target=ver.static_test, name='StaticThread', args=(self.static_ui.textBrowser, ))
        # self.static_test_thread = StaticTestStart(self.static_ui.textBrowser, self.debug, self.test_dict)
        self.thread_executor.submit(ver.static_test, self.static_ui.textBrowser, self.debug, self.test_dict)
        # self.check_thread = thread(target=self.thread_check, name='CheckThread')
        # self.static_test_thread.start(timeout=1)
        # self.check_thread.start()
        self.static_ui.runButton.setEnabled(False)
        self.static_ui.settingButton.setEnabled(False)
        self.static_ui.clearButton.setEnabled(False)
    
    def cancel_test(self):
        if self.static_test_thread is None:
            return
        
        if self.static_test_thread.isRunning() == True:
            reply = QMessageBox.question(self, 'WARNING',
                                            "Are you sure to abort test?",
                                            QMessageBox.Yes |
                                            QMessageBox.No,
                                            QMessageBox.No)
            if reply == QMessageBox.Yes:
                global_var.set_value('AsyncSnifferEnable', False)
                time.sleep(0.5)
                self.thread_close(self.static_test_thread)
            else:
                return

    def open_setting_dialog(self):
        self.settingD = SettingDialog(mode="static")
        self.settingD.open()

    def clear_textbrowser(self):
        self.static_ui.textBrowser.clear()
        self.static_ui.progressBar.setValue(0)

    def progressBar_update(self, pb_val):
        self.thread_setprogressbar_value = SendProgressBarSignal()
        self.thread_setprogressbar_value.progressBarValue.connect(self.progressbarSignal2Value)
        self.thread_setprogressbar_value.start()

    def progressbarSignal2Value(self, pb_val):
        self.static_ui.progressBar.setValue(pb_val)

    # def open(self):
    #     self.static_ui.show()
    #     self.static_ui.exec_()

    #----------------------------------------------------------------
    # thread management
    def thread_check(self):
        while True:
            if self.static_test_thread.isRunning() == False:
                self.static_ui.runButton.setEnabled(True)
                self.static_ui.settingButton.setEnabled(True)
                self.static_ui.clearButton.setEnabled(True)
                break

    def thread_close(self, t):
        if t is not None:
            t.stop()

    # --------------------------------------------------------------------------------------------
    # events
    def closeEvent(self, event):
        if self.static_test_thread is None:
            return
        if self.static_test_thread.isRunning() == True:
            reply = QMessageBox.question(self, 'WARNING',
                                            "Are you sure to quit?",
                                            QMessageBox.Yes |
                                            QMessageBox.No,
                                            QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.thread_close(self.static_test_thread)
                event.accept()
            else:
                event.ignore()


class DynamicDialog(QDialog):
    def __init__(self, data_path, result_file_path, debug=False, test_dict=None):
        super(DynamicDialog, self).__init__()
        self.debug = debug
        self.test_dict = test_dict
        # dynamic dialog initialization
        self.data_path = data_path
        self.result_file_path = result_file_path
        dynamic_qfile = QFile('ui/dynamic_test_dialog.ui')
        dynamic_qfile.open(QFile.ReadOnly)
        dynamic_qfile.close()
        self.dynamic_ui = UiLoader().loadUi(dynamic_qfile, self) # load the UI & class self to adapt the function 'DynamicDialog().show'

         # button function initialization
        self.dynamic_ui.runButton.clicked.connect(self.start_test)
        self.dynamic_ui.runButton.clicked.connect(self.progressBar_update)
        self.dynamic_ui.cancelButton.clicked.connect(self.cancel_test)
        self.dynamic_ui.settingButton.clicked.connect(self.open_setting_dialog)
        # self.dynamic_ui.clearButton.clicked.connect(self.clear_textbrowser)

        # progress bar function initialization
        self.dynamic_ui.progressBar.hide()
        global_var.set_value("ProgressBarValue", 0)

        # thread initialization
        self.dynamic_test_thread = None

        # add icon
        icon = QIcon("./aceinna.ico")
        self.dynamic_ui.setWindowIcon(icon)

    def start_test(self):
        # ver = Verification()
        self.dynamic_ui.progressBar.show()
        
        # self.static_test_thread = thread(target=ver.static_test, name='StaticThread', args=(self.static_ui.textBrowser, ))
        self.dynamic_test_thread = DynamicTestStart(self.dynamic_ui.textBrowser, self.data_path, self.result_file_path, self.debug, self.test_dict)
        self.check_thread = thread(target=self.thread_check, name='CheckThread')
        self.dynamic_test_thread.start()
        self.check_thread.start()
        self.dynamic_ui.runButton.setEnabled(False)
        self.dynamic_ui.settingButton.setEnabled(False)
        self.dynamic_ui.clearButton.setEnabled(False)

    def cancel_test(self):
        if self.dynamic_test_thread is None:
            return
        
        if self.dynamic_test_thread.isRunning() == True:
            reply = QMessageBox.question(self, 'WARNING',
                                            "Are you sure to abort test?",
                                            QMessageBox.Yes |
                                            QMessageBox.No,
                                            QMessageBox.No)
            if reply == QMessageBox.Yes:
                global_var.set_value('AsyncSnifferEnable', False)
                time.sleep(0.5)
                self.thread_close(self.dynamic_test_thread)
            else:
                return

    def progressBar_update(self, pb_val):
        self.thread_setprogressbar_value = SendProgressBarSignal()
        self.thread_setprogressbar_value.progressBarValue.connect(self.progressbarSignal2Value)
        self.thread_setprogressbar_value.start()

    def open_setting_dialog(self):
        self.settingD = SettingDialog(mode="dynamic")
        self.settingD.open()

    def clear_textbrowser(self):
        self.dynamic_ui.textBrowser.clear()
        self.dynamic_ui.progressBar.setValue(0)

    def progressBar_update(self, pb_val):
        self.thread_setprogressbar_value = SendProgressBarSignal()
        self.thread_setprogressbar_value.progressBarValue.connect(self.progressbarSignal2Value)
        self.thread_setprogressbar_value.start()

    def progressbarSignal2Value(self, pb_val):
        self.dynamic_ui.progressBar.setValue(pb_val)

    #---------------------------------------------------------------------------------------------
    # thread management
    def thread_check(self):
        while True:
            if self.dynamic_test_thread.isRunning() == False:
                self.dynamic_ui.runButton.setEnabled(True)
                self.dynamic_ui.settingButton.setEnabled(True)
                self.dynamic_ui.clearButton.setEnabled(True)
                break  

    def thread_close(self, t):
        if t is not None:
            t.stop()

    # --------------------------------------------------------------------------------------------
    # events
    def closeEvent(self, event):
        if self.dynamic_test_thread is None:
            return
        if self.dynamic_test_thread.isRunning() == True:
            reply = QMessageBox.question(self, 'WARNING',
                                            "Are you sure to quit?",
                                            QMessageBox.Yes |
                                            QMessageBox.No,
                                            QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.thread_close(self.dynamic_test_thread)
                event.accept()
            else:
                event.ignore()

class MainWidget(QMainWindow):
    def __init__ (self):
        super().__init__()
        # load main widget ui file
        main_qfile = QFile('ui/main.ui')
        main_qfile.open(QFile.ReadOnly)
        main_qfile.close()
        
        self.main_ui = UiLoader().loadUi(main_qfile)

        # control unit function initialization
        self.main_ui.RunButton.clicked.connect(self.handle_mode_chosed)
        self.main_ui.ModeButtonGroup.buttonClicked.connect(self.handle_button_click)
        self.main_ui.toolButton_1.clicked.connect(self.handle_select_data_path)
        self.main_ui.toolButton_2.clicked.connect(self.handle_select_result_file_path)
        # self.main_ui.DebugRdoButton.setEnabled(False)
        self.assign_network_card()

        self.main_ui.DebugModeComboBox.setEnabled(False)
        self.main_ui.NetworkCardComboBox.setEnabled(False)
        self.main_ui.LocalMacComboBox.setEnabled(False)
        self.main_ui.DataPathLineEdit.setEnabled(False)
        self.main_ui.ResFileLineEdit.setEnabled(False)
        self.main_ui.toolButton_1.setEnabled(False)
        self.main_ui.toolButton_2.setEnabled(False)

        # test mode parameter initialization
        self.static_test_act = False
        self.dynamic_test_act = False
        self.debug_test_act = False

        # Enviroment initialization
        global_var._init()
        self.network_card_list = []
        self.data_path = None

        # thread initialization
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.inDynamic = False
        self.inDebug = False

        # add icon
        icon = QIcon("./aceinna.ico")
        self.main_ui.setWindowIcon(icon)

    #----------------------------------------------------------------

    def handle_select_data_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files(*);;Text Files (*.txt)")
        if file_path:
            self.data_path = file_path
            self.main_ui.DataPathLineEdit.setText(self.data_path)

    def handle_select_result_file_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files(*);;Text Files (*.txt)")
        if file_path:
            self.result_file_path = file_path
            self.main_ui.ResFileLineEdit.setText(self.result_file_path)

    def handle_button_click(self):
        mode_val = self.main_ui.ModeButtonGroup.checkedButton().text()
        if mode_val == 'Static Test':
            self.static_test_act = True
            self.dynamic_test_act = False
            self.debug_test_act = False
            self.inDebug = False
            self.inDynamic = False
            time.sleep(0.1) # the time to wait for Reset control state

            self.main_ui.DebugModeComboBox.setEnabled(False)
            self.main_ui.NetworkCardComboBox.setEnabled(True)
            self.main_ui.LocalMacComboBox.setEnabled(True)

            self.main_ui.DataPathLineEdit.setEnabled(False)
            self.main_ui.ResFileLineEdit.setEnabled(False)
            self.main_ui.toolButton_1.setEnabled(False)
            self.main_ui.toolButton_2.setEnabled(False)

        elif mode_val == 'Dynamic Test':
            self.dynamic_test_act = True
            self.static_test_act = False
            self.debug_test_act = False
            self.inDebug = False
            self.inDynamic = True
            time.sleep(0.1) # the time to wait for Reset control state

            self.main_ui.DebugModeComboBox.setEnabled(False)
            self.main_ui.NetworkCardComboBox.setEnabled(False)
            self.main_ui.LocalMacComboBox.setEnabled(False)

            self.main_ui.DataPathLineEdit.setEnabled(True)
            self.main_ui.ResFileLineEdit.setEnabled(True)
            self.main_ui.toolButton_1.setEnabled(True)
            self.main_ui.toolButton_2.setEnabled(True)

            self.thread_executor.submit(self.check_input_path)

        elif mode_val == 'Debug Test':
            self.debug_test_act = True
            self.static_test_act = False
            self.dynamic_test_act = False
            self.inDebug = True
            self.inDynamic = False
            time.sleep(0.1) # the time to wait for Reset control state

            self.main_ui.DebugModeComboBox.setEnabled(True)
            self.main_ui.NetworkCardComboBox.setEnabled(False)
            self.main_ui.LocalMacComboBox.setEnabled(False)

            self.main_ui.DataPathLineEdit.setEnabled(False)
            self.main_ui.ResFileLineEdit.setEnabled(False)
            self.main_ui.toolButton_1.setEnabled(False)
            self.main_ui.toolButton_2.setEnabled(False)

            self.thread_executor.submit(self.check_debug_mode)

    def handle_mode_chosed(self):
        self.inDynamic = False
        self.inDebug = False
        if self.static_test_act == True:
            self.static_test_act = False
            self.open_static_test_dialog()
        elif self.dynamic_test_act == True:
            self.dynamic_test_act = False
            self.open_dynamic_test_dialog()
        elif self.debug_test_act == True:
            self.debug_test_act = False
            # self.open_debug_test_dialog()
            self.open_debug_setting_dialog()

    def assign_network_card(self):
        self.eth = Ethernet_Dev()
        self.network_card_list = self.eth.comfire_network_card()
        for card in self.network_card_list:
            self.main_ui.NetworkCardComboBox.addItem(card[0])
            self.main_ui.LocalMacComboBox.addItem(card[1])
            
    #----------------------------------------------------------------  
    def open_static_test_dialog(self):
        global_var.set_value('iface', self.main_ui.NetworkCardComboBox.currentText())
        global_var.set_value('src mac', self.main_ui.LocalMacComboBox.currentText())
        self.staticD = StaticDialog()
        self.staticD.show()
    
    def open_dynamic_test_dialog(self):
        self.dynamicD = DynamicDialog(self.data_path, self.result_file_path)
        self.dynamicD.show()

    def open_debug_setting_dialog(self):
        if self.main_ui.DebugModeComboBox.currentText() == 'Static':
            global_var.set_value('iface', self.main_ui.NetworkCardComboBox.currentText())
            global_var.set_value('src mac', self.main_ui.LocalMacComboBox.currentText())
            self.static_debug_setting_dialog = StaticDebugSettingWidget()
            self.static_debug_setting_dialog.show()
        elif self.main_ui.DebugModeComboBox.currentText() == 'Dynamic':
            if self.data_path == None:
                self.data_path = self.main_ui.DataPathLineEdit.text()
                self.dynamic_debug_setting_dialog = DynamicDebugSettingWidget(self.data_path, self.result_file_path)
            else:
                self.dynamic_debug_setting_dialog = DynamicDebugSettingWidget(self.data_path, self.result_file_path)
            self.inDynamic = False
            self.dynamic_debug_setting_dialog.show()
        
    #----------------------------------------------------------------
    def check_debug_mode(self):
        while self.inDebug == True:
            if self.main_ui.DebugModeComboBox.isEnabled() == False:
                continue
            
            if self.main_ui.DebugModeComboBox.currentText() == 'Static':
                self.inDynamic = False
                self.main_ui.NetworkCardComboBox.setEnabled(True)
                self.main_ui.LocalMacComboBox.setEnabled(True)

                self.main_ui.DataPathLineEdit.setEnabled(False)
                self.main_ui.ResFileLineEdit.setEnabled(False)
                self.main_ui.toolButton_1.setEnabled(False)
                self.main_ui.toolButton_2.setEnabled(False)
                
            elif self.main_ui.DebugModeComboBox.currentText() == 'Dynamic':
                self.inDynamic = True
                self.main_ui.NetworkCardComboBox.setEnabled(False)
                self.main_ui.LocalMacComboBox.setEnabled(False)

                self.main_ui.DataPathLineEdit.setEnabled(True)
                self.main_ui.ResFileLineEdit.setEnabled(True)
                self.main_ui.toolButton_1.setEnabled(True)
                self.main_ui.toolButton_2.setEnabled(True)

                self.thread_executor.submit(self.check_input_path)

    def check_input_path(self):
        while self.inDynamic:
            if self.main_ui.DataPathLineEdit.text() == '' or self.main_ui.ResFileLineEdit.text() == '':
                self.main_ui.RunButton.setEnabled(False)
            else:
                self.main_ui.RunButton.setEnabled(True)
        self.main_ui.RunButton.setEnabled(True)

#-----------------------------------------------------------------
# debug functions
class StaticDebugSettingWidget(QWidget):
    def __init__(self):
        super(StaticDebugSettingWidget, self).__init__()

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(['Test Cases'])
        self.resize(600, 400)
        self.setWindowTitle("Select test cases")

        sections = self.get_debug_sections()

        # add checkboxes tree widget
        for section, cases in sections.items():
            parent_item = QTreeWidgetItem(self.tree_widget)
            parent_item.setText(0, section)
            parent_item.setFlags(parent_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for case_name in cases:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, case_name)
                child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                child_item.setCheckState(0, Qt.Unchecked)

        self.treelayout = QVBoxLayout()
        self.treelayout.addWidget(self.tree_widget)

        self.buttonlayout = QHBoxLayout()
        self.reset_button = QPushButton('Reset', self)
        self.confirm_button = QPushButton('OK', self)
        self.cancel_button = QPushButton('Cancel', self)

        font = QFont("Yu Gothic UI", 9)
        self.reset_button.setFont(font)
        self.confirm_button.setFont(font)
        self.cancel_button.setFont(font)

        self.reset_button.clicked.connect(self.reset)
        self.confirm_button.clicked.connect(self.confirm)
        self.cancel_button.clicked.connect(self.cancel)

        self.buttonlayout.addWidget(self.reset_button)
        self.buttonlayout.addWidget(self.confirm_button)
        self.buttonlayout.addWidget(self.cancel_button)

        self.mainlayout = QVBoxLayout()
        self.mainlayout.addLayout(self.treelayout)
        self.mainlayout.addLayout(self.buttonlayout)
        self.setLayout(self.mainlayout)

        # add icon
        icon = QIcon("./aceinna.ico")
        self.setWindowIcon(icon)

    def get_debug_sections(self):
        env = Test_Environment()
        env.setup_static_tests()

        sections = {}
        for section in env.test_sections:
            cases = []
            for case in section.test_cases:
                cases.append(case.test_case_name)
            sections[f'{section.section_name}'] = cases

        return sections

    def reset(self):
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.All)
        while iterator.value():
            item = iterator.value()
            item.setCheckState(0, Qt.CheckState.Unchecked)
            iterator += 1

    def confirm(self):
        sections = {}
        for i in range(self.tree_widget.topLevelItemCount()):
            top_level_item = self.tree_widget.topLevelItem(i)
            cases = []
            for j in range(top_level_item.childCount()):
                child_item = top_level_item.child(j)
                if child_item.checkState(0) == Qt.Checked:
                    cases.append(child_item.text(0))
            if len(cases) != 0:
                sections[top_level_item.text(0)] = cases
        self.sections = sections
        # print(self.sections)
        # self.close()
        self.open_static_test_dialog(True, self.sections)

    def open_static_test_dialog(self, debug, test_dict):
        self.staticD = StaticDialog(debug, test_dict)
        self.staticD.show()

    def cancel(self):
        self.close()
        
class DynamicDebugSettingWidget(QWidget):
    def __init__(self, data_path, result_file_path):
        super(DynamicDebugSettingWidget, self).__init__()

        self.data_path = data_path
        self.result_file_path = result_file_path
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(['Test Cases'])
        self.resize(600, 400)
        self.setWindowTitle("Select test cases")

        sections = self.get_debug_sections()

        # add checkboxes tree widget
        for section, cases in sections.items():
            parent_item = QTreeWidgetItem(self.tree_widget)
            parent_item.setText(0, section)
            parent_item.setFlags(parent_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for case_name in cases:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, case_name)
                child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                child_item.setCheckState(0, Qt.Unchecked)

        self.treelayout = QVBoxLayout()
        self.treelayout.addWidget(self.tree_widget)

        self.buttonlayout = QHBoxLayout()
        self.reset_button = QPushButton('Reset', self)
        self.confirm_button = QPushButton('OK', self)
        self.cancel_button = QPushButton('Cancel', self)

        font = QFont("Yu Gothic UI", 9)
        self.reset_button.setFont(font)
        self.confirm_button.setFont(font)
        self.cancel_button.setFont(font)

        self.reset_button.clicked.connect(self.reset)
        self.confirm_button.clicked.connect(self.confirm)
        self.cancel_button.clicked.connect(self.cancel)

        self.buttonlayout.addWidget(self.reset_button)
        self.buttonlayout.addWidget(self.confirm_button)
        self.buttonlayout.addWidget(self.cancel_button)

        self.mainlayout = QVBoxLayout()
        self.mainlayout.addLayout(self.treelayout)
        self.mainlayout.addLayout(self.buttonlayout)
        self.setLayout(self.mainlayout)

        # add icon
        icon = QIcon("./aceinna.ico")
        self.setWindowIcon(icon)

    def get_debug_sections(self):
        env = Test_Environment()
        env.setup_dynamic_tests(self.data_path)

        sections = {}
        for section in env.test_sections:
            cases = []
            for case in section.test_cases:
                cases.append(case.test_case_name)
            sections[f'{section.section_name}'] = cases
        return sections

    def reset(self):
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.All)
        while iterator.value():
            item = iterator.value()
            item.setCheckState(0, Qt.CheckState.Unchecked)
            iterator += 1

    def confirm(self):
        sections = {}
        for i in range(self.tree_widget.topLevelItemCount()):
            top_level_item = self.tree_widget.topLevelItem(i)
            cases = []
            for j in range(top_level_item.childCount()):
                child_item = top_level_item.child(j)
                if child_item.checkState(0) == Qt.Checked:
                    cases.append(child_item.text(0))
            if len(cases) != 0:
                sections[top_level_item.text(0)] = cases
        self.sections = sections
        # print(self.sections)
        self.open_dynamic_test_dialog(True, self.sections)

    def open_dynamic_test_dialog(self, debug, test_dict):
        self.dynamicD = DynamicDialog(self.data_path, self.result_file_path, debug, test_dict)
        self.dynamicD.show()

    def cancel(self):
        self.close()

#--------------------------------------------------------------------------------------------------------------------
# Attached classes
class SendProgressBarSignal(QThread):
    progressBarValue = Signal(int)
 
    def __init__(self):
        super(SendProgressBarSignal, self).__init__()
 
    def run(self):
        pb_val = 0
        while True:
            try:
                update_val = global_var.get_value("ProgressBarValue")
                if update_val > pb_val:
                    pb_val = update_val
                    self.progressBarValue.emit(pb_val)
            except Exception as e:
                print(e)
                break

class StaticTestStart(QThread):
    def __init__(self, textBrowser, debug=False, test_dict=None):
        super(StaticTestStart, self).__init__()
        self.textBrowser = textBrowser
        self.debug = debug
        self.test_dict = test_dict
    
    def run(self):
        self.setObjectName("StaticTest")
        self.ver = Verification()
        self.ver.static_test(text_browser=self.textBrowser, debug=self.debug, test_dict=self.test_dict)

    def stop(self):
        self.quit()
        self.wait()

class DynamicTestStart(QThread):
    def __init__(self, textBrowser, data_path, result_file_path, debug=False, test_dict=None):
        super(DynamicTestStart, self).__init__()
        self.textBrowser = textBrowser
        self.data_path = data_path
        self.result_file_path = result_file_path
        self.debug = debug
        self.test_dict = test_dict
    
    def run(self):
        self.setObjectName("DynamicTest")
        self.ver = Verification()
        self.ver.dynamic_test(self.textBrowser, self.data_path, self.result_file_path, self.debug, self.test_dict)

    def stop(self):
        self.quit()
        self.wait()