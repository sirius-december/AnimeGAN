import asyncio
import dotenv
import aiogram
import os
from PIL import Image
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import common

from telegram.database.core import create_user_if_not_exists, decrement_videos_left

dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
dp = aiogram.Dispatcher()

file_fromat_names = ["Видео", "Фотография"]
models_names = ["Первая", "Вторая"]


async def main():
    await dp.start_polling(bot)

def make_buttons_keyboard(items: list[str]):
    row = [aiogram.types.KeyboardButton(text=item) for item in items]
    return aiogram.types.ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class Form(StatesGroup):
    choosing_format_of_file = State()
    choosing_model = State()
    selecting_file = State()

@dp.message(aiogram.filters.StateFilter(None), aiogram.filters.Command("file"))
async def cmd_file(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Выберите, что хотите стилизовать",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )
    await state.set_state(Form.choosing_format_of_file)


@dp.message(Form.choosing_format_of_file, aiogram.F.text.in_(file_fromat_names))
async def format_chosen(message: aiogram.types.Message, state: FSMContext):
    await message.answer(
        text="Выберите какой моделью хотите воспользоваться",
        reply_markup=make_buttons_keyboard(models_names)
    )
    await state.set_state(Form.choosing_model)

@dp.message(Form.choosing_format_of_file)
async def format_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="Выберите пожалуйста формат из предложенного списка",
        reply_markup=make_buttons_keyboard(file_fromat_names)
    )

@dp.message(Form.choosing_model, aiogram.F.text.in_(models_names))
async def model_chosen(message: aiogram.types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали обработать моделью {message.text}",
        reply_markup=aiogram.types.ReplyKeyboardRemove()
    )
    await state.set_state(Form.selecting_file)

@dp.message(Form.choosing_model)
async def model_chosen_incorrect(message: aiogram.types.Message):
    await message.answer(
        text="У нас нет такой модели, выберите пожалуйста модель из предложенного списка:",
        reply_markup=make_buttons_keyboard(models_names)
    )

@dp.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message, state : FSMContext):
    await message.reply_photo(message.photo[-1].file_id)
    file = await message.bot.get_file(message.photo[-1].file_id)
    with Image.open(file) as img:
        img.thumbnail((512,512))
        if(img.getbands()!='L'):
            img = img.convert("RGB")
    await bot.download_file(file.file_path, r"AnimeGAN/downloads/photo/" + str(message.photo[-1].file_id))

@dp.message(aiogram.F.content_type == "video_note")
async def get_video_note(message: aiogram.types.Message):
    await message.reply_video_note(message.video_note.file_id)
    file = await message.bot.get_file(message.video_note.file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/downloads/video_note/" + str(message.video_note.file_id))

@dp.message(aiogram.F.content_type == "video")
async def get_video(message: aiogram.types.Message):
    user = create_user_if_not_exists(message.from_user.id)

    if user.videos_left <= 0:
        await message.answer('Ты израсходовал свой лимит :( Приходи позже')
        return

    decrement_videos_left(user.id)

    await message.reply_video(message.video.file_id)
    file = await message.bot.get_file(message.video.file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/downloads/video/" + str(message.video.file_id))


def make_dir():
    if not os.path.exists(r"AnimeGAN/downloads/"):
        os.mkdir("AnimeGAN/downloads")
    if not os.path.exists(r"AnimeGAN/downloads/photo/"):
        os.mkdir("AnimeGAN/downloads/photo/")
    if not os.path.exists(r"AnimeGAN/downloads/video/"):
        os.mkdir("AnimeGAN/downloads/video/")
    if not os.path.exists(r"AnimeGAN/downloads/video_note/"):
        os.mkdir("AnimeGAN/downloads/video_note/")


def start_bot():
    make_dir()
    asyncio.run(main())