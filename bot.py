import asyncio
import logging
import os
import requests
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

# ============== ВАШИ КЛЮЧИ ==============
BOT_TOKEN           = os.getenv("BOT_TOKEN", "8856543463:AAENT8FIGQYxnVEREkZOZcErxVjABo10MoA")
SUPABASE_URL        = os.getenv("SUPABASE_URL", "https://yrzyskhbgwbamjlsbhos.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyenlza2hiZ3diYW1qbHNiaG9zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTkyODU2MywiZXhwIjoyMDk3NTA0NTYzfQ.iiBTSn4nxgTEPvclA9ndpH8RfoUGj6UdWm-GK0zb6zk")
ADMIN_IDS           = [6407261611]
# ========================================

bot       = Bot(token=BOT_TOKEN)
storage   = MemoryStorage()
dp        = Dispatcher(bot, storage=storage)   # BUG FIX: bot passed here
scheduler = AsyncIOScheduler()

# ─── Supabase helpers ───────────────────────────────────────────────────────

def _headers():
    return {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }

def supabase_select(table, filters=None):
    url    = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in (filters or {}).items()}
    r = requests.get(url, headers=_headers(), params=params)
    return r.json() if r.status_code == 200 else []

def supabase_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    h   = {**_headers(), "Prefer": "return=minimal"}
    r   = requests.post(url, headers=h, json=data)
    return r.status_code == 201

def supabase_update(table, data, filters):
    url    = f"{SUPABASE_URL}/rest/v1/{table}"
    h      = {**_headers(), "Prefer": "return=minimal"}
    params = {k: f"eq.{v}" for k, v in filters.items()}
    r = requests.patch(url, headers=h, json=data, params=params)
    return r.status_code == 204

# ─── FSM States ─────────────────────────────────────────────────────────────

class Registration(StatesGroup):
    phone = State()
    level = State()

class BookingLesson(StatesGroup):
    select_lesson = State()
    confirm       = State()

class AdminAddHorse(StatesGroup):
    name    = State()
    desc_ru = State()
    desc_kz = State()
    desc_en = State()
    photo   = State()

class AdminAddLesson(StatesGroup):
    date             = State()
    time             = State()
    type             = State()
    max_participants = State()
    horse            = State()
    instructor       = State()

# ─── i18n ───────────────────────────────────────────────────────────────────

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
        'walk': "🌳 Прогулка",
        'beginner': "🟢 Начинающий",
        'intermediate': "🟡 Средний",
        'advanced': "🔴 Продвинутый",
        'yes': "✅ Да, записаться",
        'no': "❌ Отмена",
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
        'booking_success': "✅ Сіз жазылдыңыз! Еске салу бір сағат бұрын келеді.",
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
        'walk': "🌳 Серуен",
        'beginner': "🟢 Бастаушы",
        'intermediate': "🟡 Орташа",
        'advanced': "🔴 Жоғары",
        'yes': "✅ Иә, жазылу",
        'no': "❌ Бас тарту",
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
        'lesson_info': "{type} | {time} | {horse} | Instructor: {instr} | Spots: {free}",
        'confirm_booking': "Book for {date} at {time} ({horse})?",
        'booking_success': "✅ Booked! You'll get a reminder one hour before.",
        'already_booked': "You already booked this lesson.",
        'full': "No spots left.",
        'my_bookings_list': "Your bookings:\n{list}",
        'no_bookings': "You have no active bookings.",
        'cancelled': "✅ Booking cancelled.",
        'admin_menu': "🔐 Admin menu:",
        'add_horse': "Add horse",
        'add_lesson': "Add lesson",
        'view_bookings': "View bookings",
        'horse_added': "✅ Horse added!",
        'send_lesson_date': "Enter date (YYYY-MM-DD):",
        'send_lesson_time': "Enter time slot (10:00-11:00):",
        'send_lesson_type': "Choose lesson type:",
        'send_lesson_max': "Max participants:",
        'send_lesson_horse': "Choose a horse:",
        'send_lesson_instructor': "Enter instructor name:",
        'lesson_added': "✅ Lesson added!",
        'reminder_text': "⏰ Reminder: your lesson is on {date} at {time} (horse {horse}).",
        'training': "🏇 Training",
        'walk': "🌳 Walk",
        'beginner': "🟢 Beginner",
        'intermediate': "🟡 Intermediate",
        'advanced': "🔴 Advanced",
        'yes': "✅ Yes, book",
        'no': "❌ Cancel",
    },
}

def get_text(key, lang='ru'):
    return LANG.get(lang, LANG['ru']).get(key, key)

