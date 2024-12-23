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

from aiogram.types import BufferedInputFile, URLInputFile, InputFile, File

from .utils import image_check, video_check

from ..database.core import (
    create_user_if_not_exists,
    decrement_videos_left,
    is_file_exists,
    save_file, update_user_limits, decrement_photos_left,
)
from ..datasphere.Model import Model

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
dp = aiogram.Dispatcher()

info_or_file = ["Больше информации", "Выбрать файл"]
file_fromat_names = ["Фотография", "Видео"]
model_names = ["Arcane", "Shinkai"]
s3 = boto3.client("s3")
BUCKET_NAME = "animegan-s3"

# arcane photo
arcane_photo_model = Model("bt14a37brj1bvff0r2sb", "b1g6t0mm2iipgl1677oo", "bt1cuv003aib6td7fcka", 1024)

# arcane video
arcane_video_model = Model("bt1fcctem48v436sal27", "b1g6t0mm2iipgl1677oo", "bt1gitamskgv67aqi3cc", 512, 'FP16')

# shinkai photo
shinkai_photo_model = Model("bt1rtcs34k5n8v7a1gli", "b1g6t0mm2iipgl1677oo", "bt18q785h1mfo70jls77", 1024)

# shinkai video
shinkai_video_model = Model("bt18j7v0tojjkp3fas45", "b1g6t0mm2iipgl1677oo", "bt18hqbmflk896amqkuj", 512, 'FP16')

async def main():
    await dp.start_polling(bot)


def make_buttons_keyboard(items: list[str]):
    row = [aiogram.types.KeyboardButton(text=item) for item in items]
    return aiogram.types.ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class Form(StatesGroup):
    choosing_format_of_file = State()
    choosing_model = State()
    selecting_file = State()
    file_selecting = State()
    choosing_info_or_file = State()


#START
@dp.message(aiogram.filters.Command("start"))
async def cmd_start(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Привет! 🎨 Добро пожаловать в нашего бота для стилизации фотографий и видео с помощью нейронных сетей! 🚀\n \
            Здесь ты можешь легко преобразить свои фото и видео в уникальные произведения искусства, добавив различные стили. \
            Всё, что тебе нужно — отправить своё изображение или видео, выбрать модель и наблюдать, как твой контент преображается!\n \
            Чтобы начать, просто следуй инструкции.✨",
        reply_markup=make_buttons_keyboard(info_or_file)
    )
    await state.set_state(Form.choosing_info_or_file)


#CANCEL
@dp.message(aiogram.filters.Command("cancel"))
async def cmd_cancel(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="❌ Отменили ваш выбор!",
        reply_markup=make_buttons_keyboard(info_or_file)
    )
    await state.set_state(Form.choosing_info_or_file)


#INFO_OR_FILE
@dp.message(Form.choosing_info_or_file, aiogram.F.text.in_(info_or_file))
async def info_or_file_chooser(message: aiogram.types.Message, state: FSMContext):
    text = ""
    if message.text == info_or_file[0]:
        text="🤖 Для стилизации фото и видео в нашем боте используется GAN.\n \
            GAN (Generative Adversarial Networks) — это тип нейросетей, состоящий из двух модулей: генератора, создающего новые данные, и дискриминатора, оценивающего их реалистичность.\n \
            Эти модули соревнуются друг с другом, что позволяет генерировать высококачественные изображения, видео и другие медиа, часто используемые для стилизации и генерации контента."
    else:
        text = "✅ Выберите формат файла"
    await message.answer(
        text=text,
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )
    await state.set_state(Form.choosing_format_of_file)


#INFO_OR_FILE_INCORRECT
@dp.message(Form.choosing_info_or_file)
async def info_or_file_incorrect(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="👇 Пожалуйста сделайте выбор из предложенного списка",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )


#FILE CHOSEN CORRECT
@dp.message(aiogram.F.text.in_(file_fromat_names))
async def format_chosen_photo(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(chosen_format_of_file=message.text.lower())
    text=""
    if message.text==file_fromat_names[0]:
        text="📷 фото"
    else:
        text="🎥 видео"
    await message.answer(
        text=f"Вы выбрали стилизовать {text}, какой моделью хотите стилизовать 🤔",
        reply_markup=make_buttons_keyboard(model_names)    
    )
    await state.set_state(Form.choosing_model)


#FILE INCORRECT
@dp.message(Form.choosing_format_of_file)
async def format_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="👇 Выберите пожалуйста формат из предложенного списка",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )


#MODEL
@dp.message(Form.choosing_model, aiogram.F.text.in_(model_names))
async def choosing_model_for_photo(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(chosen_model=message.text.lower())
    user_data = await state.get_data()
    print(user_data['chosen_model'])
    for model in model_names:
        if message.text == model:
            await message.answer(
                text=f"Вы выбрали модель {model}, теперь прикрепите файл 📎",
                reply_markup=aiogram.types.ReplyKeyboardRemove()
            )
            break
    await state.set_state(Form.selecting_file)


#MODEL_INCORRET
@dp.message(Form.choosing_model)
async def model_for_photo_chosen_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="👇 У нас нет такой модели, выберите пожалуйста модель из предложенного списка:",
        reply_markup=make_buttons_keyboard(model_names)
    )


#SELECTING PHOTO
@dp.message(Form.selecting_file, aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message, state : FSMContext):
    data = await state.get_data()
    model = data['chosen_model']

    file = await message.bot.get_file(message.photo[-1].file_id)
    if not image_check(file):
        await message.answer("😢 Изображение слишком большое, бот не сможет его обработать")
        return

    user = create_user_if_not_exists(message.from_user.id)
    update_user_limits(user.id)

    if user.photos_left <= 0:
        await message.answer("😢 Ты израсходовал свой лимит на фотографии.\n Приходи завтра!")
        return

    decrement_photos_left(user.id)

    await message.answer("⏱️ Обрабатываем... Возможно, придется немного подождать")

    try:
        unique_id = message.photo[-1].file_unique_id + '-' + model

        if is_file_exists(unique_id):
            url = s3.generate_presigned_url(ClientMethod='get_object',
                                            Params={'Bucket': BUCKET_NAME, 'Key': unique_id + '-processed'})
            send_file = URLInputFile(url, filename='img.jpg')

            await message.reply_photo(send_file)

            return

        binary: io.BytesIO = await bot.download_file(file.file_path)
        img = cv2.imdecode(np.frombuffer(binary.read(), np.uint8), 1)
        binary.seek(0)
        s3.upload_fileobj(binary, BUCKET_NAME, unique_id)

        if model == 'arcane':
            img = arcane_photo_model.process_image(img)
        elif model == 'shinkai':
            img = shinkai_photo_model.process_image(img)

        img_encoded = cv2.imencode('.jpg', img)[1]

        s3.upload_fileobj(BytesIO(img_encoded.tobytes()), BUCKET_NAME, unique_id + '-processed')

        send_file = BufferedInputFile(img_encoded, filename='img.jpg')

        save_file(unique_id, user.id)

        await message.reply_photo(send_file)
        await state.clear()
        await state.set_state(Form.choosing_info_or_file)
        await message.answer(text="Можем продолжать",reply_markup=make_buttons_keyboard(info_or_file))
    except:
        await state.clear()
        await state.set_state(Form.choosing_info_or_file)
        await message.answer(text="Возможно, что-то пошло не так. Если кнопки не работают, используйте /start", reply_markup=make_buttons_keyboard(info_or_file))

