import telebot
from telebot import types
from api import get_recommendations

bot = telebot.TeleBot('5256675994:AAE-I2gfhv0jNukp2Squl9rHnNylpneB86g')

# @bot.message_handler(commands=['start'])
# def start(message):

#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("🇷🇺 Русский")
#     btn2 = types.KeyboardButton('🇬🇧 English')
#     markup.add(btn1, btn2)
#     bot.send_message(message.from_user.id, "🇷🇺 Выберите язык / 🇬🇧 Choose your language", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, '❓ Напишите интересующее вас аниме') #ответ бота

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    data = get_recommendations(message.text)
    text = "Вот список Похожих аниме:\n"
    for i in range(10):
        text += f"{i+1}. '{data[0][i]}' ссылка на anilist.co: https://anilist.co/anime/{data[1][i]}\n"
    bot.send_message(message.from_user.id, text)


bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть