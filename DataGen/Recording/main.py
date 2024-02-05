import sys
import cv2
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import QTimer, Qt, pyqtSlot, QByteArray, QMutex
from PyQt5.QtGui import QImage, QPixmap
from datetime import datetime
import threading
import serial
import serial.tools.list_ports as sp

import SOC_ICD
from IMG_PROCESS import *
from SOC_CMD import *
from USBCAM_LIST_GET import *


ConnectionAbortedError
form_class = uic.loadUiType("QuantumRED_MAIN_TEMP.ui")[0]
__platform__ = sys.platform

class SerialReadThread(QThread):
    # 사용자 정의 시그널 선언
    # 받은 데이터 그대로를 전달 해주기 위해 QByteArray 형태로 전달
    received_data = pyqtSignal(QByteArray, name="receivedData")

    def __init__(self, serial):
        QThread.__init__(self)
        self.mutex = QMutex()
        self.serial = serial
        self.working = True

    def __del__(self):
        self.wait()

    def setSerial(self, serial):
        self.serial = serial
        self.working = True

    def run(self):
        while self.working:
            try:
                num = self.serial.inWaiting()            
            except:
                break
            self.mutex.lock()
            buf = self.serial.read(num)
            if buf:                                
                self.received_data.emit(buf)
            self.usleep(1)
            self.mutex.unlock()

    def stop(self):
        self.working = False
        self.serial.close()            
        self.quit()
        print("Serial Thread END!")
        self.wait(2000)


