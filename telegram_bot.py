"""
Telegram бот для збору анкет користувачів
Використовує aiogram 3.x та FSM для управління станами
"""

import asyncio
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# ============= КОНФІГУРАЦІЯ =============
BOT_TOKEN = "8149744887:AAEusA2GD-YQKgWPznMwmP0HOKESvWiom50"  # 👈 Вставте сюди токен вашого бота
ADMIN_ID = 5893945619, 1320280691

# ============= СТАНИ FSM =============
class FormStates(StatesGroup):
    waiting_for_start = State()
    entering_name = State()
    entering_age = State()
    entering_nick = State()
    entering_birthday = State()
    entering_zodiac = State()
    entering_location = State()
    entering_version = State()
    entering_about = State()
    entering_telegram = State()

# ============= ІНІЦІАЛІЗАЦІЯ =============
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ============= КЛАВІАТУРИ =============
def get_start_keyboard():
    """Клавіатура для початкового питання"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Так"), KeyboardButton(text="❌ Ні")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_zodiac_keyboard():
    """Клавіатура зі знаками зодіаку (3 в ряд)"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="♈ Овен"), KeyboardButton(text="♉ Телець"), KeyboardButton(text="♊ Близнюки")],
            [KeyboardButton(text="♋ Рак"), KeyboardButton(text="♌ Лев"), KeyboardButton(text="♍ Діва")],
            [KeyboardButton(text="♎ Терези"), KeyboardButton(text="♏ Скорпіон"), KeyboardButton(text="♐ Стрілець")],
            [KeyboardButton(text="♑ Козоріг"), KeyboardButton(text="♒ Водолій"), KeyboardButton(text="♓ Риби")]
        ],
        resize_keyboard=True
    )
    return keyboard

# ============= ВАЛІДАЦІЯ =============
def validate_age(age_text: str) -> bool:
    """Перевірка, чи вік є числом"""
    return age_text.isdigit() and 1 <= int(age_text) <= 120

