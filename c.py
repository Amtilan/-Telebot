import telebot
from telebot import types
import pymongo

bot = telebot.TeleBot("6733446707:AAH4aqWAUYqmRxUxqn9kgGCAuAHc7RfP0LM")

DB_NAME2 = "Клиенты"
DB_NAME3 = "Продавцы"

uri = "mongodb+srv://rzhaxilikov:yEDZtx07GJvaJ68I@cluster0.2anmjpi.mongodb.net/?retryWrites=true&w=majority"

COLLECTION_NAME_2 = "Клиент"
COLLECTION_NAME_3 = "Продавец"

client = pymongo.MongoClient(uri)
db2 = client[DB_NAME2]
db3 = client[DB_NAME3]
collection2 = db2[COLLECTION_NAME_2]
collection3 = db3[COLLECTION_NAME_3]
# Доступные продукты

products = {
    "1": {
        'name': "калкулус 1",
        "price": 10000,
        "description": "эм чел что ты учил в 11 классе?"
    },
    "2": {
        'name': "бля",
        "price": 20000,
        "description": "не желание учить пп"
    },
    "3": {
        'name': "жёпа",
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
        inline_keyboard.add(telebot.types.InlineKeyboardButton(text=product['name'], callback_data=product_id))
    bot.send_message(message.chat.id, "Вот наш каталог товаров:", reply_markup=inline_keyboard)
# Все продукты
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    product_id = call.data
    product = products[product_id]
    bot.send_message(call.message.chat.id, f"* {product['name']} - {product['price']} тенге\n\n{product['description']}")
    
# Регистрация на клиента либо продавщика
@bot.message_handler(commands=["register"])
def register(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    client_button = telebot.types.KeyboardButton('клиент')
    seller_button = telebot.types.KeyboardButton('продавец')
    markup.add(client_button, seller_button)
    bot.send_message(message.chat.id, "Выберите тип регистрации:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.lower() in ['клиент', 'продавец'])
def registration(message):
    chat_id = message.chat.id
    user_type = message.text.lower()

    if user_type == 'клиент':
        # Регистрация клиента
        user_data = {
            'chat_id': chat_id,
            'user_type': user_type,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }

        collection2.insert_one(user_data)
        telebot.types.ReplyKeyboardRemove
        bot.send_message(chat_id, f"Вы успешно зарегистрированы как {user_type}")
    elif user_type == 'продавец':
        # Регистрация продавца и предоставление выбора категории
        
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for product in products:
            keyboard.add(telebot.types.KeyboardButton(product['name']))
        telebot.types.ReplyKeyboardRemove
        bot.send_message(message.chat.id, "Выберите категорию товаров:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text in ['калкулус 1', 'бля', 'жёпа'])
def save_seller_category(message):
    chat_id = message.chat.id
    user_type = message.text.lower()

    # Сохранение данных продавца в базе данных
    user_data = {
        'chat_id': chat_id,
        'user_type': 'продавец',
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'category': user_type
    }
    collection3.insert_one(user_data)
    telebot.types.ReplyKeyboardRemove
    bot.send_message(chat_id, f"Вы успешно зарегистрированы как продавец в категории {user_type}")



bot.polling()