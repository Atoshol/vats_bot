"""This module contains all bot handlers"""
import random
import re
import time

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

import bot.texts as texts
import logging
import bot.keyboards as keyboards

from datetime import datetime, timedelta
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from bot.main import dp, bot, db_clients, db_messages
from aiogram.fsm.context import FSMContext
from bot.states import AdminState, PotentialSubscriber
from bot.filters import IsAdmin, BackToMainMenu, IsSubscriber, PrivateChat, SubscribeCallback
from bot.keyboards import get_clients_kb
from utils.functions import find_closest_time_frame, get_data, get_history, escape_markdown_v2, \
    get_display_message
from db.facade import DB

# logging.basicConfig(filename='logs.log', level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     await message.answer(await escape_markdown_v2(f"Hello, {message.from_user.full_name}!"))


# @dp.message(F.text.startswith('@pricepredictiontest_bot'))
# async def message_handler(message: Message) -> None:
#     text = message.text or None
#     date_unknown = False
#     if text is not None:
#         try:
#             user_input = text.split(' ')[1:]
#             symbol, date = [i for i in user_input if i != '']
#         except (ValueError, TypeError):
#             await message.reply(text='Something went wrong.')
#             return
#         symbol = symbol.upper()
#         date = date.upper()
#         if date not in ['1H', '1D', '7D', '30D', '90D', '180D', '365D', '3Y', '5Y']:
#             date_unknown = True
#         correct_date = find_closest_time_frame(date)
#         data = get_data(symbol, period=correct_date)
#         price_prediction_data = data['price_prediction']
#         all_data = data['price_prediction']['all_data']
#         fng_index = data['fng_data']
#
#         current_price = price_prediction_data['current_price']
#         future_price = price_prediction_data['future_price']
#         if isinstance(future_price, str):
#             await message.answer(await escape_markdown_v2(f'Sorry, NO data available for {symbol}.'))
#             return
#         try:
#             vol_index = data['volatility_index']
#         except (KeyError, TypeError):
#             vol_index = 'No data available'
#         percnt_chng = price_prediction_data['percentage_change']
#         date_msg = f"*Your {symbol} forecast for {date}:*\n\n" \
#             if not date_unknown else (f'*Sorry, the {date} forecast is not available.'
#                                       f' Here is the {correct_date} forecast:*\n\n')
#         percnt_chng_str = f"+{percnt_chng}% 🟢" if percnt_chng > 0 else f"{percnt_chng}% 🔴"
#
#         response_text = (date_msg +
#                          f"💰 *{symbol} current price:* *_$ {current_price}_*\n"
#                          f"😱 *Greed/Fear index:* *_{fng_index}_*\n"
#                          f"📈 *Volatility index:* *_{vol_index}_*\n\n"
#                          f"🔮 *{symbol} forecast price:* *_$ {future_price}_*\n"
#                          f"💳 *Gains/Loss % from current price:* *_{percnt_chng_str}_*\n"
#                     )
#
#         img_bytes = create_image_with_text(percnt_chng)
#
#         eth_data = get_history(symbol)
#         predictions_data = [value for key, value in all_data.items() if key.startswith('price_change_')]
#         # img_bytes = create_price_history_and_predictions_graphic(eth_data=eth_data,
#         #                                                                   predictions_data=predictions_data,
#         #                                                                   symbol=symbol)
#         input_file = BufferedInputFile(file=img_bytes, filename="image.jpg")
#
#         display_ad = await get_display_message()
#         if not display_ad:
#             clear_text = await escape_markdown_v2(response_text)
#             await message.reply_photo(photo=input_file, caption=clear_text)
#
#         else:
#             ad_text = display_ad['text']
#             ad_url = display_ad['url']
#             clear_text = await escape_markdown_v2(text=response_text + '\n\n' + ad_text)
#             if ad_url:
#                 kb = await keyboards.form_url_button(url=ad_url, text=ad_text)
#                 clear_text = await escape_markdown_v2(text=response_text + '\n\n' + ad_text)
#                 await message.reply_photo(photo=input_file,
#                                           caption=clear_text,
#                                           reply_markup=kb)
#             else:
#                 await message.reply_photo(photo=input_file, caption=clear_text)


