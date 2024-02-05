import os
import time
import platform
import warnings

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtGui import QImage, QPixmap
from ctypes import *
from PIL import Image

class IMAGE_PROCESS(QThread, QObject):
    frame_signal1 = pyqtSignal(QPixmap)
    state_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.working = True
        self.auto_check = True
        self.Thermal_mode = False
        self.m_nXres = 640
        self.m_nYres = 480
        self.data_mode = 8
        self.run = False
        self.IF_mode = "YUV"
        self.UVC_CH = 0
        self.Mat_list = dict()
        self.Video_Save_flag = False
        self.Video_Stop_flag = False
        self.SNAP_Save_flag = False
        self.Video_save_file_path = ''
        self.Snap_save_file_path = ''
        self.Video_save_file_folder = ''
        self.Snap_save_file_folder = ''
        self.video_file_name = ''
        self.snap_file_name = ''
        self.recordingInfo = ''
        self.FPS = 0
        self.simul_stop = False
        self.OSD_TEC = False
        self.OSD_TARGET = False
        self.OSD_TEC_START = [0, 0]
        self.OSD_TEC_END   = [0, 0]
        self.OSD_TARGET_START = [0, 0]
        self.OSD_TARGET_END = [0, 0]
        self.DEAD_PIX = [0,0]
        self.DEAD_DETECT=False
        self.TARGET_ROI_MEAN = 0
        self.TEC_ROI_MEAN = 0
        self.img_label_width = 640
        self.img_label_height = 480
        # TEMP_VALUE BUFFER
        self.TEMP_LIST = []
        self.CEM_TYPE = '1'
        self.GET_TYPE = 'AVG'
        self.GET_BIT = '16 Bit'        

        # IMG_PROC_VIEWER       
        self.COLOR_ON = False
        self.COLOR_Type = "COLOR1"
        self.R_L_REVERSE = False

        self.SNAP_BIT = '8 Bit'
        self.channel = 1
        
        self.TRSMGuideOn=False

    def FLIP_ON_OFF(self, img):
        if self.R_L_REVERSE :
            img = cv2.flip(img, 1)
        else:
            img = img
        return img

    def run(self):
        if self.simul_mode == False:
            self.uvc_cap = cv2.VideoCapture(int(self.UVC_CH), cv2.CAP_DSHOW)
            self.uvc_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', '1', '6', ' '))

            if self.IF_mode == "Y-16":
                self.uvc_cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        else:
            self.uvc_cap = cv2.VideoCapture(self.Video_read_file_path)
            self.FPS = int(self.uvc_cap.get(5))

        prev_time = 0

        if self.uvc_cap.isOpened():
            self.state_signal.emit(self.IF_mode + " : CONNECT!")
            self.working = True
        else:
            self.state_signal.emit(self.IF_mode + " FAIL!")
            self.working = False

        while self.working:
            if self.IF_mode == "Y-16":
                ret, frame = self.uvc_cap.read()
                if ret:
                    current_time = time.time()
                    self.FPS = 1. / (current_time - prev_time)
                    self.m_nYres, self.m_nXres = frame.shape[0], frame.shape[1]
                    frame = self.FLIP_ON_OFF(frame)
                    image = np.zeros((self.m_nYres, self.m_nXres))
                            
                    if self.GET_BIT == '8 Bit':                        
                        frame = frame & 0x00FF;                        
                    elif self.GET_BIT == '10 Bit':                        
                        frame = frame & 0x03FF;                        
                    elif self.GET_BIT == '12 Bit':                        
                        frame = frame & 0x0FFF;                                                                        
                    elif self.GET_BIT == '14 Bit':
                        frame = frame & 0x3FFF

                    frame_test = frame.copy()

                    if len(frame_test.shape) == 3 and frame_test.shape[2] == 3 and frame_test.dtype == 'uint8':
                        print(frame_test.dtype)
                        self.state_signal.emit("Check it by YUV mode")
                        break

                    if len(frame_test.shape) == 3 and frame_test.shape[2] == 3:
                        frame_test = cv2.cvtColor(frame_test, cv2.COLOR_BGR2GRAY)
                        image = cv2.split(frame_test)[0]
                    else:
                        image = cv2.normalize(frame_test, image, 0, 255, cv2.NORM_MINMAX)
                        image = image.astype("uint8")

                    image = self.COLOR_MAP_APPLY(image)
                    if len(image.shape) == 3 and image.shape[2] == 3:
                        self.channel = 3
                    else:
                        self.channel = 1

                    if self.OSD_TEC or self.OSD_TARGET:
                        image = self.OSD_DRAW(image)
                        try:
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore", category=RuntimeWarning)
                                if self.GET_TYPE == 'AVG':
                                    self.TARGET_ROI_MEAN = frame[self.OSD_TARGET_START[1]:self.OSD_TARGET_END[1],
                                                           self.OSD_TARGET_START[0]:self.OSD_TARGET_END[0]].mean()
                                if self.GET_TYPE == 'MAX':
                                    self.TARGET_ROI_MEAN = np.max(frame[self.OSD_TARGET_START[1]:self.OSD_TARGET_END[1],
                                                           self.OSD_TARGET_START[0]:self.OSD_TARGET_END[0]])
                                if self.GET_TYPE == 'MIN':
                                    self.TARGET_ROI_MEAN = np.min(frame[self.OSD_TARGET_START[1]:self.OSD_TARGET_END[1],
                                                           self.OSD_TARGET_START[0]:self.OSD_TARGET_END[0]])
                        except:
                            self.TARGET_ROI_MEAN = 0
                            self.TEC_ROI_MEAN = 0

                    if self.Video_Save_flag:
                        try:
                            if self.video_out:
                                self.video_out.write(image)
                                now = time.localtime(current_time)
                                self.recordingInfo = "Recording Time : " + str(now.tm_hour) + ":" + str(
                                    now.tm_min) + ":" + str(now.tm_sec)
                        except:
                            pass

                    if self.Video_Stop_flag:
                        self.video_out.release()
                        self.state_signal.emit("Video Save Complete!")
                        self.Video_Stop_flag = False
                        
                    if self.SNAP_Save_flag:
                        try:
                            if self.SNAP_BIT == '8 Bit' :
                                cv2.imwrite(self.Snap_save_file_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                                self.state_signal.emit("Snap_IMG 8Bit Save Complete!")
                            else :
                                cv2.imwrite(self.Snap_save_file_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                                self.state_signal.emit("Snap_IMG 16Bit Save Complete!")
                            self.SNAP_Save_flag = False
                        except:
                            pass

                    if len(image.shape) == 3 and image.shape[2] == 3:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    qt_img1 = self.convert_cv_qt(image)
                    self.frame_signal1.emit(qt_img1)

                    prev_time = current_time
                else:
                    self.uvc_cap.release()
                    self.IF_mode = ''
                    print(self.working)
                    break

            elif self.IF_mode == "YUV":
                ret, frame = self.uvc_cap.read()
                if ret:
                    current_time = time.time()
                    self.FPS = int(1 / (current_time - prev_time))
                    self.m_nXres, self.m_nYres = frame.shape[1], frame.shape[0]
                    frame = self.FLIP_ON_OFF(frame)
                    frame = self.COLOR_MAP_APPLY(frame)

                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    if self.OSD_TEC or self.OSD_TARGET:
                        image = self.OSD_DRAW(image)

                    qt_img1 = self.convert_cv_qt(image)
                    self.frame_signal1.emit(qt_img1)

                    if self.Video_Save_flag:
                        if self.video_out:
                            self.video_out.write(frame)
                            now = time.localtime(current_time)
                            self.recordingInfo = "Recording Time : " + str(now.tm_hour) + ":" + str(
                                now.tm_min) + ":" + str(now.tm_sec)

                    if self.Video_Stop_flag:
                        self.video_out.release()
                        self.state_signal.emit("Video Save Complete!")
                        self.Video_Stop_flag = False

                    if self.SNAP_Save_flag:
                        try:
                            cv2.imwrite(self.Snap_save_file_path, frame)
                            self.state_signal.emit("Snap_IMG Save Complete!")
                            self.SNAP_Save_flag = False
                        except:
                            pass
                    prev_time = current_time
                else:
                    self.uvc_cap.release()
                    self.IF_mode = ''
                    break

        self.uvc_cap.release()
        cv2.destroyAllWindows()
        self.IF_mode = ''

    def stop(self):
        self.working = False
        print("Image Process END!")

    def COLOR_MAP_APPLY(self, img):
        if self.COLOR_ON:
            if self.COLOR_Type == 'AUTUMN':
                img = cv2.applyColorMap(img, cv2.COLORMAP_AUTUMN)
            elif self.COLOR_Type == 'BONE':
                img = cv2.applyColorMap(img, cv2.COLORMAP_BONE)
            elif self.COLOR_Type == 'JET':
                img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
            elif self.COLOR_Type == 'WINTER':
                img = cv2.applyColorMap(img, cv2.COLORMAP_WINTER)
            elif self.COLOR_Type == 'RAINBOW':
                img = cv2.applyColorMap(img, cv2.COLORMAP_RAINBOW)
            elif self.COLOR_Type == 'OCEAN':
                img = cv2.applyColorMap(img, cv2.COLORMAP_OCEAN)
            elif self.COLOR_Type == 'SUMMER':
                img = cv2.applyColorMap(img, cv2.COLORMAP_SUMMER)
            elif self.COLOR_Type == 'SPRING':
                img = cv2.applyColorMap(img, cv2.COLORMAP_SPRING)
            elif self.COLOR_Type == 'COOL':
                img = cv2.applyColorMap(img, cv2.COLORMAP_COOL)
            elif self.COLOR_Type == 'HSV':
                img = cv2.applyColorMap(img, cv2.COLORMAP_HSV)
            elif self.COLOR_Type == 'PINK':
                img = cv2.applyColorMap(img, cv2.COLORMAP_PINK)
            elif self.COLOR_Type == 'HOT':
                img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)
            elif self.COLOR_Type == 'PARULA':
                img = cv2.applyColorMap(img, cv2.COLORMAP_PARULA)
            else:
                pass
        return img

    def OSD_DRAW(self, img):
        try:
            img_RGB = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            if self.OSD_TEC:
                cv2.rectangle(img_RGB, tuple(self.OSD_TEC_START), tuple(self.OSD_TEC_END), (255, 0, 0), 1)
            if self.OSD_TARGET:
                cv2.rectangle(img_RGB, tuple(self.OSD_TARGET_START), tuple(self.OSD_TARGET_END), (0, 0, 255), 1)
        except:
            img_RGB = img
            if self.OSD_TEC:
                cv2.rectangle(img_RGB, tuple(self.OSD_TEC_START), tuple(self.OSD_TEC_END), (255, 0, 0), 1)
            if self.OSD_TARGET:
                cv2.rectangle(img_RGB, tuple(self.OSD_TARGET_START), tuple(self.OSD_TARGET_END), (0, 0, 255), 1)
        return img_RGB

    def VIDEO_SAVE_INIT(self):
        w = round(self.m_nXres)
        h = round(self.m_nYres)
        fps = int(self.FPS)
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        delay = round(1000 / fps)
        if self.IF_mode == "YUV":
            self.video_out = cv2.VideoWriter(self.Video_save_file_path, fourcc, fps, (w, h))
        else:
            if self.channel == 3:
                self.video_out = cv2.VideoWriter(self.Video_save_file_path, fourcc, fps, (w, h))
            else :
                self.video_out = cv2.VideoWriter(self.Video_save_file_path, fourcc, fps, (w, h), isColor=False)

        if not self.video_out.isOpened():
            print('File open failed!')
            self.Video_Save_flag = False
            self.video_out.release()

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        # 컬러 이미지일 경우
        if cv_img.shape[-1] == 3:
            image = cv_img.copy()
            h, w, ch = image.shape
            bytes_per_line = w * ch
            convert_to_Qt_format = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(self.img_label_width, self.img_label_height, Qt.KeepAspectRatio)

        # GRAYSCALE 경우
        else:
            image = cv_img.copy()
            h, w = image.shape
            bytes_per_line = w
            convert_to_Qt_format = QImage(image.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
            p = convert_to_Qt_format.scaled(self.img_label_width, self.img_label_height, Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)