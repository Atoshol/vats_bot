from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import calendar
from db.facade import DB

async def messages_menu(all_messages: dict):
    buttons = []
    messages_buttons = [[InlineKeyboardButton(text=message_data['text'],
                                              callback_data=str(message_id))]
                        for message_id, message_data in all_messages.items()]

    add_client_add_message_buttons = [InlineKeyboardButton(text='Add new message',
                                                           callback_data='add_message'),
                                      InlineKeyboardButton(text='Add new client',
                                                           callback_data='add_client')]

    back_button = [InlineKeyboardButton(text='Back',
                                        callback_data='back')]

    buttons.extend(messages_buttons)
    buttons.append(add_client_add_message_buttons)
    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_main_menu_kb():
    buttons = []
    messages_buttons = [InlineKeyboardButton(text='Messages',
                                             callback_data='messages')]

    settings_button = [InlineKeyboardButton(text='Default settings',
                                            callback_data='settings')]

    buttons.append(messages_buttons)
    buttons.append(settings_button)

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
    url = 'https://telegram.me/collablandbot?start=VFBDI1RFTCNDT01NIy0xMDAyMTY4NzM2MjA2'
    url_button = [[InlineKeyboardButton(text='Subscribe!',
                                        url=url)]]

    kb = InlineKeyboardMarkup(inline_keyboard=url_button)

    return kb


async def get_subscriber_menu():
    buttons = [[InlineKeyboardButton(text='Settings',
                                     callback_data='settings')]]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_subscriber_plans_kb():
    buttons = [[InlineKeyboardButton(text='1 month',
                                     callback_data='1'),
                InlineKeyboardButton(text='3 months',
                                     callback_data='3'),
                InlineKeyboardButton(text='6 months',
                                     callback_data='6')
                ]]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_settings_kb():
    # -Market cap(minimum - max)
    # -Volume 5m, 1hr(min)
    # -Liquidity(minimum - max)
    # -Price change 5 m, 1 hr(min)
    # -Transaction count 5 m, 1 hr(min)
    # -Holders(min)
    # -Renounced? (Not all projects are renounced)

    buttons = [[InlineKeyboardButton(text='Market cap',
                                     callback_data='market_cap')],
                [InlineKeyboardButton(text='Volume',
                                      callback_data='volume')],
                [InlineKeyboardButton(text='Liquidity',
                                      callback_data='liquidity')],
                [InlineKeyboardButton(text='Price change',
                                      callback_data='price_change')],
                [InlineKeyboardButton(text='Transaction count',
                                      callback_data='transaction_count')],
                [InlineKeyboardButton(text='Holders',
                                      callback_data='holders')],
                [InlineKeyboardButton(text='LP locked',
                                      callback_data='lp_locked')],
                [InlineKeyboardButton(text='LP burned',
                                      callback_data='lp_burned')],
                [InlineKeyboardButton(text='Renounced',
                                      callback_data='renounced')],
                [InlineKeyboardButton(text='Back',
                                      callback_data='back')]]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_renounced_kb(update_setting: str, user_id: int = None, admin: bool = False):
    if admin:
        settings = await DB.default_settings_crud.read(id_=1)
    else:
        settings = await DB.user_settings_crud.read(id_=user_id)

    settings_mapper = {'Liquidity pool locked': settings.lp_locked,
                       'Liquidity poll burned': settings.lp_burned,
                       'Renounced': settings.renounced}

    current_setting = settings_mapper.get(update_setting)
    check_mark = "\u2714"
    if current_setting:
        buttons = [[InlineKeyboardButton(text=f'True {check_mark}',
                                         callback_data='true'),
                   InlineKeyboardButton(text='False',
                                        callback_data='false')]]

    else:
        buttons = [[InlineKeyboardButton(text='True',
                                         callback_data='true'),
                   InlineKeyboardButton(text=f'False {check_mark}',
                                        callback_data='false')]]

    back_button = [InlineKeyboardButton(text='Back',
                                         callback_data='back')]

    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb
