from config.db import *


class Order:

    id = ''
    color_name = ''
    dop_info = ''
    whats_app = ''
    metrs_count = ''
    is_pref = ''
    total_price = ''
    price_for_1_m = ''
    status = ''
    user_id = ''
    manager_id = ''

    def __init__(self, data):
        self.id = data['id']
        self.color_name = data['color_name']
        self.dop_info = data['dop_info']
        self.whats_app = data['whats_app']
        self.metrs_count = data['metrs_count']
        self.is_pref = data['is_perf']
        self.total_price = data['total_price']
        self.price_for_1m = data['price_for_1m']
        self.status = data['status']
        self.user_id = data['user_id']
        self.manager_id = data['manager_id']


    def set_moder_data(self, price_for_1m, total_price, manager_id):
        conn, cur = connect_to_db()
        data = (price_for_1m, total_price, manager_id, self.id)
        cur.execute(
            "UPDATE orders SET price_for_1m = ? , total_price = ? , manager_id = ? WHERE id = ? ;", data)
        conn.commit()
