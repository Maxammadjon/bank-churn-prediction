import sys
import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardRemove
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.predict import predict_client

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN не найден')

router = Router()



# ---------------- КЛАВИАТУРЫ ----------------

kb_start = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='🚀 Начать прогноз')]
    ]
)

country_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🇫🇷 Франция'),
            KeyboardButton(text='🇩🇪 Германия')
        ],
        [
            KeyboardButton(text='🇪🇸 Испания')
        ]
    ],
    resize_keyboard=True
)

gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='👨 Мужчина'),
            KeyboardButton(text='👩 Женщина')
        ]
    ],
    resize_keyboard=True
)

yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='✅ Да'),
            KeyboardButton(text='❌ Нет')
        ]
    ],
    resize_keyboard=True
)



kb_finish = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='📈 Показать результат',
                callback_data='show_result'
            )
        ]
    ]
)

# ---------------- FSM ----------------

class ClientForm(StatesGroup):
    credit_score = State()
    geography = State()
    gender = State()
    age = State()
    tenure = State()
    balance = State()
    products = State()
    has_card = State()
    active_member = State()
    salary = State()

# ---------------- START ----------------

@router.message(Command('start'))
async def cmd_start(message: Message):
    text = (
        'Здравствуйте!\n\n'
        'Я бот для прогнозирования оттока клиентов банка.\n\n'
        'Нажмите "Начать"'
    )

    await message.answer(text, reply_markup=kb_start)

@router.message(F.text == '🚀 Начать прогноз')
async def start_form(message: Message, state: FSMContext):
    await state.set_state(ClientForm.credit_score)
    await message.answer('Введите кредитный рейтинг клиента:', reply_markup=ReplyKeyboardRemove())

# ---------------- CREDIT SCORE ----------------

@router.message(ClientForm.credit_score)
async def save_credit_score(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(',', '.'))

        if value < 350 or value > 850:
            await message.answer(
                'Ошибка ❌\n'
                'Кредитный рейтинг должен быть от 350 до 850'
            )
            return

        await state.update_data(CreditScore=value)

        await state.set_state(ClientForm.geography)

        await message.answer(
            '🌍 Выберите страну:',
            reply_markup=country_kb
        )

    except:
        await message.answer(
            'Ошибка ❌\n'
            'Введите число.\n'
            'Пример: 650'
        )

# ---------------- GEOGRAPHY ----------------

@router.message(ClientForm.geography)
async def save_geography(message: Message, state: FSMContext):

    text = message.text.lower()

    countries = {
        '🇫🇷 франция': 'France',
        '🇩🇪 германия': 'Germany',
        '🇪🇸 испания': 'Spain'
    }

    if text not in countries:
        await message.answer(
            '❌ Выберите страну кнопкой ниже',
            reply_markup=country_kb
        )
        return

    await state.update_data(
        Geography=countries[text]
    )

    await state.set_state(ClientForm.gender)

    await message.answer(
        '👤 Выберите пол:',
        reply_markup=gender_kb
    )

# ---------------- GENDER ----------------

@router.message(ClientForm.gender)
async def save_gender(message: Message, state: FSMContext):

    text = message.text.lower()

    genders = {
        '👨 мужчина': 'Male',
        '👩 женщина': 'Female'
    }

    if text not in genders:
        await message.answer(
            '❌ Выберите пол кнопкой ниже',
            reply_markup=gender_kb
        )
        return

    await state.update_data(
        Gender=genders[text]
    )

    await state.set_state(ClientForm.age)

    await message.answer(
        '🎂 Введите возраст:',
        reply_markup=ReplyKeyboardRemove()
    )



# ---------------- AGE ----------------

@router.message(ClientForm.age)
async def save_age(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(',', '.'))

        if value < 18 or value > 100:
            await message.answer(
                'Ошибка ❌\n'
                'Возраст должен быть от 18 до 100'
            )
            return

        await state.update_data(Age=value)

        await state.set_state(ClientForm.tenure)

        await message.answer(
            'Введите стаж клиента в банке:'
        )

    except:
        await message.answer(
            'Ошибка ❌\n'
            'Введите число'
        )

# ---------------- TENURE ----------------

