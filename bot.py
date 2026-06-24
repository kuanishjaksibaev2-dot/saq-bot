# УСТАНОВКА БИБЛИОТЕК
# pip install aiogram==2.25.1 supabase==1.2.0 pydantic==2.5.0 python-dotenv==1.0.1 requests==2.31.0 apscheduler==3.10.1 nest-asyncio

import asyncio
import nest_asyncio
nest_asyncio.apply()
import logging
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from supabase import create_client, Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

# ============== ВАШИ КЛЮЧИ ==============
BOT_TOKEN = "8856543463:AAENT8FIGQYxnVEREkZOZcErxVjABo10MoA"
SUPABASE_URL = "https://yrzyskhbgwbamjlsbhos.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyenlza2hiZ3diYW1qbHNiaG9zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE5Mjg1NjMsImV4cCI6MjA5NzUwNDU2M30.eO3DG9429EXzAGZzjNbbPqhTeMsRCEm-I_agVpotPWM"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyenlza2hiZ3diYW1qbHNiaG9zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTkyODU2MywiZXhwIjoyMDk3NTA0NTYzfQ.iiBTSn4nxgTEPvclA9ndpH8RfoUGj6UdWm-GK0zb6zk"
ADMIN_IDS = [6407261611]
# ========================================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()

class Registration(StatesGroup):
    phone = State()
    level = State()

class BookingLesson(StatesGroup):
    select_lesson = State()
    confirm = State()

class AdminAddHorse(StatesGroup):
    name = State()
    desc_ru = State()
    desc_kz = State()
    desc_en = State()
    photo = State()

class AdminAddLesson(StatesGroup):
    date = State()
    time = State()
    type = State()
    max_participants = State()
    horse = State()
    instructor = State()

