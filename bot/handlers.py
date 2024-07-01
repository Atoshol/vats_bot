
import re
import time
import bot.texts as texts
import logging
import bot.keyboards as keyboards
from datetime import timedelta
from aiogram.types import Message, CallbackQuery
from bot.main import dp, bot, db_clients, db_messages
from aiogram.fsm.context import FSMContext
from bot.states import AdminState, PotentialSubscriber, SubscriberState
from utils.functions import escape_markdown_v2
from db.facade import DB
import bot.filters as filters


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
async def handle_main_menu(call: CallbackQuery, state: FSMContext):
    if call.data == 'messages':
        all_messages = await db_messages.get_messages_by_clients()
        await state.update_data(all_messages=all_messages)

        if len(all_messages.keys()) >= 1:
            text = await escape_markdown_v2(
                text='Here is your clients messages (press button to get detailed preview):')

        else:
            text = await escape_markdown_v2(text='You have no messages. Press button below to add client or message.')

        kb = await keyboards.messages_menu(all_messages=all_messages)

        await call.message.edit_text(text=text, reply_markup=kb)
        await state.set_state(AdminState.messages)

    else:
        kb = await keyboards.get_settings_kb()

        await state.set_state(AdminState.default_settings)
        default_settings = await DB.default_settings_crud.read(id_=1)
        message_text = texts.user_settings.format(default_settings.market_cap_max,
                                                  default_settings.market_cap_min,
                                                  default_settings.volume_5_minute_min,
                                                  default_settings.volume_1_hour_min,
                                                  default_settings.liquidity_min,
                                                  default_settings.liquidity_max,
                                                  default_settings.price_change_5_minute_min,
                                                  default_settings.price_change_1_hour_min,
                                                  default_settings.transaction_count_5_minute_min,
                                                  default_settings.transaction_count_1_hour_min,
                                                  default_settings.holders_min,
                                                  default_settings.lp_locked,
                                                  default_settings.lp_burned,
                                                  default_settings.renounced)

        await call.message.edit_text(text=message_text,
                                     reply_markup=kb)
        await state.set_state(AdminState.default_settings)


@dp.callback_query(AdminState.messages)
async def handle_messages(call: CallbackQuery, state: FSMContext):
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

            kb = await keyboards.messages_menu(all_messages=all_messages)

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


@dp.callback_query(filters.BackToMainMenu())
async def handle_back_to_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AdminState.main_menu)

    all_messages = await db_messages.get_messages_by_clients()
    await state.update_data(all_messages=all_messages)

    if len(all_messages.keys()) >= 1:
        text = await escape_markdown_v2(text='Here is your clients messages (press button to get detailed preview):')

    else:
        text = await escape_markdown_v2(text='You have no messages. Press button below to add client or message.')

    kb = await keyboards.messages_menu(all_messages=all_messages)

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

    kb = await keyboards.messages_menu(all_messages=all_messages)

    await message.answer(text=text,
                         reply_markup=kb)

    await state.set_state(AdminState.messages)


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

        kb = await keyboards.messages_menu(all_messages=all_messages)

        await message.answer(text=text, reply_markup=kb)
        await state.set_state(AdminState.messages)


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

        kb = await keyboards.messages_menu(all_messages=all_messages)

        await call.message.edit_text(text=text, reply_markup=kb)
        await state.set_state(AdminState.messages)


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
    pattern = r'\https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]+)+(?::\d+)?(?:/[^\s]*)?'
    if re.match(pattern=pattern, string=url):
        state_data = await state.get_data()
        new_text = state_data['new_ad_text']
        message_to_change_id = state_data['message_to_change_id']
        new_message_data = {'text': new_text,
                            'url': url}
        await db_messages.update(id_=message_to_change_id, **new_message_data)

        await state.clear()

        await state.set_state(AdminState.messages)
        all_messages = await db_messages.get_messages_by_clients()
        await state.update_data(all_messages=all_messages)

        text = await escape_markdown_v2(text='Message edited!\n\n'
                                             'Here is your clients messages (press button to get detailed preview):')

        kb = await keyboards.messages_menu(all_messages=all_messages)

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

        await state.set_state(AdminState.messages)
        all_messages = await db_messages.get_messages_by_clients()
        await state.update_data(all_messages=all_messages)

        text = await escape_markdown_v2(text='Message edited!\n\n'
                                             'Here is your clients messages (press button to get detailed preview):')

        kb = await keyboards.messages_menu(all_messages=all_messages)

        await call.message.edit_text(text=text, reply_markup=kb)

    else:
        text = await escape_markdown_v2(text='Please type message text:')
        kb = await keyboards.get_back_button()
        await call.message.edit_text(text=text,
                                     reply_markup=kb)

        await state.set_state(AdminState.adding_message)


