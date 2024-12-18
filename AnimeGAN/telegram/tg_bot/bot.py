import asyncio
import io
from utils import image_check, video_check
import dotenv
import aiogram
import os
import boto3
import logging

from telegram.database.core import (
    create_user_if_not_exists,
    decrement_videos_left,
    save_file,
    is_file_exists,
)

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
dp = aiogram.Dispatcher()

s3 = boto3.client("s3")
BUCKET_NAME = "animegan-s3"


async def main():
    await dp.start_polling(bot)


@dp.message(aiogram.filters.Command("start"))
async def send_welcome(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Информация"),
            aiogram.types.KeyboardButton(text="Начать!"),
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите как продолжить",
    )
    await message.answer("Добро пожаловать в AnimeGan!", reply_markup=keyboard)


@dp.message(aiogram.F.text.lower() == "начать!")
async def photo_or_video_choose(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Фотография"),
            aiogram.types.KeyboardButton(text="Видео"),
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Что будем стилизовать?",
    )
    await message.answer(
        "Для начала выберите, что будем стилизовать", reply_markup=keyboard
    )


@dp.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message):
    file = await message.bot.get_file(message.video.file_id)
    if not image_check(file):
        logging.info("image file is too large")
        return

    # <TODO> аналогично как в get_video


@dp.message(aiogram.F.content_type == "video_note")
async def get_video_note(message: aiogram.types.Message):
    file = await message.bot.get_file(message.video.file_id)
    if not video_check(file):
        logging.info("video_note file is too large")
        return

    # <TODO> аналогично как в get_video


@dp.message(aiogram.F.content_type == "video")
async def get_video(message: aiogram.types.Message):
    file = await message.bot.get_file(message.video.file_id)
    if not video_check(file):
        logging.info("video file is too large")
        return

    user = create_user_if_not_exists(message.from_user.id)
    # <TODO> где-то здесь (или внутри функции выше) должна быть логика обновления лимитов для юзера
    # условно его лимиты действуют в течение суток и с каждым днем они должны обновляться
    if user.videos_left <= 0:
        await message.answer("Ты израсходовал свой лимит :( Приходи позже")
        return

    decrement_videos_left(user.id)

    unique_id = message.video.file_unique_id
    if not is_file_exists(unique_id):
        save_file(unique_id, user.id)
        binary: io.BytesIO = await bot.download_file(file.file_path)

        s3.upload_fileobj(binary, BUCKET_NAME, unique_id)

    # <TODO> отправить в ноду для обработки, сохранить обработанный файл в s3, вернуть пользователю ответом обработанный файл


@dp.message(aiogram.F.text.lower() == "информация" or aiogram.types.Command("help"))
async def send_common_information(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Как это работает?"),
            aiogram.types.KeyboardButton(text="Начать!"),
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Как продолжим?"
    )
    await message.answer(
        "Привет!\n\nТы используешь AnimeGAN бота, он создан для стилизации нетяжелых фотографий и коротких видео.\n\n\
Всё, что тебе нужно это просто выбрать файл. Бот проверит, что он подходит по размеру и качеству, сгенерирует новое, уже стилизованное, изображение!",
        reply_markup=keyboard,
    )


def start_bot():
    asyncio.run(main())