LANG = {
    'ru': {
        'start': "Добро пожаловать в конный клуб! Выберите действие:",
        'register': "📝 Регистрация",
        'horses': "🐴 Наши лошади",
        'schedule': "📅 Расписание",
        'book': "✍️ Записаться",
        'my_bookings': "📋 Мои записи",
        'change_lang': "🌐 Сменить язык",
        'send_phone': "Отправьте номер телефона (нажмите кнопку ниже):",
        'choose_level': "Ваш уровень катания:",
        'reg_complete': "✅ Регистрация завершена!",
        'no_horses': "Лошадей пока нет.",
        'horse_info': "🐴 {name}\n{desc}",
        'schedule_text': "Расписание на {date}:",
        'no_lessons': "На сегодня занятий нет.",
        'lesson_info': "{type} | {time} | {horse} | Инструктор: {instr} | Мест: {free}",
        'confirm_booking': "Записаться на {date} в {time} ({horse})?",
        'booking_success': "✅ Вы записаны! Напоминание придёт за час.",
        'already_booked': "Вы уже записаны на это занятие.",
        'full': "Мест нет.",
        'my_bookings_list': "Ваши записи:\n{list}",
        'no_bookings': "У вас нет активных записей.",
        'cancelled': "✅ Запись отменена.",
        'admin_menu': "🔐 Админ-меню:",
        'add_horse': "Добавить лошадь",
        'add_lesson': "Добавить занятие",
        'view_bookings': "Просмотр записей",
        'horse_added': "✅ Лошадь добавлена!",
        'send_lesson_date': "Введите дату (ГГГГ-ММ-ДД):",
        'send_lesson_time': "Введите время (10:00-11:00):",
        'send_lesson_type': "Выберите тип занятия:",
        'send_lesson_max': "Максимум участников:",
        'send_lesson_horse': "Выберите лошадь:",
        'send_lesson_instructor': "Введите инструктора:",
        'lesson_added': "✅ Занятие добавлено!",
        'reminder_text': "⏰ Напоминание: у вас занятие {date} в {time} (лошадь {horse}).",
        'training': "🏇 Тренировка",
        'walk': "🌳 Прогулка"
    },
    'kz': {
        'start': "Ат клубына қош келдіңіз! Әрекетті таңдаңыз:",
        'register': "📝 Тіркелу",
        'horses': "🐴 Біздің аттар",
        'schedule': "📅 Кесте",
        'book': "✍️ Жазылу",
        'my_bookings': "📋 Менің жазбаларым",
        'change_lang': "🌐 Тілді өзгерту",
        'send_phone': "Телефон нөмірін жіберіңіз:",
        'choose_level': "Сіздің шабу деңгейіңіз:",
        'reg_complete': "✅ Тіркелу аяқталды!",
        'no_horses': "Әлі ат жоқ.",
        'horse_info': "🐴 {name}\n{desc}",
        'schedule_text': "{date} күнгі кесте:",
        'no_lessons': "Бүгін сабақ жоқ.",
        'lesson_info': "{type} | {time} | {horse} | Нұсқаушы: {instr} | Орын: {free}",
        'confirm_booking': "{date} күні {time} ({horse}) сабағына жазылу?",
        'booking_success': "✅ Сіз жазылдыңыз! Еске салу сабақтан бір сағат бұрын келеді.",
        'already_booked': "Сіз бұл сабаққа жазылып қойғансыз.",
        'full': "Орын жоқ.",
        'my_bookings_list': "Сіздің жазбаларыңыз:\n{list}",
        'no_bookings': "Сізде белсенді жазба жоқ.",
        'cancelled': "✅ Жазба өшірілді.",
        'admin_menu': "🔐 Админ мәзірі:",
        'add_horse': "Ат қосу",
        'add_lesson': "Сабақ қосу",
        'view_bookings': "Жазбаларды қарау",
        'horse_added': "✅ Ат қосылды!",
        'send_lesson_date': "Күнді енгізіңіз (ЖЖЖЖ-АА-КК):",
        'send_lesson_time': "Уақытты енгізіңіз (10:00-11:00):",
        'send_lesson_type': "Сабақ түрін таңдаңыз:",
        'send_lesson_max': "Қатысушылардың макс саны:",
        'send_lesson_horse': "Атты таңдаңыз:",
        'send_lesson_instructor': "Нұсқаушыны енгізіңіз:",
        'lesson_added': "✅ Сабақ қосылды!",
        'reminder_text': "⏰ Еске салу: сіздің сабағыңыз {date} {time} (ат {horse}).",
        'training': "🏇 Жаттығу",
        'walk': "🌳 Серуен"
    },
    'en': {
        'start': "Welcome to the Horse Club! Choose an action:",
        'register': "📝 Registration",
        'horses': "🐴 Our Horses",
        'schedule': "📅 Schedule",
        'book': "✍️ Book a Lesson",
        'my_bookings': "📋 My Bookings",
        'change_lang': "🌐 Change language",
        'send_phone': "Send your phone number:",
        'choose_level': "Your riding level:",
        'reg_complete': "✅ Registration complete!",
        'no_horses': "No horses yet.",
        'horse_info': "🐴 {name}\n{desc}",
        'schedule_text': "Schedule for {date}:",
        'no_lessons': "No lessons today.",
        'lesson_info': "{type} | {time} | {horse} | Instructor: {instr} | Slots: {free}",
        'confirm_booking': "Book for {date} at {time} ({horse})?",
        'booking_success': "✅ Booked! You will get a reminder 1 hour before.",
        'already_booked': "You already booked this lesson.",
        'full': "No slots available.",
        'my_bookings_list': "Your bookings:\n{list}",
        'no_bookings': "You have no active bookings.",
        'cancelled': "✅ Booking cancelled.",
        'admin_menu': "🔐 Admin Menu:",
        'add_horse': "Add Horse",
        'add_lesson': "Add Lesson",
        'view_bookings': "View Bookings",
        'horse_added': "✅ Horse added!",
        'send_lesson_date': "Enter date (YYYY-MM-DD):",
        'send_lesson_time': "Enter time (10:00-11:00):",
        'send_lesson_type': "Choose lesson type:",
        'send_lesson_max': "Max participants:",
        'send_lesson_horse': "Choose a horse:",
        'send_lesson_instructor': "Enter instructor name:",
        'lesson_added': "✅ Lesson added!",
        'reminder_text': "⏰ Reminder: you have a lesson {date} at {time} (horse {horse}).",
        'training': "🏇 Training",
        'walk': "🌳 Walk"
    }
}

def get_text(key: str, lang: str) -> str:
    return LANG.get(lang, LANG['ru']).get(key, key)

def get_user_lang(tg_id: int) -> str:
    res = supabase.table('users').select('language').eq('tg_id', tg_id).execute()
    if res.data:
        return res.data[0]['language']
    return 'ru'

def main_menu(lang: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=get_text('register', lang), callback_data='register'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('horses', lang), callback_data='horses'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('schedule', lang), callback_data='schedule'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('book', lang), callback_data='book'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('my_bookings', lang), callback_data='my_bookings'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('change_lang', lang), callback_data='change_lang'))
    return keyboard

