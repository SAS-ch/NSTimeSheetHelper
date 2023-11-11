import asyncio
import datetime
import logging
import os
import sys

import openpyxl

import user_storages

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InputFile, FSInputFile
from aiogram.utils.markdown import hbold

from src.generate_pdf import convert_to_pdf
from src.generate_xlsx import fill_workbook_with_data_time_format, get_holidays_from_xmlcalendar, MONTHS_RU
from src.key_reader import read_libre_office_path

dp = Dispatcher()


class Form(StatesGroup):
    setting_name = State("setting_name")
    setting_personnel_number = State("setting_personnel_number")
    setting_department = State("setting_department")

    setting_working_time_for_Monday = State("setting_working_time_for_Monday")
    setting_working_time_for_Tuesday = State("setting_working_time_for_Tuesday")
    setting_working_time_for_Wednesday = State("setting_working_time_for_Wednesday")
    setting_working_time_for_Thursday = State("setting_working_time_for_Thursday")
    setting_working_time_for_Friday = State("setting_working_time_for_Friday")

    setting_need_to_randomize = State("setting_need_to_radomize")

    users_submitting = State("users_submitting")
    ok = State("ok")


async def main() -> None:
    # first get the token
    from src.key_reader import read_key
    api_token = read_key()
    # then start the bot
    bot = Bot(token=api_token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


@dp.message(Command("get_time_sheet"))
async def get_time_sheet(message: Message) -> None:
    user = user_storages.get_user_by_telegram_id(message.from_user.id)
    if user.isUserExist():
        await message.answer("Твой табель генерируется")
    else:
        await message.answer("Ты не зарегистрирован, напиши /start")

    template_path = "template.xlsx"
    workbook = openpyxl.load_workbook(template_path)
    # get current year
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    filled_workbook_adjusted = fill_workbook_with_data_time_format(workbook, year, month, user.name, user.department,
                                                                   get_holidays_from_xmlcalendar(year),
                                                                   user.working_time, user.randomize)
    output_path_adjusted = f"../generated/g{user.telegram_id}_{year}_{month}.xlsx"
    output_path_pdf = "../generated"
    filled_workbook_adjusted.save(output_path_adjusted)
    convert_to_pdf(output_path_adjusted, output_path_pdf, read_libre_office_path())

    await message.answer_document(
        FSInputFile(f"../generated/g{user.telegram_id}_{year}_{month}.xlsx",
                    f"Табель_{user.name}_за_{MONTHS_RU[month]}_{year}год.xlsx"))

    # Send the generated PDF file to the user
    await message.answer_document(
        FSInputFile(f"../generated/g{user.telegram_id}_{year}_{month}.pdf",
                    f"Табель_{user.name}_за_{MONTHS_RU[month]}_{year}год.pdf"))
    # remove generate file from filesystem
    os.remove(f"../generated/g{user.telegram_id}_{year}_{month}.xlsx")
    os.remove(f"../generated/g{user.telegram_id}_{year}_{month}.pdf")


@dp.message(Command("get_my_id"))
async def get_my_id(message: Message) -> None:
    await message.answer(f"Your id is {message.from_user.id}")


@dp.message(Command("remove_me"))
async def remove_me(message: Message) -> None:
    user = user_storages.get_user_by_telegram_id(message.from_user.id)
    if user.isUserExist():
        user_storages.remove_user_by_telegram_id(user)
        await message.answer("Ты удален из базы")
    else:
        await message.answer("Ты не зарегистрирован, напиши /start")


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        user_exist = user_storages.get_user_by_telegram_id(message.from_user.id).isUserExist()
    except:
        user_exist = False
    if user_exist:
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
    # user_data = await state.get_data()
    await message.answer(
        f"Спасибо, {hbold(message.from_user.full_name)}! \n Теперь подскажи мне свой отдел")
    await state.set_state(Form.setting_department)


@dp.message(Form.setting_department)
async def setting_department(message: Message, state: FSMContext) -> None:
    await state.update_data(department=message.text)
    await message.answer(
        f"Так, теперь давай разберемся как ты работаешь, напиши свой график работы в понеделький в таком формате: \n 9:00-12:00 13:00-17:30")
    await state.set_state(Form.setting_working_time_for_Monday)


@dp.message(Form.setting_working_time_for_Monday)
async def setting_working_time_for_Monday(message: Message, state: FSMContext) -> None:
    await state.update_data(working_time_for_Monday=message.text)
    await message.answer(
        f"Так, теперь давай разберемся как ты работаешь, напиши свой график работы во вторник в таком формате: \n 9:00-12:00 13:00-17:30")
    await state.set_state(Form.setting_working_time_for_Tuesday)


@dp.message(Form.setting_working_time_for_Tuesday)
async def setting_working_time_for_Tuesday(message: Message, state: FSMContext) -> None:
    await state.update_data(working_time_for_Tuesday=message.text)
    await message.answer(
        f"Так, теперь давай разберемся как ты работаешь, напиши свой график работы в среду в таком формате: \n 9:00-12:00 13:00-17:30")
    await state.set_state(Form.setting_working_time_for_Wednesday)


@dp.message(Form.setting_working_time_for_Wednesday)
async def setting_working_time_for_Wednesday(message: Message, state: FSMContext) -> None:
    await state.update_data(working_time_for_Wednesday=message.text)
    await message.answer(
        f"Так, теперь давай разберемся как ты работаешь, напиши свой график работы в четверг в таком формате: \n 9:00-12:00 13:00-17:30")
    await state.set_state(Form.setting_working_time_for_Thursday)


@dp.message(Form.setting_working_time_for_Thursday)
async def setting_working_time_for_Thursday(message: Message, state: FSMContext) -> None:
    await state.update_data(working_time_for_Thursday=message.text)
    await message.answer(
        f"Так, теперь давай разберемся как ты работаешь, напиши свой график работы в пятницу в таком формате: \n 9:00-12:00 13:00-17:30")
    await state.set_state(Form.setting_working_time_for_Friday)


@dp.message(Form.setting_working_time_for_Friday)
async def setting_working_time_for_Friday(message: Message, state: FSMContext) -> None:
    await state.update_data(working_time_for_Friday=message.text)
    await message.answer(
        f"Так, теперь скажи мне нужно ли при генерации табелей тебе немного рандомить время обеда, прихода и ухода с работы? (Если у тебя указано время прихода 9:30 то может сгенерировать 9:30, 9:35, 9:40, 9:45) \n Напиши 'Да' или 'Нет'")
    await state.set_state(Form.setting_need_to_randomize)


@dp.message(Form.setting_need_to_randomize)
async def setting_need_to_randomize(message: Message, state: FSMContext) -> None:
    await state.update_data(need_to_radomize=message.text.lower() == "да")
    user_data = await state.get_data()
    await message.answer(
        f"Спасибо, {hbold(message.from_user.full_name)}! \n Давай проверим данные, которые ты мне дал \n Твое полное имя: {user_data['name']} \n Твой табельный номер: {user_data['personnel_number']} \n Твой график работы по понедельникам: {user_data['working_time_for_Monday']}, по вторникам:"
        f"{user_data['working_time_for_Tuesday']}, средам: {user_data['working_time_for_Wednesday']}, четвергам: {user_data['working_time_for_Thursday']}, пятницам: {user_data['working_time_for_Friday']}, ты хочешь делать время прихода случайными: {user_data['need_to_radomize']}   Если все верно, то напиши 'Да', если нет, то напиши 'Нет'")
    await state.set_state(Form.users_submitting)


@dp.message(Form.users_submitting)
async def users_submitting(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    if message.text.lower() == "да":
        await state.set_state(Form.ok)

        weekly_schedule = {0: user_storages.parse_schedule(user_data['working_time_for_Monday']),
                           1: user_storages.parse_schedule(user_data['working_time_for_Tuesday']),
                           2: user_storages.parse_schedule(user_data['working_time_for_Wednesday']),
                           3: user_storages.parse_schedule(user_data['working_time_for_Thursday']),
                           4: user_storages.parse_schedule(user_data['working_time_for_Friday'])}

        user = user_storages.User(
            user_data['name'],
            user_data['personnel_number'],
            message.from_user.id,
            weekly_schedule,
            user_data['department'],
            user_data['need_to_radomize']
        )
        user_storages.add_new_user(user)
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
