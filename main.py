import argparse
import os
import sys
import time

import pytesseract
from PIL import Image
from PyQt5.QtCore import QPoint, QRect, Qt, QByteArray
from PyQt5.QtGui import QMouseEvent, QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QFrame,
                             QLabel, QLineEdit, QMainWindow, QPushButton,
                             QRubberBand, QTextEdit, QVBoxLayout,
                             QWidget)

class Capture(QWidget):
    def __init__(self, main_window):
        super().__init__()
        
        self.main = main_window
        self.image_path = self.main.image_path # .text()
        self.tesseract_path = self.main.tesseract_path # .text()
        
        self.lang = 'eng'
        if self.main.lang_text.text() in ('vie', 'vi'):
            self.lang = 'vie'
            
        
        self.ensure_directory_exists(self.image_path)
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        self.main.hide()
        
        self.setMouseTracking(True)
        desk_size = QApplication.desktop()
        self.setGeometry(0, 0, desk_size.width(), desk_size.height())
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.15)

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

        QApplication.setOverrideCursor(Qt.CrossCursor)
        screen = QApplication.primaryScreen()
        rect = QApplication.desktop().rect()

        time.sleep(0.31)
        self.imgmap = screen.grabWindow(
            QApplication.desktop().winId(),
            rect.x(), rect.y(), rect.width(), rect.height()
        )

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.rubber_band.show() 

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        if not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.LeftButton:
            self.rubber_band.hide()
            
            rect = self.rubber_band.geometry()
            self.imgmap = self.imgmap.copy(rect)
            QApplication.restoreOverrideCursor()
            
            self.imgmap.save(self.image_path)
            
            text_ocr = self.perform_ocr(self.image_path)
            
            # set clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(text_ocr)

            self.main.ocr_text.setText(text_ocr)
            self.main.show()

            self.close()
            
    def perform_ocr(self, image_path):
        # Mở ảnh đã lưu
        image = Image.open(image_path)
        
        # Thực hiện OCR
        text = pytesseract.image_to_string(image, lang=self.lang)  # 'eng', 'vie'
        return text
        
    def ensure_directory_exists(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
class ScreenRegionSelector(QMainWindow):
    
    def __init__(self):
        super().__init__(None)
        self.m_width = 500
        self.m_height = 300
        
        self.setWindowTitle("OCR by vanquan223")
        self.setMinimumSize(self.m_width, self.m_height)

        frame = QFrame()
        frame.setContentsMargins(0, 0, 0, 0)
        lay = QVBoxLayout(frame)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(5, 5, 5, 5)
        
        image_base64 = b"iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAG2ElEQVR4nOybW1ATZxTHGVtn2pk+dvrSl74406e++GpnbPsqGEC8xSoitynV1qrcjOUiqIxSFURBRRiLYIIQdRRRQNAEKiSQwOYGSUhCgHBRTAXHh449/b6NuxBgc93dAM038x/Cly/fnPPbs+ecL5eICB+HVqv9Huk+0jQSsKUB1Qijnraa3kvv6FskEvunvtrJyUCGnmLTaZ8BtJhBUqeHBrFBLZFoPwuJ8xqNJokr530FEDIISqVyPTJyciUACAkEZOC3XDrvLwDeISADhSsNAK8QkIHxKxEAVqOEBwhMADQaLTQ1PYX6+kcBSyp9Av39AwED4AUCEwCx+CFkZ5cGrdLSW0EB4BwCE4CysjpWAOTkXAkaAKcQmAA0N3eASHQpaAA1NfdZAcAZBE9JUKHog7Y2OZIsIHV19QSVBHmBEOoq0O4nALJESvS9rJ0dQg1A1jHsNwBWIYQagFppQ84YQgeBCUBnZzecOVMZVALMz68gewlPALC6ZBa4c9t/ACSEeoNCIoGPWAdQXi5mpQzm5ZV7BYClfGGFx01GuNcwCNIGg8+622D4t+3JUCrrAKqrG1kBUFR0wycAwYjoN19nHYBK1Y8gSKGk5FbAqqgQk6VwVQLgKwmGAYQBhAGEAYQBhArA1LEtG+xnkp+N5wlhIjMKJtK3cKK3MTGcaXbnNphJ3eecTYj6zi/nJ9MjBci4t1w5zRcASnOxMeDcLzjlm/NHo75Bhr3jw3m+AFAQXh8QCLwCQEZJ+XKeTwBYfwujxzw6D8kb1/N59fkGgKMA4jd/wgjg5eEtX/LpPN8AsJyJgo2MAByZgq8CdcTx+w5SAQOIjQVncgpSKrzdto05jOMTwHkgidbczl1+AZhJiN7EGgD72TQwNt0GXb+Krus6dR8YH9bB6Lk0n/YYP3sBdPJ+VLNtC+q3DfQdSpjMPelmvL20ctlaP9jUCdPHjvMHwJG5FcyNlZ6bHI0GTA3XybXL7pEVTYLy1sjYqmpp44332pnX9tlgIr+IBwAZkWB8UDt/xQfUYLp/E6xVp0nhx3iOet704Bb5msUAh1rvLegEbWBofQHDtVIwNzSBXq4G4kNEDDXLlgAwtCrBUXCW1EhZFRAvhsh5TY8J3vy4l1sA1mv5tHODHY9gPFe4NKxR9zj4rJleZ7ua6/b8cM35+Uj5SwvOlNQlhr48kg7W6jp4s3ffEgDGu0/d1k5niOhI8BYFwQFALbG+p4s0XN8tB4cojvk2ObGdXEOuRa+hosBxPJbMEyRAeSvM7hb6nMCYAMzu2k0DGCu+zB0Ae/HB+at6Lc9rrlgYLfYPSXHkcvb8XMkxvzI4DQD9XTg/dq6MBjCZnccdANuNQtr48Zzd3jM8uhWo9dbKAnLOUlviyh0aAkXU1oAAaOV4PzFYqiQw9EBGO69vUcBcXBx3ACx/FtMOTWQJvJc5tIZaj1+L58x3rroAqJTufYAfAJaT7jkBr386xG0VwGFPOTRWsN8rALxmcSK01PxBl8lxEXPD4ysATZcBRs9XuCVLzgAsdMhSe9ErACrcFwKzFx9yuy0CAaBHZVArc5VQotdCVgFf9wi6DFLlDXd/o6cTGdeNnk6iO0RcLunqkBEFhm6Za4/ebnj162+Mxo5dvALTWaIlAIyNbTCT9gtouo2uKFCY4dVB5n1YBTCKryBBuBzoU6BGJMu90UGPcabHz1HJzr6oLbaVZdJRQPRZYOx8mXtZ2xdPNkauDs9KlrnFAPD/0+kiMgLIxNipg9eJKdwDIMsb6vjwPUw5geu96ZEYnQvEqOZ3urXD1srCZfcYrit1e09Q02sGnUxNNkYDKuv8e3pofi5u+7IAsByF5+arALo1ZoV7uAdA1XN9bw/jWUCPwhtfaY8gr5+kW97lpOkZhJmf5zP7kLTNBaChxc2phYeksaKL/AAg72fU1eErbGyuB4O8jRR+jJObIzvGpz3eJByAYTE6F6ATIaE0AqEwgv65CkauVtNXntKkKB8Mj7th6viiZgcdpUeu3CRPhc6kpW01ZwDYkD9VgA15BDBxNPqLtQ7gZXLs14wAIDd3HTJqes0CiIt5DxER6xgBkFGQEVmyVgE49whUHp3HY/xI5OfIMNtaAzC3PfqfqfjYDV4B4IE/FkPGEWsFwNzOmHfOFMEPPjlPDcjd/DE6/pbbKnLAfuEwZ3ImCDnTq7REcBSc0Hr8LMDT+F9/OhwGEAYQBhDyH02xIc3A8KVgAGxa7QC0hDnwr8qG+oeTQUtte9/ebgmsBFJDp9MlrlYAxIC5MijnqYEMLVxtAAi1WcaK89QgCGIzMvgu0tRKBUCgkCfUlnFCbTroq1//AQAA///EETkNAAAABklEQVQDABcU2rGnMqFrAAAAAElFTkSuQmCC"

        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray.fromBase64(image_base64))
        self.setWindowIcon(QIcon(pixmap))

        self.ocr_title = QLabel("Text:")
        self.ocr_text = QTextEdit()  # QTextEdit to allow text input
        self.ocr_text.setPlaceholderText("The ocr text content displayed here has been saved to the clipboard.")
        self.ocr_text.setStyleSheet("background-color: white;")
        
        self.image_path = r'Screenshots\screenshot.png'
        self.tesseract_path = r'Tesseract-OCR\tesseract'
        
        self.lang_title = QLabel("Language:")
        self.lang_text = QLineEdit()
        self.lang_text.setPlaceholderText(r"Default is eng, enter vi or vie to ocr Vietnamese.")
        
        self.btn_capture = QPushButton("Capture (Ctrl+Shift+C)")
        self.btn_capture.clicked.connect(self.capture)
        self.btn_capture.setShortcut('Ctrl+Shift+C')

        lay.addWidget(self.btn_capture)
        lay.addWidget(self.lang_title)
        lay.addWidget(self.lang_text)
        
        lay.addWidget(self.ocr_title)
        lay.addWidget(self.ocr_text)

        self.setCentralWidget(frame)

    def capture(self):
        self.capturer = Capture(self)
        self.capturer.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR by vanquan223")
    
    app = QApplication(sys.argv)    
    app.setStyleSheet("""
    QFrame {
        background-color: rgb(245, 246, 247);
    }
                      
    QPushButton {
        border-radius: 5px;
        background-color: rgb(60, 90, 255);
        padding: 10px;
        color: white;
        font-weight: bold;
        font-family: Arial;
        font-size: 12px;
    }
                      
    QPushButton::hover {
        background-color: rgb(60, 20, 255)
    }
    """)
    selector = ScreenRegionSelector()
    selector.show()
    app.exit(app.exec_())
    