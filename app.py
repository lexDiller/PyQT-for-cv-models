import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QPolygonF
from ultralytics import YOLO
import easyocr

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QFileDialog)

class OcrQt(QMainWindow):
    def __init__(self, urlorpath, language, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("PyQt Video Stream & ROI Selector")
        self.setGeometry(0, 0, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.resize(800, 600)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        self.cap = cv2.VideoCapture(urlorpath)
        # Получаем FPS из видеопотока
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.timer_interval = int(1000 / fps) if fps > 0 else 40  # Корректировка интервала таймера на основе FPS

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(self.timer_interval)  # Использование скорректированного интервала


        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.points = []
        self.current_roi = None
        self.is_painting = False

        self.reader = easyocr.Reader([language], gpu=True)

        self.paused = False

    def update_frame(self):
        ret, self.frame = self.cap.read()
        self.frame = cv2.resize(self.frame, (1920, 1080))
        if ret:
            self.display_image()
            if self.current_roi and self.is_painting:
                self.perform_ocr()

    def toggle_play_pause(self):
        if self.paused:
            self.timer.start(self.timer_interval)  # Возобновление таймера
            self.play_button.setText('Pause')
            self.paused = False
        else:
            self.timer.stop()  # Остановка таймера
            self.play_button.setText('Play')
            self.paused = True
    def display_image(self):
        qformat = QImage.Format_Indexed8
        if len(self.frame.shape) == 3:
            if self.frame.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        out_image = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], qformat)
        out_image = out_image.rgbSwapped()
        painter = QPainter(out_image)

        # Рисование и соединение точек
        if self.points:
            pen = QPen(QColor(255, 0, 0), 8)  # Цвет и размер пера для точек
            painter.setPen(pen)
            for point in self.points:
                painter.drawPoint(QPoint(point[0], point[1]))

            if len(self.points) > 1:
                pen = QPen(QColor(255, 0, 0), 2)  # Цвет и размер пера для линий
                painter.setPen(pen)
                polygon = QPolygonF([QPoint(x, y) for x, y in self.points])
                painter.drawPolyline(polygon)

            if len(self.points) > 2:
                painter.drawLine(QPoint(self.points[-1][0], self.points[-1][1]),
                                 QPoint(self.points[0][0], self.points[0][1]))

        painter.end()
        self.image_label.setPixmap(QPixmap.fromImage(out_image))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.points.append((event.x(), event.y()))
            self.update_frame()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.points = []
            self.current_roi = None
            self.is_painting = False
            self.update_frame()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.points:
                self.current_roi = self.calculate_bounding_box(self.points)
                self.is_painting = True
        elif event.key() == Qt.Key_Q:
            self.close()
            self.main_window.show()
    def calculate_bounding_box(self, points):
        min_x = min(points, key=lambda x: x[0])[0]
        max_x = max(points, key=lambda x: x[0])[0]
        min_y = min(points, key=lambda x: x[1])[1]
        max_y = max(points, key=lambda x: x[1])[1]
        return [min_x, min_y, max_x, max_y]

    def perform_ocr(self):
        x_start, y_start, x_end, y_end = self.current_roi
        roi = self.frame[y_start:y_end, x_start:x_end]
        if roi.size > 0:
            results = self.reader.readtext(roi)
            for result in results:
                print("Detected text:", result[1])

    def close_and_show_main(self):
        self.close()
        self.main_window.show()


def EasyocrQT(urlorpath, language):
    app = QApplication(sys.argv)
    main_window = OcrQt(urlorpath, language)
    main_window.show()
    sys.exit(app.exec_())