@dp.callback_query(AdminState.default_settings)
async def handle_setting_choice(call: CallbackQuery, state: FSMContext):
    if call.data == 'back':
        kb = await keyboards.get_main_menu_kb()
        text = 'Choose your option:'

        await call.message.edit_text(text=text, reply_markup=kb)
        await state.set_state(AdminState.main_menu)

    else:
        settings_mapper = {'market_cap': 'Market cap',
                           'volume': 'Volume',
                           'liquidity': 'Liquidity',
                           'price_change': 'Price change',
                           'transaction_count': 'Transaction count',
                           'holders': 'Holders',
                           'renounced': 'Renounced',
                           'lp_locked': 'Liquidity pool locked',
                           'lp_burned': 'Liquidity poll burned'}

        true_false_settings = ['Liquidity pool locked', 'Liquidity poll burned', 'Renounced']

        back_kb = await keyboards.get_back_button()

        setting = settings_mapper.get(call.data)
        await state.update_data(update_setting=setting)
        if setting == 'Holders':
            text = texts.holders_text.format(setting)
            await state.set_state(AdminState.holders)
            await call.message.edit_text(text=text,
                                         reply_markup=back_kb)

        elif setting in true_false_settings:
            text = texts.renounced_text.format(setting)
            kb = await keyboards.get_renounced_kb(admin=True)
            await state.set_state(AdminState.true_false)
            await call.message.edit_text(text=text,
                                         reply_markup=kb)

        else:
            text = texts.basic_text.format(setting)
            await state.set_state(AdminState.basic_settings)
            await call.message.edit_text(text=text,
                                         reply_markup=back_kb)


@dp.callback_query(filters.BackToAdminSettingsChoice())
async def handle_back_to_settings(call: CallbackQuery, state: FSMContext):
    kb = await keyboards.get_settings_kb()

    await state.set_state(AdminState.default_settings)
    default_settings = await DB.default_settings_crud.read(id_=1)
    message_text = texts.user_settings.format(default_settings.market_cap_max,
                                              default_settings.market_cap_min,
                                              default_settings.volume_5_minute_min,
                                              default_settings.volume_1_hour_min,
                                              default_settings.liquidity_min,
                                              default_settings.liquidity_max,
                                              default_settings.price_change_5_minute_min,
                                              default_settings.price_change_1_hour_min,
                                              default_settings.transaction_count_5_minute_min,
                                              default_settings.transaction_count_1_hour_min,
                                              default_settings.holders_min,
                                              default_settings.lp_locked,
                                              default_settings.lp_burned,
                                              default_settings.renounced)

    await call.message.edit_text(text=message_text,
                                 reply_markup=kb)
    await state.set_state(AdminState.default_settings)


