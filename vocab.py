# -*- coding: utf-8 -*-
import telebot
import os
import random
from model import get_audio, save_audio
from bot_token import token, folders, admin_comm
from utils import norm_, get_words, clear_all


markup = telebot.types.InlineKeyboardMarkup()
users = [] 
words = [] #general list for a game
curr_folder = []
# running lists
game_type = []
used = []
err = []
ans = []
misspelled_words = []

#bot init
bot = telebot.TeleBot(token)

#start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.clear()
    users.append('user')
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Русский', callback_data='rus'))
    markup.add(telebot.types.InlineKeyboardButton(text='English', callback_data='eng'))
    markup.add(telebot.types.InlineKeyboardButton(text='Custom(admin)', callback_data='cust'))
    bot.send_message(message.from_user.id, 'Привет, ты готов к словарному диктанту? \nНа каком языке будет тренировка?', reply_markup=markup)


#add new word
@bot.message_handler(commands=[admin_comm])  #admin command
def new_word(message):
    users.clear()
    users.append('admin')
    bot.send_message(message.from_user.id,'Для добавления аудио отправьте нужные слова через запятую(не более 5 слов на батч, ударение обозначается знаком + перед ударным гласным')       

 
@bot.message_handler(content_types=['text']) 
def get_text_messages(message): 

    # add new word
    if users[0] == 'admin':
        batch = message.text.split(',')
        folder = folders['cust']
        if len(batch) > 5:
            batch = batch[:6]
        try:
            audio = get_audio(batch)
            bot.send_message(message.from_user.id, 'Audio was generated successfully')
        except Exception as e:
            bot.send_message(message.from_user.id, 'Model failed to generate audio')
            pass
        try:
            save_audio(audio, batch, folder)
            bot.send_message(message.from_user.id, 'Files were saved to the corresponding custom folder')
        except Exception as e:
            bot.send_message(message.from_user.id, 'Saving failed')
            pass

    # answers    
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        curr_word = message.text#.lower()
        if len(ans) > 0: 
            answer = ans[0]
            if  curr_word == answer:
                markup.add(telebot.types.InlineKeyboardButton(text='Следующее слово', callback_data='get_word'))
                bot.send_message(message.from_user.id, 'Верно!', reply_markup=markup)
                ans.clear()
                
            else:
                err.append(1)
                misspelled_words.append((curr_word, answer))
                if len(err) < 2:
                    bot.send_message(message.from_user.id, 'Неверно, подумай еще!')
                    print(ans)
                else:
                    markup.add(telebot.types.InlineKeyboardButton(text='Начать заново', callback_data='start'))
                    bot.send_message(message.from_user.id, f'Снова неверно, правильный ответ - {norm_(ans[0])}. К сожалению, игра окончена!', reply_markup=markup)
                    ans.clear()
        else:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text='Слово', callback_data='get_word'))
            bot.send_message(message.from_user.id, 'Для прослушивания первого слова, нажмите Слово')
        
            
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):

    if call.data == 'rus':
        markup = telebot.types.InlineKeyboardMarkup()
        clear_all(words, curr_folder, err, used)
        words.extend(get_words(folders['ru']))
        curr_folder.append(folders['ru'])
        markup.add(telebot.types.InlineKeyboardButton(text='Слово', callback_data='word'))
        markup.add(telebot.types.InlineKeyboardButton(text='Игра', callback_data='game'))
        bot.send_message(call.message.chat.id, text="Чтобы писать от руки под диктовку  - нажми Слово \nЧтобы начать игру - нажми Игра", reply_markup=markup)
        
    elif call.data == 'eng':
        markup = telebot.types.InlineKeyboardMarkup()
        clear_all(words, curr_folder, err, used)
        words.extend(get_words(folders['en']))
        curr_folder.append(folders['en'])
        markup.add(telebot.types.InlineKeyboardButton(text='Русский', callback_data='rus'))
        bot.send_message(call.message.chat.id, text="Английский будет добавлен позже =)", reply_markup=markup)
    
    elif call.data == 'cust':
        markup = telebot.types.InlineKeyboardMarkup()
        clear_all(words, curr_folder, err, used)
        words.extend(get_words(folders['cust']))
        curr_folder.append(folders['cust'])
        markup.add(telebot.types.InlineKeyboardButton(text='Слово', callback_data='word'))
        markup.add(telebot.types.InlineKeyboardButton(text='Игра', callback_data='game'))
        bot.send_message(call.message.chat.id, text="Чтобы писать от руки под диктовку  - нажми Слово \nЧтобы начать игру - нажми Игра", reply_markup=markup)

    elif call.data == 'word':
        markup = telebot.types.InlineKeyboardMarkup()
        game_type.clear()
        game_type.append('word')
        markup.add(telebot.types.InlineKeyboardButton(text='Прослушать слово', callback_data='get_word'))
        bot.send_message(call.message.chat.id, 'Подготовь бумагу и ручку, бот будет диктовать тебе слово, правильное написание можно посмотреть нажав на кнопку - Ответ.', reply_markup=markup)

    elif call.data ==  'game':
        markup = telebot.types.InlineKeyboardMarkup()
        game_type.clear()
        game_type.append('game')
        markup.add(telebot.types.InlineKeyboardButton(text='Прослушать слово', callback_data='get_word'))
        bot.send_message(call.message.chat.id, 'Добро пожаловать в игру! \nБот будет диктовать тебе слово, а твоя задача набрать это слово в сообщении. \nУ тебя есть одно право на ошибку, затем игра будет окончена. \nУдачи!', reply_markup=markup)

    elif call.data == 'get_word':
        markup = telebot.types.InlineKeyboardMarkup()
        ans.clear()
        if len(used) == len(words):
            bot.send_message(call.message.chat.id, 'Ты написал все слова из словаря! Повторим еще раз? \nЧтобы начать заново - отправь /start', reply_markup=markup)
        else:
            word_idx = random.randint(0,len(words)-1)
            while word_idx in used:
                word_idx = random.randint(0,len(words)-1)
            flname = words[word_idx]
            ans.append(flname.split('.')[0])
            if game_type[0] == 'word':
                markup.add(telebot.types.InlineKeyboardButton(text='Ответ', callback_data='ans'))
            bot.send_voice(call.message.chat.id, open(os.path.join(os.path.abspath(os.curdir), curr_folder[0]) + '/' + flname, 'rb'), reply_markup=markup)
            used.append(word_idx)

    elif call.data == 'ans':
        markup = telebot.types.InlineKeyboardMarkup()  
        markup.add(telebot.types.InlineKeyboardButton(text='Следующее слово', callback_data='get_word'))
        bot.send_message(call.message.chat.id, f'Верный ответ - {norm_(ans[0])}', reply_markup=markup)


    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['mistakes'])
def mistakes(message):
    bot.send_message(message.from_user.id, misspelled_words)

@bot.message_handler(commands=['end'])
def end(message):
    #users.clear()
    bot.send_message(message.from_user.id,'Буду с нетерпением ждать новой тренировки! :) Чтобы начать заново - отправь /start')       
            

bot.polling(none_stop=True, interval=0)