def language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data='set_lang_ru'),
        types.InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data='set_lang_kz'),
        types.InlineKeyboardButton(text="🇬🇧 English", callback_data='set_lang_en')
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user = supabase.table('users').select('*').eq('tg_id', message.from_user.id).execute()
    if not user.data:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Зарегистрироваться", callback_data='register'))
        await message.answer("Сначала зарегистрируйтесь!", reply_markup=keyboard)
        return
    lang = user.data[0]['language']
    await message.answer(get_text('start', lang), reply_markup=main_menu(lang))

@dp.callback_query_handler(text='register')
async def register_start(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    await callback.message.answer(get_text('send_phone', lang), reply_markup=types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True,
        keyboard=[[types.KeyboardButton(text="📱 Отправить телефон", request_contact=True)]]
    ))
    await state.set_state(Registration.phone)
    await callback.answer()

@dp.message_handler(state=Registration.phone, content_types=['contact'])
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    lang = get_user_lang(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Начинающий", callback_data='level_beginner'))
    keyboard.add(types.InlineKeyboardButton(text="Средний", callback_data='level_intermediate'))
    keyboard.add(types.InlineKeyboardButton(text="Продвинутый", callback_data='level_advanced'))
    await message.answer(get_text('choose_level', lang), reply_markup=keyboard)
    await state.set_state(Registration.level)

@dp.callback_query_handler(state=Registration.level, text_startswith='level_')
async def process_level(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split('_')[1]
    data = await state.get_data()
    phone = data['phone']
    tg_id = callback.from_user.id
    supabase.table('users').upsert({
        'tg_id': tg_id,
        'username': callback.from_user.username,
        'first_name': callback.from_user.first_name,
        'phone': phone,
        'level': level,
        'language': 'ru'
    }).execute()
    lang = 'ru'
    await callback.message.answer(get_text('reg_complete', lang), reply_markup=main_menu(lang))
    await state.clear()
    await callback.answer()

@dp.callback_query_handler(text='horses')
async def show_horses(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    horses = supabase.table('horses').select('*').eq('active', True).execute()
    if not horses.data:
        await callback.message.answer(get_text('no_horses', lang))
        await callback.answer()
        return
    for horse in horses.data:
        desc = horse[f'description_{lang}'] or horse['description_ru'] or ''
        text = get_text('horse_info', lang).format(name=horse['name'], desc=desc)
        await callback.message.answer(text)
    await callback.answer()

@dp.callback_query_handler(text='schedule')
async def show_schedule(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    today = datetime.now().strftime('%Y-%m-%d')
    lessons = supabase.table('lessons').select('*, horses(name)').eq('lesson_date', today).eq('active', True).execute()
    if not lessons.data:
        await callback.message.answer(get_text('no_lessons', lang))
        await callback.answer()
        return
    text = get_text('schedule_text', lang).format(date=today) + '\n\n'
    for l in lessons.data:
        horse_name = l['horses']['name'] if l['horses'] else '—'
        free = l['max_participants'] - l['current_participants']
        l_type = get_text('training', lang) if l.get('type') == 'training' else get_text('walk', lang)
        text += get_text('lesson_info', lang).format(type=l_type, time=l['time_slot'], horse=horse_name, instr=l.get('instructor', '—'), free=free) + '\n'
    await callback.message.answer(text)
    await callback.answer()

@dp.callback_query_handler(text='book')
async def book_lesson_start(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    today = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    lessons = supabase.table('lessons').select('*, horses(name)').gte('lesson_date', today).lte('lesson_date', end_date).eq('active', True).execute()
    if not lessons.data:
        await callback.message.answer("Нет доступных занятий.")
        await callback.answer()
        return
    keyboard = types.InlineKeyboardMarkup()
    for l in lessons.data:
        free = l['max_participants'] - l['current_participants']
        if free <= 0: continue
        horse_name = l['horses']['name'] if l['horses'] else '—'
        btn_text = f"{l['lesson_date']} {l['time_slot']} | {horse_name}"
        keyboard.add(types.InlineKeyboardButton(text=btn_text, callback_data=f"book_{l['id']}"))
    keyboard.add(types.InlineKeyboardButton(text="Отмена", callback_data='cancel'))
    await callback.message.answer("Выберите занятие:", reply_markup=keyboard)
    await state.set_state(BookingLesson.select_lesson)
    await callback.answer()

@dp.callback_query_handler(state=BookingLesson.select_lesson, text_startswith='book_')
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    lesson_id = callback.data.split('_')[1]
    lesson = supabase.table('lessons').select('*, horses(name)').eq('id', lesson_id).single().execute()
    if not lesson.data: return
    lang = get_user_lang(callback.from_user.id)
    if lesson.data['current_participants'] >= lesson.data['max_participants']:
        await callback.message.answer(get_text('full', lang)); await callback.answer(); return
    horse_name = lesson.data['horses']['name'] if lesson.data['horses'] else '—'
    text = get_text('confirm_booking', lang).format(date=lesson.data['lesson_date'], time=lesson.data['time_slot'], horse=horse_name)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{lesson_id}"))
    keyboard.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data='cancel'))
    await callback.message.answer(text, reply_markup=keyboard)
    await state.set_state(BookingLesson.confirm)
    await callback.answer()

@dp.callback_query_handler(state=BookingLesson.confirm, text_startswith='confirm_')
async def finalize_booking(callback: types.CallbackQuery, state: FSMContext):
    lesson_id = callback.data.split('_')[1]
    user_id = callback.from_user.id
    supabase.table('bookings').insert({'user_id': user_id, 'lesson_id': lesson_id}).execute()
    supabase.rpc('increment_participants', {'lesson_id': lesson_id}).execute()
    lang = get_user_lang(user_id)
    await callback.message.answer(get_text('booking_success', lang))
    await state.clear()
    await callback.answer()

@dp.callback_query_handler(text='my_bookings')
async def my_bookings(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    bookings = supabase.table('bookings').select('*, lessons(lesson_date, time_slot, horses(name))').eq('user_id', callback.from_user.id).eq('status', 'confirmed').execute()
    if not bookings.data:
        await callback.message.answer(get_text('no_bookings', lang))
        await callback.answer()
        return
    text = get_text('my_bookings_list', lang).format(list='')
    for b in bookings.data:
        les = b['lessons']
        horse = les['horses']['name'] if les['horses'] else '—'
        text += f"\n📅 {les['lesson_date']} {les['time_slot']} | {horse}"
    await callback.message.answer(text)
    await callback.answer()

@dp.callback_query_handler(text='change_lang')
async def change_lang(callback: types.CallbackQuery):
    await callback.message.answer("Выберите язык:", reply_markup=language_keyboard())
    await callback.answer()

@dp.callback_query_handler(text_startswith='set_lang_')
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split('_')[2]
    supabase.table('users').update({'language': lang}).eq('tg_id', callback.from_user.id).execute()
    await callback.message.answer(get_text('start', lang), reply_markup=main_menu(lang))
    await callback.answer()

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    lang = 'ru'
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=get_text('add_horse', lang), callback_data='admin_add_horse'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('add_lesson', lang), callback_data='admin_add_lesson'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('view_bookings', lang), callback_data='admin_view_bookings'))
    await message.answer(get_text('admin_menu', lang), reply_markup=keyboard)

@dp.callback_query_handler(text='admin_add_horse')
async def admin_add_horse_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите имя лошади:")
    await state.set_state(AdminAddHorse.name)
    await callback.answer()

@dp.message_handler(state=AdminAddHorse.name)
async def admin_horse_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание на русском:")
    await state.set_state(AdminAddHorse.desc_ru)

@dp.message_handler(state=AdminAddHorse.desc_ru)
async def admin_horse_desc_ru(message: types.Message, state: FSMContext):
    await state.update_data(desc_ru=message.text)
    await message.answer("Введите описание на казахском (или пропустите):")
    await state.set_state(AdminAddHorse.desc_kz)

@dp.message_handler(state=AdminAddHorse.desc_kz)
async def admin_horse_desc_kz(message: types.Message, state: FSMContext):
    await state.update_data(desc_kz=message.text)
    await message.answer("Введите описание на английском (или пропустите):")
    await state.set_state(AdminAddHorse.desc_en)

@dp.message_handler(state=AdminAddHorse.desc_en)
async def admin_horse_desc_en(message: types.Message, state: FSMContext):
    await state.update_data(desc_en=message.text)
    await message.answer("Отправьте фото лошади (или пропустите):")
    await state.set_state(AdminAddHorse.photo)

@dp.message_handler(state=AdminAddHorse.photo, content_types=['photo', 'text'])
async def admin_horse_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_url = message.photo[-1].file_id if message.photo else None
    supabase.table('horses').insert({
        'name': data['name'],
        'description_ru': data['desc_ru'],
        'description_kz': data.get('desc_kz', ''),
        'description_en': data.get('desc_en', ''),
        'photo_url': photo_url,
        'active': True
    }).execute()
    await message.answer(get_text('horse_added', 'ru'))
    await state.clear()

@dp.callback_query_handler(text='admin_add_lesson')
async def admin_add_lesson_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(get_text('send_lesson_date', 'ru'))
    await state.set_state(AdminAddLesson.date)
    await callback.answer()

@dp.message_handler(state=AdminAddLesson.date)
async def admin_lesson_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer(get_text('send_lesson_time', 'ru'))
    await state.set_state(AdminAddLesson.time)

@dp.message_handler(state=AdminAddLesson.time)
async def admin_lesson_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=get_text('training', 'ru'), callback_data='type_training'))
    keyboard.add(types.InlineKeyboardButton(text=get_text('walk', 'ru'), callback_data='type_walk'))
    await message.answer(get_text('send_lesson_type', 'ru'), reply_markup=keyboard)
    await state.set_state(AdminAddLesson.type)

