import multiprocessing
from multiprocessing import Process

from bot import execute as bot_execute
from services.open_cv_service import execute as motion_detection_execute


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    queue = manager.Queue()

    motion_detection_process = Process(target=motion_detection_execute, args=(queue,))
    bot_process = Process(target=bot_execute, args=(queue,))

    motion_detection_process.start()
    bot_process.start()

    motion_detection_process.join()
    bot_process.join()