@dp.message(AdminState.basic_settings)
async def handle_settings_update(message: Message, state: FSMContext):
    state_data = await state.get_data()
    chosen_setting = state_data['update_setting']
    settings_mapper = {'Market cap': ['market_cap_min', 'market_cap_max'],
                       'Volume': ['volume_5_minute_min', 'volume_1_hour_min'],
                       'Liquidity': ['liquidity_min', 'liquidity_max'],
                       'Price change': ['price_change_5_minute_min', 'price_change_1_hour_min'],
                       'Transaction count': ['transaction_count_5_minute_min', 'transaction_count_1_hour_min']}

    setting_to_update = settings_mapper.get(chosen_setting)
    pattern = '^\d+-\d+$'
    updated_value = message.text.replace(' ', '')
    if re.match(pattern=pattern, string=updated_value):
        values = updated_value.split('-')
        min_value = values[0]
        max_value = values[1]
        update_data = {setting_to_update[0]: min_value,
                       setting_to_update[1]: max_value}

        await DB.default_settings_crud.update(id_=1,
                                              **update_data)

        default_settings = await DB.default_settings_crud.read(id_=1)
        message_text = (texts.settings_updated.format(chosen_setting, f'{min_value} - {max_value}') +
                        '\n\n' +
                        texts.user_settings.format(default_settings.market_cap_max,
                                                   default_settings.market_cap_min,
                                                   default_settings.volume_5_minute_min,
                                                   default_settings.volume_1_hour_min,
                                                   default_settings.liquidity_min,
                                                   default_settings.liquidity_max,
                                                   default_settings.price_change_5_minute_min,
                                                   default_settings.price_change_1_hour_min,
                                                   default_settings.transaction_count_5_minute_min,
                                                   default_settings.transaction_count_1_hour_min,
                                                   default_settings.holders_min,
                                                   default_settings.lp_locked,
                                                   default_settings.lp_burned,
                                                   default_settings.renounced))

        kb = await keyboards.get_settings_kb()
        await state.set_state(AdminState.default_settings)
        cur_state = await state.get_state()
        await message.answer(text=message_text,
                             reply_markup=kb)

    else:
        kb = await keyboards.get_back_button()
        text = texts.incorrect_settings_input.format(chosen_setting, 'digits - digits (example 123 - 123)')
        await message.answer(text=text, reply_markup=kb)


@dp.callback_query(AdminState.true_false)
async def handle_renounced_choice(call: CallbackQuery, state: FSMContext):
    true_false_mapper = {'true': True,
                         'false': False}

    settings = {'renounced': true_false_mapper.get(call.data)}
    await DB.default_settings_crud.update(id_=1,
                                          **settings)

    default_settings = await DB.default_settings_crud.read(id_=1)
    message_text = (texts.renounced_updated.format(true_false_mapper.get(call.data)) +
                    '\n\n' +
                    texts.user_settings.format(default_settings.market_cap_max,
                                               default_settings.market_cap_min,
                                               default_settings.volume_5_minute_min,
                                               default_settings.volume_1_hour_min,
                                               default_settings.liquidity_min,
                                               default_settings.liquidity_max,
                                               default_settings.price_change_5_minute_min,
                                               default_settings.price_change_1_hour_min,
                                               default_settings.transaction_count_5_minute_min,
                                               default_settings.transaction_count_1_hour_min,
                                               default_settings.holders_min,
                                               default_settings.lp_locked,
                                               default_settings.lp_burned,
                                               default_settings.renounced))
    kb = await keyboards.get_settings_kb()
    await state.set_state(AdminState.default_settings)
    await call.message.edit_text(text=message_text,
                                 reply_markup=kb)


@dp.message(AdminState.holders)
async def handle_holders_settings(message: Message, state: FSMContext):
    new_settings = message.text
    if new_settings.isdigit():
        settings = {'holders_min': new_settings}
        await DB.default_settings_crud.update(id_=1,
                                              **settings)

        default_settings = await DB.default_settings_crud.read(id_=1)
        message_text = (texts.settings_updated.format('Holders', new_settings) +
                        '\n\n' +
                        texts.user_settings.format(default_settings.market_cap_max,
                                                   default_settings.market_cap_min,
                                                   default_settings.volume_5_minute_min,
                                                   default_settings.volume_1_hour_min,
                                                   default_settings.liquidity_min,
                                                   default_settings.liquidity_max,
                                                   default_settings.price_change_5_minute_min,
                                                   default_settings.price_change_1_hour_min,
                                                   default_settings.transaction_count_5_minute_min,
                                                   default_settings.transaction_count_1_hour_min,
                                                   default_settings.holders_min,
                                                   default_settings.lp_locked,
                                                   default_settings.lp_burned,
                                                   default_settings.renounced))
        kb = await keyboards.get_settings_kb()
        await state.set_state(AdminState.default_settings)
        await message.answer(text=message_text,
                             reply_markup=kb)

    else:
        kb = await keyboards.get_back_button()
        text = texts.incorrect_settings_input.format('Holders', 'digits only (example - 1234)')
        await message.answer(text=text,
                             reply_markup=kb)


