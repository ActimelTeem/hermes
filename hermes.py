import telebot
import sqlite3

Token = '467379466:AAFfwviUU9AHO2Sb9bs8YGssFYGmE9EhbB4'
bot = telebot.TeleBot(Token)

courier_list = {}

class DataBase:
    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()

    def login(self, log):
        self.cursor.execute("SELECT * FROM crm_couriers WHERE login = :login", {"login": log})
        return self.cursor.fetchone()

    def close(self):
        self.connection.commit()
        self.connection.close()

DB = DataBase("db.sqlite3")


class Courier:
    def __init__(self):
        self.login = ""
        self.password = ""
        self.name = ""
        self.surname = ""
        self.state = "no"
        self.login_status = False
        self._order_status = False


@bot.message_handler(commands=['start'])
def login(message):    #/login
    if message.chat.id not in courier_list:
        newCourier = Courier()
        newCourier.state = "login"
        courier_list[message.chat.id] = newCourier
        bot.send_message(message.chat.id, "Логин: ")

@bot.message_handler(content_types = ['text'])
def check_answer(message):
    if courier_list[message.chat.id].state == "password":
        print(message.text)
        # DB.login(message.text)
        courier_list[message.chat.id].login_status = True

        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row("/get_order")
        keyboard.row("/exit")
        bot.send_message(message.chat.id, "Вы были авторизованы как {}".format(courier_list[message.chat.id].login), reply_markup=keyboard)

    if courier_list[message.chat.id].state == "login":
        print(message.text)
        #DB.login(message.text)
        courier_list[message.chat.id].state = "password"
        bot.send_message(message.chat.id, "Пароль: ")


"""@bot.message_handler(commands=['exit'])
def logout(self):   #/exit
    self._login_status = False

@bot.message_handler(commands = ['get_order'])
def get_new_order(self):    #/get_order
    pass

@bot.message_handler(commands = ['order_info'])
def get_order_info():
    pass

@bot.message_handler(commands = ['complete'])
def complete_order(self):   #/complete
    pass

@bot.message_handler(commands = ['cancel'])
def cancel_order(self): #/cancel <message>
    pass
"""

bot.polling(none_stop = True, interval = 0)