def get_user_lang(tg_id):
    users = supabase_select('users', {'tg_id': tg_id})
    if users:
        return users[0].get('language', 'ru')
    return 'ru'

# ─── Keyboards ──────────────────────────────────────────────────────────────

def main_menu(lang='ru'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(get_text('horses', lang),    callback_data='horses'),
        types.InlineKeyboardButton(get_text('schedule', lang),  callback_data='schedule'),
        types.InlineKeyboardButton(get_text('book', lang),      callback_data='book'),
        types.InlineKeyboardButton(get_text('my_bookings', lang), callback_data='my_bookings'),
        types.InlineKeyboardButton(get_text('change_lang', lang), callback_data='change_lang'),
    )
    return kb

def language_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🇷🇺 Русский",  callback_data='set_lang_ru'),
        types.InlineKeyboardButton("🇰🇿 Қазақша", callback_data='set_lang_kz'),
        types.InlineKeyboardButton("🇬🇧 English",  callback_data='set_lang_en'),
    )
    return kb

# ─── /start ─────────────────────────────────────────────────────────────────

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    tg_id = message.from_user.id
    users = supabase_select('users', {'tg_id': tg_id})

    if not users:
        # New user — ask for phone
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton("📱 Поделиться номером", request_contact=True))
        await message.answer("Добро пожаловать! Пожалуйста, поделитесь номером телефона:", reply_markup=kb)
        await Registration.phone.set()
    else:
        lang = users[0].get('language', 'ru')
        await message.answer(get_text('start', lang), reply_markup=main_menu(lang))

# ─── Registration ───────────────────────────────────────────────────────────

@dp.message_handler(state=Registration.phone, content_types=types.ContentTypes.CONTACT)
async def reg_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone, first_name=message.from_user.first_name)
    lang = 'ru'
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(get_text('beginner', lang),     callback_data='level_beginner'),
        types.InlineKeyboardButton(get_text('intermediate', lang),  callback_data='level_intermediate'),
        types.InlineKeyboardButton(get_text('advanced', lang),     callback_data='level_advanced'),
    )
    await message.answer(get_text('choose_level', lang),
                         reply_markup=types.ReplyKeyboardRemove())
    await message.answer(get_text('choose_level', lang), reply_markup=kb)
    await Registration.level.set()

@dp.callback_query_handler(lambda c: c.data.startswith('level_'), state=Registration.level)
async def reg_level(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split('_', 1)[1]
    data  = await state.get_data()
    supabase_insert('users', {
        'tg_id':      callback.from_user.id,
        'first_name': data.get('first_name', ''),
        'phone':      data.get('phone', ''),
        'level':      level,
        'language':   'ru',
    })
    await state.finish()
    await callback.message.answer(get_text('reg_complete', 'ru'), reply_markup=main_menu('ru'))
    await callback.answer()

# ─── Horses ─────────────────────────────────────────────────────────────────

@dp.callback_query_handler(text='horses')
async def show_horses(callback: types.CallbackQuery):
    lang   = get_user_lang(callback.from_user.id)
    horses = supabase_select('horses', {'active': True})
    if not horses:
        await callback.message.answer(get_text('no_horses', lang))
    for horse in horses:
        desc_key = f"description_{lang}"
        desc = horse.get(desc_key) or horse.get('description_ru', '')
        text = get_text('horse_info', lang).format(name=horse['name'], desc=desc)
        if horse.get('photo_url'):
            await callback.message.answer_photo(horse['photo_url'], caption=text)
        else:
            await callback.message.answer(text)
    await callback.answer()

# ─── Schedule ───────────────────────────────────────────────────────────────

@dp.callback_query_handler(text='schedule')
async def show_schedule(callback: types.CallbackQuery):
    lang    = get_user_lang(callback.from_user.id)
    today   = datetime.now().strftime('%Y-%m-%d')
    lessons = supabase_select('lessons', {'lesson_date': today, 'active': True})
    text    = get_text('schedule_text', lang).format(date=today) + "\n\n"
    if not lessons:
        text += get_text('no_lessons', lang)
    else:
        for les in lessons:
            horses = supabase_select('horses', {'id': les.get('horse_id')})
            horse_name = horses[0]['name'] if horses else '—'
            free = les.get('max_participants', 0) - les.get('current_participants', 0)
            text += get_text('lesson_info', lang).format(
                type=les.get('type', ''),
                time=les.get('time_slot', ''),
                horse=horse_name,
                instr=les.get('instructor', ''),
                free=free,
            ) + "\n"
    await callback.message.answer(text)
    await callback.answer()

# ─── Book a lesson ──────────────────────────────────────────────────────────

@dp.callback_query_handler(text='book')
async def book_lesson(callback: types.CallbackQuery, state: FSMContext):
    lang    = get_user_lang(callback.from_user.id)
    today   = datetime.now().strftime('%Y-%m-%d')
    lessons = supabase_select('lessons', {'lesson_date': today, 'active': True})
    if not lessons:
        await callback.message.answer(get_text('no_lessons', lang))
        await callback.answer()
        return
    kb = types.InlineKeyboardMarkup()
    for les in lessons:
        horses = supabase_select('horses', {'id': les.get('horse_id')})
        horse_name = horses[0]['name'] if horses else '—'
        free = les.get('max_participants', 0) - les.get('current_participants', 0)
        if free > 0:
            label = f"{les.get('time_slot')} | {horse_name} | {free} мест"
            kb.add(types.InlineKeyboardButton(label, callback_data=f"book_{les['id']}"))
    await callback.message.answer(get_text('book', lang), reply_markup=kb)
    await BookingLesson.select_lesson.set()
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('book_'), state=BookingLesson.select_lesson)
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    lang      = get_user_lang(callback.from_user.id)
    lesson_id = callback.data.split('_', 1)[1]
    await state.update_data(lesson_id=lesson_id)
    lessons = supabase_select('lessons', {'id': lesson_id})
    if not lessons:
        await callback.answer("Занятие не найдено.")
        return
    les    = lessons[0]
    horses = supabase_select('horses', {'id': les.get('horse_id')})
    horse_name = horses[0]['name'] if horses else '—'
    text = get_text('confirm_booking', lang).format(
        date=les.get('lesson_date'), time=les.get('time_slot'), horse=horse_name
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(get_text('yes', lang), callback_data='confirm_yes'),
        types.InlineKeyboardButton(get_text('no', lang),  callback_data='confirm_no'),
    )
    await callback.message.answer(text, reply_markup=kb)
    await BookingLesson.confirm.set()
    await callback.answer()