@dp.callback_query(AdminState.main_menu)
async def handle_main_menu_callback(call: CallbackQuery, state: FSMContext):
    if call.data == 'add_client':
        text = await escape_markdown_v2(text='Please type new client name:')
        kb = await keyboards.get_back_button()
        await call.message.edit_text(text=text,
                                     reply_markup=kb)

        await state.set_state(AdminState.adding_client)

    elif call.data == 'add_message':
        all_clients = await db_clients.get_all()
        if len(all_clients) < 1:
            all_messages = await db_messages.get_messages_by_clients()
            text = 'You have no created clients.'

            kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

            await call.message.edit_text(text=text,
                                         reply_markup=kb)

        elif len(all_clients) == 1:
            client_id = all_clients[0].id
            await state.update_data(client_id=client_id)
            text = await escape_markdown_v2(text='Please type message text:')
            kb = await keyboards.get_back_button()
            await call.message.edit_text(text=text,
                                         reply_markup=kb)

            await state.set_state(AdminState.adding_message)

        else:
            clear_clients = [client.as_dict() for client in all_clients]
            kb = await keyboards.get_clients_kb(all_clients=clear_clients)
            text = await escape_markdown_v2(text='Choose a client for a new message:')
            await call.message.edit_text(text=text,
                                         reply_markup=kb)

            await state.set_state(AdminState.choosing_client)

    else:
        all_messages = await db_messages.get_messages_by_clients()
        message_id = int(call.data)
        message_data = all_messages[message_id]
        message_text = message_data['text']
        message_url = message_data['url']
        current_time = time.time()
        last_time = message_data['expire_time']
        seconds_left = last_time - current_time

        time_delta = timedelta(seconds=seconds_left)
        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_left = f"Left: {days} day(s), {hours}:{minutes}:{seconds}\n\n"
        preview_text = await escape_markdown_v2(text='Below is message preview: \n' + time_left + message_text)
        kb = await keyboards.get_preview_kb(message_id=str(message_id), text=message_text, url=message_url)
        await call.message.edit_text(text=preview_text,
                                     reply_markup=kb)

        await state.set_state(AdminState.message_preview)


@dp.callback_query(BackToMainMenu())
async def handle_back_to_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AdminState.main_menu)

    all_messages = await db_messages.get_messages_by_clients()
    await state.update_data(all_messages=all_messages)

    if len(all_messages.keys()) >= 1:
        text = await escape_markdown_v2(text='Here is your clients messages (press button to get detailed preview):')

    else:
        text = await escape_markdown_v2(text='You have no messages. Press button below to add client or message.')

    kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

    await call.message.edit_text(text=text,
                                 reply_markup=kb)


@dp.callback_query(AdminState.choosing_client)
async def handle_client_choice(call: CallbackQuery, state: FSMContext):
    client_id = int(call.data)
    await state.update_data(client_id=client_id)
    text = await escape_markdown_v2(text='Please type message text:')
    kb = await keyboards.get_back_button()
    await call.message.edit_text(text=text,
                                 reply_markup=kb)

    await state.set_state(AdminState.adding_message)


@dp.message(AdminState.adding_client)
async def handle_client_name(message: Message, state: FSMContext):
    new_client_name = message.text
    client_data = {'username': new_client_name}
    await db_clients.create(**client_data)
    all_messages = await db_messages.get_messages_by_clients()

    await state.update_data(all_messages=all_messages)

    if len(all_messages.keys()) >= 1:
        text = await escape_markdown_v2(text='Client created and saved!\n\n' +
                                             'Here is your clients messages (press button to get detailed preview):')

    else:
        text = await escape_markdown_v2(text='Client created and saved!\n\n' +
                                             'You have no messages. Press button below to add client or message.')

    kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

    await message.answer(text=text,
                         reply_markup=kb)

    await state.set_state(AdminState.main_menu)


@dp.message(AdminState.adding_message)
async def handle_message_text(message: Message, state: FSMContext):
    message_text = message.text
    await state.update_data(message_text=message_text)
    text = await escape_markdown_v2(text='Please provide url or choose skip:')
    kb = await keyboards.get_add_url_kb()

    await message.answer(text=text,
                         reply_markup=kb)

    await state.set_state(AdminState.adding_url)


@dp.message(AdminState.adding_url)
async def handle_url(message: Message, state: FSMContext):
    url = message.text
    pattern = r'\bhttps?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]+)+(?::\d+)?(?:/[^\s]*)?'
    if re.match(pattern=pattern, string=url):
        await state.update_data(url=url)
        text = await escape_markdown_v2(text='Please enter active hours (should be digit):')
        kb = await keyboards.get_back_button()
        await message.answer(text=text,
                             reply_markup=kb)

        await state.set_state(AdminState.setting_duration)

    else:
        text = await escape_markdown_v2(text='Please provide url in correct format!')
        kb = await keyboards.get_add_url_kb()
        await message.answer(text=text,
                             reply_markup=kb)