#SELECTING VIDEO_NOTE
@dp.message(Form.selecting_file, aiogram.F.content_type == "video_note")
async def get_video_note(message: aiogram.types.Message, state: FSMContext):
    file = await message.bot.get_file(message.video_note.file_id)
    if not video_check(file):
        await message.answer("😢 Кружок слишком большой, бот не сможет его обработать")
        return

    user = create_user_if_not_exists(message.from_user.id)
    update_user_limits(user.id)

    if user.videos_left <= 0:
        await message.answer("😢 Ты израсходовал свой лимит на видео.\n Приходи завтра!")
        return

    decrement_videos_left(user.id)

    await message.answer("⏱️ Обрабатываем... Возможно, придется немного подождать")

    try:
        unique_id = message.video_note.file_unique_id
        binary: io.BytesIO = await bot.download_file(file.file_path)

        data = await state.get_data()
        model = data['chosen_model']
        send_file = process_video(unique_id + '-' + model, binary, user.id, model)

        await message.reply_video(send_file)
        await state.clear()
        await state.set_state(Form.choosing_info_or_file)
        await message.answer(text="Можем продолжать!",reply_markup=make_buttons_keyboard(info_or_file))
    except:
        await state.clear()
        await state.set_state(Form.choosing_info_or_file)
        await message.answer(text="Возможно, что-то пошло не так. Если кнопки не работают, используйте /start",
                             reply_markup=make_buttons_keyboard(info_or_file))


#SELECTING VIDEO
@dp.message(Form.selecting_file, aiogram.F.content_type == "video")
async def get_video(message: aiogram.types.Message, state: FSMContext):
    file = await message.bot.get_file(message.video.file_id)
    if not video_check(file):
        await message.answer("😢 Кружок слишком большой, бот не сможет его обработать")
        return

    user = create_user_if_not_exists(message.from_user.id)
    update_user_limits(user.id)

    if user.videos_left <= 0:
        await message.answer("😢 Ты израсходовал свой лимит на видео.\n Приходи завтра!")
        return

    decrement_videos_left(user.id)

    await message.answer("⏱️ Обрабатываем... Возможно, придется немного подождать")

    try:
        unique_id = message.video.file_unique_id
        binary: io.BytesIO = await bot.download_file(file.file_path)

        data = await state.get_data()
        model = data['chosen_model']
        send_file = process_video(unique_id + '-' + model, binary, user.id, model)

        await message.reply_video(send_file)
        await state.clear()
        await state.set_state(Form.choosing_info_or_file)
        await message.answer(text="Можем продолжать",reply_markup=make_buttons_keyboard(info_or_file))
    except:
        await state.clear()
        await state.set_state(Form.choosing_info_or_file)
        await message.answer(text="Возможно, что-то пошло не так. Если кнопки не работают, используйте /start", reply_markup=make_buttons_keyboard(info_or_file))

def process_video(unique_id: str, binary: io.BytesIO, user_id: int, model: str) -> InputFile:
    if is_file_exists(unique_id):
        url = s3.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': BUCKET_NAME, 'Key': unique_id + '-processed'})
        send_file = URLInputFile(url, filename='vid.mp4')

        return send_file

    s3.upload_fileobj(binary, BUCKET_NAME, unique_id)

    url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': BUCKET_NAME, 'Key': unique_id})
    video_capture = cv2.VideoCapture(url)

    if model == 'arcane':
        video = arcane_video_model.process_video(video_capture)
    elif model == 'shinkai':
        video = shinkai_video_model.process_video(video_capture)
    else:
        video = None

    video.seek(0)

    send_file = BufferedInputFile(video.read(), filename='vid.mp4')
    video.seek(0)

    s3.upload_fileobj(video, BUCKET_NAME, unique_id + '-processed')
    save_file(unique_id, user_id)

    return send_file

#SELECTING PHOTO_VIDEO_NOTE INCORRECT
@dp.message(Form.selecting_file)
async def incorrect_selecting_file(message: aiogram.types.Message):
    await message.answer(
        text="Пожалуйста прикрепите файл нажав на иконку 📎 скрепки и отправьте его в чат",
        reply_markup=aiogram.types.ReplyKeyboardRemove()
    )


def start_bot():
    asyncio.run(main())
