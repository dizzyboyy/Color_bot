import sqlite3
from config.admins import admins
from objects.user import *
import gspread
import math
from pyciede2000 import ciede2000
from Levenshtein import distance
from claptcha import Claptcha
import random
import string
import datetime
from objects.order import *
import gspread
import math
from pyciede2000 import ciede2000
from Levenshtein import distance
import requests
import logging
from urllib.parse import urlencode
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.callback_data import CallbackData
from objects.user import User
from config.admins import *
import json
from objects.order import Order
import asyncio
from config.db import *



def fing_user(user_id):
    conn, cur = connect_to_db()
    cur.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    result = cur.fetchall()
    return result


def get_mos_time():
    offset = datetime.timezone(datetime.timedelta(hours=3))
    times = str(datetime.datetime.now(offset))
    date = times.split()[0]
    time_plus3 = times.split()[1].split(".")[0]
    result = date + " " + time_plus3
    return result


def register_user(data):
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO users (user_id, name, surname, patronymic, username, access, is_wait_access, root, "
                "is_company, company_name, company_link, phone, city, goals)"
                " VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", data)
    conn.commit()

    sa = gspread.service_account(filename="config/service_account.json")
    sh = sa.open("TelegramBot")
    wks = sh.worksheet("Users")

    insert_data_array = []

    for i in range(5):
        insert_data_array.append(data[i])

    if data[5] == 0: insert_data_array.append("Нет доступа")
    else: insert_data_array.append("Есть доступ")

    if data[7] == 0: insert_data_array.append("Нет")
    else: insert_data_array.append("Да")

    insert_data_array.append(get_mos_time())

    if data[8] == "0": insert_data_array.append("Частое лицо")
    else: insert_data_array.append("Компания")

    for i in range(9, 14):
        insert_data_array.append(data[i])

    wks.append_row(insert_data_array) 


async def check_user(message, bot, Form):
    user_id = message.from_user.id
    user_data = fing_user(user_id)
    if len(user_data) == 0:
        text = f"Здравствуйте, {message.from_user['first_name']}.\nВы впервые у нас. " \
               f"Сначала Вам нужно пройти регистрацию.\n Введите, пожалуйста, свое имя:"
        await bot.send_message(message.from_user.id, text)
        await Form.name.set()
    else:
        user = User(user_data[0])
        if user.access == '0':
            if user.is_wait_access == '1':
                text = 'Ваше регистрация ожидает подтверждения от модератора.'
            else:
                text = 'К сожалению, Вам отказано в доступе'
            await bot.send_message(message.from_user.id, text)
        else:
            return True
    return False


def get_wait_users():
    conn, cur = connect_to_db()
    cur.execute(f'SELECT * FROM users WHERE is_wait_access = 1 ORDER BY date DESC')
    result = cur.fetchall()
    return result


def set_access_user(user_id, access):
    conn, cur = connect_to_db()
    data = (access, user_id)
    cur.execute("UPDATE users SET access = ?, is_wait_access = 0 WHERE user_id = ? ;", data)
    conn.commit()

    sa = gspread.service_account(filename="config/service_account.json")
    sh = sa.open("TelegramBot")
    wks = sh.worksheet("Users")
    sheet = wks.get_all_values()

    for row in range(1, len(sheet)):
        if sheet[row][0] == user_id:
            wks.update(f'F{row+1}', 'Есть доступ')



def cie76(L1, a1, b1, L2, a2, b2):
    return math.sqrt((L2 - L1) ** 2 + (a2 - a1) ** 2 + (b2 - b1) ** 2)


def ciede2000deltaE(L1, a1, b1, L2, a2, b2):
    e = ciede2000((L1, a1, b1), (L2, a2, b2))
    return e['delta_E_00']

def get_table_values(tablename, listname):
    sa = gspread.service_account(filename="config/service_account.json")
    sh = sa.open(tablename)
    wks = sh.worksheet(listname)
    sheet = wks.get_all_values()
    return sheet