class YoloQt(QMainWindow):
    def __init__(self, main_window, urlorpath, path_to_model, conf=0.6, imgsz=320, verbose=False):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("PyQt Video Stream & YOLO Detection")
        self.setGeometry(0, 0, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.resize(800, 600)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)


        self.cap = cv2.VideoCapture(urlorpath)  # Источник видео
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.timer_interval = int(1000 / fps) if fps > 0 else 40  # Корректировка интервала таймера на основе FPS

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(self.timer_interval)  # Использование скорректированного интервала

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_button)

        self.paused = False

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.points = []
        self.current_roi = None
        self.is_painting = False

        # Загрузка модели YOLO
        self.model = YOLO(path_to_model)
        self.verbose = verbose
        self.conf = conf
        self.imgsz = imgsz


    def update_frame(self):
        ret, self.frame = self.cap.read()
        if ret:
            self.display_image()
            if self.current_roi and self.is_painting:
                self.perform_detection()

    def toggle_play_pause(self):
        if self.paused:
            self.timer.start(self.timer_interval)  # Возобновление таймера
            self.play_button.setText('Pause')
            self.paused = False
        else:
            self.timer.stop()  # Остановка таймера
            self.play_button.setText('Play')
            self.paused = True
    def display_image(self):
        qformat = QImage.Format_Indexed8
        if len(self.frame.shape) == 3:
            if self.frame.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        out_image = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], qformat)
        out_image = out_image.rgbSwapped()
        painter = QPainter(out_image)

        # Рисование каждой точки
        if self.points:
            # Цвет и размер пера для точек
            pen = QPen(QColor(255, 0, 0), 8)  # Красный цвет, толщина 8
            painter.setPen(pen)
            for point in self.points:
                painter.drawPoint(QPoint(point[0], point[1]))

            # Соединение точек линиями
            if len(self.points) > 1:
                # Цвет и размер пера для линий
                pen = QPen(QColor(255, 0, 0), 2)  # Красный цвет, толщина 2
                painter.setPen(pen)
                polygon = QPolygonF([QPoint(x, y) for x, y in self.points])
                painter.drawPolyline(polygon)

            if len(self.points) > 2:
                painter.drawLine(QPoint(self.points[-1][0], self.points[-1][1]),
                                 QPoint(self.points[0][0], self.points[0][1]))

        painter.end()
        self.image_label.setPixmap(QPixmap.fromImage(out_image))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.points.append((event.x(), event.y()))
            self.update_frame()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.points = []
            self.current_roi = None
            self.is_painting = False
            self.update_frame()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.points:
                self.current_roi = self.calculate_bounding_box(self.points)
                self.is_painting = True
        elif event.key() == Qt.Key_Q:
            self.close()
            self.main_window.show()

    def calculate_bounding_box(self, points):
        min_x = min(points, key=lambda x: x[0])[0]
        max_x = max(points, key=lambda x: x[0])[0]
        min_y = min(points, key=lambda x: x[1])[1]
        max_y = max(points, key=lambda x: x[1])[1]
        return [min_x, min_y, max_x, max_y]

    def perform_detection(self):
        x_start, y_start, x_end, y_end = self.current_roi
        roi = self.frame[y_start:y_end, x_start:x_end]
        if roi.size > 0:
            results = self.model(roi, conf=self.conf, imgsz=self.imgsz, verbose=self.verbose)

    def close_and_show_main(self):
        self.close()
        self.main_window.show()

def YOLOwithQT(urlorpath, path_to_model, conf=0.6, imgsz=320, verbose=False):
    app = QApplication(sys.argv)
    main_window = YoloQt(urlorpath, path_to_model, conf, imgsz, verbose)
    main_window.show()
    sys.exit(app.exec_())


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Video Stream Selector")  # Название окна
        self.setGeometry(100, 100, 800, 200)  # Размеры и позиция окна

        # Создаем виджет и макет для конфигурации элементов интерфейса
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)  # Важно привязать макет к центральному виджету

        # Кнопка для выбора видео или URL
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Введите путь до видео или URL")
        layout.addWidget(self.url_input)

        self.browse_button = QPushButton("Выбрать видео", self)
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)

        # Выбор модели
        self.easyocr_button = QPushButton("Использовать EasyOCR", self)
        self.easyocr_button.clicked.connect(lambda: self.set_model("easyocr"))
        layout.addWidget(self.easyocr_button)

        self.yolo_button = QPushButton("Использовать YOLO", self)
        self.yolo_button.clicked.connect(lambda: self.set_model("yolo"))
        layout.addWidget(self.yolo_button)

        # Кнопка воспроизведения
        self.play_button = QPushButton("Воспроизвести", self)
        self.play_button.clicked.connect(self.play_video)
        layout.addWidget(self.play_button)

        # Кнопка выхода
        self.exit_button = QPushButton("Выход", self)
        self.exit_button.clicked.connect(self.close_application)
        layout.addWidget(self.exit_button)

        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет с макетом

        self.current_model = None  # Текущая модель для обработки видео
        self.video_path = None    # Путь к видеопотоку или файлу

    def browse_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/')
        if fname[0]:
            self.url_input.setText(fname[0])

    def set_model(self, model_name):
        self.current_model = model_name
        print(f"Модель {model_name} выбрана")

    def play_video(self):
        if not self.url_input.text() or not self.current_model:
            print("Необходимо выбрать видео и модель")
            return

        self.video_path = self.url_input.text()

        if self.current_model == "easyocr":
            self.ocr_window = OcrQt(self.video_path, "ru", self)  # Передаем self как ссылку на главное окно
            self.ocr_window.show()
        elif self.current_model == "yolo":
            self.yolo_window = YoloQt(self, self.video_path, "/home/user/PycharmProjects/lee_rubbish/yolov8s.pt", 0.6, 320, True)  # Передаем self как ссылку на главное окно
            self.yolo_window.show()

        self.hide()  # Скроем главное окно при открытии другого окна

    def close_application(self):
        self.close()



def main():
    app = QApplication(sys.argv)
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
