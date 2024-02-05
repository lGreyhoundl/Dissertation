import device 
# from pymf import get_MF_devices

from PyQt5.QtCore import QThread, pyqtSignal

#=======================================================================================================================
# USB Camera List GET CLASS
#=======================================================================================================================
class DEVICE_USBCAM_LIST(QThread):
    USBCAM_DEVICE_LIST = pyqtSignal(list)
    def __init__(self):
        QThread.__init__(self)
        self.device_init_flag = True
        self.device_list = []
        self.sleep_time = 2
        self.working=True

    def __del__(self):
        self.quit()
        self.wait()
        self.device_init_flag=False

    def run(self):
        while self.working:
            if self.exit == True: break
            # temp_device_list = device.getDeviceList()
            # temp_device_list = get_MF_devices()
            temp_device_list = ['COM-4']
            self.device_list = self.Classify_Duplicate_USB_LIST(temp_device_list)
            #print(self.device_list)
            self.USBCAM_DEVICE_LIST.emit(self.device_list)
            self.sleep(self.sleep_time)

    # 같은이름의 USB Camera List distinction
    def Classify_Duplicate_USB_LIST(self, device_list):
        list_duplicate_element = set([x for x in device_list if device_list.count(x) > 1])
        new_device_list = []
        if len(list_duplicate_element) >= 1:
            for num, data in enumerate(device_list):
                if data == list(list_duplicate_element)[0]:new_device_list.append(str(data) + str(num))
                else:new_device_list.append(data)
        else:
            new_device_list = device_list
        return new_device_list

    def stop(self):
        self.working = False
        self.quit()
        print("GET_DEVICE END!")
        self.wait(3000)  # 5000ms = 5s