class CameraApp(QMainWindow, form_class, QObject):
    BAUDRATES = (
        QSerialPort.Baud1200,
        QSerialPort.Baud2400,
        QSerialPort.Baud4800,
        QSerialPort.Baud9600,
        QSerialPort.Baud19200,
        QSerialPort.Baud38400,
        QSerialPort.Baud57600,
        QSerialPort.Baud115200,
    )

    DATABITS = (
        QSerialPort.Data5,
        QSerialPort.Data6,
        QSerialPort.Data7,
        QSerialPort.Data8,
    )

    FLOWCONTROL = (
        QSerialPort.NoFlowControl,
        QSerialPort.HardwareControl,
        QSerialPort.SoftwareControl,
    )

    PARITY = (
        QSerialPort.NoParity,
        QSerialPort.EvenParity,
        QSerialPort.OddParity,
        QSerialPort.SpaceParity,
        QSerialPort.MarkParity,
    )

    STOPBITS = (
        QSerialPort.OneStop,
        QSerialPort.OneAndHalfStop,
        QSerialPort.TwoStop,
    )

    shutterTimer = pyqtSignal(str)
    sent_data = pyqtSignal(str, name="sentData")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera App with Qt5")
        self.setGeometry(100, 100, 1280, 720)
        self.image_label = QLabel(self)
        self.image_label.resize(1280, 720)
        self.capture = None
        self.timer = QTimer(self)  # 타이머 설정
        self.timer.timeout.connect(self.update_frame)  # 타이머 시그널
        self.is_recording = False
        self.video_writer = None

        self.recording_label = QLabel("● Recording", self)
        self.recording_label.setStyleSheet("color: red; font-weight: bold;")
        self.recording_label.setGeometry(10, 10, 100, 20)  # 위치와 크기 조정
        self.recording_label.hide()  # 초기 상태에서는 숨김

        self.bSerial = False
        self.serial = 0
        self.first_RX_flag = False
        self.line_data = []
        self.serialReadThread = SerialReadThread(self.serial)
        self.serialReadThread.received_data.connect(lambda buf: self.read_data(buf))
        self.shutterTimer.connect(lambda: self.SOC_CMD_SEND("1-REF_NUC"))

        self.IMG_PROCESS = IMAGE_PROCESS()
        self.DEVICE_GET = DEVICE_USBCAM_LIST()

        self.IMG_PROCESS.frame_signal1.connect(lambda img: self.FRAME_RAW_DISPLAY(img))
        self.IMG_PROCESS.state_signal.connect(self.UVC_state_control)
        self.DEVICE_GET.USBCAM_DEVICE_LIST.connect(self.GET_USB_DEVICE_LIST)
        self.TABLE_MAT = dict()

        self.SERIAL_CONNECTED = False

    @pyqtSlot(list)
    def GET_USB_DEVICE_LIST(self, device_list):
        self.device_list = device_list
        if self.prev_device_list == device_list:
            pass
        else:
            self.IMG_PROCESS.device_list = self.device_list
            self.comBox_CamSelect.clear()
            self.comBox_CamSelect.insertItems(0, self.device_list)
            # for idx in range(len(self.device_list)):
                # self.comBox_CamSelect.setItemIcon(idx, QIcon(":/ICON/resource/ICON/004-camera.png"))
            self.prev_device_list = self.device_list

    def _get_available_port(self):
        available_port = list()
        ports = list(sp.comports())
        for element in ports:
            available_port.append(element.device)
        return available_port

    def UVC_state_control(self, msg):
        self.textBrowser.append(msg)

    def Timer_start(self):
        self.shutterTimer.emit('1-REF_NUC')
        period = self.spinBox_NUCPeriod.value()
        self.timer = threading.Timer(period, self.Timer_start)
        self.timer.start()


    def start_camera(self):
        self.capture = cv2.VideoCapture(0)  # 카메라 디바이스 열기
        self.timer.start(30)  # 프레임 업데이트 간격 설정

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            # 영상 녹화
            if self.is_recording:
                self.video_writer.write(frame)
                
            # 영상을 QLabel에 표시
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if len(frame.shape) == 3 else frame
            h, w = frame.shape[:2]
            bytes_per_line = 3 * w if len(frame.shape) == 3 else w
            format = QImage.Format_RGB888 if len(frame.shape) == 3 else QImage.Format_Grayscale8
            convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, format)
            p = convert_to_Qt_format.scaled(1280, 720, Qt.IgnoreAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(p))

    def read_data(self, rd):
        try:            
            for c in rd:
                if c == b'\n':
                    self.first_RX_flag = True
                else:
                    if self.first_RX_flag:
                        temp = ord(c)
                        self.line_data.append(chr(temp))
                        try:
                            if c == b'\r':
                                data = "".join(self.line_data)
                                #self.textBrowser.insertPlainText(data)
                                self.first_RX_flag = False
                                del self.line_data[:]
                        except:
                            pass
        except:
            pass

    def SOC_CMD_SEND(self, CMD):
        print(CMD)
        if self.bSerial:
            STX = b'\x02'
            ETX = b'\x03'
            data_dummy = b'\x00\x00\x00\x00\x00\x00\x00'
                                                          
            # if  self.RADIO_SURV.isChecked():
            self.ICD = SOC_ICD.SOC_SURV_ICD()
            # else:
                # self.ICD = SOC_ICD.SOC_EOST_ICD()
            
            try:
                ICD = self.ICD.SEND_ICD[CMD]
                cmd_data = STX.__add__(ICD['CONSOLE_SOURCE']).__add__(ICD['CONSOLE_DESTINATION']).__add__(
                ICD['CONSOLE_HEADER']).__add__(ICD['data']).__add__(data_dummy).__add__(ETX)

                CRC = 0
                cmd_data_array = bytearray(cmd_data)
                for index in range(1, 12):
                    CRC = CRC^cmd_data_array[index]
                cmd_data_array[12] = CRC
                cmd_data = bytes(cmd_data_array)
                self.SOC_SERIAL_SEND(cmd_data)
                print(cmd_data)
                # self.textBrowser.append(CMD)
                return cmd_data
            except:
                pass
        else:
            pass
            # QMessageBox.information(self, "MSG", "serial port is not connect!")

    def connect_serial(self, name):
        if ~self.bSerial:
            try:
                self.serial = serial.Serial(name, QSerialPort.Baud115200, timeout=0)
                self.serialReadThread.setSerial(self.serial)
                self.serialReadThread.start()
                print("serial connected")
            except:
                print("error")
    
    def disconnect_serial(self):
        if self.bSerial:
            self.serialReadThread.stop()    

    def keyPressEvent(self, event):
        if event.key() == ord('R') or event.key() == ord('r'):
            if self.is_recording:
                self.is_recording = False
                self.video_writer.release()
                self.recording_label.hide()  # 녹화 중지 시 라벨 숨김
            else:
                self.is_recording = True
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.avi")  # 파일 이름 설정
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                self.video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (640, 480))
                self.recording_label.show()  # 녹화 시작 시 라벨 표시

        if event.key() == ord('S') or event.key() == ord('s'):
            if self.SERIAL_CONNECTED == False:
                self.connect_serial(self._get_available_port()[1])
                time.sleep(0.1)
                if self.serial.isOpen():
                    self.bSerial = True
                    self.SERIAL_CONNECTED = True
                    print("Serial Connect Success!")
                    print(self.SOC_CMD_SEND("1-REF_NUC"))
            else:
                # self.SOC_CMD_SEND("1-REF_NUC")
                print(self.SOC_CMD_SEND("1-REF_NUC"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = CameraApp()
    main_window.show()
    main_window.start_camera()
    sys.exit(app.exec_())
