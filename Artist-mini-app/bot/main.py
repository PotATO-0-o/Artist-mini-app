import os
import json
import logging
from datetime import datetime
from pathlib import Path
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TOKEN")
WEB_APP_URL = "https://artist-web-potato-0-o.amvera.io/"
CHANNEL_LINK = "https://t.me/TFArtist"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Константы
PROGRESS_FILE = Path("progress.json")
LESSONS = [
    {"id": 1, "title": "Рисование кота"},
    {"id": 2, "title": "Вязание шарфа"},
    {"id": 3, "title": "Игра песни на гитаре"},
    {"id": 4, "title": "Рисование акварелью"},
    {"id": 5, "title": "Каллиграфия пером"}
]

def load_progress():
    if not PROGRESS_FILE.exists():
        return {}
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки прогресса: {e}")
        return {}

def save_progress(data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_progress(user_id: int, lesson_id: int):
    progress = load_progress()
    user_key = str(user_id)
    lesson_key = f"lesson_{lesson_id}"
    
    if user_key not in progress:
        progress[user_key] = {
            "first_access": datetime.now().isoformat(),
            "lessons": {}
        }
    
    if lesson_key not in progress[user_key]["lessons"]:
        progress[user_key]["lessons"][lesson_key] = {
            "started_at": datetime.now().isoformat(),
            "status": "в процессе"
        }
    
    progress[user_key]["last_access"] = datetime.now().isoformat()
    save_progress(progress)
    return progress[user_key]

@dp.message(Command("start"))
async def start(message: types.Message):
    web_app_button = InlineKeyboardButton(
        text="🎨 Открыть уроки",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    channel_button = InlineKeyboardButton(
        text="📢 Наш канал",
        url=CHANNEL_LINK
    )
    progress_button = InlineKeyboardButton(
        text="📊 Мой прогресс",
        callback_data="show_progress"
    )
    
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [web_app_button],
            [channel_button],
            [progress_button]
        ]
    )
    
    await message.answer(
        "Добро пожаловать в творческие уроки!",
        reply_markup=markup
    )

@dp.callback_query(lambda query: query.data == "show_progress")
async def show_progress_callback(query: types.CallbackQuery):
    await show_progress(query.message)

async def show_progress(message: types.Message):
    progress = load_progress()
    user_key = str(message.from_user.id)
    
    if user_key not in progress:
        await message.answer("Вы ещё не начинали уроки.")
        return
    
    user_data = progress[user_key]
    text = "📊 Ваш прогресс:\n\n"
    text += f"🕒 Первый вход: {datetime.fromisoformat(user_data['first_access']).strftime('%d.%m.%Y %H:%M')}\n"
    text += f"⏱ Последняя активность: {datetime.fromisoformat(user_data['last_access']).strftime('%d.%m.%Y %H:%M')}\n\n"
    text += "🎨 Уроки:\n"
    
    for lesson in LESSONS:
        lesson_key = f"lesson_{lesson['id']}"
        if lesson_key in user_data["lessons"]:
            start_time = datetime.fromisoformat(user_data["lessons"][lesson_key]["started_at"]).strftime('%d.%m.%Y')
            text += f"{lesson['id']}. {lesson['title']} - начат {start_time}\n"
        else:
            text += f"{lesson['id']}. {lesson['title']} - не начат\n"
    
    await message.answer(text)

@dp.message(lambda msg: msg.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "lesson_start":
            lesson_id = int(data["lesson_id"])
            if 1 <= lesson_id <= 5:
                update_progress(message.from_user.id, lesson_id)
                await message.answer(f"✅ Урок {lesson_id} начат!")
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")

async def main():
    if not PROGRESS_FILE.exists():
        save_progress({})
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())