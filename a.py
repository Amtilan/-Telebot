import telebot
from pymongo import MongoClient
import pymongo

# Подключение к базе данных
DB_NAME = "users"

uri = "mongodb+srv://rzhaxilikov:yEDZtx07GJvaJ68I@cluster0.2anmjpi.mongodb.net/?retryWrites=true&w=majority"

COLLECTION_NAME = "users"

client = pymongo.MongoClient(uri)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Создание бота
bot = telebot.TeleBot('6733446707:AAH4aqWAUYqmRxUxqn9kgGCAuAHc7RfP0LM')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    # Получение списка городов из базы данных
    cities = collection.find()

    # Создание клавиатуры
    keyboard = telebot.types.InlineKeyboardMarkup()
    for city in cities:
        keyboard.add(telebot.types.InlineKeyboardButton(text=city['username'], callback_data=city['username']))

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, 'Список городов:', reply_markup=keyboard)

# Обработчик нажатия на кнопку в клавиатуре
@bot.callback_query_handler(lambda callback_query: True)
def callback(callback_query: telebot.types.CallbackQuery):
    # Получение города из клавиатуры
    city = callback_query.data

    # Отправка сообщения с названием города
    bot.send_message(callback_query.message.chat.id, f'Вы выбрали город {city}')

# Запуск бота
bot.polling()
