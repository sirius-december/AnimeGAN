import asyncio
import dotenv
import aiogram
import os
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = aiogram.Router()

@router.message(aiogram.filters.Command("start"))
async def cmd_start(message: aiogram.types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Выберите как хотите продолжить:\n\n"
             "Прикрепить файл(/file) или посмтреть больше информации(/info)",
        reply_markup=aiogram.types.ReplyKeyboardRemove()
    )


@router.message(aiogram.filters.Command("cancel"))
async def cmd_cancel(message: aiogram.types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=aiogram.types.ReplyKeyboardRemove()
    )