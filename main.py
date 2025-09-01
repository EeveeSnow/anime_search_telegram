import telebot
from telebot import types
from api import get_recommendations, find_similar_title, get_anime_by_id

import json
with open("api.json") as f:
    config = json.load(f)
api_key = config["api_key"]

bot = telebot.TeleBot(api_key)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    response = (
            "/searchid <название аниме> для поиска 🆔 и информаии об аниме.\n"
            "/search <id аниме> для поиска похожих аниме."
        )
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['searchid'])
def search_anime(message):
    try:
        title = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажи название аниме после /searchid, например: /searchid Frieren")
        return
    idx, _ = find_similar_title(title)
    
    if idx is None:
        bot.reply_to(message, "Похожие аниме не найдено. Попробуй другое название. 😢")
    else:
        anime = get_anime_by_id(idx)
        response = (
            f"🎬 *{anime['title']}*\n"
            f"🆔 *{idx}*\n"
            f"📝 *Описание*: {anime['description']}\n" 
            f"📚 *Жанры*: {anime['genres']}\n"
            f"⭐ *Рейтинг*: {anime['rating']}\n"
            "❓ Если вы искали другое аниме попробуйте уточнить название. 😢"
        )
        bot.reply_to(message, response, parse_mode='Markdown')


@bot.message_handler(commands=['search'])
def search_anime(message):
    try:
        idx = int(message.text.split(maxsplit=1)[1])
    except IndexError or TypeError:
        bot.reply_to(message, "Пожалуйста, укажи 🆔 аниме после /search, например: /search Frieren")
        return
    
    if any(get_anime_by_id(idx)) == None:
        bot.reply_to(message, "Пожалуйста, укажи 🆔 аниме после /search, например: /search Frieren")
    else:
        data = get_recommendations(idx)
        response = "Вот список Похожих аниме:\n"
        for i in range(10):
            response += f"{i+1}. '{data[0][i]}' ссылка на anilist.co: https://anilist.co/anime/{data[1][i]}\n"
        bot.reply_to(message, response, parse_mode='Markdown')


# @bot.message_handler(content_types=['text'])
# def get_text_messages(message):
#     data = get_recommendations(message.text)
#     text = "Вот список Похожих аниме:\n"
#     for i in range(10):
#         text += f"{i+1}. '{data[0][i]}' ссылка на anilist.co: https://anilist.co/anime/{data[1][i]}\n"
#     bot.send_message(message.from_user.id, text)


bot.polling(none_stop=True, interval=0)