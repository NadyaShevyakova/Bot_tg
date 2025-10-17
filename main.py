from gc import callbacks
import emoji
import telebot
import webbrowser

import bd_id_k
import database
from datetime import datetime, timedelta
from database import init_db, clear_schedule, add_schedule_entry
from bd_id_k import *
from telebot import types

import sqlite3

# bd_id_k.clear()
bd_id_k.init_bd()

bot = telebot.TeleBot("8123602638:AAEs-dnefoZauAzDFSBOnSDDWwXHpMUMlGc")
# k = 0

def koaf(message):
	info = bd_id_k.get_all_from_bd(message.chat.id)
	return info[0][0]

def gr(message):
	info = bd_id_k.get_all_from_bd(message.chat.id)
	return info[0][-1]

def time_StrDM_fromData(day_notStr): #На вход Дату, на выход Строка вида d.m
	return datetime.strftime(day_notStr, "%d.%m")

def time_keyboard(str_weekDay,k):#На вход пн вт...(подходит для календаря и бд)    вместо time_for_keyboard_d_m
	return datetime.strftime(time_d_m_y_notStr(str_weekDay,k), "%d.%m")

def time_d_m_y_notStr(str_day_week,k): #Чтобы определить дату по дню недели
	now = datetime.today()
	day_now = now.weekday()

	days = {'Пн': 0, 'Вт': 1, 'Ср': 2, 'Чт': 3, 'Пт': 4, 'Сб': 5, 'Вс': 6}
	if (k==0) and (days[str_day_week] == day_now):
		return now
	elif (k==0) and (days[str_day_week] != day_now):
		delta = timedelta(days=(abs(days[str_day_week] - day_now)))
		if days[str_day_week] > day_now:
			new_date = now + delta
			return new_date
		else:
			new_date = now - delta
			return new_date
	elif k<0:
		delta = timedelta(days=(6 - days[str_day_week] + day_now + (abs(k)-1)*6 + abs(k)))
		new_date = now - delta
		return new_date
	elif k>0:
		delta = timedelta(days=(6 - day_now + days[str_day_week] + (abs(k)-1)*6 + abs(k)))
		new_date = now + delta
		return new_date

def format_keyboard(str_day,date,message): #'Пн' и '6.10'
	k = koaf(message)
	now = datetime.today()
	day_now = now.weekday()
	days = {'Пн':0,'Вт':1,'Ср':2,'Чт':3,'Пт':4,'Сб':5,'Вс':6}
	if k==0 and days[str_day]==day_now:
		return ('>' + str_day + ' ' + date + '<')
	else:
		return (str_day + ' ' + date)

def schedule(massive,day): #day это дата (НЕ строка)
	day_of_week = day.weekday()
	days = {0:'Понедельник',1: 'Вторник',2: 'Среда',3: 'Четверг',4: 'Пятница',5: 'Суббота', 6: 'Воскресенье'}
	s = days[day_of_week] + ' ' + time_StrDM_fromData(day) + '\n' + '\n'
	for lesson in massive:
		s+=(lesson[2] + '\n' + lesson[-1] + ' по дисциплине: ' + lesson[0] + '\n' + 'Преподаватель: ' + lesson[1] + '\n' + 'Аудитория и корпус/online: ' + lesson[-3] + ' ' + lesson[-2]) + '\n' + '\n'
	return s

def make_keyboard_markup_2(message):
	k = koaf(message)

	now = datetime.today()
	now = datetime.strftime(now, "%d.%m")
	markup_2 = types.InlineKeyboardMarkup()
	btn1 = types.InlineKeyboardButton('Сегодня, ' + now, callback_data='сегодня')
	markup_2.row(btn1)
	btn2 = types.InlineKeyboardButton(format_keyboard('Пн', time_keyboard('Пн',k),message), callback_data='Пн')
	btn3 = types.InlineKeyboardButton(format_keyboard('Вт', time_keyboard('Вт',k),message), callback_data='Вт')
	btn4 = types.InlineKeyboardButton(format_keyboard('Ср', time_keyboard('Ср',k),message), callback_data='Ср')
	markup_2.row(btn2, btn3, btn4)
	btn5 = types.InlineKeyboardButton(format_keyboard('Чт', time_keyboard('Чт',k),message), callback_data='Чт')
	btn6 = types.InlineKeyboardButton(format_keyboard('Пт', time_keyboard('Пт',k),message), callback_data='Пт')
	btn7 = types.InlineKeyboardButton(format_keyboard('Сб', time_keyboard('Сб',k),message), callback_data='Сб')
	markup_2.row(btn5, btn6, btn7)
	btn8 = types.InlineKeyboardButton('Пред. неделя', callback_data='пред')
	btn9 = types.InlineKeyboardButton('След.неделя', callback_data='след')
	markup_2.row(btn8, btn9)
	return markup_2

def choose_group(message):
	markup_1 = types.ReplyKeyboardMarkup()
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	markup_1.row(btn1, btn2)
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton('4')
	markup_1.row(btn3, btn4)
	btn5 = types.KeyboardButton('5')
	btn6 = types.KeyboardButton('6')
	markup_1.row(btn5, btn6)
	btn7 = types.KeyboardButton('7')
	markup_1.row(btn7)
	bot.send_message(message.chat.id, 'Привет, студент! Ты должен выбрать свою группу из потока 25КНТ', reply_markup=markup_1)
	bot.register_next_step_handler(message, on_click)

@bot.message_handler(commands=['start'])
def start(message):
	db = get_all_from_bd(message.chat.id)

	if len(db) != 0:
		markup_ask_group = types.InlineKeyboardMarkup()
		btn_1 = types.InlineKeyboardButton('Да', callback_data='да_сменить_группу')
		btn_2 = types.InlineKeyboardButton('Нет', callback_data='нет_сменить_группу')
		markup_ask_group.row(btn_1,btn_2)
		bot.send_message(message.chat.id, f'Вы уже входили в свою группу {db[0][-1]}. Хотите сменить её?',reply_markup=markup_ask_group)
	else:
		choose_group(message)

def on_click(message):

	bot.send_message(message.chat.id, 'Отлично', reply_markup=types.ReplyKeyboardRemove())
	# if message.text =='1':
	#
	# 	bd_id_k.add_id_gr_to_bd(message.chat.id,0,0)
	# 	bot.send_message(message.chat.id, 'Окей')
	different_groups = ["1","2","3","4","5","6","7"]
	for i in different_groups:
		if message.text == i:
			db = get_all_from_bd(message.chat.id)
			if len(db) == 0:
				bd_id_k.add_all_to_bd(message.chat.id, int(i),0)
				# d = bd_id_k.get_all_from_bd(message.chat.id)

			else:
				bd_id_k.add_gr_to_bd(int(i),0,message.chat.id)
			markup_2 = make_keyboard_markup_2(message)
			bot.send_message(message.chat.id, 'Расписание на какой день тебя интересует?', reply_markup=markup_2)


#C:\Users\Надя\PycharmProjects\nadya_bot\users_id_k
def extra_nigth(day,message):
	# global k
	k = koaf(message)
	days = {'Пн': 'Понедельник', 'Вт': 'Вторник', 'Ср': 'Среда', 'Чт': 'Четверг', 'Пт': 'Пятница', 'Сб': 'Суббота', 'Вс': 'Воскресенье'}
	return (days[day] + ' ' + time_keyboard(day,k) + '\n' + "Нет занятий")

def buttons_mn_sat(day,callback): #day это 'Пн' или 'Вт' и тп..
	# global k
	bot.delete_message(callback.message.chat.id, callback.message.message_id)  # удаляем прошлый запрос
	k = koaf(callback.message)
	date = time_d_m_y_notStr(day,k) #возвращает НЕ строку типа day.month.year
	markup_2 = make_keyboard_markup_2(callback.message)
	try:
		# info = bd_id_k.get_all_from_bd(callback.message) #for group
		a = database.get_schedule_for_date(time_StrDM_fromData(date),gr(callback.message))
		bot.send_message(callback.message.chat.id, schedule(a,date),reply_markup=markup_2)
	except:
		# bot.send_message(callback.message.chat.id, f'{date}, {gr(callback.message)}')  # !!!!!проверка
		#2025-10-17 16:19:27.347538, 7
		bot.send_message(callback.message.chat.id, extra_nigth(day,callback.message),reply_markup=markup_2)