def get_colors(color):
    sheet = get_table_values("TelegramBot", "List1")
    # НАЧАЛЬНОЕ ЗНАЧЕНИЕ Lab для изменения в будущем
    color_lab = (0, 0, 0, ())

    # ПРОБУЕМ НАЙТИ ЦВЕТ С ТАКИМ ЖЕ НАЗВАНИЕМ
    count_color = 0
    for row in sheet:
        if row[3].lower() == color.lower():
            color_lab = (float(row[6]), float(row[7]), float(row[8]), [row[15], row[16], row[17]])
            color_name_encoded = row[3]
            count_color += 1
    if count_color > 1:
        color_lab = (0, 0, 0, ())
    # ЕСЛИ ЦВЕТА С ТАКИМ ЖЕ НАЗВАНИЕМ НЕТ, ТО ИЩЕМ ЦВЕТА, КОТОРЫЕ ОТЛИЧАЮТСЯ НЕ БОЛЕЕ ЧЕМ НА 4 СИМВОЛА ОТ ВВЕДЕННОГО, СОЗДАВАЯ И ВНОСЯ В МАССИВ colors_array ИХ НАЗВАНИЯ И Lab
    if color_lab == (0, 0, 0, ()):
        colors_array = []
        for row in sheet:
            color_name_encoded_tmp = row[3]
            if (color.lower() in color_name_encoded_tmp.lower()) or (distance(color_name_encoded_tmp.lower(), color.lower()) <= 2):
                if len(colors_array) < 3:
                    is_c = 0
                    for i in range(len(colors_array)):
                        if colors_array[i]['name'] == color_name_encoded_tmp:
                            colors_array[i]['is_color_creator'] = 1
                            is_c = 1
                    colors_array.append({'name': color_name_encoded_tmp, 'rgb':[row[15], row[16], row[17]],
                                         'creator': row[1], 'is_color_creator' : is_c})
                else:
                    break
        just_in_colors = {}
        for i in colors_array:
            if i['name'] in just_in_colors:
                just_in_colors[i['name']] = '2'
            else:
                just_in_colors[i['name']] = '1'
        for i in colors_array:
            if just_in_colors[i['name']] == '2':
                i['is_color_creator'] = 1

        # ПРОВЕРЯЕМ, НАШЛИСЬ ЛИ ПОХОЖИЕ ПО НАЗВАНИЮ ЦВЕТА. ЕСЛИ ДА, ТО ВЫВОДИМ СПИСОК ИХ НАЗВАНИЙ
        if len(colors_array) == 0:
            return {'status': 3, 'data': ''}
        else:
            return {'status': 2, 'data': colors_array}


    # ИНИЦИАЛИЗИРУЕМ МАССИВ ДЛЯ ЗАПИСИ В НЕГО ПОЛУЧЕННЫХ ЗНАЧЕНИЙ ВИДА [CIEDE2000, COLOR_NAME] ДЛЯ ПОСЛЕДУЮЩЕЙ СОРТИРОВКИ
    res_tmp = []
    e_dists_array = []
    for row in sheet:
        try:
            # БЕРЕМ ЗНАЧЕНИЯ Lab по столбцам в таблице
            l, a, b, iter_color_title, rgb, creator = float(
                row[6]), float(
                row[7]), float(
                row[8]), row[0], [row[15], row[16], row[17]], row[1]
            # ЕСЛИ ЗНАЧЕНИЕ СОВПАДАЕТ С ВХОДНЫМ, ТО ПРОПУСКАЕМ
            if (l, a, b) == (color_lab[0], color_lab[1], color_lab[2]):
                continue
            # ЕСЛИ ЗНАЧЕНИЯ РАЗНЫЕ, ТО ВЫВОДИМ CIE76 и CIEDE2000
            else:
                cie76_value = cie76(l, a, b, color_lab[0], color_lab[1], color_lab[2])
                ciede2000_value = ciede2000deltaE(l, a, b, color_lab[0], color_lab[1], color_lab[2])
                e_dists_array.append([ciede2000_value, cie76_value, iter_color_title, rgb, creator, 0])
        except BaseException:
            pass

    res = []
    res.append({'name': color_name_encoded, 'C2000': 0, 'c76': 0, 'rgb': color_lab[3]})

    # СОРТИРУЕМ МАССИВ ПО РАССТОЯНИЮ CIEDE2000 и CIE76 И ВЫВОДИМ САМЫЕ БЛИЗКИЕ ЦВЕТА В КОЛИЧЕСТВЕ 9 ШТУК
    if e_dists_array:
        idx = 1
        e_dists_array.sort()

        for e in e_dists_array:
            if idx > 9:
                break
            res_tmp.append({'name': e[2], 'C2000': e[0], 'c76': e[1], 'rgb': e[3], 'creator': e[4]})
            idx += 1
    just_in_colors = {}
    for i in res_tmp:
        if i['name'] in just_in_colors:
            just_in_colors[i['name']] = '2'
        else:
            just_in_colors[i['name']] = '1'
    for i in res_tmp:
        if just_in_colors[i['name']] == '2':
            i['name'] = i['name'] + ' ' + i['creator']

    for i in res_tmp:
        res.append(i)

    return {'status': 1, 'data': res}



