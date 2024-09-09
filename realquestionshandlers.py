# Start Command Handler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Final
from data import get_random_questions

AI_GENERATED: Final = "Assesment book questions"
REAL_PAPER: Final = "Past Year Questions"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Assesment book questions", callback_data="ai_generated")],
        [InlineKeyboardButton("Past Year Questions", callback_data="real_paper")]
    ]
    ## making it inline meaning right under the message
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

# Menu Callback Handler (no changes needed here)
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai_generated":
        context.user_data["question_type"] = AI_GENERATED
        keyboard = [
            [InlineKeyboardButton("Upload Image", callback_data="upload_image")],
            [InlineKeyboardButton("Type Topic", callback_data="type_topic")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Choose how to generate AI-based questions:", reply_markup=reply_markup)

    elif query.data == "real_paper":
        keyboard = [
            [InlineKeyboardButton("Primary", callback_data="primary")],
            [InlineKeyboardButton("Secondary", callback_data="secondary")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["question_type"] = REAL_PAPER
        await query.edit_message_text(text="Choose your grade level:", reply_markup=reply_markup)

# Primary or Secondary Callback Handler (extended for grade selection)
async def cat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "primary":
        context.user_data["category"] = "Primary"
        keyboard = [
            [InlineKeyboardButton("P1", callback_data="P1")],
            [InlineKeyboardButton("P2", callback_data="P2")],
            [InlineKeyboardButton("P3", callback_data="P3")],
            [InlineKeyboardButton("P4", callback_data="P4")],
            [InlineKeyboardButton("P5", callback_data="P5")],
            [InlineKeyboardButton("P6", callback_data="P6")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Choose your grade:", reply_markup=reply_markup)

    elif query.data == "secondary":
        context.user_data["category"] = "Secondary"
        keyboard = [
            [InlineKeyboardButton("Sec1", callback_data="Sec1")],
            [InlineKeyboardButton("Sec2", callback_data="Sec2")],
            [InlineKeyboardButton("Sec3", callback_data="Sec3")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Choose your grade:", reply_markup=reply_markup)

# Subject Selection After Grade
async def grade_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["grade"] = query.data  # Save the grade

    # Define the subjects for the grade
    subjects = ["Math", "Science", "English"]
    keyboard = [[InlineKeyboardButton(sub, callback_data=sub)] for sub in subjects]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Choose a subject:", reply_markup=reply_markup)

# Subtopic Selection After Subject
async def subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["subject"] = query.data  # Save the subject

    # Define subtopics for the chosen subject (you can expand these)
    subtopics = ["Algebra", "Geometry", "Numbers"] if query.data == "Math" else ["Photosynthesis", "Cells", "Forces"]
    keyboard = [[InlineKeyboardButton(sub, callback_data=sub)] for sub in subtopics]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Choose a subtopic:", reply_markup=reply_markup)

# Handling the selected subtopic and generating questions
async def subtopic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["subtopic"] = query.data  # Save the subtopic

    # Now you can generate the real paper questions based on grade, subject, and subtopic
    grade = context.user_data.get("grade")
    subject = context.user_data.get("subject")
    subtopic = context.user_data.get("subtopic")

    # Simulating question generation - replace this with actual retrieval of questions
    questions = get_random_questions(grade, subject, subtopic)

    # Respond with the questions
    if questions:
        response_text = "Here are your questions:\n\n"
        for i, (question, answer) in enumerate(questions, 1):
            response_text += f"Question {i}: {question}\nAnswer: {answer}\n\n"
        await query.edit_message_text(text=response_text)
    else:
        await query.edit_message_text(text="No questions found for the selected criteria.")


# Error Handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")
