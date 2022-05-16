import telebot
import datetime
import config
import sqlite3

name = None
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['help'])
def help_user(message):
    bot.send_message(
        message.chat.id,
        f'Вы можете выбрать необходимый раздел в меню внизу окна.\n\n'
        f'В каждом разделе вы сможете в меню выбрать предложенный вариант коммуникации\n\n'
        f'В случае, когда Вам будет необходимо просто связаться со мной, выберите кнопку \'Связаться\'\n'
        f'она есть в любом из разделов\n\n'
        f'В разделе \'Оставить заявку\' я запрошу у Вас Ваш контактный номер телефона. '
        f'Эти данные нужны, чтобы связаться с Вами, они не будут переданы третьим лицам', parse_mode='html'
    )
    send_kb_main(message)


@bot.message_handler(commands=['start'])
def welcome_user(message):
    bot.send_message(
        message.chat.id,
        f'Привет, <b>{message.from_user.first_name}</b> !\n\n'
        f'Меня зовут Руслан Слепухин,\n\n'
        f'Этот бот сможет помочь:\n'
        f'- получить информацию об услугах,\n '
        f'- о том как это работает,\n'
        f'- сориентировать в стоимости\n'
        f'- и найти подходящее время для наших встреч\n\n'
        f'/start - перезапустить бот\n'
        f'/help - получить помощь', parse_mode='html'
    )

    send_kb_main(message)
    send_to_bd(
        'add_user',
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
        message.chat.id
    )
    print(message.text)
    info_activity(message, f'user clicks {message.text}')


def info_activity(message, message_to_me=None, phone=None):

    bot.send_message(
        137336064,
        f"{message_to_me}\n\n"
        f"customer <b>@{message.from_user.username}</b>\n"
        f"chat_id: <b>{message.chat.id}</b>\n"
        f"first name: <b>{message.from_user.first_name}</b>\n"
        f"last name: <b>{message.from_user.last_name}</b>\n"
        f"phone: <b>{phone}</b>\n"
        f"time: <b>{datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}</b>\n\n"
        f"contact with customer @{message.from_user.username}",
        parse_mode='html'
    )


def send_kb_main(message, text="Выберите интересующую вас тему"):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    it1 = telebot.types.KeyboardButton('Аранжировка')
    it2 = telebot.types.KeyboardButton('Мероприятие')
    it3 = telebot.types.KeyboardButton('Занятие')
    kb.add(it1, it2, it3)
    bot.send_message(message.chat.id, text, reply_markup=kb)


# глобальная переменная name содержит данные в каком разделе находится пользователь для вызова предыдущего меню


@bot.message_handler(content_types=['text'])
def some_text(message):
    global name


    if message.text == 'Аранжировка':
        send_arragement_inline(message)
        name = message

    elif message.text == 'Мероприятие':
        send_ivent_inline(message)
        name = message

    elif message.text == "Занятие":
        send_work_inline(message)
        name = message

    elif message.text == "Не отправлять номер":
        bot.send_message(message.chat.id, 'Без номера телефона я не могу гарантировать, что свяжусь с Вами')
        send_to_bd(
            'add_application',
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            message.chat.id,
            datetime.datetime.now(),
            None,
            True,
            name.text
        )
        info_activity(message, f"Поступила заявка из раздела '{name.text}'")
        send_kb_main(name)

    else:
        bot.send_message(
            message.chat.id,
            'Наверняка Вы пишете что-то важное, но этот бот не обучен принимать текст,'
            'воспользуйтесь кнопками, пожалуйста')

# меню с переданным текстом и кнопкой назад.
# использует глобальную переменную name, в которой записаны данные в каком разделе меню находится пользователь
# если передается tag=False, то используется bot.send_message,
# если передается tag=True, используется bot.edit_message_text


def back_menu(message, message_to_user, tag):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('<<< назад в меню', callback_data='back_to_menu'))
    match tag:
        case False:
            bot.send_message(message.chat.id, message_to_user, reply_markup=markup)
        case True:
            bot.edit_message_text(message_to_user, message.chat.id, message.message_id, reply_markup=markup)


def send_arragement_inline(message):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    it1 = telebot.types.InlineKeyboardButton('Как это происходит', callback_data='1-1')
    it2 = telebot.types.InlineKeyboardButton('Оставить заявку', callback_data='1-2')
    it3 = telebot.types.InlineKeyboardButton('Отправить референс', callback_data='1-3')
    it4 = telebot.types.InlineKeyboardButton('Примеры работ', callback_data='1-4')
    it5 = telebot.types.InlineKeyboardButton('Связаться', callback_data='1-5')
    it6 = telebot.types.InlineKeyboardButton('Стоимость', callback_data='1-6')
    kb.add(it1, it2, it3, it4, it5, it6)
    bot.send_message(message.chat.id, f'Меню <{message.text}>', reply_markup=kb)


