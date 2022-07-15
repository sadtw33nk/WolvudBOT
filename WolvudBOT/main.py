
# ! WolvudBOT
# ? Made by @Tw33nk (telegram)

import datetime
from json import load
import telebot
from telebot import types
import sqlite3
from tabulate import tabulate
from functions import *

token = '5555649833:AAE-8SEK414LZg6Vj7cvl_2q2VUYbKCjTak' # ? Токен бота, взять у @BotFather (telegram)
Wolvud = telebot.TeleBot(token) # ? Инициализация бота

images = { # ? Массив с картинками
    'welcome': 'https://sun9-88.userapi.com/impf/gqXIDyISfNHn18eNfFlNU7q5PeN_5tzHc5nXrA/BvSD00y3nEM.jpg?size=1280x512&quality=96&sign=674c6ff633a20f921115517b087b31d1&type=album'
}

conn = sqlite3.connect('db.db', check_same_thread=False)
cursor = conn.cursor()

def ProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Генерация прогресс бара в текстовом формате
    """

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    
    return f'\r{prefix}|{bar}| {percent}% {suffix}'

@Wolvud.message_handler(commands=['start'], func=lambda message: message.chat.type == 'private')
def start_message(message):
    """
    Вывод стартового сообщения в приватном чате
    """

    gen_message = ( # ? Генерация сообщения
        "Привет, *@{0}*\n"
        "Меня зовут Wolvud, и я буду твоим помощником в модерации группы!\n"
        "Чтобы начать, добавь меня в группу."
    ).format(
        message.from_user.username
    )

    Wolvud.send_message(message.chat.id, gen_message, parse_mode="markdown")

@Wolvud.message_handler(commands=['me'], func=lambda message: message.chat.type != 'private')
def send_profile_me(message):
    """
    Вывод информации о участнике, который вызвал команду
    """

    cursor.execute('SELECT messages, level FROM users WHERE user_id = {0};'.format(message.from_user.id))
    load_profile = cursor.fetchone()

    cursor.execute('SELECT achiev FROM achievements WHERE user_id = {0} AND group_id = {1};'.format(message.from_user.id, message.chat.id))
    load_achievements = cursor.fetchall()

    l = 100
    ost = int(load_profile[0] % 100)
    progress = "\n" + ProgressBar(ost, l, length = 12) + "\n\n"

    achievements = []
    for achievement in load_achievements:
        achiev = [achievement[0]]
        achievements.append(achiev)

    if load_profile:
        
        gen_message = "Информация о @{0}\n`".format(message.from_user.username) + tabulate([
                [load_profile[0], get_level_member(load_profile[0])]
            ], headers=['Messages', 'Level'], tablefmt='pretty') + progress + tabulate(
                achievements, headers=['Achievements'], tablefmt='pretty') + "`"

        Wolvud.reply_to(message, gen_message, parse_mode="markdown")

@Wolvud.message_handler(commands=['profile'], func=lambda message: message.chat.type != 'private' and message.reply_to_message)
def send_profile(message):
    """
    Вывод информации о участнике, сообщение которого переслали
    Добавление кнопок управления участника, если участник вызвавший команду является создателем или администратором
    """

    cursor.execute('SELECT messages, level FROM users WHERE user_id = {0};'.format(message.reply_to_message.from_user.id))
    load_profile = cursor.fetchone()
    
    cursor.execute('SELECT achiev FROM achievements WHERE user_id = {0} AND group_id = {1};'.format(message.reply_to_message.from_user.id, message.chat.id))
    load_achievements = cursor.fetchall()

    l = 100
    ost = int(load_profile[0] % 100)
    progress = "\n" + ProgressBar(ost, l, length = 12) + "\n\n"

    achievements = []
    for achievement in load_achievements:
        achiev = [achievement[0]]
        achievements.append(achiev)
    
    if load_profile:
        gen_message = "Информация о @{0}\n`".format(message.reply_to_message.from_user.username) + tabulate([
                [load_profile[0], get_level_member(load_profile[0])]
            ], headers=['Messages', 'Level'], tablefmt='pretty')  + progress + tabulate(
                achievements, headers=['Achievements'], tablefmt='pretty') + "`"

        get_sender = Wolvud.get_chat_member(message.chat.id, message.from_user.id)
        if get_sender.status == 'creator' or get_sender.status == 'administrator':
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            button_mute = types.InlineKeyboardButton("Mute", callback_data='mute' + str(message.reply_to_message.from_user.id))
            button_kick = types.InlineKeyboardButton("Kick", callback_data='kick' + str(message.reply_to_message.from_user.id))
            keyboard.add(button_mute, button_kick)

            Wolvud.send_message(message.chat.id, gen_message, parse_mode="markdown", reply_markup=keyboard)
        else:
            Wolvud.send_message(message.chat.id, gen_message, parse_mode="markdown")

@Wolvud.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """
    CallBack ответы на нажатия кнопок
    Проверка на то, что участник, который нажал на кнопку является создателем или администратором группы
    """
    if call.message:
        get_sender = Wolvud.get_chat_member(call.message.chat.id, call.from_user.id)
        get_reply_user = Wolvud.get_chat_member(call.message.chat.id, call.data[4:])

        if get_sender.status == 'creator' or get_sender.status == 'administrator':
            if call.data[:4] == "mute":
                Wolvud.restrict_chat_member(call.message.chat.id, call.data[4:], until_date=datetime.datetime.now().timestamp()+86400)
                Wolvud.send_message(call.message.chat.id, "@{0} был замучен на 1 день".format(get_reply_user.user.username))
            
            if call.data[:4] == "kick":
                Wolvud.kick_chat_member(call.message.chat.id, call.data[4:])
                Wolvud.send_message(call.message.chat.id, "@{0} был замучен на 1 день".format(get_reply_user.user.username))
        
            Wolvud.answer_callback_query(call.id, text="Действие выполнено.", show_alert=True)
        else:
            Wolvud.answer_callback_query(call.id, text="Вам не хватает прав.", show_alert=True)

@Wolvud.message_handler(commands=['mute'], func=lambda message: message.chat.type != 'private' and message.reply_to_message)
def mute_user(message):
    """
    Команда /mute
    Замутить участника из группы, сообщение которого переслали
    Проверка, что участник, который вызвал команду является создателем или администратором группы 
    """

    get_sender = Wolvud.get_chat_member(message.chat.id, message.from_user.id)

    if get_sender.status == 'creator' or get_sender.status == 'administrator':
        get_options = message.text.split()
        if get_options[2] == 'm':
            time = int(get_options[1]) * 60
            reply_message = ' замучен на `{0}` минут'.format(int(time / 60))
        elif get_options[2] == 'h':
            time = int(get_options[1]) * 3600
            reply_message = ' замучен на `{0}` часов'.format(int(time / 3600)) 
        elif get_options[2] == 'd':
            time = int(get_options[1]) * 86400
            reply_message = ' замучен на `{0}` дней'.format(int(time / 86400))

        Wolvud.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=datetime.datetime.now().timestamp() + time)
        Wolvud.send_message(message.chat.id,
        "@{0} был".format(message.reply_to_message.from_user.username) + reply_message,
        parse_mode="markdown")

@Wolvud.message_handler(commands=['kick'], func=lambda message: message.chat.type != 'private' and message.reply_to_message)
def kick_user(message):
    """
    Команда /kick
    Исключить участника из группы, сообщение которого переслали
    Проверка, что участник, который вызвал команду является создателем или администратором группы 
    """
    get_sender = Wolvud.get_chat_member(message.chat.id, message.from_user.id)

    if get_sender.status == 'creator' or get_sender.status == 'administrator':
        Wolvud.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        Wolvud.send_message(message.chat.id,
        "@{0} был кикнут".format(message.reply_to_message.from_user.username),
        parse_mode="markdown")

@Wolvud.message_handler(commands=['info'], func=lambda message: message.chat.type != 'private')
def send_info_chat(message):
    """
    Команда /info
    Вывод информации о группе
    """
    cursor.execute('SELECT is_premium, level, messages FROM groups WHERE group_id = {0};'.format(message.chat.id))
    load_group = cursor.fetchone()
    
    if load_group:
        gen_message = "Информация о канале {0}\n`".format(message.chat.title) + tabulate([
                [load_group[0], get_level_group(load_group[2]), load_group[2]]
            ], headers=['Premium', 'Level', 'Messages'], tablefmt='pretty') + "`"

        Wolvud.send_photo(message.chat.id, images['welcome'], caption=gen_message, parse_mode="markdown")

@Wolvud.message_handler(commands=['help'], func=lambda message: message.chat.type != 'private')
def send_info_chat(message):
    """
    Команда /help
    Вывод всех команд
    """

    gen_message = (
        "/start - Активация группы в боте (А)\n"
        "/settings - Настройки бота (A)\n"
        "/me - Информация о участнике, который написал\n"
        "/profile - Информация о участнике, на чье сообщение ответили\n"
        "/kick - Удалить участника из группы (A)\n"
        "/mute - Мут участника (A)\nПример: /mute 1 d\nПервый аргумент количество времени\nВторой на какую единицу времени замутить\nd - день, h - час, m - минута\n"
        "/info - Информация о группе\n"
        "/help - Команды бота\n"
    )

    Wolvud.send_message(message.chat.id, gen_message, parse_mode="markdown")

@Wolvud.message_handler(commands=['change'], func=lambda message: message.chat.type != 'private')
def send_info_chat(message):
    """
    Команда /change
    Вывод шанса на что-то
    """

    text = message.text[8:]
    rand = randint(0, 100)

    gen_message = "Шанс на то, что {0}, равно {1}%".format(text, rand)

    Wolvud.send_message(message.chat.id, gen_message, parse_mode="markdown")

@Wolvud.message_handler(func=lambda message: True)
def check_message_in_group(message):
    """
    Проверка каждого сообщения
    Проверка что группа есть в базе данных
    Проверка что участник есть в базе данных
    Выдача достижений
    """

    cursor.execute('SELECT messages, spam_detect, lastdate FROM users WHERE user_id = {0};'.format(message.from_user.id))
    load_user = cursor.fetchone()

    cursor.execute('SELECT messages FROM groups WHERE group_id = {0};'.format(message.chat.id))
    load_group = cursor.fetchone()

    if not load_user:
        cursor.execute('INSERT INTO users (user_id, username, group_id, level, lastdate) VALUES (?, ?, ?, ?, ?)',
            (message.from_user.id, message.from_user.username, message.chat.id, 0, int(datetime.datetime.now().timestamp())))
        
        conn.commit()

        gen_message = ( # ? Генерация сообщения
            "*Привет, @{0}!*\n"
            "Ты был добавлен в список людей, которых надо отстрапонить!\n"
        ).format(
            message.from_user.username
        )

        Wolvud.send_message(message.chat.id, gen_message, parse_mode="markdown")
    else:
        date_now = datetime.datetime.now().timestamp()
        lastdate_user = int(load_user[2])
        if int(load_user[1]) > 3:
            try:
                Wolvud.restrict_chat_member(message.chat.id, message.from_user.id, until_date=datetime.datetime.now().timestamp() + 300)
            except:
                pass
            Wolvud.send_message(message.chat.id, "@{0} был замучен за подозрение в спаме на 5 минут".format(message.from_user.username))
            cursor.execute('UPDATE users SET spam_detect="0" WHERE user_id="{0}";'
            .format(
                message.from_user.id
            ))

        if date_now - lastdate_user < 2:
            cursor.execute('UPDATE users SET spam_detect="{0}" WHERE user_id="{1}";'
            .format(
                load_user[1] + 1,
                message.from_user.id
            ))

        cursor.execute('UPDATE users SET lastdate="{0}", messages="{1}" WHERE user_id="{2}";'
        .format(
            int(datetime.datetime.now().timestamp()),
            load_user[0] + 1,
            message.from_user.id
        ))

        achievement = get_achievement()
        if achievement != 'none':
            cursor.execute('INSERT INTO achievements (achiev, user_id, group_id) VALUES (?, ?, ?)',
            (achievement, message.from_user.id, message.chat.id))

            Wolvud.send_message(message.chat.id, "@{0} получил достижение `{1}`".format(message.from_user.username, achievement), parse_mode='markdown')

        conn.commit()

    if load_group:
        cursor.execute('UPDATE groups SET messages="{0}" WHERE group_id="{1}";'
        .format(
            load_group[0] + 1,
            message.chat.id
        ))

        conn.commit()
    else:
        cursor.execute('INSERT INTO groups (group_id, is_premium, level) VALUES (?, ?, ?)',
            (message.chat.id, 'false', 0))
        
        conn.commit()

        gen_message_chat_add = ( # ? Генерация сообщения
            "Группа была добавлена в базу данных!"
        )

        gen_message = ( # ? Генерация сообщения
            "*Привет, народ!*\n"
            "Напишите /help, чтобы посмотреть мои команды\n"
            "Команды помеченные (A) доступны только админам!"
        )   

        Wolvud.send_photo(message.chat.id, images['welcome'], caption=gen_message, parse_mode="markdown")
        Wolvud.send_message(message.chat.id, gen_message_chat_add, parse_mode="markdown")

Wolvud.infinity_polling() # ? Бесконечный полинг