#ПОИСК ЦВЕТОВ ПО RGB & HEX
def get_colors_by_code(code):
    sheet = get_table_values("TelegramBot", "List1")
    # НАЧАЛЬНОЕ ЗНАЧЕНИЕ Lab для изменения в будущем
    color_lab = (0, 0, 0, code.split())
    color_name = code
    let = "0123456789"

    if len(code) == 6 or len(code) == 7:
        # ПРОБУЕМ НАЙТИ ЦВЕТ С ТАКИМ ЖЕ HEX
        for row in sheet:
            if row[18] == code:
                color_lab = (float(row[6]), float(row[7]), float(row[8]), [row[15], row[16], row[17]])
                color_name = ' '.join(row[0])
                break
    else:
        code = code.split()
        for i in range(len(code)):
            for j in range(len(code[i])):
                if code[i][j] not in let:
                    code[i] = code[i].replace(code[i][j], "")

        # ПРОБУЕМ НАЙТИ ЦВЕТ С ТАКИМ ЖЕ RGB
        for row in sheet:
            if row[15] == code[0] and row[16] == code[1] and row[17] == code[2]:
                color_lab = (float(row[6]), float(row[7]), float(row[8]), [row[15], row[16], row[17]])
                color_name = " ".join(row[0])
                break


    # ИНИЦИАЛИЗИРУЕМ МАССИВ ДЛЯ ЗАПИСИ В НЕГО ПОЛУЧЕННЫХ ЗНАЧЕНИЙ ВИДА [CIEDE2000, COLOR_NAME] ДЛЯ ПОСЛЕДУЮЩЕЙ СОРТИРОВКИ
    e_dists_array = []
    for row in sheet:
        try:
            # БЕРЕМ ЗНАЧЕНИЯ Lab по столбцам в таблице
            l, a, b, iter_color_title, rgb, title = float(
                row[6]), float(
                row[7]), float(
                row[8]), row[0], [row[15], row[16], row[17]], row[3]
            # ЕСЛИ ЗНАЧЕНИЕ СОВПАДАЕТ С ВХОДНЫМ, ТО ПРОПУСКАЕМ
            if (l, a, b) == (color_lab[0], color_lab[1], color_lab[2]):
                continue
            # ЕСЛИ ЗНАЧЕНИЯ РАЗНЫЕ, ТО ВЫВОДИМ CIE76 и CIEDE2000
            else:
                cie76_value = cie76(l, a, b, color_lab[0], color_lab[1], color_lab[2])
                ciede2000_value = ciede2000deltaE(l, a, b, color_lab[0], color_lab[1], color_lab[2])
                e_dists_array.append([ciede2000_value, cie76_value, iter_color_title, rgb, title])
        except BaseException:
            pass
    res = []
    res.append({'name': color_name, 'C2000': 0, 'c76': 0, 'rgb': color_lab[3]})
    # СОРТИРУЕМ МАССИВ ПО РАССТОЯНИЮ CIEDE2000 и CIE76 И ВЫВОДИМ САМЫЕ БЛИЗКИЕ ЦВЕТА В КОЛИЧЕСТВЕ 9 ШТУК
    if e_dists_array:
        idx = 1
        e_dists_array.sort()

        for e in e_dists_array:
            if idx > 9:
                break
            res.append({'name': e[2], 'C2000': e[0], 'c76': e[1], 'rgb': e[3]})
            idx += 1
        return {'status': 1, 'data': res}

    else:
        return "К сожалению, такого цвета у нас нет. Попробуйте другой."

def get_all_admins():
    conn, cur = connect_to_db()
    cur.execute(f'SELECT * FROM users WHERE root=1')
    result = cur.fetchall()
    return result


def randomString():
    rndLetters = (random.choice(string.ascii_uppercase) for _ in range(6))
    return "".join(rndLetters)

def get_captcha():
    c = Claptcha(randomString(), "assets/FreeMono.ttf")
    text, bytes = c.bytes
    return {'text': text, 'photo': bytes}

def get_new_user_to_admin(data):
    text = "Появилась новая заявка на модерацию\n"
    text += f'ФИО: {data["surname"]} {data["name"]} {data["patronimyc"]}\n'
    text += f'Телефон: {data["phone"]}\n'
    if data['is_a_company'] == '0':
        text += 'Тип: Частное лицо\n'
        text += f"Страна и город: {data['city']}\n"
        text += f"Цель использования: {data['goals']}"
    else:
        text += 'Тип: Компания\n'
        text += f'Название: {data["company_name"]}\n'
        text += f'Ссылка: {data["company_link"]}\n'
        text += f"Страна и город: {data['city']}\n"
        text += f"Цель использования: {data['goals']}"
    return text


