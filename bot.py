from bot_methods.registration import *
from bot_methods.create_order import *
from bot_methods.user_access import *
from bot_methods.work_of_order import *
from bot_methods.other import *




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True)