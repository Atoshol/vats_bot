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


class UserState(StatesGroup):
    pass


class SubscriberState(StatesGroup):
    pass