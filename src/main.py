import asyncio
import logging
import sys
import user_storages

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.markdown import hbold

dp = Dispatcher()


class Form(StatesGroup):
    setting_name = State("setting_name")
    setting_personnel_number = State("setting_personnel_number")
    users_submitting = State("users_submitting")
    ok = State("ok")


async def main() -> None:
    # first get the token
    from src.key_reader import read_key
    api_token = read_key()
    # then start the bot
    bot = Bot(token=api_token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


@dp.message(Command("getMyId"))
async def get_my_id(message: Message) -> None:
    await message.answer(f"Your id is {message.from_user.id}")


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    if user_storages.get_user_by_telegram_id(message.from_user.id).isUserExist():
        await message.answer(
            f"Привет!, {hbold(message.from_user.full_name)}! \n Ты уже зарегистрирован, все ок, можешь генерить табели")
    else:
        await message.answer(f"Привет!, {hbold(message.from_user.full_name)}! \n Подскажи мне своё ФИО")
        await state.set_state(Form.setting_name)


@dp.message(Form.setting_name)
async def setting_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(
        f"Спасибо, {hbold(message.from_user.full_name)}! \n Теперь подскажи мне свой табельный номер (это нужно на будущее, когда будет добавленна поддержка отпусков)")
    await state.set_state(Form.setting_personnel_number)


@dp.message(Form.setting_personnel_number)
async def setting_personnel_number(message: Message, state: FSMContext) -> None:
    await state.update_data(personnel_number=message.text)
    user_data = await state.get_data()
    await message.answer(
        f"Спасибо, {hbold(message.from_user.full_name)}! \n Давай проверим данные, которые ты мне дал \n Твое полное имя: {user_data['name']} \n Твой табельный номер: {user_data['personnel_number']} \n Если все верно, то напиши 'Да', если нет, то напиши 'Нет'")
    await state.set_state(Form.users_submitting)


@dp.message(Form.users_submitting)
async def users_submitting(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    if message.text.lower() == "да":
        await state.set_state(Form.ok)
        user_storages.add_new_user(user_data['name'], message.text, message.from_user.id)
        await ok(message, state)
    elif message.text.lower() == "нет":
        await state.set_state(Form.setting_name)
        await setting_name(message, state)
    else:
        await message.answer(
            f"Введи Да или Нет")


@dp.message(Form.ok)
async def ok(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Спасибо, {hbold(message.from_user.full_name)}! \n Теперь я буду генерировать тебе табель")

    await state.set_state(Form.ok)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
