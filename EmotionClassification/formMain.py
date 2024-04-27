import sys
import time
import pyrealsense2 as rs
import numpy as np
import cv2
import time
import math
import os
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg
from EmotionClassification.UI.MainForm import Ui_MainForm

from PySide6.QtCore import QTimer,QPoint,QDateTime
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader



from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
pyqtSignal = Signal
pyqtSlot = Slot


class Map(QWidget):
    def __init__(self,image,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.image = QImage(image)

        #self.setFixedSize(600, 600)


        self.setFixedSize(self.image.width(),self.image.height())

        #self.amr_location = QPoint(self.width()//2, self.height()//2)
        # self.amr_location = QPoint(0, 0)
        # self.point_start_loc = QPoint(0, 0)
        #self.point_start_loc = QPoint(self.width() // 2, self.height() // 2)

        #self.status = False

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = event.rect()
        painter.drawImage(rect, self.image, rect)  # Added Background map
        painter.setRenderHint(QPainter.Antialiasing)

    def getMapSize(self):
        return self.size()

    def getParentSize(self):
        return self.parent().size()

    def getMapImageSize(self):
        return self.image.size()


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        pipe = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipe.start(config)

        self.isRunning = True

        while self.isRunning:
            frame = pipe.wait_for_frames()
            color_frame = frame.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())
            color_frame_cv = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            h, w, ch =color_frame_cv.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(color_frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)


    def stop(self):
        self.isRunning = False
        self.quit()
        self.terminate()


class MainForm(qtw.QWidget, Ui_MainForm):

    @pyqtSlot(QImage)
    def setImage(self, image):
        # update image
        self.lb_Map.setPixmap(QPixmap.fromImage(image))
        self.lb_Map.setAlignment(Qt.AlignCenter)


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        img_path = "Images/map.png"
        self.padding = 10

        """
        self.th=Thread(self)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()
        self.show()
        
        """


        self.map = Map(img_path, parent=self.lb_Map)
        #print(self.map.getMapSize())


#import signal #close signal with Ctrl+C
#signal.signal(signal.SIGINT, signal.SIG_DFL)



if __name__ == "__main__":

    app = qtw.QApplication(sys.argv)

    window = MainForm()
    window.show()

    sys.exit(app.exec())