@dp.callback_query_handler(text='confirm_yes', state=BookingLesson.confirm)
async def do_booking(callback: types.CallbackQuery, state: FSMContext):
    lang      = get_user_lang(callback.from_user.id)
    data      = await state.get_data()
    lesson_id = data.get('lesson_id')
    tg_id     = callback.from_user.id

    # Check already booked
    existing = supabase_select('bookings', {'user_id': tg_id, 'lesson_id': lesson_id})
    if existing:
        await callback.message.answer(get_text('already_booked', lang))
        await state.finish()
        await callback.answer()
        return

    # Check spots
    lessons = supabase_select('lessons', {'id': lesson_id})
    if not lessons:
        await callback.answer()
        await state.finish()
        return
    les  = lessons[0]
    free = les.get('max_participants', 0) - les.get('current_participants', 0)
    if free <= 0:
        await callback.message.answer(get_text('full', lang))
        await state.finish()
        await callback.answer()
        return

    supabase_insert('bookings', {
        'user_id':   tg_id,
        'lesson_id': lesson_id,
        'status':    'confirmed',
    })
    supabase_update('lessons',
                    {'current_participants': les.get('current_participants', 0) + 1},
                    {'id': lesson_id})
    await callback.message.answer(get_text('booking_success', lang))
    await state.finish()
    await callback.answer()

@dp.callback_query_handler(text='confirm_no', state=BookingLesson.confirm)
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.answer("Отменено.")
    await callback.answer()

# ─── My bookings ────────────────────────────────────────────────────────────

@dp.callback_query_handler(text='my_bookings')
async def my_bookings(callback: types.CallbackQuery):
    lang     = get_user_lang(callback.from_user.id)
    bookings = supabase_select('bookings', {'user_id': callback.from_user.id, 'status': 'confirmed'})
    if not bookings:
        await callback.message.answer(get_text('no_bookings', lang))
        await callback.answer()
        return
    lines = []
    kb    = types.InlineKeyboardMarkup()
    for b in bookings:
        lessons = supabase_select('lessons', {'id': b['lesson_id']})
        if lessons:
            les    = lessons[0]
            horses = supabase_select('horses', {'id': les.get('horse_id')})
            horse_name = horses[0]['name'] if horses else '—'
            lines.append(f"📅 {les.get('lesson_date')} {les.get('time_slot')} | {horse_name}")
            kb.add(types.InlineKeyboardButton(
                f"❌ Отменить {les.get('lesson_date')} {les.get('time_slot')}",
                callback_data=f"cancel_book_{b['id']}_{b['lesson_id']}"
            ))
    text = get_text('my_bookings_list', lang).format(list='\n'.join(lines))
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('cancel_book_'))
async def cancel_one_booking(callback: types.CallbackQuery):
    lang       = get_user_lang(callback.from_user.id)
    parts      = callback.data.split('_')
    booking_id = parts[2]
    lesson_id  = parts[3]
    supabase_update('bookings', {'status': 'cancelled'}, {'id': booking_id})
    lessons = supabase_select('lessons', {'id': lesson_id})
    if lessons:
        les = lessons[0]
        supabase_update('lessons',
                        {'current_participants': max(0, les.get('current_participants', 1) - 1)},
                        {'id': lesson_id})
    await callback.message.answer(get_text('cancelled', lang))
    await callback.answer()

