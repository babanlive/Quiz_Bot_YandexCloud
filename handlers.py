from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from service import (
    get_total_questions,
    get_question,
    get_question_from_db,
    get_quiz_index,
    new_quiz,
    update_quiz_index,
)

router = Router()


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    await callback.message.answer("Верно!")
    current_question_index, score = await get_quiz_index(callback.from_user.id)
    current_question_index += 1
    score += 1
    await update_quiz_index(callback.from_user.id, current_question_index, score)

    total_questions = await get_total_questions()

    if current_question_index < total_questions:
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(
            f"Это был последний вопрос. Квиз завершен!\nВы правильно ответили на: {score} из 10 вопросов"
        )


@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    current_question_index, score = await get_quiz_index(callback.from_user.id)

    results = await get_question_from_db(callback.from_user.id)

    options = results["options"]
    correct_option = results["correct_option"]

    await callback.message.answer(
        f"Неправильно. Правильный ответ: {options[correct_option]}"
    )

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, score)

    total_questions = await get_total_questions()

    if current_question_index < total_questions:
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(
            f"Это был последний вопрос. Квиз завершен!\nВы правильно ответили на: {score} из 10 вопросов"
        )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))

    image_url = "https://storage.yandexcloud.net/quizbacket/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0_20240919_230814.png"

    await message.answer_photo(photo=image_url, caption="Добро пожаловать в квиз!")
    await message.answer(
        "Нажмите кнопку, чтобы начать!",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)
