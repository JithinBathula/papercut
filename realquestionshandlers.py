from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Final
from data import get_random_questions, get_grades_from_db, get_subjects_for_grade, get_grade_id, get_subject_id, get_topics_for_grade_and_subject
from telegram.constants import ParseMode

AI_GENERATED: Final = "Assessment book questions"
REAL_PAPER: Final = "Past Year Questions"

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)

# Start Command Handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Assessment book questions", callback_data="ai_generated")],
        [InlineKeyboardButton("Past Year Questions", callback_data="real_paper")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    else:
        # For callback queries without message
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose an option:", reply_markup=reply_markup)

# Menu Callback Handler
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai_generated" :
        context.user_data["question_type"] = AI_GENERATED
        keyboard = [
            [InlineKeyboardButton("Upload Image", callback_data="upload_image")],
            [InlineKeyboardButton("Type Topic", callback_data="type_topic")]
            
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query.message:
            await query.edit_message_text(text="Choose how to generate AI-based questions:", reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=query.from_user.id, text="Choose how to generate AI-based questions:", reply_markup=reply_markup)

    elif query.data == "real_paper" :
        grades = await get_grades_from_db()
        valid_grades = [grade_tuple[0] for grade_tuple in grades if isinstance(grade_tuple[0], str) and grade_tuple[0].strip()]

        if not valid_grades:
            if query.message:
                await query.edit_message_text(text="No grades available at the moment.")
            else:
                await context.bot.send_message(chat_id=query.from_user.id, text="No grades available at the moment.")
            return

        keyboard = [
            [InlineKeyboardButton(grade, callback_data=f"grade_{grade}")] for grade in valid_grades
        ] 

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["question_type"] = REAL_PAPER

        if query.message:
            await query.edit_message_text(text="Choose your grade:", reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=query.from_user.id, text="Choose your grade:", reply_markup=reply_markup)
    
    elif query.data == "back_to_start":
        await start_command(update, context)

# Category Callback Handler
async def cat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_start":
        await start_command(update, context)
        return
    elif query.data == "back_to_grades":
        # Redirect to grade selection
        #query.data = "real_paper"
        await menu_callback(update, context)
        return

    context.user_data["selected_grade"] = query.data.split("grade_")[1]
    selected_grade = context.user_data["selected_grade"]
    grade_id = await get_grade_id(selected_grade)

    subjects = await get_subjects_for_grade(grade_id)
    valid_subjects = [subject_tuple[0] for subject_tuple in subjects if isinstance(subject_tuple[0], str) and subject_tuple[0].strip()]

    if not valid_subjects:
        if query.message:
            await query.edit_message_text(text=f"No subjects available for grade {selected_grade}.")
        else:
            await context.bot.send_message(chat_id=query.from_user.id, text=f"No subjects available for grade {selected_grade}.")
        return

    keyboard = [
        [InlineKeyboardButton(subject, callback_data=f"subject_{subject}")] for subject in valid_subjects
    ] 

    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message:
        await query.edit_message_text(text=f"Choose your subject for grade {selected_grade}:", reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=query.from_user.id, text=f"Choose your subject for grade {selected_grade}:", reply_markup=reply_markup)

# Topic Callback Handler
async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_grades":
        # Redirect to grade selection
        #query.data = "real_paper"
        await menu_callback(update, context)
        return
    elif query.data == "back_to_subjects":
        # Redirect to subject selection
        grade = context.user_data.get("selected_grade")
        #query.data = f"grade_{grade}"
        await cat_callback(update, context)
        return

    context.user_data["selected_subject"] = query.data.split("subject_")[1]
    grade = context.user_data.get("selected_grade")
    subject = context.user_data.get("selected_subject")
    grade_id = await get_grade_id(grade)
    subject_id = await get_subject_id(subject)

    topics = await get_topics_for_grade_and_subject(grade_id, subject_id)
    valid_topics = [topic_tuple[0] for topic_tuple in topics if isinstance(topic_tuple[0], str) and topic_tuple[0].strip()]

    if not valid_topics:
        if query.message:
            await query.edit_message_text(text=f"No topics available for subject {subject}.")
        else:
            await context.bot.send_message(chat_id=query.from_user.id, text=f"No topics available for subject {subject}.")
        return

    keyboard = [
        [InlineKeyboardButton(topic, callback_data=f"topic_{topic}")] for topic in valid_topics
    ] 
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message:
        await query.edit_message_text(text=f"Choose your topic for subject {subject}:", reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=query.from_user.id, text=f"Choose your topic for subject {subject}:", reply_markup=reply_markup)

# Generate Questions Callback Handler
async def generate_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_topics":
        # Redirect to topic selection
        subject = context.user_data.get("selected_subject")
        query.data = f"subject_{subject}"
        await topic_callback(update, context)
        return
    elif query.data == "show_answer":
        await show_answer(update, context)
        return
    elif query.data == "new_question":
        # Proceed to generate a new question
        pass
    elif query.data.startswith("topic_"):
        context.user_data["selected_topic"] = query.data.split("topic_")[1]

    grade = context.user_data.get("selected_grade")
    subject = context.user_data.get("selected_subject")
    topic = context.user_data.get("selected_topic")

    questions = await get_random_questions(grade, subject, topic)

    if questions:
        for question, answer in questions:
            context.user_data["current_answer"] = answer  # Store the answer
            formatted_question = f"<b>Question</b>: {question}"
            keyboard = [
                [InlineKeyboardButton("Show Answer", callback_data="show_answer")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if query.message:
                await query.message.reply_text(formatted_question, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await context.bot.send_message(chat_id=query.from_user.id, text=formatted_question, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        if query.message:
            await query.message.reply_text("No questions found for the selected criteria.")
        else:
            await context.bot.send_message(chat_id=query.from_user.id, text="No questions found for the selected criteria.")

# Show Answer Callback Handler
async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    answer = context.user_data.get("current_answer", "No answer available")
    keyboard = [
        [InlineKeyboardButton("Generate New Question", callback_data="new_question")],
        [InlineKeyboardButton("Back to Start", callback_data="back_to_start")]  # Back button to start
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message:
        await query.message.reply_text(f"<b>Answer</b>: {answer}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await context.bot.send_message(chat_id=query.from_user.id, text=f"<b>Answer</b>: {answer}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)

# Handle new question generation
async def new_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.data = f"topic_{context.user_data.get('selected_topic')}"
    await generate_questions(update, context)

# Error Handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")