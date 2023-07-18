import time
import struct
import datetime
import threading
import collections
from scapy.all import AsyncSniffer, sendp, sniff, conf

from module.mytimer import Timer, send_data_timer
import module.global_var as global_var



PING_TYPE     = [0x01, 0xcc]
COMMAND_START = [0x55, 0x55]

class Ethernet_Dev:
    def __init__(self):
        super().__init__()
        '''
        Parameters of Class:
            src_mac: pc mac address
            dst_mac: INS401/402 mac address (default: 'FF:FF:FF:FF:FF:FF')
            ifac: network interface
            ifac_confirmed: check the status of iface (default: False)

            serial_number: serial number (use in device connection) (default:None)
            model_string: model string (use in device connection) (default:None)
            app_version: application version (use in device connection) (default:None)

            receice_cache: bidirectional queue for collecting data (default: [->{len:1000}->])
            async_sniffer: the async thread to catch packets from ETH (default:None)
            tlock: thread lock to make sure the safe of catch data thread
        '''
        self.type = '100base-t1'
        self.src_mac = global_var.get_value('src mac')
        self.dst_mac = 'FF:FF:FF:FF:FF:FF'
        self.iface = global_var.get_value('iface')
        self.iface_confirmed = False
        
        self.serial_number = None
        self.model_string = None
        self.app_version = None

        self.receive_cache = collections.deque(maxlen=10000)
        self.async_sniffer = None
        self.tlock = threading.Lock()

    #-------------------------------------------------------------------------------------------------------------------------------------------------------
    # Interface initialization and connection
    def reset_dev_info(self):
        self.app_version = None
        self.dst_mac = 'FF:FF:FF:FF:FF:FF'
        self.iface_confirmed = False

    def find_device(self):
        filter_exp = 'ether dst host ' + \
            self.src_mac + ' and ether[16:2] == 0x01cc'
        src_mac = bytes([int(x, 16) for x in self.src_mac.split(':')])
        command_line = self.build_packet(
            self.get_dst_mac(), src_mac, PING_TYPE)
        self.async_sniffer = AsyncSniffer(
            iface=self.iface, prn=self.handle_receive_packet, filter=filter_exp)
        global_var.set_value('AsyncSnifferEnable', True)
        self.async_sniffer.start()
        time.sleep(0.1)
        sendp(command_line, self.iface, verbose=0)
        Timer('AsyncSnifferEnable', 1)
        self.async_sniffer.stop()

        if self.iface_confirmed:            
            # print('Successful connection')
            return True
        else:
            return False

    def find_device_(self):
        '''
        Dsec:
            debug function cooperate to test.py
        '''
        result = False
        self.iface_confirmed = False 

        iface_list = self.get_network_card()
        lens = len(iface_list)
        for i in range(lens):
            self.confirm_iface(iface_list[i])
            if self.iface_confirmed:
                print(f'[NetworkCard]{self.iface}')
                result = True
                break
            else:
                if i == len(iface_list) - 1:
                    result = False
                    error_print('No available Ethernet card was found.')
                    break
        return result

    def confirm_iface(self, iface):
        '''
        Parameters:
            iface: network card name (type: string; example: '以太网')
        '''
        filter_exp = 'ether dst host ' + \
            iface[1] + ' and ether[16:2] == 0x01cc'
        src_mac = bytes([int(x, 16) for x in iface[1].split(':')])
        command_line = self.build_packet(
            self.get_dst_mac(), src_mac, PING_TYPE)
        async_sniffer = AsyncSniffer(
            iface=iface[0], prn=self.handle_receive_packet, filter=filter_exp)
        async_sniffer.start()
        time.sleep(0.01)
        sendp(command_line, iface=iface[0], verbose=0, count=2)
        time.sleep(0.5)
        async_sniffer.stop()

        if self.iface_confirmed:
            self.iface = iface[0]
            self.src_mac = iface[1]
    
    def comfire_network_card(self):
        self.device = None
        self.iface_confirmed = False
        # find network connection
        ifaces_list = self.get_network_card()
        return ifaces_list

    def ping_device(self):
        command_line = self.build_packet(
        self.get_dst_mac(), self.get_src_mac(), PING_TYPE)
        data_buffer = []
        cmd_type = struct.unpack('>H', bytes(PING_TYPE))[0]
        read_line = self.write_read(command_line, cmd_type, 1)
        if read_line:
            packet_raw = read_line[14:]
            packet_type = packet_raw[2:4]
            if packet_type == bytes(PING_TYPE):
                packet_length = struct.unpack('<I', packet_raw[4:8])[0]
                data_buffer = packet_raw[8: 8 + packet_length]
                info_text = self.format_string(data_buffer)
                if info_text.find('INS401') > -1:
                    # print(info_text)
                    split_text = info_text.split(' ')
                    self.model_string = split_text[0]
                    self.serial_number = int(split_text[2])
                    self.app_version = split_text[9]
                    return True
                elif info_text.find('INS402') > -1:
                    split_text = info_text.split(' ')
                    self.model_string = split_text[0]
                    self.serial_number = int(split_text[2])
                    self.app_version = split_text[9]
                    return True
        return False

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Interface information interaction
    def start_listen_data(self, filter_type=None, log2pcap=False):
        '''
        Desc:
            generate a async thread to listen data from ethernet
        Parameters:
            filter_type: use to filte the target data (type: {int, list}; example: 0x0a03)
            log2pcap: choose log mode (type: bool; example: True)
        '''
        hard_code_mac = '04:00:00:00:00:04'
        if filter_type == None:
            filter_exp = f'ether src host {self.dst_mac} and ether[16:2] == 0x010a or ether[16:2] == 0x020a or ether[16:2] ==  0x030a or ether[16:2] == 0x050a'
        elif isinstance(filter_type, int):
            filter_exp = f'ether src host {self.dst_mac} or {hard_code_mac}  and ether[16:2] == {filter_type}'
        elif isinstance(filter_type, list):
            filter_exp = f'ether src host {self.dst_mac} or {hard_code_mac}  and ether[16:2] == {filter_type[0]}'
            for i in range(len(filter_type)-1):
                target_filter_type = filter_type[i+1]
                if isinstance(target_filter_type, int):
                    filter_exp += f' || ether[16:2] == {target_filter_type}'
                if isinstance(target_filter_type, str):
                    target_filter_type = '0x' + target_filter_type.encode().hex()[2:]
                    filter_exp += f' || ether[16:4] == {target_filter_type}'
        if log2pcap == False:
            self.async_sniffer = AsyncSniffer(
                iface=self.iface, prn=self.handle_catch_packet, filter=filter_exp, store=0)
        elif log2pcap == True:
            self.async_sniffer = AsyncSniffer(
                iface=self.iface, prn=self.handle_catch_whole_eth_packet, filter=filter_exp, store=0)
        self.async_sniffer.start()
        time.sleep(0.1)

    def stop_listen_data(self):
        if self.async_sniffer is None:
            return
        if self.async_sniffer.running == True:
            self.async_sniffer.stop()
        else:
            return
    
    def read_data(self):
        if len(self.receive_cache) > 0:
            data = self.receive_cache.popleft()
            # self.async_sniffer.stop()
            return data
        return

    def send_message(self,  command, message=[]):
        '''
        Desc:
            just send command, no response
        Parameters:
            command: command type (type: bytes; example: b'\x01\x0c')
            message: command payload (type: list; example: [0x00, 0x00])
        '''
        command_line = self.build_packet(self.get_dst_mac(), self.get_src_mac(), command, message)
        self.write(command_line)
        
    def write_read(self, data, filter_cmd_type=None, timeout=0.5): 
        '''
        Desc:
            send user command and read the response of it. (return data buffer)
        Parameters:
            data: command buffer (type: bytes; example: b'\x55\x55\x03\x0c\x00\x00\x00\x00')
            filter_cmd_type: the command type of response (type: int; example: 460) # [0x01, 0xcc]
        '''
        if not self.src_mac:
            return None
    
        if filter_cmd_type:
            filter_exp = 'ether dst host ' + self.src_mac + \
                ' and ether[16:2] == %d' % filter_cmd_type
        else:
            filter_exp = 'ether dst host ' + self.src_mac

        self.read_result = None
        self.async_sniffer = AsyncSniffer(
            iface=self.iface, prn=self.handle_receive_read_result, filter=filter_exp, store=0)

        self.async_sniffer.start()
        time.sleep(0.1)
        sendp(data, iface=self.iface, verbose=0)
        time.sleep(timeout)
        self.async_sniffer.stop()
        if self.read_result is not None:
            return self.read_result
        return None

    def write_read_response(self, command, message=[], timeout = 1): 
        '''
        Desc:
            send user command and read the response of it. (return [Packet_type, Payload_length, payload])
        Parameters:
            command: the type of command (type: bytes; example: b'\x03\x0a')
            message: the payload of the command (type: list; example: [0x01, 0x02, 0x03])
        '''
        packet_type = []
        packet_length = 0
        packet_length_list = []
        data_buffer = []
        
        command_line = self.build_packet(self.get_dst_mac(), self.get_src_mac(), command, message)
        cmd_type = struct.unpack('>H', command)[0]         
        read_line = self.write_read(command_line, cmd_type, timeout)

        if read_line:
            packet_raw = read_line[14:]
            packet_type = packet_raw[2:4]
            if packet_type == command:
                packet_length_list = packet_raw[4:8]
                packet_length = struct.unpack('<I', packet_raw[4:8])[0]
                packet_crc = list(packet_raw[packet_length+8:packet_length+10])
                if packet_crc == self.calc_crc(packet_raw[2:8+packet_length]): 
                    data_buffer = packet_raw[8:8+packet_length]
                else:
                    print('crc error')
                    pass
        return packet_type, packet_length_list, data_buffer
        
    def reset_buffer(self):
        self.receive_cache = collections.deque(maxlen=100000)

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------\
    # other methods (Components for embedding)
    def get_src_mac(self):
        if self.src_mac:        
            return bytes([int(x, 16) for x in self.src_mac.split(':')])
        return None

    def get_dst_mac(self):
        if self.dst_mac:
            return bytes([int(x, 16) for x in self.dst_mac.split(':')])
        return None

    def get_network_card(self):
        network_card_info = []
        for item in conf.ifaces:
            if conf.ifaces[item].ip == '127.0.0.1' or conf.ifaces[item].mac == '':
                continue
            network_card_info.append(
                (conf.ifaces[item].name, conf.ifaces[item].mac))
        return network_card_info

    def build_packet(self, dest, src, message_type, message_bytes=[]):
        '''
        Desc:
            Combine data into packet and calculate CRC, data should have packet_type + payload_len + payload
        Parameters:
            dest: destination address (type: bytes; example: b'\x01\x02\x03\x04\x05\x06')
            src: source address (type: bytes; example: b'\x01\x02\x03\x04\x05\x06')
            message_type: the type of message ()
        '''
        header = [0x55, 0x55]
        packet = []
        if not dest or not src:
            return None
        packet.extend(message_type)
        msg_len = len(message_bytes)
        packet_len = struct.pack("<I", msg_len)
        packet.extend(packet_len)
        final_packet = packet + message_bytes
        msg_len = len(COMMAND_START) + len(final_packet) + 2
        payload_len = struct.pack('<H', len(COMMAND_START) + len(final_packet) + 2)
        whole_packet=[]
        header = dest + src + bytes(payload_len)
        whole_packet.extend(header)
        whole_packet.extend(COMMAND_START)
        whole_packet.extend(final_packet)
        whole_packet.extend(self.calc_crc(final_packet))
        if msg_len < 46:
            fill_bytes = bytes(46-msg_len)
            whole_packet.extend(fill_bytes)
        return bytes(whole_packet)
   
    def format_string(self, data_buffer):
        parsed = bytearray(data_buffer) if data_buffer and len(
            data_buffer) > 0 else None
        formatted = ''
        if parsed is not None:
            try:
                formatted = str(struct.pack(
                    '{0}B'.format(len(parsed)), *parsed), 'utf-8')
            except UnicodeDecodeError:
                formatted = ''
        return formatted

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # callback functions
    def handle_receive_packet(self, packet):
        self.iface_confirmed = True
        self.dst_mac = packet.src
    
    def handle_catch_packet(self, packet):
        self.tlock.acquire()
        try:
            packet_raw = bytes(packet)[12:]
            self.receive_cache.append(packet_raw[2:])
        finally:
            self.tlock.release()

    def handle_catch_whole_eth_packet(self, packet):
        self.receive_cache.append(packet)
    
    def handle_receive_read_result(self, packet):
        self.read_result = bytes(packet)

    # calculate CRC
    def calc_crc(self, payload):
        '''
        Calculates 16-bit CRC-CCITT
        '''
        crc = 0x1D0F
        for bytedata in payload:
            crc = crc ^ (bytedata << 8)
            i = 0
            while i < 8:
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
                i += 1

        crc = crc & 0xffff
        crc_msb = (crc & 0xFF00) >> 8
        crc_lsb = (crc & 0x00FF)
        return [crc_msb, crc_lsb]