# -*- coding: utf-8 -*-
import telebot
import os
import re
import random
from bot_token import token


# fix issue with 'й'
def norm_filename(filename):
    if isinstance(filename, str):
        from unicodedata import normalize
        filename = normalize('NFC', filename)
    return filename


words = []
used = []
err = []
ans = []
misspelled_words = []
for root, dirs, files in os.walk("words"):  
    for filename in files:
        words.append(norm_filename(filename))


#bot init
bot = telebot.TeleBot(token)
#start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет, ты готов к словарному диктанту? \nЧтобы писать от руки под диктовку  - отправь /word \nЧтобы начать игру - отправь /game \nЧтобы закончить - отправь /end")
    err.clear()
    used.clear()
#@bot.message_handler(commands=['help'])
#def help(message):
#    bot.send_message(message.from_user.id,'')

@bot.message_handler(commands=['mistakes'])
def mistakes(message):
    bot.send_message(message.from_user.id, misspelled_words)

@bot.message_handler(commands=['end'])
def end(message):
    bot.send_message(message.from_user.id,'Буду с нетерпением ждать новой тренировки! :) Чтобы начать заново - отправь /start')       
#word
@bot.message_handler(commands=['word']) 
def word(message): 
    ans.clear()
    if len(used) == len(words):
        bot.send_message(message.from_user.id, 'Ты написал все слова из словаря! Повторим еще раз? \nДля повтора отправь /start')
    #elif len(err) > 1:
    #    bot.send_message(message.from_user.id, 'К сожалению, игра окончена! Начать заново - /start')
    else:
        word_idx = random.randint(0,len(words)-1)
        if word_idx not in used:
            flname = words[word_idx]
            ans.append(flname.split('.')[0])
            bot.send_document(message.chat.id, open(os.path.join(os.path.abspath(os.curdir), 'words/') + flname, 'rb'))
            used.append(word_idx)

@bot.message_handler(commands=['game']) 
def game(message): 
    bot.send_message(message.from_user.id, 'Добро пожаловать в игру! \nБот будет диктовать тебе слово, а твоя задача набрать это слово в сообщении. \nУ тебя есть одно право на ошибку, затем игра будет окончена. \nЧтобы получить первое слово отправь /word \nУдачи!')

            
        
@bot.message_handler(content_types=['text']) 
def get_text_messages(message): 
    curr_word = message.text#.lower()
    if len(ans) > 0: 
        answer = ans[0]
        if  curr_word == answer:
            bot.send_message(message.from_user.id, 'Верно! Следующее слово - /word')
        else:
            err.append(1)
            misspelled_words.append((curr_word, answer))
            if len(err) < 2:
                bot.send_message(message.from_user.id, 'Неверно, подумай еще!')
            else:
                bot.send_message(message.from_user.id, 'Снова неверно, к сожалению, игра окончена! Начать заново - /start')
                ans.clear()
    else:
        bot.send_message(message.from_user.id, 'Для прослушивания первого слова, нажмите /word')
        
            


            

bot.polling(none_stop=True, interval=0)

