import datetime

from user.models import UserModels, UserMessageModels
from telebot import types, telebot

from calendar_pytba import Calendar
from calendar_pytba.utils.types import CalendarLanguage, CallBackData
from calendar_pytba.utils.handler import callback_handler




TOKEN = '6596766576:AAGmGcM04SVrBQLzLalos1Id-MEqsv_rEnM'
bot = telebot.TeleBot(TOKEN, threaded=False)




"""
    START CALENDAR AND TIMESLOTS
    *the calendar should be placed before 'callback_query_handler'
"""

callback_handler(bot, CalendarLanguage.RU)
@bot.callback_query_handler(
    func=lambda call: call.data.startswith(CallBackData.SELECTED_DATE)
)
def selected_date_callback(call: types.CallbackQuery) -> None:
    date_as_string = call.data.split(":")[1]
    date = datetime.datetime.strptime(date_as_string, "%Y-%m-%d")
    # Do whatever you want with the date
    date = date.strftime('%d.%m.%Y')
    #text = f"Дата: {date}"
    #bot.send_message(call.message.chat.id, call.data)

    #for some reason 'register_next_step_handler' doesn't work
    show_timeslots(message=call.message, date=date)


def show_timeslots(message: telebot.types.Message, date):
    btn_list = []
    timeslots = [
        '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
        '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
    ]

    for time in timeslots:
        btn_list.append(
            types.InlineKeyboardButton(time, callback_data=f"personal-data_{time}_{date}")
        )

    markup = types.InlineKeyboardMarkup(row_width=4)
    markup.add(*btn_list)

    text = 'Выберете время:'
    bot.send_message(message.chat.id, text, reply_markup=markup)

"""
    END CALENDAR AND TIMESLOTS
"""


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    text = """
Я даю свое согласие 000 «ИТ-Регул» на обработку моих персональных данных. Согласие касается фамилии, имени, номера сотового телефона, а также сведений использования данного бота.

Я даю согласие на хранение всех вышеназванных данных на электронных носителях. Также данным согласием я разрешаю сбор моих персональных данных, их хранение, систематизацию, обновление, использование (в тч. передачу третьим лицам для обмена информацией), а также осуществление любых иных действий. предусмотренных действующим законом Российской Федерации.

До моего сведения доведено, что ООО «ИТ-Регул» гарантирует обработку моих персональных данных в соответствии с действующим законодательством Российской Федерации. Срок действия данного согласия не ограничен Согласие может быть отозвано, в любой момент по моему письменному заявлению Подтверждаю, что, давая согласие, я действую без принуждения, по собственной воле и в своих интересах.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Принять', callback_data='accept'))

    bot.send_message(message.chat.id, text, reply_markup=markup)


"""
    START CALLBACK
"""

@bot.callback_query_handler(func=lambda call:True)
def callback_data(call: telebot.types.CallbackQuery):
    def _start_registration():
        text = 'Введите ваш номер телефона:'
        bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(call.message, user_firstname)

    if call.data == 'accept':
        check_user = UserModels.objects.get(external_id=call.from_user.id)
        if check_user:
            text = f"{check_user.firstname} {check_user.lastname}, вы уже зарегистрированы!"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Изменить данные', callback_data='update'))
            markup.add(types.InlineKeyboardButton('Продолжить', callback_data='show_menu'))
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
        else:
            _start_registration()

    if call.data == 'update':
        _start_registration()

    if call.data == 'show_menu':
        menu(message=call.message)

    if 'personal-data' in call.data:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Подтверждаю', callback_data='show_menu'))
        try:
            user_id = UserModels.objects.get(external_id=call.from_user.id)
            user_id = user_id.pk
            last_message = UserMessageModels.objects.all().filter(user_id=user_id).last()
            last_message = last_message.message
            personal_data, time, date = call.data.split('_')
            text = f"Подтвердите запись: \nУслуга: {last_message} \nДата: {date} \nВремя: {time} \nСтоимость: xxxx p"
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
        except:
            text = 'Ошибка! Попробуйте заново.'
            bot.send_message(call.message.chat.id, text)
            return
        
"""
    END CALLBACK
