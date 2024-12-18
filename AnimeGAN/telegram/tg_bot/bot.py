import asyncio
import aiogram.filters
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


info_or_file = ["Больше информации", "Выбрать файл"]
file_fromat_names = ["Фотография", "Видео"]
models_names_for_photo = ["Первая", "Вторая"]
models_names_for_video = ["Первая", "Вторая"]


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