@dp.message(filters.IsAdmin())
async def handle_admin_message(message: Message, state: FSMContext):
    kb = await keyboards.get_main_menu_kb()
    text = 'Choose your option:'

    await message.answer(text=text, reply_markup=kb)
    await state.set_state(AdminState.main_menu)


@dp.callback_query(SubscriberState.main_menu)
async def handle_main_menu(call: CallbackQuery, state: FSMContext):
    if call.data == 'settings':
        message_text = 'Choose setting to change:'
        kb = await keyboards.get_settings_kb()

        await call.message.edit_text(text=message_text,
                                     reply_markup=kb)
        await state.set_state(SubscriberState.settings)

    else:
        pass


@dp.callback_query(SubscriberState.settings)
async def handle_setting_choice(call: CallbackQuery, state: FSMContext):
    if call.data == 'back':
        user_id = call.from_user.id
        user_settings = await DB.user_settings_crud.read(id_=user_id)
        message_text = texts.user_settings.format(user_settings.market_cap_max,
                                                  user_settings.market_cap_min,
                                                  user_settings.volume_5_minute_min,
                                                  user_settings.volume_1_hour_min,
                                                  user_settings.liquidity_min,
                                                  user_settings.liquidity_max,
                                                  user_settings.price_change_5_minute_min,
                                                  user_settings.price_change_1_hour_min,
                                                  user_settings.transaction_count_5_minute_min,
                                                  user_settings.transaction_count_1_hour_min,
                                                  user_settings.holders_min,
                                                  user_settings.lp_locked,
                                                  user_settings.lp_burned,
                                                  user_settings.renounced)

        kb = await keyboards.get_subscriber_menu()
        await state.set_state(SubscriberState.main_menu)
        await call.message.edit_text(text=message_text,
                                     reply_markup=kb)

    else:
        settings_mapper = {'market_cap': 'Market cap',
                           'volume': 'Volume',
                           'liquidity': 'Liquidity',
                           'price_change': 'Price change',
                           'transaction_count': 'Transaction count',
                           'holders': 'Holders',
                           'renounced': 'Renounced'}

        true_false_settings = ['Liquidity pool locked', 'Liquidity poll burned', 'Renounced']

        back_kb = await keyboards.get_back_button()

        setting = settings_mapper.get(call.data)
        await state.update_data(update_setting=setting)
        if setting == 'Holders':
            text = texts.holders_text.format(setting)
            await state.set_state(SubscriberState.holders)
            await call.message.edit_text(text=text,
                                         reply_markup=back_kb)

        elif setting in true_false_settings:
            text = texts.renounced_text.format(setting)
            kb = await keyboards.get_renounced_kb(user_id=call.from_user.id)
            await state.set_state(SubscriberState.true_false)
            await call.message.edit_text(text=text,
                                         reply_markup=kb)

        else:
            text = texts.basic_text.format(setting)
            await state.set_state(SubscriberState.basic_settings)
            await call.message.edit_text(text=text,
                                         reply_markup=back_kb)


@dp.callback_query(filters.BackToSettingsChoice())
async def handle_back_to_settings(call: CallbackQuery, state: FSMContext):
    message_text = 'Choose setting to change:'
    kb = await keyboards.get_settings_kb()

    await call.message.edit_text(text=message_text,
                                 reply_markup=kb)
    await state.set_state(SubscriberState.settings)


