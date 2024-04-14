from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
BOT_USER_ID = int(getenv("BOT_USER_ID"))
BOT_CHAT_ID = int(getenv("BOT_CHAT_ID"))

STATIC_DIR = getenv("STATIC_DIR", default="static/")
VIDEO_RECORDING_TIME = 10