@dp.callback_query_handler(state=AdminAddLesson.type, text_startswith='type_')
async def admin_lesson_type(callback: types.CallbackQuery, state: FSMContext):
    lesson_type = callback.data.split('_')[1]
    await state.update_data(type=lesson_type)
    await callback.message.answer(get_text('send_lesson_max', 'ru'))
    await state.set_state(AdminAddLesson.max_participants)
    await callback.answer()

@dp.message_handler(state=AdminAddLesson.max_participants)
async def admin_lesson_max(message: types.Message, state: FSMContext):
    await state.update_data(max_participants=int(message.text))
    horses = supabase.table('horses').select('*').eq('active', True).execute()
    keyboard = types.InlineKeyboardMarkup()
    for horse in horses.data:
        keyboard.add(types.InlineKeyboardButton(text=horse['name'], callback_data=f"horse_{horse['id']}"))
    await message.answer(get_text('send_lesson_horse', 'ru'), reply_markup=keyboard)
    await state.set_state(AdminAddLesson.horse)

@dp.callback_query_handler(state=AdminAddLesson.horse, text_startswith='horse_')
async def admin_lesson_horse(callback: types.CallbackQuery, state: FSMContext):
    horse_id = callback.data.split('_')[1]
    await state.update_data(horse_id=horse_id)
    await callback.message.answer(get_text('send_lesson_instructor', 'ru'))
    await state.set_state(AdminAddLesson.instructor)
    await callback.answer()