# ─── Language ────────────────────────────────────────────────────────────────

@dp.callback_query_handler(text='change_lang')
async def change_lang(callback: types.CallbackQuery):
    await callback.message.answer("Выберите язык / Тілді таңдаңыз / Choose language:",
                                  reply_markup=language_keyboard())
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('set_lang_'))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split('_')[2]
    supabase_update('users', {'language': lang}, {'tg_id': callback.from_user.id})
    await callback.message.answer(get_text('start', lang), reply_markup=main_menu(lang))
    await callback.answer()

# ─── Admin ───────────────────────────────────────────────────────────────────

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(get_text('add_horse', 'ru'),    callback_data='admin_add_horse'))
    kb.add(types.InlineKeyboardButton(get_text('add_lesson', 'ru'),   callback_data='admin_add_lesson'))
    kb.add(types.InlineKeyboardButton(get_text('view_bookings', 'ru'), callback_data='admin_view_bookings'))
    await message.answer(get_text('admin_menu', 'ru'), reply_markup=kb)

@dp.callback_query_handler(text='admin_add_horse')
async def admin_add_horse_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.")
        return
    await callback.message.answer("Введите имя лошади:")
    await AdminAddHorse.name.set()
    await callback.answer()

@dp.message_handler(state=AdminAddHorse.name)
async def admin_horse_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание на русском:")
    await AdminAddHorse.desc_ru.set()

@dp.message_handler(state=AdminAddHorse.desc_ru)
async def admin_horse_desc_ru(message: types.Message, state: FSMContext):
    await state.update_data(desc_ru=message.text)
    await message.answer("Введите описание на казахском (или напишите '-'):")
    await AdminAddHorse.desc_kz.set()

@dp.message_handler(state=AdminAddHorse.desc_kz)
async def admin_horse_desc_kz(message: types.Message, state: FSMContext):
    await state.update_data(desc_kz=message.text if message.text != '-' else '')
    await message.answer("Введите описание на английском (или напишите '-'):")
    await AdminAddHorse.desc_en.set()

@dp.message_handler(state=AdminAddHorse.desc_en)
async def admin_horse_desc_en(message: types.Message, state: FSMContext):
    await state.update_data(desc_en=message.text if message.text != '-' else '')
    await message.answer("Отправьте фото лошади (или напишите '-'):")
    await AdminAddHorse.photo.set()

@dp.message_handler(state=AdminAddHorse.photo, content_types=[types.ContentType.PHOTO, types.ContentType.TEXT])
async def admin_horse_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_url = message.photo[-1].file_id if message.photo else None
    supabase_insert('horses', {
        'name':           data['name'],
        'description_ru': data['desc_ru'],
        'description_kz': data.get('desc_kz', ''),
        'description_en': data.get('desc_en', ''),
        'photo_url':      photo_url,
        'active':         True,
    })
    await message.answer(get_text('horse_added', 'ru'))
    await state.finish()

@dp.callback_query_handler(text='admin_add_lesson')
async def admin_add_lesson_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.")
        return
    await callback.message.answer(get_text('send_lesson_date', 'ru'))
    await AdminAddLesson.date.set()
    await callback.answer()

@dp.message_handler(state=AdminAddLesson.date)
async def admin_lesson_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer(get_text('send_lesson_time', 'ru'))
    await AdminAddLesson.time.set()

@dp.message_handler(state=AdminAddLesson.time)
async def admin_lesson_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(get_text('training', 'ru'), callback_data='type_training'))
    kb.add(types.InlineKeyboardButton(get_text('walk', 'ru'),     callback_data='type_walk'))
    await message.answer(get_text('send_lesson_type', 'ru'), reply_markup=kb)
    await AdminAddLesson.type.set()

