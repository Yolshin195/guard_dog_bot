import asyncio
import logging
import sys
import io
from multiprocessing import Queue
from pathlib import Path

import cv2
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile, FSInputFile

from middleware.auth_middleware import AuthMiddleware
from settings import BOT_TOKEN, BOT_CHAT_ID

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

# Добавление middleware
dp.message.middleware(AuthMiddleware())

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("check"))
async def send_photo(message: types.Message):
    cap = cv2.VideoCapture(0)  # Инициализация камеры
    ret, frame = cap.read()    # Захват изображения
    cap.release()              # Освобождение камеры

    if ret:
        # Конвертация изображения в формат, подходящий для отправки
        is_success, buffer = cv2.imencode(".jpg", frame)
        if is_success:
            bio = io.BytesIO(buffer)  # Создание объекта BytesIO из буфера
            bio.name = 'image.jpeg'
            photo_file = BufferedInputFile(bio.getvalue(), filename=bio.name)  # Создание объекта InputFile
            await message.reply_photo(photo=photo_file)  # Отправка фото
        else:
            await message.reply("Ошибка при кодировании изображения.")
    else:
        await message.reply("Не удалось захватить изображение.")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def send_message(bot: Bot, queue: Queue):
    logger.info(f"{send_message.__name__}: start")
    while True:
        logger.info(f"send_message: {queue=}")
        try:
            video_path = Path(queue.get_nowait())
            logger.info(f"{send_message.__name__}: get new video {video_path=}")
            try:
                input_file = FSInputFile(video_path, filename=video_path.name)
                await bot.send_video(chat_id=BOT_CHAT_ID, video=input_file, supports_streaming=True)
                logger.info(f"{send_message.__name__}: success!!!")
            except FileNotFoundError:
                logger.exception(f"{send_message.__name__}: Файл {video_path} не найден.")
            except Exception as e:
                logger.exception(f"{send_message.__name__}: Произошла ошибка: {e}")
        except Exception as e:
            logger.exception(f"{send_message.__name__}: Очередь пуста, ожидание новых элементов... {e=}")
            await asyncio.sleep(5)  # небольшая пауза перед следующей попыткой
            continue


async def main(queue: Queue) -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    send_message_task = asyncio.create_task(send_message(bot, queue))

    await dp.start_polling(bot)
    await send_message_task


def execute(queue: Queue):
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main(queue))

