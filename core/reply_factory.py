
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is None:
        return False, "No current question selected."

    question = PYTHON_QUESTION_LIST[current_question_id]
    correct_answer = question['answer']

    # Store the user's answer in session
    if 'answers' not in session:
        session['answers'] = {}
    session['answers'][current_question_id] = answer

    # Validate the user's answer
    if answer == correct_answer:
        return True, ""
    else:
        return False, "Incorrect answer. The correct answer is: {}".format(correct_answer)


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    next_question_id = current_question_id + 1 if current_question_id is not None else 0
    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]
        return next_question['question_text'], next_question_id
    else:
        return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''

    answers = session.get('answers', {})
    correct_count = sum(1 for k, v in answers.items() if v == PYTHON_QUESTION_LIST[int(k)]['answer'])
    total = len(PYTHON_QUESTION_LIST)
    return "Quiz completed! You got {}/{} correct answers.".format(correct_count, total)