"""


"""
    START USER REGISTRATION
"""

def user_firstname(message: telebot.types.Message):
    data = {}
    data['phone'] = message.text.replace('+', '').replace(' ', '')
    try:
        data['phone'] = int(data['phone'])
    except ValueError as e:
        text = 'Введен неправильный номер телефона. Попробуйте заново.'
        bot.send_message(message.chat.id, text)
        return

    text = 'Введите имя:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, user_lastname, data)


def user_lastname(message: telebot.types.Message, data):
    data['firstname'] = message.text.strip()

    text = 'Введите фамилию:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, user_save, data)


def user_save(message: telebot.types.Message, data):
    data['lastname'] = message.text.strip()
    data['external_id'] = message.from_user.id
    text = ''

    check_user = UserModels.objects.get(external_id=message.from_user.id)
    if check_user:
        try:
            check_user.firstname = data['firstname']
            check_user.lastname = data['lastname']
            check_user.phone = data['phone']
            #check_user.external_id = data['external_id']
            check_user.save()
        except Exception as e:
            text = 'Ошибка! Попробуйте заново'
            bot.send_message(message.chat.id, text)
            return

        text = f"{data['firstname']} {data['lastname']}, данные обновлены!"

    else:
        try:
            user = UserModels()
            user.firstname = data['firstname']
            user.lastname = data['lastname']
            user.phone = data['phone']
            user.external_id = data['external_id']
            user.save()
        except Exception as e:
            text = 'Ошибка! Попробуйте заново'
            bot.send_message(message.chat.id, text)
            return
        text = f"{data['firstname']} {data['lastname']}, вы были зарегистрированы!"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Изменить данные', callback_data='update'))
    markup.add(types.InlineKeyboardButton('Продолжить', callback_data='show_menu'))
    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, menu)

"""
    END USER REGISTRATION
"""


"""
    START MENU
"""

@bot.message_handler(commands=['menu'])
def menu(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Услуга 1')
    item2 = types.KeyboardButton('Услуга 2')
    markup.row(item1, item2)
    text = 'Выберете услугу:'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(content_types=["text"])
def any_msg(message: telebot.types.Message):
    try:
        msg = UserMessageModels()
        msg.user_id = UserModels.objects.get(external_id=message.from_user.id)
        msg.message = message.text
        msg.save()
    except:
        text = 'Произошла ошибка! Повторите попытку'
        bot.send_message(message.chat.id, text, reply_markup=markup)

    def _show_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Услуга 1')
        item2 = types.KeyboardButton('Услуга 2')
        markup.row(item1, item2)

        text = 'Выберете услугу:'
        bot.send_message(message.chat.id, text, reply_markup=markup)

    def _show_calendar():
        calendar = Calendar(CalendarLanguage.RU)
        markup = calendar.get_calendar()
        text = "Выберете дату:"
        bot.send_message(message.chat.id, text, reply_markup=markup)

    if message.chat.type == 'private':   
        if message.text == 'Услуга 1':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Услуга 1.1')
            item2 = types.KeyboardButton('Услуга 1.2')
            item3 = types.KeyboardButton('Вернуться')
            markup.row(item1, item2).add(item3)

            text = 'Выберете услугу:'
            bot.send_message(message.chat.id, text, reply_markup=markup)
        elif message.text == 'Услуга 2':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Услуга 2.1')
            item2 = types.KeyboardButton('Услуга 2.2')
            item3 = types.KeyboardButton('Вернуться')
            markup.row(item1, item2).add(item3)

            text = 'Выберете услугу:'
            bot.send_message(message.chat.id, text, reply_markup=markup)
        elif message.text == 'Вернуться':
            _show_menu()
        elif message.text == 'Услуга 1.1':
            _show_calendar()
        elif message.text == 'Услуга 1.2':
            _show_calendar()
        elif message.text == 'Услуга 2.1':
            _show_calendar()
        elif message.text == 'Услуга 2.2':
            _show_calendar()

"""
    END MENU 
"""