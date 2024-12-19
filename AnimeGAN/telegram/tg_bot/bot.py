import asyncio
from io import BytesIO

import aiogram.filters
import cv2
import dotenv
import aiogram
import os

import numpy as np
from PIL import Image
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
import boto3
import dotenv
import io

from aiogram.types import BufferedInputFile

from .utils import image_check, video_check

from telegram.database.core import (
    create_user_if_not_exists,
    decrement_videos_left,
    is_file_exists,
    save_file,
)
from ..datasphere.Model import Model

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
dp = aiogram.Dispatcher()


info_or_file = ["Больше информации", "Выбрать файл"]
file_fromat_names = ["Фотография", "Видео"]
model_names = ["Hayao", "Arcane", "Shinkai"]
s3 = boto3.client("s3")
BUCKET_NAME = "animegan-s3"

model = Model("bt1soaafjmhtf1f2j6ko", "b1gbnhth47rchbtmstlr", "bt16jq41r6uelhtvm018", 512)


async def main():
    await dp.start_polling(bot)

def make_buttons_keyboard(items: list[str]):
    row = [aiogram.types.KeyboardButton(text=item) for item in items]
    return aiogram.types.ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class Form(StatesGroup):
    choosing_format_of_file = State()
    choosing_model = State()
    selecting_file = State()
    choosing_info_or_file = State()



#START
@dp.message(aiogram.filters.Command("start"))
async def cmd_start(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Привет! Я бот для стилизации нетяжелых фото и видео",
        reply_markup=make_buttons_keyboard(info_or_file)
    )
    await state.set_state(Form.choosing_info_or_file)


#CANCEL
@dp.message(aiogram.filters.Command("cancel"))
async def cmd_cancel(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Отменили ваш выбор",
        reply_markup=make_buttons_keyboard(info_or_file)
    )
    await state.set_state(Form.choosing_info_or_file)


#INFO_OR_FILE
@dp.message(Form.choosing_info_or_file, aiogram.F.text.in_(info_or_file))
async def info_or_file_chooser(message: aiogram.types.Message, state: FSMContext):
    text=""
    if message.text==info_or_file[0]:
        text="Инфа про бота"
    else:
        text="Выберите формат файла"
    await message.answer(
        text=text,
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )
    await state.set_state(Form.choosing_format_of_file)



#INFO_OR_FILE_INCORRECT
@dp.message(Form.choosing_info_or_file)
async def info_or_file_incorrect(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Пожалуйста сделайте выбор из списка",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )


#FILE CHOSEN CORRECT
@dp.message(Form.choosing_format_of_file, aiogram.F.text.in_(file_fromat_names))
async def format_chosen_photo(message: aiogram.types.Message, state: FSMContext):
    # TODO: Дать прикрепить файл
    # TODO: Проверить, что файл нужного формата и отредактировать его
    text=""
    if message.text==file_fromat_names[0]:
        text="Вы выбрали стилизовать фото, выберите какой моделью хотите воспользоваться"
    else:
        text="Вы выбрали стилизовать видео, выберите какой моделью хотите воспользоваться"
    await message.answer(
        text=text,
        reply_markup=make_buttons_keyboard(model_names)
    )
    await state.set_state(Form.choosing_model)


#FILE INCORRECT
@dp.message(Form.choosing_format_of_file)
async def format_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="Выберите пожалуйста формат из предложенного списка",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )



#MODEL
@dp.message(Form.choosing_model, aiogram.F.text.in_(model_names))
async def choosing_model_for_photo(message: aiogram.types.Message, state: FSMContext):
    # <TODO> : Надо пронести файл по всем переходам между state
    for model in model_names:
        if message.text == model:
            await message.answer(text=f"Вы выбрали модель {model}, идет обработка")
            print(state.get_state)
            break
    # <TODO> : Отправить файл на обработку и сохранить новое 
    await message.answer(
        text="Вот что у нас получилось",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )
    await state.set_state(Form.choosing_format_of_file)
    


#MODEL_INCORRET
@dp.message(Form.choosing_model)
async def model_for_photo_chosen_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="У нас нет такой модели, выберите пожалуйста модель из предложенного списка:",
        reply_markup=make_buttons_keyboard(model_names)
    )


@dp.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message, state : FSMContext):
    file = await message.bot.get_file(message.photo[-1].file_id)
    if not image_check(file):
        logging.info("image file is too large")
        return

    # <TODO> аналогично как в get_video

    binary: io.BytesIO = await bot.download_file(file.file_path)
    img = cv2.imdecode(np.frombuffer(binary.read(), np.uint8), 1)

    img = model.process(img)

    img_encoded = cv2.imencode('.jpg', img)[1]
    send_file = BufferedInputFile(img_encoded, filename='img.jpg')
    await message.reply_photo(send_file)


@dp.message(aiogram.F.content_type == "video_note")
async def get_video_note(message: aiogram.types.Message):
    file = await message.bot.get_file(message.video_note.file_id)
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



def start_bot():
    asyncio.run(main())
