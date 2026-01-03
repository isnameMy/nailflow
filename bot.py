

# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔑 ШАГ 1: ВСТАВЬ СВОЙ ТОКЕН ОТ @BotFather
BOT_TOKEN = "8353531055:AAENeGl3Pt6HwzjFSaPKC868e8Del59FteA"

# 🔑 ШАГ 2: ВСТАВЬ ID МАСТЕРА (узнать — написать /start самому себе и посмотреть в консоль)
MASTER_ID = 1442572717

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

bookings = []

# 🧾 /start — приветствие + кнопка в Mini App
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user = message.from_user
    name = user.first_name or "Клиент"
    print(f"✅ {name} (ID: {user.id}) запустил бота")

    await message.answer(
        f"Привет, {name}! ✨\nЯ — ассистент Анны, мастера маникюра.\n\n"
        "Что хотите сделать?",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="💅 Портфолио + запись",
                web_app=types.WebAppInfo(url="https://nailflow-lt4n.vercel.app/")
            )],
            [types.InlineKeyboardButton(
                text="📅 Записаться (текстом)",
                callback_data="book_now"
            )]
        ])
    )

# 📋 /portfolio — отдельная команда
@dp.message(Command("portfolio"))
async def show_portfolio(message: types.Message):
    await message.answer(
        "💅 Моё портфолио — работы, отзывы, прайс:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="✨ Посмотреть",
                web_app=types.WebAppInfo(url="https://nailflow-ten.vercel.app")
            )]
        ])
    )

# 📅 Кнопка "Записаться (текстом)"
@dp.callback_query(lambda c: c.data == "book_now")
async def book_now(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите удобное время:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Пн, 18:00", callback_data="book_18")],
            [types.InlineKeyboardButton(text="Ср, 14:00", callback_data="book_14")],
            [types.InlineKeyboardButton(text="Чт, 20:00", callback_data="book_20")],
        ])
    )

# ✅ Выбор времени
@dp.callback_query(lambda c: c.data.startswith("book_"))
async def process_booking(callback: types.CallbackQuery):
    time_map = {"book_18": "Пн, 18:00", "book_14": "Ср, 14:00", "book_20": "Чт, 20:00"}
    selected_time = time_map[callback.data]
    user = callback.from_user
    name = user.first_name or "Клиент"
    user_id = user.id

    bookings.append({"user_id": user_id, "name": name, "time": selected_time})

    # 📩 Уведомление мастеру
    if MASTER_ID:
        try:
            await bot.send_message(
                MASTER_ID,
                f"🔔 Новая запись!\n"
                f"👤 [{name}](tg://user?id={user_id}) (ID: `{user_id}`)\n"
                f"📅 {selected_time}",
                parse_mode="Markdown",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(
                        text="✉️ Написать клиенту",
                        url=f"tg://user?id={user_id}"
                    )]
                ])
            )
        except Exception as e:
            print(f"⚠️ Ошибка отправки: {e}")

    # 🧾 Клиенту — панель управления
    await callback.message.edit_text(
        f"✅ Отлично, {name}! Записали вас на {selected_time}.\n\n"
        "Можете управлять записью:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{user_id}")],
            [types.InlineKeyboardButton(text="🔄 Перенести", callback_data="reschedule")],
            [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{user_id}")],
        ])
    )

# 🔄 Обработчики кнопок
@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_booking(callback: types.CallbackQuery):
    await callback.message.edit_text("✅ Запись подтверждена! До встречи! 🌸")

@dp.callback_query(lambda c: c.data.startswith("cancel_"))
async def cancel_booking(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Запись отменена. Будем рады видеть в другой раз!")

@dp.callback_query(lambda c: c.data == "reschedule")
async def reschedule(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите новое время:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Пн, 18:00", callback_data="book_18")],
            [types.InlineKeyboardButton(text="Ср, 14:00", callback_data="book_14")],
            [types.InlineKeyboardButton(text="Чт, 20:00", callback_data="book_20")],
        ])
    )

# 🚀 Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())