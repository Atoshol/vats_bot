"""This module contains custom created filters: IsAdminProgramState, NewChatMembersFilter, IsSuperAdmin"""


from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.main import bot
from db.facade import DB


class IsAdmin(Filter):
    async def __call__(self, message: Message):

        #admins = [341302373, 669944831, 282659644, 6508260399]
        admins = []

        if message.from_user.id in admins and message.chat.type == 'private':
            return True
        return False


class BackToMainMenu(Filter):
    async def __call__(self, call: CallbackQuery, state: FSMContext):
        user_state = await state.get_state()
        second_level_states = ['AdminState:message_preview', 'AdminState:adding_client', 'AdminState:adding_message',
                               'AdminState:choosing_client']

        if user_state in second_level_states and call.data == 'back':
            return True
        return False


class IsSubscriber(Filter):
    async def __call__(self, message: Message):
        user_id = message.from_user.id
        chat_type = message.chat.type
        subscriber = await DB.user_crud.read(id_=user_id)
        if subscriber and chat_type == 'private':
            return True
        return False


class PrivateChat(Filter):
    async def __call__(self, message: Message):
        user_id = message.from_user.id
        subscriber = await DB.user_crud.read(id_=user_id)
        if message.chat.type == 'private' and subscriber is None:
            return True
        return False
