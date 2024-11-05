from bot_settings import *


@dp.callback_query_handler(moder_keyboard_callbacks.filter(action=["start_order"]))
async def get_color(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as proxy:
        order_id = int(callback_data["order_id"])
        order = get_order(order_id)
        proxy['order_id'] = order_id
        text = f"Введите цену за метр материала цвета {order.color_name}"
        await bot.send_message(call.from_user.id, text)
        await WorkOrderForm.price_for_1m.set()


@dp.message_handler(state=WorkOrderForm.price_for_1m)
async def get_company_name(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['price_for_1m'] = message.text
        text = "Впишите итоговую цену за весь заказ"
        await bot.send_message(message.from_user.id, text)
        await WorkOrderForm.total_price.set()

@dp.message_handler(state=WorkOrderForm.total_price)
async def get_company_name(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['total_price'] = message.text
        text = "Платежна информация обрабатывается..."
        order = get_order(proxy['order_id'])
        order.set_moder_data(proxy['price_for_1m'], proxy['total_price'], message.from_user.id)
        await bot.send_message(message.from_user.id, text)
        await state.finish()
