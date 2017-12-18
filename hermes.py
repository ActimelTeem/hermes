import telebot
import sqlite3
import requests
import constants

bot = telebot.TeleBot(constants.token)

courier_list = {}

#классы
class DataBase: #класс для работы с БД
    def __init__(self, db): #инициализация БД
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()

    def login(self, log, pw):   #проверка пользовательских данных в БД при авторизации
        self.cursor.execute("SELECT * FROM crm_couriers WHERE login = :login AND password = :password", {"login": log, "password": pw})
        return self.cursor.fetchone()

    def check_order(self, courier_id):  #проверка на наличие у данного курьера заказа в БД
        self.cursor.execute("SELECT * FROM crm_order WHERE order_status_id = 3 AND order_courier_id = :courier_id", {"courier_id": courier_id})
        answer = self.cursor.fetchone()
        try:
            answer[0]
            return answer
        except TypeError:
            return False

    def get_order(self, courier_id):    #получение информации о первом доступном заказе из БД
        self.cursor.execute("SELECT * FROM crm_order WHERE order_status_id = 4")
        answer = self.cursor.fetchone()
        try:
            self.cursor.execute("UPDATE crm_order SET order_courier_id =:courier_id WHERE id = :number", {"courier_id": courier_id, "number": answer[-1]})
            self.cursor.fetchone()
            return answer
        except:
            return False

    def change_order_status(self, number, status):  #изменение статуса заказа в БД
        self.cursor.execute("UPDATE crm_order SET order_status_id = :status WHERE id = :number", {"status": status, "number": number})
        self.cursor.fetchone()

    def courier_comment(self, number, text):
        self.cursor.execute("UPDATE crm_order SET order_courier_comment = :text WHERE id = :number", {"text": text, "number": number})
        self.cursor.fetchone()

    def close(self):    #закрытие БД
        self.connection.commit()
        self.connection.close()

class Order:
    def __init__(self, result):
        self.number = result[-1]  # order_number,
        self.content = result[0]
        self.date = result[7]  # order_date,
        self.location = result[1]  # order_location,
        self.client = result[5]  # order_client,
        self.client_comment = result[4]  # order_client_comment,
        self.cost = result[8]  # order_cost,
        self.payment_status = result[6]  # payment_status
        self.courier_comment = result[3]  # order_courier_comment
        self.order_status = result[2]  # order_status,
        self.dest_date = result[11]
        self.manager = result[9]  # order_manager id,
        self.courier = result[10]  # order_courier,

    def info(self):   #получение строки с информацией о заказе
        info = "Номер: {}\nСодержимое: {}\nАдрес: {}\nКлиент: {}\nКоментарий: {}\nСтоимость: {}\nДата оформления: {}\nПлатежный статус: {}\n".format(self.number, self.content, self.location, self.client, self.client_comment, self.cost, self.date, self.payment_status)
        url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(self.location.replace(" ", "+"), constants.maps_key)
        results = requests.get(url).json()
        try:
            return info, results["results"][0]["geometry"]["location"]
        except IndexError:
            return info, False

    def complete(self):
        DB = DataBase(constants.db)
        DB.change_order_status(self.number, 2)  # изменение статуса взятого заказа на выполненный
        DB.close()

    def cancel(self, text):
        DB = DataBase(constants.db)
        DB.courier_comment(self.number, text)
        DB.change_order_status(self.number, 1)  # изменение статуса взятого заказа на отмененный
        DB.close()

