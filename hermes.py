import telebot

TOKEN = '467379466:AAFfwviUU9AHO2Sb9bs8YGssFYGmE9EhbB4'
bot = telebot.TeleBot(TOKEN)

class Hermes:
    def __init__(self):
        self._login_status = False

    '''не первоочередная задача
    @bot.message_handler(commands=['start'])
    def login(self):    #/start
        self._login_status = True

    @bot.message_handler(commands=['exit'])
    def logout(self):   #/exit
        self._login_status = False
    '''

    @bot.message_handler(commands=['get_order'])
    def get_new_order(self):    #/get_order
        pass

    @bot.message_handler(commands=['complete'])
    def complete_order(self):   #/complete
        pass

    @bot.message_handler(commands=['cancel'])
    def cancel_order(self): #/cancel <message>
        pass