def get_order_text_admins(res, get_user):
    et_color = res[5]
    fio = get_user['surname'] + ' ' + get_user['name'] + ' ' + get_user['patronymic']
    text_admins = f'''
        Новая заявка:\n
        ФИО: {fio}\n
        Эталонный цвет: {et_color}\n
        Цвет: {res[0]}\n
        WhatsApp: {res[1]}\n
        Количество: {res[2]}\n
        Дополнительно: {res[3]}\n
        Нужна ли перфорация: {res[6]}\n\n'''
    if get_user['is_company'] == '1':
        text_admins += f'        Тип клиента: компания\n\n'
        text_admins += f"        Название комании: {get_user['company_name']}\n\n"
        text_admins += f"        Актуальный телефон: {get_user['phone']}\n\n"
        text_admins += f"        Страна и город: {get_user['city']}\n\n"
        text_admins += f"        Цель использования: {get_user['goals']}"
    else:
        text_admins += f'        Тип клиента: частный\n\n'
        text_admins += f"        Актуальный телефон: {get_user['phone']}\n\n"
        text_admins += f"        Страна и город: {get_user['city']}\n\n"
        text_admins += f"        Цель использования: {get_user['goals']}"
    return text_admins


def create_order(res, get_user):
    conn, cur = connect_to_db()
    data = (res[0], res[3], res[1], res[2], res[6], 0, res[5], get_user['id'])
    cur.execute("INSERT INTO orders (color_name, dop_info, whats_app, metrs_count, is_perf, status, et_color, user_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?);", data)
    conn.commit()
    return cur.lastrowid


def get_order(order_id):
    conn, cur = connect_to_db()
    cur.execute(f'SELECT * FROM orders WHERE id = "{order_id}"')
    result = cur.fetchall()[0]
    result = Order(result)
    return result

def get_colors_with_creator(color, creator):
    sheet = get_table_values("TelegramBot", "List1")
    # НАЧАЛЬНОЕ ЗНАЧЕНИЕ Lab для изменения в будущем
    color_lab = (0, 0, 0, ())
    print(color, creator)
    # ПРОБУЕМ НАЙТИ ЦВЕТ С ТАКИМ ЖЕ НАЗВАНИЕМ
    count_color = 0
    for row in sheet:
        if row[3].lower() == color.lower() and row[1] == creator:
            color_lab = (float(row[6]), float(row[7]), float(row[8]), [row[15], row[16], row[17]])
            color_name_encoded = row[3]

        # ИНИЦИАЛИЗИРУЕМ МАССИВ ДЛЯ ЗАПИСИ В НЕГО ПОЛУЧЕННЫХ ЗНАЧЕНИЙ ВИДА [CIEDE2000, COLOR_NAME] ДЛЯ ПОСЛЕДУЮЩЕЙ СОРТИРОВКИ
    e_dists_array = []
    for row in sheet:
        try:
            # БЕРЕМ ЗНАЧЕНИЯ Lab по столбцам в таблице
            l, a, b, iter_color_title, rgb, creator = float(
                row[6]), float(
                row[7]), float(
                row[8]), row[0], [row[15], row[16], row[17]], row[1]
            # ЕСЛИ ЗНАЧЕНИЕ СОВПАДАЕТ С ВХОДНЫМ, ТО ПРОПУСКАЕМ
            if (l, a, b) == (color_lab[0], color_lab[1], color_lab[2]):
                continue
            # ЕСЛИ ЗНАЧЕНИЯ РАЗНЫЕ, ТО ВЫВОДИМ CIE76 и CIEDE2000
            else:
                cie76_value = cie76(l, a, b, color_lab[0], color_lab[1], color_lab[2])
                ciede2000_value = ciede2000deltaE(l, a, b, color_lab[0], color_lab[1], color_lab[2])
                e_dists_array.append([ciede2000_value, cie76_value, iter_color_title, rgb, creator, 0])
        except BaseException:
            pass

    res = []
    res_tmp = []
    res.append({'name': color_name_encoded, 'C2000': 0, 'c76': 0, 'rgb': color_lab[3]})

    # СОРТИРУЕМ МАССИВ ПО РАССТОЯНИЮ CIEDE2000 и CIE76 И ВЫВОДИМ САМЫЕ БЛИЗКИЕ ЦВЕТА В КОЛИЧЕСТВЕ 9 ШТУК
    if e_dists_array:
        idx = 1
        e_dists_array.sort()

        for e in e_dists_array:
            if idx > 9:
                break
            res_tmp.append({'name': e[2], 'C2000': e[0], 'c76': e[1], 'rgb': e[3], 'creator': e[4]})
            idx += 1
    just_in_colors = {}
    for i in res_tmp:
        if i['name'] in just_in_colors:
            just_in_colors[i['name']] = '2'
        else:
            just_in_colors[i['name']] = '1'
    for i in res_tmp:
        if just_in_colors[i['name']] == '2':
            i['name'] = i['name'] + ' ' + i['creator']

    for i in res_tmp:
        res.append(i)
    return {'status': 1, 'data': res}