@dp.message(SubscriberState.basic_settings)
async def handle_settings_update(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = message.from_user.id
    chosen_setting = state_data['update_setting']
    settings_mapper = {'Market cap': ['market_cap_min', 'market_cap_max'],
                       'Volume': ['volume_5_minute_min', 'volume_1_hour_min'],
                       'Liquidity': ['liquidity_min', 'liquidity_max'],
                       'Price change': ['price_change_5_minute_min', 'price_change_1_hour_min'],
                       'Transaction count': ['transaction_count_5_minute_min', 'transaction_count_1_hour_min']}

    setting_to_update = settings_mapper.get(chosen_setting)
    pattern = '^\d+-\d+$'
    updated_value = message.text.replace(' ', '')
    if re.match(pattern=pattern, string=updated_value):
        values = updated_value.split('-')
        min_value = values[0]
        max_value = values[1]
        update_data = {setting_to_update[0]: min_value,
                       setting_to_update[1]: max_value}

        await DB.user_settings_crud.update(id_=user_id,
                                           **update_data)

        user_settings = await DB.user_settings_crud.read(id_=user_id)
        message_text = (texts.settings_updated.format(chosen_setting, f'{min_value} - {max_value}') +
                        '\n\n' +
                        texts.user_settings.format(user_settings.market_cap_max,
                                                   user_settings.market_cap_min,
                                                   user_settings.volume_5_minute_min,
                                                   user_settings.volume_1_hour_min,
                                                   user_settings.liquidity_min,
                                                   user_settings.liquidity_max,
                                                   user_settings.price_change_5_minute_min,
                                                   user_settings.price_change_1_hour_min,
                                                   user_settings.transaction_count_5_minute_min,
                                                   user_settings.transaction_count_1_hour_min,
                                                   user_settings.holders_min,
                                                   user_settings.lp_locked,
                                                   user_settings.lp_burned,
                                                   user_settings.renounced))
        kb = await keyboards.get_subscriber_menu()
        await state.set_state(SubscriberState.main_menu)
        await message.answer(text=message_text,
                             reply_markup=kb)

    else:
        kb = await keyboards.get_back_button()
        text = texts.incorrect_settings_input.format(chosen_setting, 'digits - digits (example 123 - 123)')
        await message.answer(text=text, reply_markup=kb)


@dp.callback_query(SubscriberState.true_false)
async def handle_renounced_choice(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    true_false_mapper = {'true': True,
                         'false': False}

    settings = {'renounced': true_false_mapper.get(call.data)}
    await DB.user_settings_crud.update(id_=user_id,
                                       **settings)

    user_id = call.from_user.id
    user_settings = await DB.user_settings_crud.read(id_=user_id)
    message_text = (texts.renounced_updated.format(true_false_mapper.get(call.data)) +
                    '\n\n' +
                    texts.user_settings.format(user_settings.market_cap_max,
                                               user_settings.market_cap_min,
                                               user_settings.volume_5_minute_min,
                                               user_settings.volume_1_hour_min,
                                               user_settings.liquidity_min,
                                               user_settings.liquidity_max,
                                               user_settings.price_change_5_minute_min,
                                               user_settings.price_change_1_hour_min,
                                               user_settings.transaction_count_5_minute_min,
                                               user_settings.transaction_count_1_hour_min,
                                               user_settings.holders_min,
                                               user_settings.lp_locked,
                                               user_settings.lp_burned,
                                               user_settings.renounced))
    kb = await keyboards.get_subscriber_menu()
    await state.set_state(SubscriberState.main_menu)
    await call.message.edit_text(text=message_text,
                                 reply_markup=kb)


@dp.message(SubscriberState.holders)
async def handle_holders_settings(message: Message, state: FSMContext):
    new_settings = message.text
    user_id = message.from_user.id
    if new_settings.isdigit():
        settings = {'holders_min': new_settings}
        await DB.user_settings_crud.update(id_=user_id,
                                           **settings)

        user_settings = await DB.user_settings_crud.read(id_=user_id)
        message_text = (texts.settings_updated.format('Holders', new_settings) +
                        '\n\n' +
                        texts.user_settings.format(user_settings.market_cap_max,
                                                   user_settings.market_cap_min,
                                                   user_settings.volume_5_minute_min,
                                                   user_settings.volume_1_hour_min,
                                                   user_settings.liquidity_min,
                                                   user_settings.liquidity_max,
                                                   user_settings.price_change_5_minute_min,
                                                   user_settings.price_change_1_hour_min,
                                                   user_settings.transaction_count_5_minute_min,
                                                   user_settings.transaction_count_1_hour_min,
                                                   user_settings.holders_min,
                                                   user_settings.lp_locked,
                                                   user_settings.lp_burned,
                                                   user_settings.renounced))
        kb = await keyboards.get_subscriber_menu()
        await state.set_state(SubscriberState.main_menu)
        await message.answer(text=message_text,
                             reply_markup=kb)

    else:
        kb = await keyboards.get_back_button()
        text = texts.incorrect_settings_input.format('Holders', 'digits only (example - 1234)')
        await message.answer(text=text,
                             reply_markup=kb)


@dp.message(filters.IsSubscriber())
async def handle_subscriber_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_settings = await DB.user_settings_crud.read(id_=user_id)
    message_text = texts.user_settings.format(user_settings.market_cap_max,
                                              user_settings.market_cap_min,
                                              user_settings.volume_5_minute_min,
                                              user_settings.volume_1_hour_min,
                                              user_settings.liquidity_min,
                                              user_settings.liquidity_max,
                                              user_settings.price_change_5_minute_min,
                                              user_settings.price_change_1_hour_min,
                                              user_settings.transaction_count_5_minute_min,
                                              user_settings.transaction_count_1_hour_min,
                                              user_settings.holders_min,
                                              user_settings.lp_locked,
                                              user_settings.lp_burned,
                                              user_settings.renounced)

    kb = await keyboards.get_subscriber_menu()
    await message.answer(text=message_text,
                         reply_markup=kb)
    await state.set_state(SubscriberState.main_menu)


@dp.message(filters.PrivateChat())
async def handle_private_chat(message: Message):
    kb = await keyboards.get_subscriber_button()
    await message.answer(text=texts.not_subscribed_user.format(message.from_user.first_name),
                         reply_markup=kb)


@dp.callback_query(filters.SubscribeCallback())
async def choose_plan_handler(call: CallbackQuery, state: FSMContext):
    kb = await keyboards.get_subscriber_plans_kb()
    await call.message.edit_text(text=texts.subscribe_plans,
                                 reply_markup=kb)

    await state.set_state(PotentialSubscriber.choosing_sub_plan)


# @dp.callback_query(PotentialSubscriber.choosing_sub_plan)
# async def register_user(call: CallbackQuery):
#     chosen_plan = call.data
#     months_mapper = {'1': 2592000,
#                      '3': 7776000,
#                      '6': 15552000}
#
#     months = months_mapper.get(chosen_plan)
#
#     user_id = call.from_user.id
#     username = call.from_user.username
#     today = int(time.time())
#     exp_date = today + months
#     user_data = {'id': user_id,
#                  'username': username,
#                  'payed': '+',
#                  'sub_expire_time': exp_date}
#
#     await DB.user_crud.create(**user_data)
#     settings_data = {'id': user_id}
#     await DB.user_settings_crud.create(**settings_data)
#
#     user_settings = await DB.user_settings_crud.read(id_=user_id)
#     message_text = texts.user_settings.format(user_settings.market_cap_max,
#                                               user_settings.market_cap_min,
#                                               user_settings.volume_5_minute_min,
#                                               user_settings.volume_1_hour_min,
#                                               user_settings.liquidity_min,
#                                               user_settings.liquidity_max,
#                                               user_settings.price_change_5_minute_min,
#                                               user_settings.price_change_1_hour_min,
#                                               user_settings.transaction_count_5_minute_min,
#                                               user_settings.transaction_count_1_hour_min,
#                                               user_settings.holders_min,
#                                               user_settings.renounced)
#
#     kb = await keyboards.get_subscriber_menu()
#     await call.message.edit_text(text=message_text,
#                                  reply_markup=kb)


@dp.message(filters.UserAddedFilter())
async def handle_new_member(message: Message):
    new_user = message.new_chat_member
    user_id = new_user['id']
    user_username = new_user['username']

    user_data = {'id': user_id,
                 'username': f'@{user_username}'}

    await DB.user_crud.create(**user_data)
    settings_data = {'id': user_id}
    await DB.user_settings_crud.create(**settings_data)


async def exe_bot():
    """Function to start a bot"""
    print('BOT started')
    logging.info(msg="BOT started")
    default_settings = {
        "id": 1,
        "market_cap_min": 10000,
        "market_cap_max": 400000,
        "volume_5_minute_min": 10,
        "volume_1_hour_min": 10,
        "liquidity_min": 15000,
        "liquidity_max": 400000,
        "price_change_5_minute_min": 10,
        "price_change_1_hour_min": 10,
        "transaction_count_5_minute_min": 10,
        "transaction_count_1_hour_min": 10,
        "holders_min": 25,
        "renounced": False,
        "pair_age_max": 86400
    }
    await DB.default_settings_crud.create(**default_settings)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
