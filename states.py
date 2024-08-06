from aiogram.dispatcher.filters.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone_number = State()

class LocationStates(StatesGroup):
    waiting_for_location = State()
    waiting_for_image = State()
    waiting_for_text_location = State()
    waiting_for_image_text = State()
    waiting_for_order_response = State()
