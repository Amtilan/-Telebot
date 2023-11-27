import telebot
from telebot import types
import pymongo

bot = telebot.TeleBot("6733446707:AAH4aqWAUYqmRxUxqn9kgGCAuAHc7RfP0LM")

DB_NAME = "users"

uri = "mongodb+srv://rzhaxilikov:yEDZtx07GJvaJ68I@cluster0.2anmjpi.mongodb.net/?retryWrites=true&w=majority"

COLLECTION_NAME = "users"

client = pymongo.MongoClient(uri)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
# Доступные продукты
products = {
    "1": {
        "name": "Калкулус 1",
        "price": 10000,
        "description": "эм чел что ты учил в 11 классе?"
    },
    "2": {
        "name": "Бля",
        "price": 20000,
        "description": "не желание учить пп"
    },
    "3": {
        "name": "Жёпа",
        "price": 30000,
        "description": "Коротко и ясно о дискретки"
    }
}
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать")

# Каталог
@bot.message_handler(commands=["catalog"])
def catalog(message):
    inline_keyboard = telebot.types.InlineKeyboardMarkup()
    for product_id, product in products.items():
        inline_keyboard.add(telebot.types.InlineKeyboardButton(text=product["name"], callback_data=product_id))
    bot.send_message(message.chat.id, "Вот наш каталог товаров:", reply_markup=inline_keyboard)
# Регистрация на клиента либо продавщика
@bot.message_handler(commands=["register"])
def register(message):
    user_id = message.chat.id
    username = message.chat.username
    if collection.find_one({"user_id": user_id}) is None:
        collection.insert_one({"username": username, "user_id": user_id})
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы")
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы")
# Все продукты
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    product_id = call.data
    product = products[product_id]
    bot.send_message(call.message.chat.id, f"* {product['name']} - {product['price']} тенге\n\n{product['description']}")
    # Test
        
bot.polling()