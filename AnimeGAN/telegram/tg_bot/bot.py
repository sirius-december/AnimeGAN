import asyncio
import dotenv
import aiogram
import os

dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
dp = aiogram.Dispatcher()

async def main():
    await dp.start_polling(bot)


@dp.message(aiogram.filters.Command("start"))
async def send_welcome(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Информация"),
            aiogram.types.KeyboardButton(text="Начать!")
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard = kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите как продолжить"
    )
    await message.answer("Добро пожаловать в AnimeGan!", reply_markup=keyboard)



@dp.message(aiogram.F.text.lower() == "начать!")
async def photo_or_video_choose(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Фотография"),
            aiogram.types.KeyboardButton(text="Видео")
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Что будем стилизовать?"
    )
    await message.answer("Для начала выберите, что будем стилизовать", reply_markup=keyboard)



@dp.message(aiogram.F.text.lower() == "информация" or aiogram.types.Command("help"))
async def send_common_information(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Как это работает?"),
            aiogram.types.KeyboardButton(text="Начать!")
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Как продолжим?"
    )
    await message.answer("Привет!\n\nТы используешь AnimeGAN бота, он создан для стилизации нетяжелых фотографий и коротких видео.\n\n\
Всё, что тебе нужно это просто выбрать файл. Бот проверит, что он подходит по размеру и качеству, сгенерирует новое, уже стилизованное, изображение!",\
        reply_markup=keyboard)



def start_bot():
    asyncio.run(main())