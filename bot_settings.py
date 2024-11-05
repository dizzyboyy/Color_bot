from functions import *


API_TOKEN = ''

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    name = State()
    surname = State()
    patronimyc = State()
    city = State()
    is_a_company = State()
    company_name = State()
    company_link = State()
    phone = State()
    goals = State()
    captcha = State()


class OrderForm(StatesGroup):
    color = State()
    other_colors = State()
    no_colors = State()


class WorkOrderForm(StatesGroup):
    manager_id = State()
    price_for_1m = State()
    total_price = State()


inline_btn_1 = InlineKeyboardButton('Оформить заказ', callback_data='button1')
greet_kb = InlineKeyboardMarkup().add(inline_btn_1)

yet_new_order_btn = InlineKeyboardButton('Совершить новый заказ', callback_data='yet_new_order')
yet_new_order_keyboard = InlineKeyboardMarkup().add(yet_new_order_btn)

is_copmany = InlineKeyboardButton('Компания', callback_data='is_comp:company_button')
is_people = InlineKeyboardButton('Частное лицо', callback_data='is_comp:people_button')
is_company_keyboard = InlineKeyboardMarkup().add(is_copmany)
is_company_keyboard.add(is_people)


def webAppKeyboard(data):  # создание клавиатуры с webapp кнопкой
    print(data)
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        InlineKeyboardButton(text="Перейти к выбору цвета и оформлению заказа",
                             web_app=WebAppInfo(
                                 url=f"https://ruhakachmaz.github.io/index.html?{data}")))


def webAppKeyboard_near_colors(data):  # создание клавиатуры с webapp кнопкой
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        InlineKeyboardButton(text="Цвета с похожими названиями",
                             web_app=WebAppInfo(
                                 url=f"https://ruhakachmaz.github.io/near-color.html?{data}")))

callback_access = CallbackData("access_btn", "user_id", "action")


def get_kb_access(user_id):
    buttons = [
        types.InlineKeyboardButton(text="Одобрить", callback_data=callback_access.new(user_id=user_id, action="1")),
        types.InlineKeyboardButton(text="Запретить", callback_data=callback_access.new(user_id=user_id, action="0"))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


callback_colors = CallbackData("access_btn", "color_id", "action")


def get_kb_colors(colors):
    buttons = []
    for i in range(len(colors)):
        buttons.append(types.InlineKeyboardButton(text=colors[i][0],
                                                  callback_data=callback_colors.new(color_id=i, action="choose")))
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


moder_keyboard_callbacks = CallbackData("start_moderation", "order_id", "action")


def get_order_manager_keyboard(order_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text="Взять заказ на модерацию",
                                   callback_data=moder_keyboard_callbacks.new(order_id=order_id, action="start_order")))
    return keyboard
