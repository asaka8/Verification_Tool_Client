import sys
import time
import module.global_var as global_var

from PySide2.QtWidgets import QDialog, QMainWindow, QMessageBox, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QThread, Signal

from src.conmunicator.INS401_Ethernet import Ethernet_Dev
from src.Ethernet_test.INS401_Verification import Verification
from src.test_framwork.Jsonf_Creater import Setting_Json_Creat

from module.myThread import MyThread as thread
from module.myUiLoader import myUiLoader as UiLoader

 
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
    def __init__(self):
        super(StaticDialog, self).__init__()
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

    # --------------------------------------------------------------------------------------------
    # Static test function
    def start_test(self):
        # ver = Verification()
        self.static_ui.progressBar.show()
        
        # self.static_test_thread = thread(target=ver.static_test, name='StaticThread', args=(self.static_ui.textBrowser, ))
        self.static_test_thread = StaticTestStart(self.static_ui.textBrowser)
        self.check_thread = thread(target=self.thread_check, name='CheckThread')
        self.static_test_thread.start()
        self.check_thread.start()
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
    def __init__(self, data_path, result_file_path):
        super(DynamicDialog, self).__init__()
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

    def start_test(self):
        # ver = Verification()
        self.dynamic_ui.progressBar.show()
        
        # self.static_test_thread = thread(target=ver.static_test, name='StaticThread', args=(self.static_ui.textBrowser, ))
        self.dynamic_test_thread = DynamicTestStart(self.dynamic_ui.textBrowser, self.data_path, self.result_file_path)
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

class DebugDialog(QDialog):
    def __init__(self):
        super().__init__()
        # debug dialog initialization
        debug_qfile = QFile('ui/debug_test_dialog.ui')
        debug_qfile.open(QFile.ReadOnly)
        debug_qfile.close()
        
        self.debug_ui = QUiLoader().load(debug_qfile, self)

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
        self.main_ui.DebugRdoButton.setEnabled(False)
        self.assign_network_card()

        # test mode parameter initialization
        self.static_test_act = False
        self.dynamic_test_act = False
        self.debug_test_act = False

        # Enviroment initialization
        global_var._init()
        self.network_card_list = []

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

            self.main_ui.NetworkCardComboBox.setEnabled(False)
            self.main_ui.LocalMacComboBox.setEnabled(False)

            self.main_ui.DataPathLineEdit.setEnabled(True)
            self.main_ui.ResFileLineEdit.setEnabled(True)
            self.main_ui.toolButton_1.setEnabled(True)
            self.main_ui.toolButton_2.setEnabled(True)

        elif mode_val == 'Debug Test':
            self.debug_test_act = True
            self.static_test_act = False
            self.dynamic_test_act = False

    def handle_mode_chosed(self):
        if self.static_test_act == True:
            self.open_static_test_dialog()
            self.static_test_act = False
        if self.dynamic_test_act == True:
            self.open_dynamic_test_dialog()
            self.dynamic_test_act = False
        if self.debug_test_act == True:
            self.open_debug_test_dialog()
            self.debug_test_act = False

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

    def open_debug_test_dialog(self):
        self.debugD = DebugDialog()
        self.debugD.debug_ui.show()


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
    def __init__(self, textBrowser):
        super(StaticTestStart, self).__init__()
        self.textBrowser = textBrowser
    
    def run(self):
        self.setObjectName("StaticTest")
        self.ver = Verification()
        self.ver.static_test(text_browser=self.textBrowser)

    def stop(self):
        self.quit()
        self.wait()

class DynamicTestStart(QThread):
    def __init__(self, textBrowser, data_path, result_file_path):
        super(DynamicTestStart, self).__init__()
        self.textBrowser = textBrowser
        self.data_path = data_path
        self.result_file_path = result_file_path
    
    def run(self):
        self.setObjectName("DynamicTest")
        self.ver = Verification()
        self.ver.dynamic_test(self.textBrowser, self.data_path, self.result_file_path)

    def stop(self):
        self.quit()
        self.wait()