def send_ivent_inline(message):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    it1 = telebot.types.InlineKeyboardButton('Посмотреть промо', callback_data='2-1')
    it2 = telebot.types.InlineKeyboardButton('Свободные даты', callback_data='2-2')
    it3 = telebot.types.InlineKeyboardButton('Оставить заявку', callback_data='2-3')
    it4 = telebot.types.InlineKeyboardButton('Связаться', callback_data='2-4')
    kb.add(it1, it2, it3, it4)
    bot.send_message(message.chat.id, f'Меню <{message.text}>', reply_markup=kb)


def send_work_inline(message):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    it1 = telebot.types.InlineKeyboardButton('Информация', callback_data='3-1')
    it2 = telebot.types.InlineKeyboardButton('Свободные даты/время', callback_data='2-2')
    it3 = telebot.types.InlineKeyboardButton('Оставить заявку', callback_data='2-3')
    it4 = telebot.types.InlineKeyboardButton('Связаться', callback_data='2-4')
    kb.add(it1, it2, it3, it4)
    bot.send_message(message.chat.id, f'Меню <{message.text}>', reply_markup=kb)


"""
В этом блоке функций принимаются фото, аудио, документы, голосовые сообщения от пользователя,
сохраняются на жестком диске компьютера,
а также отправляется мне в чат вместе сообщением, содержащем данные отправителя и тему, в которой находлся пользователь
"""


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_info.file_path.split('/')[1]
    bot.send_photo(137336064, downloaded_file, caption=filename)


@bot.message_handler(content_types=['audio'])
def get_audio(message):
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_info.file_path.split('/')[1]
    bot.send_audio(137336064, downloaded_file, caption=filename)
    info_activity(message, f'Получен аудиофайл {filename}')


@bot.message_handler(content_types=['voice'])
def get_voice(message):

    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_info.file_path.split('/')[1]
    bot.send_voice(137336064, downloaded_file, caption=filename)
    info_activity(message, f'Получено голосовое сообщение {filename}')


@bot.message_handler(content_types=['document'])
def get_documents(message):

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_info.file_path.split('/')[1]
    bot.send_document(137336064, downloaded_file, caption=filename)
    info_activity(message, f'Получен документ {filename}')


"""
В этом блоке запрос на отправку номера пользователя и процедура, которая его отлавливает
"""


def get_number_phone(message, mess_id):

    bot.delete_message(message.chat.id, mess_id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton('Отправить номер телефона',  request_contact=True)
    item2 = telebot.types.KeyboardButton('Не отправлять номер')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Отправьте кнопкой Ваш номер телефона для связи', reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        send_to_me = f"Поступила заявка из раздела '{name.text}'"

        send_to_user = f'Заявка принята,\nя свяжусь с Вами в ближайшее время'
        info_activity(message, send_to_me, message.contact.phone_number)
        back_menu(message, send_to_user, False)
        send_kb_main(message)

        # вносим телефон и факт запроса в БД по метке 'add_phone'
        print(name.text)
        send_to_bd(
            'add_phone',
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            message.chat.id,
            datetime.datetime.now(),
            message.contact.phone_number,
            True,
            name.text
        )


"""
Обработчик callback'ов
"""


@bot.callback_query_handler(func=lambda call: True)
def send_inline(call):
    try:
        if call.message:
            text = call.data
            if text == '1-1':  # как это происходит
                message_to_user = f'Как это происходит?\n\n'\
                                  f'1 - Вы присылаете референсы, когда есть понимание как должно звучать\n'\
                                  f'2 - Мы с Вами определяем нужные тональность и ритм\n'\
                                  f'3 - Я присылаю Вам пилот, мы обсуждаем с Вами всё ли так ' \
                                  f'и какие коррективы нужны\n' \
                                  f'(в том числе ключевые акценты, отбивки, бриджи)\n'\
                                  f'4 - По итогу  присылаю Вам сведенный готовый продукт в форматах mp3 и wav\n'\
                                  f'5 - Оплата по факту\n\n' \
                                  f'Сроки по проекту от 2 до 7 дней\n'\
                                  f'Если не двигаемся дальше п3 несколько раз, можем прекратить сотрудничество ' \
                                  f'по согласию сторон без оплаты'
                back_menu(call.message, message_to_user, True)
            elif text == '1-2' or text == '2-3' or text == '3-3':  # оставить заявку
                mess_id = call.message.message_id
                get_number_phone(call.message, mess_id)

            elif text == '1-3':  # отправить референс
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton('<<< назад в меню', callback_data='back_to_menu'))
                bot.edit_message_text(f'Вы можете в любое время отправить референс как\nголосовое сообщение, '
                                      f'аудио, фото или документ',
                                      call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=markup
                                      )
            elif text == '1-4':  # примеры работ
                markup = telebot.types.InlineKeyboardMarkup()
                item1 = telebot.types.InlineKeyboardButton(
                    'YouTube',
                    url='https://youtube.com/playlist?list=PLismiPYDjKbYuLpngEC-QGiYI66n40p1M')
                item2 = telebot.types.InlineKeyboardButton('<<< назад в меню', callback_data='back_to_menu')
                markup.add(item1, item2)
                bot.edit_message_text(
                    'Примеры работ',
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )

            elif text == '1-5' or text == '2-4' or text == '3-4':  # связаться
                back_menu(call.message, f'Вы можете со мной связаться по номеру\n'
                                        f'+375 29 644-96-90 Руслан\n'
                                        f'а также в Viber и Telegram',
                                        True
                          )

            elif text == '1-6':
                message_to_user = f'Стартовая стоимость 100$\n\n'\
                                  f'Стоимость меняется в любую сторону после обсуждения ТЗ\n'\
                                  f'В стоимость входит:\n'\
                                  f'- Создание аранжировки\n'\
                                  f'- Сведение треков\n'\
                                  f'- Мастеринг\n'\
                                  f'Сведение с вокалом - отдельная услуга'
                back_menu(call.message, message_to_user, True)

            elif text == '2-1':
                markup = telebot.types.InlineKeyboardMarkup()
                item1 = telebot.types.InlineKeyboardButton(
                    'Сайт Iris loungeband',
                    url='https://irislband.tilda.ws/'
                )
                item2 = telebot.types.InlineKeyboardButton('<<< назад в меню', callback_data='back_to_menu')
                markup.add(item1, item2)
                bot.edit_message_text(
                    'Промо Iris loungeband',
                    call.message.chat.id, call.message.message_id,
                    reply_markup=markup
                )

            elif text == '2-2' or text == '3-4':
                markup = telebot.types.InlineKeyboardMarkup()
                item1 = telebot.types.InlineKeyboardButton(
                    'google calendar',
                    url='https://calendar.google.com/calendar/u/0/embed?src=iris.loungeband@gmail.com&ctz=Europe/Minsk'
                )
                item2 = telebot.types.InlineKeyboardButton(
                    '<<< назад в меню',
                    callback_data='back_to_menu'
                )
                markup.add(item1, item2)
                bot.edit_message_text('Свободное время', call.message.chat.id, call.message.message_id,
                                      reply_markup=markup)

            elif text == '3-1':
                message_to_user = f'- Выездные занятия на дому у клиентов\n' \
                                  f'- Возраст от 6 лет\n' \
                                  f'- 1-2 занятия в неделю\n' \
                                  f'- Программа музыкальной школы +\n' \
                                  f'     - импровизация\n' \
                                  f'     - современные песни\n' \
                                  f'     - произведения современных композиторов'
                back_menu(call.message, message_to_user, True)

            elif text == 'back_to_menu':
                some_text(name)

    except Exception as e:
        print('Callback error', e)


