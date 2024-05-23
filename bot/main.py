from bot.settings import TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from db.models.message import MessageCRUD, MessageLastIndexCRUD
from db.models.client import ClientCRUD


storage = MemoryStorage()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
db_messages = MessageCRUD()
db_clients = ClientCRUD()
db_last_message = MessageLastIndexCRUD()
