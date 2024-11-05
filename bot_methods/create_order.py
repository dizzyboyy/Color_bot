from bot_settings import *

@dp.callback_query_handler(lambda c: c.data == 'button1')
async def start_order(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = fing_user(user_id)
    await bot.answer_callback_query(callback_query.id)
    if await check_user(callback_query,bot, Form):
            text = f"Введите, пожалуйста, оригинальное название цвета. Пример: SI99 черная фактурная."
            await bot.send_message(callback_query.from_user.id, text)
            await OrderForm.color.set()


@dp.message_handler(state=OrderForm.color) # Принимаем состояние
async def get_color(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['color'] = message.text
        colors = get_colors(message.text)
        if colors['status'] == 1:
            text = "Мы нашли этот цвет.\nДавайте выберем подходящий аналог и оформим заказ."
            colors['user'] = message.from_user.id
            json_colors = urlencode(colors)
            await bot.send_message(message.from_user.id, text, reply_markup=webAppKeyboard(json_colors))
            await state.finish()
        elif colors['status'] == 2:
            proxy['color'] = colors['data']
            json_colors = urlencode(colors)
            print(json_colors)
            text = "Мы нашли несколько названий, которые похожи на то, что Вы искали"
            await bot.send_message(message.from_user.id, text, reply_markup=webAppKeyboard_near_colors(json_colors))
            await state.finish()
        else:
            text = "К сожалению, мы не нашли нужный Вам цвет. В ответном сообщении укажите цвет в формате HEX или RGB," \
                   " разделяя каждое значение пробелом.\nТакже Вы можете связаться с нашим менеджером @kupisalon"
            await bot.send_message(message.from_user.id, text)
            await OrderForm.no_colors.set()


# @dp.callback_query_handler(callback_colors.filter(action=["choose"]), state=OrderForm.other_colors)
# async def get_color(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
#     async with state.proxy() as proxy:
#         color_id = int(callback_data["color_id"])
#         proxy['other_colors'] = color_id
#         color = proxy['color'][color_id][0]
#         colors = get_colors(color)
#         if colors['status'] == 1:
#             text = "Ваш цвет успешно найден, можно перейти к выбору и оформлению."
#             colors['user'] = call.from_user.id
#             json_colors = urlencode(colors)
#             await bot.send_message(call.from_user.id, text, reply_markup=webAppKeyboard(json_colors))
#             await state.finish()


@dp.message_handler(state=OrderForm.no_colors) # Принимаем состояние
async def get_color(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['no_colors'] = message.text
        proxy['other_colors'] = message.text
        code = message.text
        try:
            colors = get_colors_by_code(code)
            if colors['status'] == 1:
                text = "Ваш цвет успешно найден, можно перейти к выбору и оформлению."
                colors['user'] = message.from_user.id
                json_colors = urlencode(colors)
                await bot.send_message(message.from_user.id, text, reply_markup=webAppKeyboard(json_colors))
                await state.finish()
        except:
            text = "К сожалению, в нашей базе нет такого цвета.\nСвяжитесь с нашим менеджером для уточнения @kupisalon\nДля выбора нового цвета введите /new"
            await bot.send_message(message.from_user.id, text, reply_markup = ReplyKeyboardRemove())
            await state.finish()


@dp.message_handler(content_types="web_app_data") #получаем отправленные данные
async def answer(webAppMes, state: FSMContext):
    res = (webAppMes.web_app_data.data)
    print('web_app')
    res = json.loads(res)
    print(res)
    if res[-1] == 'choose_color':
        get_user = fing_user(res[4])[0]
        text_admins = get_order_text_admins(res, get_user)
        order = create_order(res, get_user)
        all_admins = get_all_admins()

        for i in all_admins:
            try:
                await bot.send_message(i['user_id'], text_admins, reply_markup=get_order_manager_keyboard(order))
            except:
                pass
        await bot.send_message(webAppMes.chat.id, f"Мы получили Ваш заказ.\nВы выбрали {res[0]} "
                                                  f"в количестве {res[2]} метра(-ов)."
                                                  f"\nПожалуйста, ожидайте, "
                                                  f"мы свяжемся с Вами.\n", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(webAppMes.chat.id, 'Требуются ли Вам еще наши услуги?', reply_markup=yet_new_order_keyboard)
    if res[-1] == 'near_color':
        async with state.proxy() as proxy:
            color = res[0]
            if len(res) == 4:
                colors = get_colors_with_creator(color, res[1])
            else:
                colors = get_colors(color)
            if colors['status'] == 1:
                text = "Ваш цвет успешно найден, можно перейти к выбору и оформлению."
                colors['user'] = webAppMes.chat.id
                json_colors = urlencode(colors)
                await bot.send_message(webAppMes.chat.id, text, reply_markup=webAppKeyboard(json_colors))
                await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'yet_new_order')
async def send_welcome(callback_query: types.CallbackQuery):
    await start_order(callback_query)