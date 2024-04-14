import datetime
import os
import uuid
from asyncio import Queue

import cv2

from settings import STATIC_DIR, VIDEO_RECORDING_TIME
import logging

logger = logging.getLogger(__name__)


def motion_detection() -> bool:
    no_movement_detected = True
    # Захват видеопотока с первой веб-камеры системы
    cap = cv2.VideoCapture(0)

    # Чтение первого кадра и его преобразование в оттенки серого
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    while no_movement_detected:
        # Чтение каждого следующего кадра
        ret, frame = cap.read()
        gray_new = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_new = cv2.GaussianBlur(gray_new, (21, 21), 0)

        # Вычисление разницы между текущим и предыдущим кадром
        delta = cv2.absdiff(gray, gray_new)
        threshold = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.dilate(threshold, None, iterations=2)

        # Нахождение контуров движения
        contours, _ = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            no_movement_detected = False

        # Отображение результата
        cv2.imshow("Frame", frame)
        cv2.imshow("Threshold", threshold)

        key = cv2.waitKey(1)
        if key == 27:
            break

        # Обновление предыдущего кадра
        gray = gray_new

    # Освобождение камеры и закрытие всех окон
    cap.release()
    cv2.destroyAllWindows()

    return True


def record_video(filename, duration):
    # Открытие камеры
    cap = cv2.VideoCapture(0)

    # Параметры видео: ширина, высота, количество кадров в секунду (FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30

    # Создание объекта VideoWriter для записи видео в формате MP4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    # Начало записи видео
    start_time = cv2.getTickCount()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Запись кадра в видео
        out.write(frame)

        # Прекращение записи, если прошло достаточно времени
        if cv2.getTickCount() - start_time >= duration * cv2.getTickFrequency():
            break

    # Освобождение ресурсов
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def build_file_name() -> str:
    current_date = datetime.datetime.now()
    path = f"{STATIC_DIR}/{current_date.year}_{current_date.month}_{current_date.day}"
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{uuid.uuid4()}.mp4")


def main(queue: Queue):
    while True:
        if motion_detection():
            file_name = build_file_name()
            record_video(file_name, VIDEO_RECORDING_TIME)
            queue.put_nowait(file_name)
            logger.info(f"{main.__name__}: Main {queue=}")


def execute(queue: Queue):
    main(queue)

