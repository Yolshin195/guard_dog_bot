from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("GDB_BOT_TOKEN")
BOT_USER_ID = int(getenv("GDB_BOT_USER_ID"))
BOT_CHAT_ID = int(getenv("GDB_BOT_CHAT_ID"))

STATIC_DIR = getenv("GDB_STATIC_DIR", default="static/")
VIDEO_RECORDING_TIME = int(getenv("GDB_VIDEO_RECORDING_TIME", default="10"))
