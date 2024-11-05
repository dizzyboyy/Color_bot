from bot_settings import *


@dp.message_handler()
async def other_messages(message: types.Message):
    if await check_user(message,bot, Form):
        user_id = message.from_user.id
        user_data = fing_user(user_id)
        user = User(user_data[0])
        if message.text == "Оформить заказ":
            text = f"Введите название цвета:"
            await bot.send_message(message.from_user.id, text)
            await OrderForm.color.set()
        else:
            text = f"Здравствуйте, {user.name} {user.patronymic}."
            await bot.send_message(message.from_user.id, text, reply_markup=greet_kb)
