from bot_settings import *

@dp.message_handler(commands=['start', 'new'])
async def start_message(message: types.Message):
    user_id = message.from_user.id
    user_data = fing_user(user_id)
    if await check_user(message, bot, Form):
        user = User(user_data[0])
        text = f"Здравствуйте, {user.name} {user.patronymic}."
        await bot.send_message(message.from_user.id, text, reply_markup=greet_kb)


@dp.message_handler(state=Form.name)
async def get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['name'] = message.text
        text = "Введите свою фамилию:"
        await bot.send_message(message.from_user.id, text)
        await Form.surname.set()


@dp.message_handler(state=Form.surname)
async def get_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['surname'] = message.text
        text = "Введите свое отчество:"
        await bot.send_message(message.from_user.id, text)
        await Form.patronimyc.set()


@dp.message_handler(state=Form.patronimyc)
async def get_patronimyc(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['patronimyc'] = message.text
        text = "Введите свою страну и город:"
        await bot.send_message(message.from_user.id, text)
        await Form.city.set()


@dp.message_handler(state=Form.city)
async def get_city(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['city'] = message.text
        text = "Вы представитель компании или частное лицо?"
        await bot.send_message(message.from_user.id, text, reply_markup=is_company_keyboard)
        await Form.is_a_company.set()

@dp.callback_query_handler(lambda c: c.data[:7] == 'is_comp', state=Form.is_a_company)
@dp.message_handler(state=Form.is_a_company)
async def is_company(callback_query: types.CallbackQuery,  state: FSMContext):
    async with state.proxy() as proxy:
        if callback_query.data == 'is_comp:people_button':
            proxy['is_a_company'] = '0'
            proxy['company_name'] = ''
            proxy['company_link'] = ''
            text = "Введите актуальный номер телефона"
            await bot.send_message(callback_query.from_user.id, text)
            await Form.phone.set()
        else:
            proxy['is_a_company'] = '1'
            text = "Введите название Вашей компании"
            await bot.send_message(callback_query.from_user.id, text)
            await Form.company_name.set()



@dp.message_handler(state=Form.company_name)
async def get_company_name(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['company_name'] = message.text
        text = "Отправьте ссылку на компанию"
        await bot.send_message(message.from_user.id, text)
        await Form.company_link.set()


@dp.message_handler(state=Form.company_link)
async def get_company_name(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['company_link'] = message.text
        text = "Введите актуальный номер телефона"
        await bot.send_message(message.from_user.id, text)
        await Form.phone.set()

@dp.message_handler(state=Form.phone)
async def get_company_name(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['phone'] = message.text
        text = "Опишите, для каких целей Вам нужен бот"
        await bot.send_message(message.from_user.id, text)
        await Form.goals.set()

@dp.message_handler(state=Form.goals)
async def get_patronimyc(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['goals'] =message.text
        captcha = get_captcha()
        proxy['captcha'] = captcha['text']
        text = "Подвердите, что Вы человек"
        await bot.send_message(message.from_user.id, text)
        await bot.send_photo(message.from_user.id, captcha['photo'])
        await Form.captcha.set()


@dp.message_handler(state=Form.captcha)
async def get_company_name(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        if message.text.lower() == proxy['captcha'].lower():
            text = "Ваша анкета успешно передана модератору. Пожалуйста, ожидайте подтверждения."
            await bot.send_message(message.from_user.id, text)
            text_admins = get_new_user_to_admin(proxy)
            all_admins = get_all_admins()
            for i in all_admins:
                try:
                    await bot.send_message(i['user_id'], text_admins, reply_markup=get_kb_access(message.from_user.id))
                except:
                    pass
            data = (message.from_user.id,
                    proxy['name'],
                    proxy['surname'],
                    proxy['patronimyc'],
                    message.from_user.username,
                    0, 1, 0,
                    proxy['is_a_company'],
                    proxy['company_name'],
                    proxy['company_link'],
                    proxy['phone'],
                    proxy['city'],
                    proxy['goals'])
            if message.from_user.username in admins:
                data = (message.from_user.id,
                        proxy['name'],
                        proxy['surname'],
                        proxy['patronimyc'],
                        message.from_user.username,
                        1, 0, 1,
                        proxy['is_a_company'],
                        proxy['company_name'],
                        proxy['company_link'],
                        proxy['phone'],
                        proxy['city'],
                        proxy['goals'])
            register_user(data)
            await state.finish()
        else:
            text = "Неправильный ответ. Пройдите регистрацию еще раз."
            await bot.send_message(message.from_user.id, text)
            await state.finish()
            await start_message(message)
