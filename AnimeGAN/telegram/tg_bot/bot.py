import asyncio
import aiogram.filters
import dotenv
import aiogram
import os
from PIL import Image
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
import os

import aiogram
import boto3
import dotenv

from .utils import image_check, video_check

from telegram.database.core import (
    create_user_if_not_exists,
    decrement_videos_left,
    is_file_exists,
    save_file,
)


logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv("./.env")

bot = aiogram.Bot(os.environ["TOKEN"])
dp = aiogram.Dispatcher()


info_or_file = ["Больше информации", "Выбрать файл"]
file_fromat_names = ["Фотография", "Видео"]
models_names_for_photo = ["Первая", "Вторая"]
models_names_for_video = ["Первая", "Вторая"]
s3 = boto3.client("s3")
BUCKET_NAME = "animegan-s3"


async def main():
    await dp.start_polling(bot)

def make_buttons_keyboard(items: list[str]):
    row = [aiogram.types.KeyboardButton(text=item) for item in items]
    return aiogram.types.ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class Form(StatesGroup):
    choosing_format_of_file = State()
    choosing_model_for_photo = State()
    choosing_model_for_video = State()
    selecting_file = State()
    choosing_info_or_file = State()
    end = State()



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
        
    )


#INFO_OR_FILE
# @dp.message(Form.choosing_info_or_file, aiogram.F.text.in_(info_or_file))
# async def info_or_file_chooser(mess)

#INFO
@dp.message(Form.choosing_info_or_file, aiogram.F.text==info_or_file[0])
async def file_chooser(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Инфа про бота",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )
    await state.set_state(Form.choosing_format_of_file)


#FILE
@dp.message(Form.choosing_info_or_file, aiogram.F.text==info_or_file[1])
async def file_chooser(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Выберите, что хотите стилизовать",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )
    await state.set_state(Form.choosing_format_of_file)



#FILE CHOSEN CORRECT
@dp.message(Form.choosing_format_of_file, aiogram.F.text.in_(file_fromat_names))
async def format_chosen_photo(message: aiogram.types.Message, state: FSMContext):
    # TODO: Дать прикрепить файл
    if message.text==file_fromat_names[0]:
        # TODO: Проверить, что файл нужного формата и отредактировать его
        await message.answer(
            text="Вы выбрали стилизовать фото, выберите какой моделью хотите воспользоваться",
            reply_markup=make_buttons_keyboard(models_names_for_photo)
        )
    else:
        # TODO: Проверить, что файл нужного формата и отредактировать его
        await message.answer(
            text="Вы выбрали стилизовать видео, выберите какой моделью хотите воспользоваться",
            reply_markup=make_buttons_keyboard(models_names_for_photo)
        )
    await state.set_state(Form.choosing_model)


#FILE Inccorect
@dp.message(Form.choosing_format_of_file)
async def format_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="Выберите пожалуйста формат из предложенного списка",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )


#MODEL_FOR_PHOTO
@dp.message(Form.choosing_model_for_photo, aiogram.F.text.in_(models_names_for_photo))
async def choosing_model_for_photo(message: aiogram.types.Message, state: FSMContext):
    for model in models_names_for_photo:
        if message.text == model:
            await message.answer(text=f"Вы выбрали модель {model}")
            await state.set_state(Form.end)
            break


#MODEL_FOR_VIDEO
@dp.message(Form.choosing_model_for_video, aiogram.F.text.in_(models_names_for_video))
async def choosing_model_for_video(message: aiogram.types.Message, state: FSMContext):
    for model in models_names_for_video:
        if message.text == model:
            await message.answer(text=f"Вы выбрали модель {model}")
            await state.set_state(Form.end)
            break

#MODEL_PHOTO_INCORRET
@dp.message(Form.choosing_model_for_photo)
async def model_for_photo_chosen_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="У нас нет такой модели для фотографий, выберите пожалуйста модель из предложенного списка:",
        reply_markup=make_buttons_keyboard(models_names_for_photo)
    )

#MODEL_VIDEO_INCORRET
@dp.message(Form.choosing_model_for_photo)
async def model_for_video_chosen_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="У нас нет такой модели для видео, выберите пожалуйста модель из предложенного списка:",
        reply_markup=make_buttons_keyboard(models_names_for_video)
    )


@dp.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message, state : FSMContext):
    await message.reply_photo(message.photo[-1].file_id)
    file = await message.bot.get_file(message.photo[-1].file_id)
    if not image_check(file):
        logging.info("image file is too large")
        return

    # <TODO> аналогично как в get_video


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
