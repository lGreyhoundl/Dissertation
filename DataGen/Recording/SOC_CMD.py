import time

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog
import os

#os.system('Pyrcc5 SOC_Dialog.qrc -o SOC_Dialog_rc.py')
dialog_class = uic.loadUiType("SOC_COMMAND.ui")[0]
class SOC_COMMAND_DIALOG(QDialog, dialog_class, QObject):
    SOC_REF_MOVE_CMD = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_widget()
        self.Guide_ON = False

    def closeEvent(self, event):
        self.close()

    def init_widget(self):
        # SOC REF MOVE CMD
        self.PBtn_RefUP.setAutoRepeat(True)
        self.PBtn_RefUP.setAutoRepeatDelay(100)
        self.PBtn_RefUP.setAutoRepeatInterval(100)
        self.PBtn_RefRIGHT.setAutoRepeat(True)
        self.PBtn_RefRIGHT.setAutoRepeatDelay(100)
        self.PBtn_RefRIGHT.setAutoRepeatInterval(100)
        self.PBtn_RefLEFT.setAutoRepeat(True)
        self.PBtn_RefLEFT.setAutoRepeatDelay(100)
        self.PBtn_RefLEFT.setAutoRepeatInterval(100)
        self.PBtn_RefDOWN.setAutoRepeat(True)
        self.PBtn_RefDOWN.setAutoRepeatDelay(100)
        self.PBtn_RefDOWN.setAutoRepeatInterval(100)
        self.PBtn_RefUP.clicked.connect(lambda : self.SOC_REF_MOVE_SEND("TRSM_REF_GUIDE_UP"))
        self.PBtn_RefRIGHT.clicked.connect(lambda: self.SOC_REF_MOVE_SEND("TRSM_REF_GUIDE_RIGHT"))
        self.PBtn_RefLEFT.clicked.connect(lambda: self.SOC_REF_MOVE_SEND("TRSM_REF_GUIDE_LEFT"))
        self.PBtn_RefDOWN.clicked.connect(lambda: self.SOC_REF_MOVE_SEND("TRSM_REF_GUIDE_DOWN"))
        self.PBtn_GuideOnOff.clicked.connect(self.REF_GUIDE_ON_OFF)
        self.PBtn_GuideSave.clicked.connect(lambda: self.SOC_REF_MOVE_SEND("TRSM_REF_GUIDE_SAVE"))
        #self.PB_APPLY.clicked.connect(lambda: self.SOC_REF_MOVE_SEND("TRSM_REF_APPLY"))

    def SOC_REF_MOVE_SEND(self, CMD):
        self.SOC_REF_MOVE_CMD.emit(CMD)


    def REF_GUIDE_ON_OFF(self):
        if self.Guide_ON :
            self.SOC_REF_MOVE_SEND("TRSM_REF_GUIDE_OFF")
            self.Guide_ON = False
            self.PBtn_GuideOnOff.setStyleSheet(
                "QPushButton{border-image :url(:/BTN/resource/QuantumRED_MAIN/GUIDE_ON.png);}"
                "QPushButton:hover{border-image :url(:/BTN/resource/QuantumRED_MAIN/GUIDE_ON_HOVER.png);}"
                "QPushButton:pressed{border-image :url(:/BTN/resource/QuantumRED_MAIN/GUIDE_ON_PRESSED.png);}")
        else:
            self.SOC_REF_MOVE_SEND("TRSM_REF_GUIDE_ON")
            self.Guide_ON = True
            self.PBtn_GuideOnOff.setStyleSheet(
                "QPushButton{border-image :url(:/BTN/resource/QuantumRED_MAIN/GUIDE_OFF.png);}"
                "QPushButton:hover{border-image :url(:/BTN/resource/QuantumRED_MAIN/GUIDE_OFF_HOVER.png);}"
                "QPushButton:pressed{border-image :url(:/BTN/resource/QuantumRED_MAIN/GUIDE_OFF_PRESSED.png);}")