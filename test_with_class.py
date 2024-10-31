import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QPolygonF


class VideoWindow(QMainWindow):
    def __init__(self, urlorpath, fps=30):
        super().__init__()
        self.setWindowTitle("PyQt Video Stream with Controls")
        # Используем встроенные методы Qt для управления размером окна
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

        self.fps = fps
        self.paused = False

        self.image_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.cap = cv2.VideoCapture(urlorpath)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Обратите внимание на использование функции `int()` для округления времени интервала
        self.timer.start(int(1000 / self.fps))

        # Показать окно максимизированным
        self.showMaximized()

    def update_frame(self):
        if not self.paused:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                q_img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(q_img))

    def toggle_play_pause(self):
        if self.paused:
            self.play_button.setText('Pause')
            self.paused = False
        else:
            self.play_button.setText('Play')
            self.paused = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


def main(urlorpath, fps=30):
    app = QApplication(sys.argv)
    window = VideoWindow(urlorpath, fps)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main('/home/user/PycharmProjects/rubbish/output22.mp4', 25)  # Пример использования: путь к видео или камере, FPS = 25