@dp.callback_query(AdminState.adding_url)
async def handle_url_callback(call: CallbackQuery, state: FSMContext):
    if call.data == 'skip':
        url = None
        await state.update_data(url=url)
        text = await escape_markdown_v2(text='Please enter active hours (should be digit):')
        kb = await keyboards.get_back_button()
        await call.message.edit_text(text=text,
                                     reply_markup=kb)

        await state.set_state(AdminState.setting_duration)

    else:
        text = await escape_markdown_v2(text='Please type message text:')
        kb = await keyboards.get_back_button()
        await call.message.edit_text(text=text,
                                     reply_markup=kb)

        await state.set_state(AdminState.adding_message)


@dp.message(AdminState.setting_duration)
async def handle_duration(message: Message, state: FSMContext):
    duration = message.text
    if duration.isdigit():
        hours = int(duration)
        total_duration = 3600 * hours
        current_time = time.time()
        time_limit = current_time + total_duration
        state_data = await state.get_data()

        message_text = state_data['message_text']
        url = state_data['url']
        client_id = state_data['client_id']
        expire_time = time_limit

        await db_messages.create(text=message_text, url=url, client_id=client_id, expire_time=expire_time)

        all_messages = await db_messages.get_messages_by_clients()
        await state.update_data(all_messages=all_messages)

        text = await escape_markdown_v2(text='Message successfully created!' +
                                             'Here is your clients messages (press button to get detailed preview):')

        kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

        await message.answer(text=text, reply_markup=kb)
        await state.set_state(AdminState.main_menu)


@dp.callback_query(AdminState.setting_duration)
async def handle_back_duration(call: CallbackQuery, state: FSMContext):
    text = await escape_markdown_v2(text='Please provide url or choose skip:')
    kb = await keyboards.get_add_url_kb()

    await call.message.edit_text(text=text,
                                 reply_markup=kb)

    await state.set_state(AdminState.adding_url)


@dp.callback_query(AdminState.message_preview)
async def handle_callback_preview(call: CallbackQuery, state: FSMContext):
    if 'change' in call.data:
        state_data = await state.get_data()
        all_messages = state_data['all_messages']
        message_to_change_id = int(call.data.split('_')[1])
        message_to_change = all_messages[message_to_change_id]
        message_to_change_text = message_to_change['text']
        message_to_change_url = message_to_change['url']
        await state.update_data(message_to_change_id=message_to_change_id)

        if message_to_change_url:
            text = await escape_markdown_v2(text='Here is ad text:\n\n' + message_to_change_text + '\n\n'
                                            + f'Button URL:\n{message_to_change_url}\n\n' + 'Please type new ad text:')
        else:
            text = await escape_markdown_v2(text='Here is current message text:\n\n' + message_to_change_text + '\n\n'
                                                 + 'Please type new ad text:')

        kb = await keyboards.get_cancel_button()
        await call.message.edit_text(text=text, reply_markup=kb)

        await state.set_state(AdminState.input_new_message_text)

    elif 'delete' in call.data:
        message_to_delete_id = int(call.data.split('_')[1])
        await db_messages.delete(id_=message_to_delete_id)
        all_messages = await db_messages.get_messages_by_clients()
        await state.update_data(all_messages=all_messages)

        if len(all_messages.keys()) >= 1:
            text = await escape_markdown_v2(text='Message deleted!\n\n' +
                                                 'Here is your clients messages '
                                                 '(press button to get detailed preview):')

        else:
            text = await escape_markdown_v2(text='Message deleted!\n\n' +
                                                 'You have no messages. Press button below to add client or message.')

        kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

        await call.message.edit_text(text=text, reply_markup=kb)
        await state.set_state(AdminState.main_menu)


@dp.message(AdminState.input_new_message_text)
async def handle_new_ad_text(message: Message, state: FSMContext):
    new_ad_text = message.text
    await state.update_data(new_ad_text=new_ad_text)
    kb = await keyboards.get_add_url_kb()
    text = await escape_markdown_v2(text='Please add new URL or press skip if URL in text already')

    await message.answer(text=text,
                         reply_markup=kb)

    await state.set_state(AdminState.adding_new_url)


