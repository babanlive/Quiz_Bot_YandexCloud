from database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import quiz_data


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data="right_answer"
                if option == right_answer
                else "wrong_answer",
            )
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question_from_db(user_id):
    question_index, score = await get_quiz_index(user_id)

    query = """
        DECLARE $question_id AS Uint64;
        
        SELECT question, options, correct_option
        FROM `quiz_questions`
        WHERE question_id == $question_id;
    """

    results = execute_select_query(pool, query, question_id=question_index)

    question = (
        results[0]["question"].decode("utf-8")
        if isinstance(results[0]["question"], bytes)
        else results[0]["question"]
    )
    options = (
        results[0]["options"].decode("utf-8").split(";")
        if isinstance(results[0]["options"], bytes)
        else results[0]["options"].split(";")
    )
    correct_option = results[0]["correct_option"]

    return {"question": question, "options": options, "correct_option": correct_option}


async def get_question(message, user_id):
    results = await get_question_from_db(user_id)

    question = results["question"]
    options = results["options"]
    correct_option = results["correct_option"]

    kb = generate_options_keyboard(options, options[correct_option])
    await message.answer(f"{question}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    score = 0
    await update_quiz_index(user_id, question_index=current_question_index, score=score)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index, score
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0, 0
    if results[0]["question_index"] is None:
        return 0, 0
    return results[0]["question_index"], results[0]["score"]


async def update_quiz_index(user_id, question_index, score):
    query = """
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;
        DECLARE $score AS Uint64;

        UPSERT INTO `quiz_state` (user_id, question_index, score)
        VALUES ($user_id, $question_index, $score);
    """
    execute_update_query(
        pool, query, user_id=user_id, question_index=question_index, score=score
    )

async def get_total_questions():
    query = """
    SELECT COUNT(*) AS total_questions
    FROM `quiz_questions`;
    """

    results = execute_select_query(pool, query)
    total_questions = results[0]["total_questions"]

    return total_questions