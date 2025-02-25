from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    main_menu = State()
    viewing_clients = State()
    message_preview = State()
    adding_client = State()
    adding_message = State()
    adding_url = State()
    setting_duration = State()
    choosing_client = State()
    input_new_message_text = State()
    adding_new_url = State()
    default_settings = State()
    basic_settings = State()
    holders = State()
    true_false = State()
    messages = State()
    min_hour_settings = State()


class UserState(StatesGroup):
    pass


class SubscriberState(StatesGroup):
    main_menu = State()
    settings = State()
    holders = State()
    true_false = State()
    basic_settings = State()
    min_hour_settings = State()


class PotentialSubscriber(StatesGroup):
    choosing_sub_plan = State()