@router.message(ClientForm.tenure)
async def save_tenure(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(',', '.'))

        if value < 0 or value > 50:
            await message.answer(
                'Ошибка ❌\n'
                'Стаж должен быть от 0 до 50'
            )
            return

        await state.update_data(Tenure=value)

        await state.set_state(ClientForm.balance)

        await message.answer(
            'Введите баланс клиента:'
        )

    except:
        await message.answer(
            'Ошибка ❌\n'
            'Введите число'
        )

# ---------------- BALANCE ----------------

@router.message(ClientForm.balance)
async def save_balance(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(',', '.'))

        if value < 0:
            await message.answer(
                'Ошибка ❌\n'
                'Баланс не может быть отрицательным'
            )
            return

        await state.update_data(Balance=value)

        await state.set_state(ClientForm.products)

        await message.answer(
            'Введите количество продуктов:'
        )

    except:
        await message.answer(
            'Ошибка ❌\n'
            'Введите число'
        )


# ---------------- PRODUCTS ----------------


@router.message(ClientForm.products)
async def save_products(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(',', '.'))

        if value < 1 or value > 10:
            await message.answer(
                'Ошибка ❌\n'
                'Количество продуктов должно быть от 1 до 10'
            )
            return

        await state.update_data(
            NumOfProducts=value
        )

        await state.set_state(ClientForm.has_card)

        await message.answer(
            '💳 Есть кредитная карта?',
            reply_markup=yes_no_kb
        )

    except:
        await message.answer(
            'Ошибка ❌\n'
            'Введите число'
        )

# ---------------- CARD ----------------

@router.message(ClientForm.has_card)
async def save_has_card(message: Message, state: FSMContext):

    text = message.text.lower()

    values = {
        '✅ да': 1,
        '❌ нет': 0
    }

    if text not in values:
        await message.answer(
            '❌ Выберите кнопкой:',
            reply_markup=yes_no_kb
        )
        return

    await state.update_data(
        HasCrCard=values[text]
    )

    await state.set_state(ClientForm.active_member)

    await message.answer(
        '🟢 Активный клиент?',
        reply_markup=yes_no_kb
    )

# ---------------- ACTIVE MEMBER ----------------

@router.message(ClientForm.active_member)
async def save_active_member(message: Message, state: FSMContext):

    text = message.text.lower()

    values = {
        '✅ да': 1,
        '❌ нет': 0
    }

    if text not in values:
        await message.answer(
            '❌ Выберите кнопкой:',
            reply_markup=yes_no_kb
        )
        return

    await state.update_data(
        IsActiveMember=values[text]
    )

    await state.set_state(ClientForm.salary)

    await message.answer(
        '💰 Введите зарплату клиента:',
        reply_markup=ReplyKeyboardRemove()
    )

# ---------------- SALARY ----------------

@router.message(ClientForm.salary)
async def save_salary(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(',', '.'))

        if value < 0:
            await message.answer(
                'Ошибка ❌\n'
                'Зарплата не может быть отрицательной'
            )
            return

        await state.update_data(
            EstimatedSalary=value
        )

        await message.answer(
            'Нажмите кнопку ниже для результата',
            reply_markup=kb_finish
        )

    except:
        await message.answer(
            'Ошибка ❌\n'
            'Введите число'
        )

# ---------------- RESULT ----------------

@router.callback_query(F.data == 'show_result')
async def show_result(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()

        result = predict_client(data)

        probability = result['probability'] * 100

        if result['prediction'] == 'Exited':

            answer = (
                f'🔴 <b>Результат прогнозирования</b>\n\n'
                f'❌ <b>Клиент может уйти из банка</b>\n'
                f'📉 Вероятность ухода: <b>{probability:.2f}%</b>'
            )

        else:

            answer = (
                f'🟢 <b>Результат прогнозирования</b>\n\n'
                f'✅ <b>Клиент останется в банке</b>\n'
                f'📈 Вероятность ухода: <b>{probability:.2f}%</b>'
            )

        await callback.message.answer(
            answer,
            parse_mode='HTML'
        )

        await state.clear()

    except Exception as e:
        await callback.message.answer(
            answer,
            parse_mode='HTML'
        )
# ---------------- MAIN ----------------

async def main():
    bot = Bot(token=BOT_TOKEN)

    await bot.set_my_commands([
        BotCommand(command='start', description='Запустить бота')
    ])

    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    print('BOT STARTED')

    asyncio.run(main())