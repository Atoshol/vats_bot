import logging
import os
from dotenv import load_dotenv

load_dotenv()

try:
    TOKEN = os.environ['BOT_TOKEN']
    # TOKEN = '7058942982:AAGcU6khizY_SO86SQijBLD-LjnU6yZ_INo'
except KeyError as err:
    logging.critical(f"Can't read token from environment variable. Message: {err}")
    raise KeyError(err)