@dp.callback_query_handler(state=AdminAddLesson.type, lambda c: c.data.startswith('type_'))
async def admin_lesson_type(callback: types.CallbackQuery, state: FSMContext):
    lesson_type = callback.data.split('_', 1)[1]
    await state.update_data(type=lesson_type)
    await callback.message.answer(get_text('send_lesson_max', 'ru'))
    await AdminAddLesson.max_participants.set()
    await callback.answer()

@dp.message_handler(state=AdminAddLesson.max_participants)
async def admin_lesson_max(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
    except ValueError:
        await message.answer("Введите число:")
        return
    await state.update_data(max_participants=count)
    horses = supabase_select('horses', {'active': True})
    kb = types.InlineKeyboardMarkup()
    for horse in horses:
        kb.add(types.InlineKeyboardButton(horse['name'], callback_data=f"selh_{horse['id']}"))
    await message.answer(get_text('send_lesson_horse', 'ru'), reply_markup=kb)
    await AdminAddLesson.horse.set()

@dp.callback_query_handler(state=AdminAddLesson.horse, lambda c: c.data.startswith('selh_'))
async def admin_lesson_horse(callback: types.CallbackQuery, state: FSMContext):
    horse_id = callback.data.split('_', 1)[1]
    await state.update_data(horse_id=horse_id)
    await callback.message.answer(get_text('send_lesson_instructor', 'ru'))
    await AdminAddLesson.instructor.set()
    await callback.answer()

@dp.message_handler(state=AdminAddLesson.instructor)
async def admin_lesson_instructor(message: types.Message, state: FSMContext):
    data = await state.get_data()
    supabase_insert('lessons', {
        'lesson_date':         data['date'],
        'time_slot':           data['time'],
        'type':                data['type'],
        'max_participants':    data['max_participants'],
        'horse_id':            data['horse_id'],
        'instructor':          message.text,
        'current_participants': 0,
        'active':              True,
    })
    await message.answer(get_text('lesson_added', 'ru'))
    await state.finish()

@dp.callback_query_handler(text='admin_view_bookings')
async def admin_view_bookings(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.")
        return
    bookings = supabase_select('bookings', {'status': 'confirmed'})
    if not bookings:
        await callback.message.answer("Записей нет.")
        await callback.answer()
        return
    text = "Все активные записи:\n"
    for b in bookings:
        users   = supabase_select('users',   {'tg_id': b['user_id']})
        lessons = supabase_select('lessons', {'id': b['lesson_id']})
        if users and lessons:
            user = users[0]
            les  = lessons[0]
            horses = supabase_select('horses', {'id': les.get('horse_id')})
            horse_name = horses[0]['name'] if horses else '—'
            text += (f"\n👤 {user.get('first_name','')} ({user.get('phone','')})\n"
                     f"📅 {les.get('lesson_date')} {les.get('time_slot')} | {horse_name}\n")
    await callback.message.answer(text)
    await callback.answer()

# ─── Cancel action ───────────────────────────────────────────────────────────

@dp.callback_query_handler(text='cancel', state='*')
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.answer("Действие отменено.")
    await callback.answer()

# ─── Reminders (scheduler) ──────────────────────────────────────────────────

async def send_reminders():
    now            = datetime.now()
    one_hour_later = now + timedelta(hours=1)
    bookings = supabase_select('bookings', {'status': 'confirmed'})
    for b in bookings:
        lessons = supabase_select('lessons', {'id': b['lesson_id']})
        if not lessons:
            continue
        les = lessons[0]
        try:
            lesson_dt = datetime.strptime(
                f"{les['lesson_date']} {les['time_slot'].split('-')[0].strip()}",
                '%Y-%m-%d %H:%M'
            )
        except Exception:
            continue
        if now <= lesson_dt <= one_hour_later:
            horses = supabase_select('horses', {'id': les.get('horse_id')})
            horse_name = horses[0]['name'] if horses else '—'
            lang = get_user_lang(b['user_id'])
            text = get_text('reminder_text', lang).format(
                date=les['lesson_date'], time=les['time_slot'], horse=horse_name
            )
            try:
                await bot.send_message(b['user_id'], text)
            except Exception:
                pass

scheduler.add_job(send_reminders, 'interval', minutes=5)

# ─── Entry point ────────────────────────────────────────────────────────────

async def main():
    scheduler.start()
    logging.info("🚀 Бот запущен! Найдите Saq_QundyZ_bot в Telegram и напишите /start")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