class Courier:  #класс курьера
    def __init__(self): #инициализация нового курьера
        self.login = ""
        self.password = ""
        self.id = 0
        self.name = ""
        self.surname = ""
        self.state = "no"   #флаг для обратной связи с клиентом
        self.login_status = False   #авторизован-ли пользователь
        self.order_status = False   #существует-ли активный заказ

    def login_system(self): #авторизация клиента
        DB = DataBase(constants.db)
        result = DB.login(self.login, self.password)
        DB.close()
        try:
            self.id = result[0]
            self.name = result[3]
            self.surname = result[4]
            self.state = "in_system"
            self.login_status = True
            return True
        except:
            return False

    def is_order(self):
        DB = DataBase(constants.db)
        result = DB.check_order(self.id)
        if result != False:
            self.Ord = Order(result)
            self.state = "order"
            self.order_status = True
            return True
        else:
            return False

    def new_order(self):    #получение нового заказа
        if not self.is_order():
            DB = DataBase(constants.db)
            result = DB.get_order(self.id)
            if result != False:
                self.Ord = Order(result)
                DB.change_order_status(self.Ord.number, 3) #изменение статуса взятого заказа на выполняющийся
                DB.close()
                self.state = "order"
                self.order_status = True
                return True
            else:
                DB.close()
                return False


#декораторы
def is_login(func):
    def new_func(message):
        if message.chat.id in courier_list and courier_list[message.chat.id].login_status == True:
            func(message)
        else:
            keyboard = telebot.types.ReplyKeyboardMarkup()
            keyboard.row("Авторизация")
            bot.send_message(message.chat.id, "Для использования сервиса войдите в систему - /start", reply_markup=keyboard)
    return new_func


#функционал бота
@bot.message_handler(commands=['start'])
def login(message):    #/login
    if message.chat.id not in courier_list or courier_list[message.chat.id].login_status == False:
        newCourier = Courier()
        newCourier.state = "login"
        courier_list[message.chat.id] = newCourier
        bot.send_message(message.chat.id, "Логин: ")
    else:
        bot.send_message(message.chat.id, "Вы уже авторизованы")

