from bot_settings import *

@dp.callback_query_handler(callback_access.filter(action=["1", "0"]))
async def callbacks_num_change_fab(call: types.CallbackQuery, callback_data: dict):
    action = callback_data["action"]
    user_id = callback_data["user_id"]
    user = fing_user(user_id)[0]
    fio = f"{user['name']} {user['patronymic']} {user['surname']}"
    if action == "1":
        set_access_user(user_id, 1)
        text = f"Доступ пользователю: {fio}\nОдобрен"
        text2 = f"Здравствуйте, {fio}.\nВам одобрен доступ к сервису"
        await bot.send_message(user_id, text2, reply_markup=greet_kb)
    if action == "0":
        set_access_user(user_id, 0)
        text = f"Доступ пользователю: {fio}\nЗапрещен"
        text2 = f"Здравствуйте, {fio}.\nВам отказано в доступе к сервису"
        await bot.send_message(user_id, text2)
    await bot.send_message(call.from_user.id, text)
    await call.answer()


@dp.message_handler(commands=['wait_users'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_data = fing_user(user_id)
    if await check_user(message,bot, Form):
        user = User(user_data[0])
        if user.root == 1:
            g_us = get_wait_users()
            if len(g_us) != 0:
                get_user = g_us[0]
                fio = get_user['surname']+ ' ' + get_user['name'] + ' ' + get_user['patronymic']
                text = f"Пользователь: {fio}"
                await bot.send_message(message.from_user.id, text, reply_markup=get_kb_access(get_user['user_id']))
            else:
                text = "Заявок нет"
                await bot.send_message(message.from_user.id, text)
