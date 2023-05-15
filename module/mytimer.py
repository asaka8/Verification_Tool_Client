import time 
import module.global_var as global_var

def Timer(key, timeout):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if global_var.get_value(key) == False:
            break

def read_data_timer(key, func, timeout):
    start_time = time.time()
    while time.time() - start_time < timeout:
        func()
        if global_var.get_value(key) == False:
            break

def send_data_timer(key, func, timeout):
    func()
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(0.001)
        if global_var.get_value(key) == False:
            break