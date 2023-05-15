import os
import time
import struct
import base64

from socket import *
from ..test_framwork.Jsonf_Creater import Setting_Json_Creat
from .print_center import pass_print, error_print

class NtripClient:
    def __init__(self, callback):

        self.is_connected = 0
        self.tcp_client_socket = None
        self.is_close = False
        self.append_header_string= None
        self.callback = callback
        
        ntrip_account = Setting_Json_Creat().creat()["ntrip account"]

        self.ip = ntrip_account["ip"]
        self.port = int(ntrip_account["port"])
        self.mountPoint = ntrip_account["mountPoint"]
        self.username = ntrip_account["username"]
        self.password = ntrip_account["password"]

    def run(self, wait_time):
        # pass_print("NTRIP run..")
        while True:
            if self.is_close:
                if self.tcp_client_socket:
                    self.tcp_client_socket.close()
                self.is_connected = 0
                return

            while True:
                time.sleep(3)
                self.is_connected = self.doConnect()
                if self.is_connected == 0:
                    time.sleep(3)
                else:
                    break
            recvData = self.recvResponse()

            if recvData != None and recvData.find(b'ICY 200 OK') != -1:
                # pass_print('NTRIP:[request] ok')
                self.recv(wait_time)
            else:
                # error_print('NTRIP:[request] fail')
                self.tcp_client_socket.close()

    def stop(self):
        self.tcp_client_socket.close()

    def set_connect_headers(self, headers:dict):
        self.append_header_string = ''
        for key in headers.keys():
            self.append_header_string += '{0}: {1}\r\n'.format(key, headers[key])

    def clear_connect_headers(self):
        self.append_header_string = None

    def doConnect(self):
        self.is_connected = 0
        self.tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        # pass_print('NTRIP:[connect] {0}:{1} start...'.format(self.ip, self.port))
        self.tcp_client_socket.connect((self.ip, self.port))
        # pass_print('NTRIP:[connect] ok')
        self.is_connected = 1

        if self.is_connected == 1:
            # send ntrip request
            ntripRequestStr = 'GET /' + self.mountPoint + ' HTTP/1.1\r\n'
            ntripRequestStr += 'User-Agent: NTRIP PythonDriver/0.1\r\n'

            if self.append_header_string:
                ntripRequestStr += self.append_header_string

            ntripRequestStr += 'Authorization: Basic '
            apikey = self.username + ':' + self.password
            apikeyBytes = apikey.encode("utf-8")
            ntripRequestStr += base64.b64encode(apikeyBytes).decode("utf-8")+'\r\n'
            ntripRequestStr += '\r\n'
            self.send(ntripRequestStr)
        return self.is_connected

    def send(self, data):
        if self.is_connected:
            if isinstance(data, str):
                self.tcp_client_socket.send(data.encode('utf-8'))
            else:
                self.tcp_client_socket.send(bytes(data))

    def recv(self, wait_time):
        self.tcp_client_socket.settimeout(10)
        if wait_time == 0:
            while True:
                if self.is_close:
                    return
                data = self.tcp_client_socket.recv(1024)
                if data:
                    self.callback(data)
                else:
                    self.tcp_client_socket.close()
                    return
        else:
            cur_time = time.time()
            while time.time() - cur_time <= wait_time:
                if self.is_close:
                    return
                data = self.tcp_client_socket.recv(1024)
                if data:
                    self.callback(data)
                else:
                    self.tcp_client_socket.close()
                    return
            self.close()
            return

    def recvResponse(self):
        self.tcp_client_socket.settimeout(3)
        while True:
            data = self.tcp_client_socket.recv(1024)
            if not data or len(data) == 0:
                return None
            return data

    def close(self):
        self.append_header_string = None
        self.is_close = True

class RuNtrip:
    def __init__(self, eth):
        path = os.getcwd()
        self.local_time = time.localtime()
        self.formatted_file_time = time.strftime("%Y_%m_%d_%H_%M_%S", self.local_time)
        self.ether = eth
        # ntrip init
        self.ntrip = NtripClient(self.ntrip_receive_callback)
        self.ntrip_rtcm_logf = None 

    '''
    ntrip
    '''
    def ntrip_client_thread(self, wait_time=0):
        data_dir = './data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        ntrip_data_dir = './data/ntrip_data'
        if not os.path.exists(ntrip_data_dir):
            os.makedirs(ntrip_data_dir)
        self.ntrip_rtcm_logf = open(f'./data/ntrip_data/ntrip_rtcm_{self.formatted_file_time}.bin', "ab")
        self.ntrip.run(wait_time)

    def stop_thread(self):
        self.ntrip.close()

    def ntrip_receive_callback(self, data):
        if data is not None:
            base_rtcm_packet = self.ether.build_packet(
                self.ether.get_dst_mac(), 
                self.ether.get_src_mac(),
                b'\x02\x0b', list(data))
            # self.ether.ping_device()
            self.ether.write(base_rtcm_packet)

            if self.ntrip_rtcm_logf is not None:
                self.ntrip_rtcm_logf.write(bytes(data))

    def calc_crc(self, payload):
        crc = 0x1D0F
        for bytedata in payload:
            crc = crc^(bytedata << 8) 
            for i in range(0,8):
                if crc & 0x8000:
                    crc = (crc << 1)^0x1021
                else:
                    crc = crc << 1

        crc = crc & 0xffff
        crc_msb = (crc & 0xFF00) >> 8
        crc_lsb = (crc & 0x00FF)
        return [crc_msb, crc_lsb]