"""
Функция создает базу данных, записывает пользователей, а также добавляет телефон и запрос с датой, если он поступил
по тегу add_or_ins со значениями:
add_user - добавить юзера
add_phone - вставить в запись номер телефона, когда пользователь его сообщит
add_application - вставить в запись наличие запроса на услугу с датой запроса
"""


def send_to_bd(
        add_or_ins,
        username,
        first_name,
        last_name,
        chat_id,
        start_date=datetime.datetime.now(),
        phone_number=None,
        application=False,
        chapter=None,
        application_date=None):

    con = sqlite3.connect(config.BD)
    cur = con.cursor()

    table = """CREATE TABLE IF NOT EXISTS users (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        username         VARCHAR(25),
        first_name       VARCHAR (25),
        last_name        VARCHAR(25),
        chat_id          INT,
        start_date       DATETIME,
        phone_number     VARCHAR(15),
        application      BOOLEAN,
        chapter          VARCHAR(20),
        application_date DATETIME);
    """

    cur.execute(table)
    con.commit()

    match add_or_ins:
        case 'add_user':
            sql = f"SELECT * FROM users WHERE username = '{username}'"
            with con:
                is_exists = (cur.execute(sql).fetchall())

            if not is_exists:
                sql = f"INSERT INTO users (" \
                      f"username," \
                      f"first_name," \
                      f"last_name," \
                      f"chat_id," \
                      f"start_date)" \
                      f"VALUES ('" \
                      f"{username}'," \
                      f"'{first_name}'," \
                      f"'{last_name}'," \
                      f"'{chat_id}'," \
                      f"'{start_date}')"
                with con:
                    cur.execute(sql)

        case 'add_phone':

            sql = f"UPDATE users SET phone_number = " \
                  f"'{phone_number}', " \
                  f"application = 'TRUE'," \
                  f"chapter = '{chapter}'," \
                  f"application_date = '{datetime.datetime.now()}' " \
                  f"WHERE username = '{username}'"
            with con:
                cur.execute(sql)

        case 'add_application':

            sql = f"UPDATE users SET " \
                  f"application = 'TRUE'," \
                  f"chapter = '{chapter}'," \
                  f"application_date = '{datetime.datetime.now()}' " \
                  f"WHERE username = '{username}'"
            with con:
                cur.execute(sql)


if __name__ == '__main__':
    print(f'bot starts on {datetime.datetime.now()}')
    bot.polling()