@dp.message(AdminState.adding_new_url)
async def handle_new_url(message: Message, state: FSMContext):
    url = message.text
    pattern = r'\bhttps?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]+)+(?::\d+)?(?:/[^\s]*)?'
    if re.match(pattern=pattern, string=url):
        state_data = await state.get_data()
        new_text = state_data['new_ad_text']
        message_to_change_id = state_data['message_to_change_id']
        new_message_data = {'text': new_text,
                            'url': url}
        await db_messages.update(id_=message_to_change_id, **new_message_data)

        await state.clear()

        await state.set_state(AdminState.main_menu)
        all_messages = await db_messages.get_messages_by_clients()
        await state.update_data(all_messages=all_messages)

        text = await escape_markdown_v2(text='Message edited!\n\n'
                                             'Here is your clients messages (press button to get detailed preview):')

        kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

        await message.answer(text=text, reply_markup=kb)

    else:
        text = await escape_markdown_v2(text='Please provide url in correct format!')
        kb = await keyboards.get_add_url_kb()
        await message.answer(text=text,
                             reply_markup=kb)


@dp.callback_query(AdminState.adding_new_url)
async def handle_new_url_callback(call: CallbackQuery, state: FSMContext):
    if call.data == 'skip':
        url = None
        state_data = await state.get_data()
        new_text = state_data['new_ad_text']
        message_to_change_id = state_data['message_to_change_id']
        new_message_data = {'text': new_text,
                            'url': url}
        await db_messages.update(id_=message_to_change_id, **new_message_data)

        await state.clear()

        await state.set_state(AdminState.main_menu)
        all_messages = await db_messages.get_messages_by_clients()
        await state.update_data(all_messages=all_messages)

        text = await escape_markdown_v2(text='Message edited!\n\n'
                                             'Here is your clients messages (press button to get detailed preview):')

        kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

        await call.message.edit_text(text=text, reply_markup=kb)

    else:
        text = await escape_markdown_v2(text='Please type message text:')
        kb = await keyboards.get_back_button()
        await call.message.edit_text(text=text,
                                     reply_markup=kb)

        await state.set_state(AdminState.adding_message)


@dp.message(IsAdmin())
async def handle_admin_message(message: Message, state: FSMContext):
    all_messages = await db_messages.get_messages_by_clients()
    await state.update_data(all_messages=all_messages)

    if len(all_messages.keys()) >= 1:
        text = await escape_markdown_v2(text='Here is your clients messages (press button to get detailed preview):')

    else:
        text = await escape_markdown_v2(text='You have no messages. Press button below to add client or message.')

    kb = await keyboards.get_main_menu_kb(all_messages=all_messages)

    await message.answer(text=text, reply_markup=kb)
    await state.set_state(AdminState.main_menu)


@dp.message(IsSubscriber())
async def handle_subscriber_message(message: Message):
    user_id = message.from_user.id
    user_settings = await DB.user_settings.read(id_=user_id)
    print(user_settings)


@dp.message(PrivateChat())
async def handle_private_chat(message: Message):
    kb = await keyboards.get_subscriber_button()
    await message.answer(text=texts.not_subscribed_user,
                         reply_markup=kb)


@dp.callback_query(SubscribeCallback())
async def choose_plan_handler(call: CallbackQuery, state: FSMContext):
    kb = await keyboards.get_subscriber_plans_kb()
    await call.message.edit_text(text=texts.subscribe_plans,
                                 reply_markup=kb)

    await state.set_state(PotentialSubscriber.choosing_sub_plan)


@dp.callback_query(PotentialSubscriber.choosing_sub_plan)
async def register_user(call: CallbackQuery):
    chosen_plan = call.data
    months_mapper = {'1': 2592000,
                     '3': 7776000,
                     '6': 15552000}

    months = months_mapper.get(chosen_plan)

    user_id = call.from_user.id
    username = call.from_user.username
    today = int(time.time())
    exp_date = today + months
    user_data = {'id': user_id,
                 'username': username,
                 'payed': '+',
                 'sub_expire_time': exp_date}

    await DB.user_crud.create(**user_data)
    settings_data = {'id': user_id}
    await DB.user_settings_crud.create(**settings_data)

    user = await DB.user_crud.read(id_=user_id)


async def exe_bot():
    """Function to start a bot"""
    print('BOT started')
    logging.info(msg="BOT started")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
