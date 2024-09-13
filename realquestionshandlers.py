# Start Command Handler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Final
from data import get_random_questions, get_subjects_from_db, get_grades_for_subject

AI_GENERATED: Final = "Assesment book questions"
REAL_PAPER: Final = "Past Year Questions"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Assessment book questions", callback_data="ai_generated")],
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
        # Get subjects from the database
        subjects = await get_subjects_from_db()
        valid_subjects = [subject_tuple[0] for subject_tuple in subjects if isinstance(subject_tuple[0], str) and subject_tuple[0].strip()]

        if not valid_subjects:
            await query.edit_message_text(text="No subjects available at the moment.")
            return

        keyboard = [
            [InlineKeyboardButton(subject, callback_data=f"subject_{subject}")] for subject in valid_subjects
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["question_type"] = REAL_PAPER
        await query.edit_message_text(text="Choose your subject:", reply_markup=reply_markup)
        
# Primary or Secondary Callback Handler (extended for grade selection)
async def cat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["subject"] = query.data
    selected_subject = query.data.split("subject_")[1]


    print (selected_subject)
    
        # Query the database for grades associated with the selected subject
    grades = await get_grades_for_subject(selected_subject)

        # Check if any grades are available for this subject
    if not grades:
        await query.edit_message_text(text=f"No grades available for {selected_subject}.")
        return

        # Dynamically generate the inline keyboard with available grades
    keyboard = [
        [InlineKeyboardButton(grade, callback_data=f"grade_{grade}")] for grade in grades
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message to the user with the list of available grades
    await query.edit_message_text(text=f"Choose your grade for {selected_subject}:", reply_markup=reply_markup)

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
'''
# topic Selection After Subject
async def subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["subject"] = query.data  # Save the subject

    # Define topics for the chosen subject (you can expand these)
    topics = ["Algebra", "Statistics", "Number and ALgebra"] if query.data == "Math" else ["Photosynthesis", "Cells", "Forces"]
    keyboard = [[InlineKeyboardButton(sub, callback_data=sub)] for sub in topics]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Choose a topic:", reply_markup=reply_markup)
'''
# Handling the selected topic and generating questions
async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["topic"] = query.data  # Save the topic

    # Now you can generate the real paper questions based on grade, subject, and topic
    grade = context.user_data.get("grade")
    subject = context.user_data.get("subject")
    topic = context.user_data.get("topic")

    # Simulating question generation - replace this with actual retrieval of questions
    questions = get_random_questions(grade, subject, topic)

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