def validate_birthday(birthday: str) -> bool:
    """Перевірка формату дати dd.mm.yyyy"""
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(pattern, birthday):
        return False
    try:
        datetime.strptime(birthday, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def validate_telegram(username: str) -> bool:
    """Перевірка, чи username починається з @"""
    return username.startswith('@') and len(username) > 1

# ============= ОБРОБНИКИ КОМАНД =============
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обробка команди /start"""
    await state.clear()
    await message.answer(
        "Стань частиною нашого Minecraft хаусу! Чи бажаєте ви заповнити анкету та приєднатися?",
        reply_markup=get_start_keyboard()
    )
    await state.set_state(FormStates.waiting_for_start)

# ============= ПОЧАТОК АНКЕТИ =============
@dp.message(FormStates.waiting_for_start, F.text == "❌ Ні")
async def decline_form(message: Message, state: FSMContext):
    """Користувач відмовився від заповнення"""
    await message.answer(
        "Добре, якщо передумаєте - просто напишіть /start 😊",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

@dp.message(FormStates.waiting_for_start, F.text == "✅ Так")
async def accept_form(message: Message, state: FSMContext):
    """Користувач погодився заповнити анкету"""
    await message.answer(
        "Вкажіть ваше ім'я:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FormStates.entering_name)

# ============= ЗБІР ДАНИХ АНКЕТИ =============
@dp.message(FormStates.entering_name)
async def process_name(message: Message, state: FSMContext):
    """Збереження імені"""
    await state.update_data(name=message.text)
    await message.answer("Скільки вам років? (введіть лише число)")
    await state.set_state(FormStates.entering_age)

@dp.message(FormStates.entering_age)
async def process_age(message: Message, state: FSMContext):
    """Збереження віку з валідацією"""
    if not validate_age(message.text):
        await message.answer("❌ Будь ласка, введіть коректний вік (число від 1 до 120)")
        return
    
    await state.update_data(age=message.text)
    await message.answer("Який ваш нік у Minecraft?")
    await state.set_state(FormStates.entering_nick)

@dp.message(FormStates.entering_nick)
async def process_nick(message: Message, state: FSMContext):
    """Збереження Minecraft ніку"""
    await state.update_data(nick=message.text)
    await message.answer("Вкажіть дату народження\n(формат: dd.mm.yyyy, приклад — 15.03.2005)")
    await state.set_state(FormStates.entering_birthday)

@dp.message(FormStates.entering_birthday)
async def process_birthday(message: Message, state: FSMContext):
    """Збереження дати народження з валідацією"""
    if not validate_birthday(message.text):
        await message.answer("❌ Будь ласка, введіть дату у форматі dd.mm.yyyy\n(наприклад: 15.03.2005)")
        return
    
    await state.update_data(birthday=message.text)
    await message.answer(
        "Оберіть ваш знак зодіаку:",
        reply_markup=get_zodiac_keyboard()
    )
    await state.set_state(FormStates.entering_zodiac)

@dp.message(FormStates.entering_zodiac)
async def process_zodiac(message: Message, state: FSMContext):
    """Збереження знаку зодіаку"""
    zodiac_signs = [
        "♈ Овен", "♉ Телець", "♊ Близнюки",
        "♋ Рак", "♌ Лев", "♍ Діва",
        "♎ Терези", "♏ Скорпіон", "♐ Стрілець",
        "♑ Козоріг", "♒ Водолій", "♓ Риби"
    ]
    
    if message.text not in zodiac_signs:
        await message.answer("❌ Будь ласка, оберіть знак зодіаку з кнопок нижче")
        return
    
    await state.update_data(zodiac=message.text)
    await message.answer(
        "Зазначте вашу область та місто:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FormStates.entering_location)

@dp.message(FormStates.entering_location)
async def process_location(message: Message, state: FSMContext):
    """Збереження локації"""
    await state.update_data(location=message.text)
    await message.answer("Яка у вас версія Minecraft?")
    await state.set_state(FormStates.entering_version)

@dp.message(FormStates.entering_version)
async def process_version(message: Message, state: FSMContext):
    """Збереження версії Minecraft"""
    await state.update_data(version=message.text)
    await message.answer("Розкажіть коротко про себе:")
    await state.set_state(FormStates.entering_about)

@dp.message(FormStates.entering_about)
async def process_about(message: Message, state: FSMContext):
    """Збереження інформації про себе"""
    await state.update_data(about=message.text)
    await message.answer("Вкажіть ваш Telegram username\n(починається з @, приклад: @username)")
    await state.set_state(FormStates.entering_telegram)

@dp.message(FormStates.entering_telegram)
async def process_telegram(message: Message, state: FSMContext):
    """Збереження Telegram username та завершення анкети"""
    if not validate_telegram(message.text):
        await message.answer("❌ Будь ласка, введіть коректний Telegram username, який починається з @")
        return
    
    await state.update_data(telegram=message.text)
    
    # Отримання всіх даних
    data = await state.get_data()
    
    # Формування анкети для адміністратора
    application_text = f"""｡･ﾟ♡ﾟ･｡ ✧ Ꭺнᴋᴇᴛᴀ ✧  ﾟ｡♡ﾟ･｡
•°•☆•°• Ім'я: {data['name']}
•°•☆•°• Вік: {data['age']}
•°•☆•°• Minecraft нік: {data['nick']}
•°•☆•°• День народження: {data['birthday']}
•°•☆•°• {data['zodiac']}
•°•☆•°• Місто / область: {data['location']}
•°•☆•°• Версія Minecraft: {data['version']}
•°•☆•°• Про себе: {data['about']}
•°•☆•°• Telegram: {data['telegram']}
☆☆ ┄─   z Z  ๑ 🎐 ๑ z Z   ─┄  ☆☆
╼╼╼╼╼╼╼╼╼╴"""
    
    # Відправка адміністратору
    try:
        await bot.send_message(ADMIN_ID, application_text)
    except Exception as e:
        print(f"Помилка відправки адміністратору: {e}")
    
    # Підтвердження користувачу
    await message.answer(
        "Дякуємо за заповнення анкети!\nБудь ласка, очікуйте відповідь від адміністрації",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Очищення стану
    await state.clear()

# ============= ЗАПУСК БОТА =============
async def main():
    """Головна функція запуску бота"""
    print("🤖 Бот запущено!")
    print("Натисніть Ctrl+C для зупинки")
    
    # Видалення старих оновлень та запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот зупинено")