# print(database.get_schedule_for_date('17.10',7))
# Обработчик callback_query (нажатий на кнопки)
@bot.callback_query_handler(func=lambda callback: True)
def callback_query(callback):
	# global k
	#bot.answer_callback_query(callback.id) не помню зачем было
	if callback.data == 'да_сменить_группу':
		bot.delete_message(callback.message.chat.id, callback.message.message_id)  # удаляем прошлый запрос
		choose_group(callback.message)

	if callback.data == 'нет_сменить_группу':
		bot.delete_message(callback.message.chat.id, callback.message.message_id)  # удаляем прошлый запрос
		bot.send_message(callback.message.chat.id,'Вы отстались в своей группе') #можно добавить f строку, в какой ты остался группе
		bd_id_k.add_k_to_bd(0, callback.message.chat.id)
		markup_2 = make_keyboard_markup_2(callback.message)
		bot.send_message(callback.message.chat.id, 'Вот твоё расписание: \n',reply_markup=markup_2)

	if callback.data == 'сегодня':
		bot.delete_message(callback.message.chat.id, callback.message.message_id)  # удаляем прошлый запрос
		# Всплывающее уведомление
		#bot.answer_callback_query(callback.id, "Сегодня")
		now = datetime.today() #надо для поиска даты в бд
		# now = datetime.strftime(now, "%d.%m.%y")
		markup_2 = make_keyboard_markup_2(callback.message)
		try:
			# info = bd_id_k.get_all_from_bd(callback.message)
			a = database.get_schedule_for_date(time_StrDM_fromData(now),gr(callback.message)) #сюда еще передаем группу как параметр
			bot.send_message(callback.message.chat.id, schedule(a,now), reply_markup=markup_2) #(это все для новой таблицы со всеми группами)
		except:
			bot.send_message(callback.message.chat.id, 'Сегодня нет занятий',reply_markup=markup_2)

	week = ['Пн','Вт','Ср','Пт']
	for day in week:
		if callback.data == day:
			buttons_mn_sat(day,callback)

	if callback.data == 'Чт' or callback.data == 'Сб':
		bot.delete_message(callback.message.chat.id, callback.message.message_id)  # удаляем прошлый запрос
		markup = make_keyboard_markup_2(callback.message)
		bot.send_message(callback.message.chat.id, 'Английский язык -> см. расписание \n https://docs.google.com/spreadsheets/d/1RB9AWtrYm6Y9m8NSy6On7Zk3byws8RonAGBqeneSxOo/edit?gid=23993546#gid=23993546', reply_markup=markup)

	first = 'назад'
	second = 'вперёд'
	if callback.data == 'пред':
		bot.delete_message(callback.message.chat.id, callback.message.message_id)  # удаляем прошлый запрос
		k = koaf(callback.message)
		bd_id_k.add_k_to_bd(k-1,callback.message.chat.id)
		# k = k - 1
		last_markup = make_keyboard_markup_2(callback.message)
		k = koaf(callback.message)

		if k!=0 and k<0:
			bot.send_message(callback.message.chat.id, f'Расписание на {abs(k)} неделю(ли) {first}', reply_markup=last_markup)
		elif k!=0 and k>0:
			bot.send_message(callback.message.chat.id, f'Расписание на {abs(k)} неделю(ли) {second}',
							 reply_markup=last_markup)
		else:
			bot.send_message(callback.message.chat.id, f'Расписание на эту неделю', reply_markup=last_markup)

	if callback.data == 'след':
		bot.delete_message(callback.message.chat.id, callback.message.message_id)  # удаляем прошлый запрос
		k = koaf(callback.message)
		bd_id_k.add_k_to_bd(k + 1, callback.message.chat.id)
		# k = k + 1
		next_markup = make_keyboard_markup_2(callback.message)
		k = koaf(callback.message)
		if k != 0 and k<0:
			bot.send_message(callback.message.chat.id, f'Расписание на {abs(k)} неделю(ли) {first}', reply_markup=next_markup)
		elif k != 0 and k>0:
			bot.send_message(callback.message.chat.id, f'Расписание на {abs(k)} неделю(ли) {second}', reply_markup=next_markup)
		else:
			bot.send_message(callback.message.chat.id, f'Расписание на эту неделю', reply_markup=next_markup)

bot.infinity_polling()
