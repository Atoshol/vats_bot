from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import calendar


async def get_main_menu_kb(all_messages: dict):
    buttons = []
    messages_buttons = [[InlineKeyboardButton(text=message_data['text'],
                                              callback_data=str(message_id))]
                        for message_id, message_data in all_messages.items()]

    add_client_add_message_buttons = [InlineKeyboardButton(text='Add new message',
                                                           callback_data='add_message'),
                                      InlineKeyboardButton(text='Add new client',
                                                           callback_data='add_client')]

    buttons.extend(messages_buttons)
    buttons.append(add_client_add_message_buttons)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_add_url_kb():
    buttons = [[InlineKeyboardButton(text='Back',
                                     callback_data='back'),
                InlineKeyboardButton(text='Skip',
                                     callback_data='skip')]]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_choices_kb(choices: list):
    buttons = [[InlineKeyboardButton(text=choice,
                                     callback_data=choice) for choice in choices]]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_clients_kb(all_clients: list):
    buttons = []

    clients = [[InlineKeyboardButton(text=client['username'],
                                     callback_data=str(client['id']))] for client in all_clients]

    buttons.extend(clients)
    back_button = [InlineKeyboardButton(text='Back',
                                        callback_data='back')]

    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_messages_kb(all_client_messages: dict):
    buttons = [[InlineKeyboardButton(text=data['text'],
                                     callback_data=str(message_id))] for message_id, data
               in all_client_messages.items()]

    add_message_button = [InlineKeyboardButton(text='Add message',
                                               callback_data='add_message')]

    add_back_button = [InlineKeyboardButton(text='Back',
                                            callback_data='back')]

    buttons.append(add_message_button)
    buttons.append(add_back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_preview_kb(message_id: str, text: str, url: str = None):
    buttons = []

    if url:
        url_button = [InlineKeyboardButton(text=text,
                                           url=url)]
        buttons.append(url_button)

    back_change_delete_button = [InlineKeyboardButton(text='Back',
                                                      callback_data='back'),
                                 InlineKeyboardButton(text='Change',
                                                      callback_data=f'change_{message_id}'),
                                 InlineKeyboardButton(text='Delete',
                                                      callback_data=f'delete_{message_id}')]

    buttons.append(back_change_delete_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_back_button():
    add_back_button = [[InlineKeyboardButton(text='Back',
                                             callback_data='back')]]

    kb = InlineKeyboardMarkup(inline_keyboard=add_back_button)

    return kb


async def form_url_button(url: str, text: str):
    url_button = [[InlineKeyboardButton(text=text,
                                        url=url)]]

    kb = InlineKeyboardMarkup(inline_keyboard=url_button)

    return kb


async def get_cancel_button():
    add_back_button = [[InlineKeyboardButton(text='Cancel',
                                             callback_data='cancel')]]

    kb = InlineKeyboardMarkup(inline_keyboard=add_back_button)

    return kb


async def get_subscriber_button():
    url_button = [[InlineKeyboardButton(text='Subscribe!',
                                        callback_data='subscribe')]]

    kb = InlineKeyboardMarkup(inline_keyboard=url_button)

    return kb


async def get_subscriber_menu():
    buttons = [[InlineKeyboardButton(text='Settings',
                                     callback_data='settings'),
                InlineKeyboardButton(text='Payment',
                                     callback_data='payment')]]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

