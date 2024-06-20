"""This module contains custom created filters: IsAdminProgramState, NewChatMembersFilter, IsSuperAdmin"""


from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.main import bot
from db.facade import DB
from aiogram.types import ChatMemberUpdated



class IsAdmin(Filter):
    async def __call__(self, message: Message):

        #admins = [341302373, 669944831, 282659644, 6508260399]
        admins = [669944831]

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


class SubscribeCallback(Filter):
    async def __call__(self, call: CallbackQuery):
        if call.data == 'subscribe':
            return True
        return False


class BackToSettingsChoice(Filter):
    async def __call__(self, call: CallbackQuery, state: FSMContext):
        needed_states = ['SubscriberState:basic_settings', 'SubscriberState:renounced', 'SubscriberState:holders']
        user_state = await state.get_state()
        if call.data == 'back' and user_state in needed_states:
            return True
        return False


class BackToAdminSettingsChoice(Filter):
    async def __call__(self, call: CallbackQuery, state: FSMContext):
        needed_states = ['AdminState:basic_settings', 'AdminState:renounced',
                         'AdminState:holders']
        user_state = await state.get_state()
        if call.data == 'back' and user_state in needed_states:
            return True
        return False


class UserAddedFilter(Filter):
    async def __call__(self, message: Message):
        target_group_id = 1
        if message.new_chat_members and message.chat.id == target_group_id:
            return True
        return False

# class NewChatMembersFilter(Filter):
#     async def __call__(self, message: Message) -> bool:
#         return bool(message.new_chat_members)