@dp.message_handler(state=AdminAddLesson.instructor)
async def admin_lesson_instructor(message: types.Message, state: FSMContext):
    data = await state.get_data()
    supabase.table('lessons').insert({
        'lesson_date': data['date'],
        'time_slot': data['time'],
        'type': data['type'],
        'max_participants': data['max_participants'],
        'horse_id': data['horse_id'],
        'instructor': message.text,
        'current_participants': 0,
        'active': True
    }).execute()
    await message.answer(get_text('lesson_added', 'ru'))
    await state.clear()

@dp.callback_query_handler(text='admin_view_bookings')
async def admin_view_bookings(callback: types.CallbackQuery):
    bookings = supabase.table('bookings').select('*, users(first_name, phone), lessons(lesson_date, time_slot, horses(name))').execute()
    if not bookings.data:
        await callback.message.answer("Записей нет.")
        await callback.answer()
        return
    text = "Все записи:\n"
    for b in bookings.data:
        user = b['users']
        lesson = b['lessons']
        horse = lesson['horses']['name'] if lesson['horses'] else '—'
        text += f"\n👤 {user['first_name']} ({user['phone']})\n📅 {lesson['lesson_date']} {lesson['time_slot']} | {horse}\n"
    await callback.message.answer(text)
    await callback.answer()

@dp.callback_query_handler(text='cancel')
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено.")
    await callback.answer()

async def send_reminders():
    now = datetime.now()
    one_hour_later = now + timedelta(hours=1)
    bookings = supabase.table('bookings').select('*, users(tg_id), lessons(lesson_date, time_slot, horses(name))').eq('status', 'confirmed').execute()
    for b in bookings.data:
        lesson = b['lessons']
        lesson_datetime = datetime.strptime(f"{lesson['lesson_date']} {lesson['time_slot']}", '%Y-%m-%d %H:%M')
        if now <= lesson_datetime <= one_hour_later:
            horse = lesson['horses']['name'] if lesson['horses'] else '—'
            text = get_text('reminder_text', 'ru').format(date=lesson['lesson_date'], time=lesson['time_slot'], horse=horse)
            try:
                await bot.send_message(b['users']['tg_id'], text)
            except:
                pass

scheduler.add_job(send_reminders, 'interval', minutes=5)

async def main():
    scheduler.start()
    print("🚀 Бот успешно запущен! Идите в Telegram, найдите Saq_QundyZ_bot и пишите /start")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
