

# bot.py — полная версия, готовая к запуску
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔑 ШАГ 1: ЗАМЕНИ ЭТУ СТРОКУ НА СВОЙ ТОКЕН ОТ @BotFather
BOT_TOKEN = "8353531055:AAENeGl3Pt6HwzjFSaPKC868e8Del59FteA"

# 🔑 ШАГ 2: СНАЧАЛА ОСТАВЬ ТАК. ПОТОМ ЗАМЕНИШЬ НА ID МАСТЕРА.
# Как узнать ID — см. ниже, в комментариях.
MASTER_ID = 1442572717  # ← ПОКА НЕ ТРОГАЙ — СНАЧАЛА ЗАПУСТИ, УЗНАЙ ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище записей (временно — в памяти)
bookings = []

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user = message.from_user
    name = user.first_name or "Клиент"
    user_id = user.id

    # 🔍 ЭТО ПЕЧАТАЕТ ID В КОНСОЛЬ — СМОТРИ ТЕРМИНАЛ!
    print(f"🌟 {name} (ID: {user_id}) запустил бота")

    # Отправляем ID клиенту — чтобы он его видел
    await message.answer(
        f"Привет, {name}! ✨\n"
        f"Ваш Telegram ID: `{user_id}`\n\n"
        "Если вы — мастер, скопируйте этот ID и сообщите разработчику.",
        parse_mode="Markdown"
    )

    # Показываем выбор времени
    await message.answer(
        "Выберите удобное время:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Пн, 18:00", callback_data="book_18")],
            [types.InlineKeyboardButton(text="Ср, 14:00", callback_data="book_14")],
            [types.InlineKeyboardButton(text="Чт, 20:00", callback_data="book_20")],
        ])
    )

@dp.callback_query(lambda c: c.data.startswith("book_"))
async def process_booking(callback: types.CallbackQuery):
    time_map = {
        "book_18": "Пн, 18:00",
        "book_14": "Ср, 14:00",
        "book_20": "Чт, 20:00"
    }
    selected_time = time_map[callback.data]
    user = callback.from_user
    name = user.first_name or "Клиент"
    user_id = user.id

    # Сохраняем
    bookings.append({
        "user_id": user_id,
        "name": name,
        "time": selected_time,
        "status": "ожидает подтверждения"
    })

    # ✅ Уведомление МАСТЕРУ — ТОЛЬКО ЕСЛИ MASTER_ID ЗАДАН
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
            print(f"⚠️ Ошибка отправки мастеру: {e}. Проверьте MASTER_ID.")
    else:
        print("❗ MASTER_ID не указан — уведомление мастеру не отправлено.")

    # ✅ Клиенту — панель управления
    await callback.message.edit_text(
        f"✅ Отлично, {name}! Записали вас на {selected_time}.\n\n"
        "Можете управлять записью:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{user_id}")],
            [types.InlineKeyboardButton(text="🔄 Перенести", callback_data="reschedule")],
            [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{user_id}")],
        ])
    )

# Обработчики кнопок
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
    print("🚀 Бот запущен! Открой Telegram и напиши /start")
    if not MASTER_ID:
        print("❗ Совет: после первого /start — вставь ID мастера в переменную MASTER_ID и перезапусти.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())