@bot.message_handler(commands=['exit'])
def logout(message):    #/logout
    if message.chat.id in courier_list and courier_list[message.chat.id].login_status == True:
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row("Авторизация")
        bot.send_message(message.chat.id, "{} вышел из системы".format(courier_list[message.chat.id].login), reply_markup=keyboard)
        print("{} вышел из системы.".format(courier_list[message.chat.id].login))
        courier_list.pop(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Вы не авторизованы")

@bot.message_handler(commands=['get_order'])
@is_login
def get_new_order(message):
    if courier_list[message.chat.id].order_status == True:
        bot.send_message(message.chat.id, "Уже есть активный заказ:")
        info = courier_list[message.chat.id].Ord.info()
        bot.send_message(message.chat.id, info)
    else:
        if courier_list[message.chat.id].new_order():
            keyboard = telebot.types.ReplyKeyboardMarkup()
            keyboard.row("Подтверждение", "Отмена")
            bot.send_message(message.chat.id, "Был получен заказ:", reply_markup=keyboard)
            info, locations = courier_list[message.chat.id].Ord.info()
            bot.send_message(message.chat.id, info)
            if locations != False:
                bot.send_location(message.chat.id, locations["lat"], locations["lng"])
            courier_list[message.chat.id].state = "request"
            print("{} получил заказ №{}.".format(courier_list[message.chat.id].login, courier_list[message.chat.id].Ord.number))
        else:
            bot.send_message(message.chat.id, "Нет доступных заказов")

@bot.message_handler(commands=['complete'])
@is_login
def complete_order(message):
    if courier_list[message.chat.id].order_status == True:
        courier_list[message.chat.id].Ord.complete()
        courier_list[message.chat.id].order_status = False
        courier_list[message.chat.id].state = "in_system"
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row("Получить заказ")
        keyboard.row("Выход")
        bot.send_message(message.chat.id, "Заказ №{} выполнен".format(courier_list[message.chat.id].Ord.number), reply_markup=keyboard)
        print("{} выполнил заказ №{}.".format(courier_list[message.chat.id].login, courier_list[message.chat.id].Ord.number))
    else:
        bot.send_message(message.chat.id, "Нет активных заказов")

@bot.message_handler(commands=['cancel'])
@is_login
def cancel_order(message):
    if courier_list[message.chat.id].order_status == True:
        print("{} отменил заказ №{}.".format(courier_list[message.chat.id].login, courier_list[message.chat.id].Ord.number))
        bot.send_message(message.chat.id, "Напишите причину отказа:")
        courier_list[message.chat.id].state = "cancel"
    else:
        bot.send_message(message.chat.id, "Нет активного заказа")

@bot.message_handler(content_types = ['text'])
def check_answer(message):
    if message.chat.id not in courier_list or courier_list[message.chat.id].state == "no":
        if message.text == "Авторизация":
            login(message)
        else:
            keyboard = telebot.types.ReplyKeyboardMarkup()
            keyboard.row("Авторизация")
            bot.send_message(message.chat.id, "Для использования сервиса войдите в систему - /start", reply_markup=keyboard)

    elif courier_list[message.chat.id].state == "password":
        courier_list[message.chat.id].password = message.text
        if courier_list[message.chat.id].login_system():
            keyboard = telebot.types.ReplyKeyboardMarkup()
            if courier_list[message.chat.id].is_order():
                keyboard.row("Информация по заказу")
                keyboard.row("Заказ выполнен")
                keyboard.row("Отменить заказ")
                keyboard.row("Выход")
            else:
                keyboard.row("Получить заказ")
                keyboard.row("Выход")
            bot.send_message(message.chat.id, "Вы были авторизованы как {}\n({} {})".format(courier_list[message.chat.id].login, courier_list[message.chat.id].name, courier_list[message.chat.id].surname), reply_markup=keyboard)
            print("{} был авторизован ({} {}).".format(courier_list[message.chat.id].login, courier_list[message.chat.id].name, courier_list[message.chat.id].surname))
        else:
            courier_list[message.chat.id].state = "no"
            bot.send_message(message.chat.id, "Неправильный логин или пароль")

    elif courier_list[message.chat.id].state == "login":
        courier_list[message.chat.id].login = message.text
        courier_list[message.chat.id].state = "password"
        bot.send_message(message.chat.id, "Пароль: ")

    elif courier_list[message.chat.id].login_status:
        if message.text == "Выход":
            logout(message)

        elif courier_list[message.chat.id].state == "request":
            if message.text == "Подтверждение":
                keyboard = telebot.types.ReplyKeyboardMarkup()
                keyboard.row("Информация по заказу")
                keyboard.row("Заказ выполнен")
                keyboard.row("Отменить заказ")
                keyboard.row("Выход")
                bot.send_message(message.chat.id, "Заказ подтвержден", reply_markup=keyboard)
                courier_list[message.chat.id].state = "order"
                print("{} подтвердил получение заказа №{}.".format(courier_list[message.chat.id].login,
                                                                   courier_list[message.chat.id].Ord.number))
            elif message.text == "Отмена":
                cancel_order(message)
            else:
                bot.send_message(message.chat.id, "Необходимо подтвердить заказ")

        elif courier_list[message.chat.id].state == "cancel":
            courier_list[message.chat.id].Ord.cancel(message.text)
            courier_list[message.chat.id].state = "in_system"
            courier_list[message.chat.id].order_status = False
            keyboard = telebot.types.ReplyKeyboardMarkup()
            keyboard.row("Получить заказ")
            keyboard.row("Выход")
            bot.send_message(message.chat.id, "Заказ отменен", reply_markup=keyboard)

        elif courier_list[message.chat.id].state == "order":
            if message.text == "Информация по заказу":
                info, locations = courier_list[message.chat.id].Ord.info()
                bot.send_message(message.chat.id, info)
                if locations != False:
                    bot.send_location(message.chat.id, locations["lat"], locations["lng"])
            elif message.text == "Заказ выполнен":
                complete_order(message)
            elif message.text == "Отменить заказ":
                cancel_order(message)

        else:
            if message.text == "Получить заказ":
                get_new_order(message)

if __name__ == "__main__":
    bot.polling(none_stop = True, interval = 0)
