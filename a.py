import telebot
from pymongo import MongoClient

# Устанавливаем токен бота
bot = telebot.TeleBot("6733446707:AAH4aqWAUYqmRxUxqn9kgGCAuAHc7RfP0LM")

# Инициализация MongoDB
mongo_client = MongoClient("mongodb+srv://rzhaxilikov:yEDZtx07GJvaJ68I@cluster0.2anmjpi.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client.telegram_bot_db
# Коллекции в базе данных MongoDB
users_collection = db.users
messages_collection = db.messages

# Словарь для отслеживания выбранного пользователем собеседника
selected_interlocutors = {}

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    # Проверяем, зарегистрирован ли пользователь
    if not users_collection.find_one({'user_id': user_id}):
        # Если нет, регистрируем его
        users_collection.insert_one({'user_id': user_id, 'username': message.from_user.username})
        bot.send_message(message.chat.id, f'Привет, {message.from_user.username}! Ты успешно зарегистрирован.')
    else:
        bot.send_message(message.chat.id, 'Привет! Ты уже зарегистрирован.')

# Обработка команды /select
@bot.message_handler(commands=['select'])
def handle_select(message):
    user_id = message.from_user.id
    # Проверяем, зарегистрирован ли пользователь
    if not users_collection.find_one({'user_id': user_id}):
        bot.send_message(message.chat.id, 'Пожалуйста, зарегистрируйтесь сначала, используя команду /start.')
        return

    # Получаем всех зарегистрированных пользователей
    all_users = users_collection.find()

    # Формируем клавиатуру с именами пользователей
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for user in all_users:
        keyboard.add(telebot.types.KeyboardButton(user['username']))

    bot.send_message(message.chat.id, 'Выберите собеседника:', reply_markup=keyboard)

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    sender_username = message.from_user.username
    message_text = message.text

    # Проверяем, зарегистрирован ли отправитель сообщения
    if not users_collection.find_one({'user_id': user_id}):
        bot.send_message(message.chat.id, 'Пожалуйста, зарегистрируйтесь сначала, используя команду /start.')
        return

    # Проверяем, выбран ли собеседник
    if user_id not in selected_interlocutors:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите собеседника, используя команду /select.')
        return

    # Получаем id выбранного собеседника
    interlocutor_id = selected_interlocutors[user_id]

    # Сохраняем сообщение в базе данных
    messages_collection.insert_one({'sender_id': user_id, 'sender_username': sender_username,
                                    'interlocutor_id': interlocutor_id, 'message': message_text})

    # Отправляем сообщение собеседнику
    try:
        bot.send_message(interlocutor_id, f'Новое сообщение от {sender_username}: {message_text}')
    except telebot.TeleBotException as e:
        bot.send_message(user_id, f'Не удалось отправить сообщение. Пожалуйста, выберите другого собеседника.')

# Обработка кнопок на клавиатуре выбора собеседника
@bot.message_handler(func=lambda message: message.text in [user['username'] for user in users_collection.find()])
def handle_interlocutor_selection(message):
    user_id = message.from_user.id
    interlocutor_username = message.text
    interlocutor = users_collection.find_one({'username': interlocutor_username})

    # Запоминаем выбранного собеседника для пользователя
    selected_interlocutors[user_id] = interlocutor['user_id']

    bot.send_message(message.chat.id, f'Вы выбрали собеседника: {interlocutor_username}')

bot.polling()