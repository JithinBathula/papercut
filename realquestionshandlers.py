# Start Command Handler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Final
from data import get_random_questions, get_grades_from_db, get_subjects_for_grade, get_grade_id, get_subject_id, get_topics_for_grade_and_subject
from telegram.constants import ParseMode

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
        grades = await get_grades_from_db()
        valid_grades = [grade_tuple[0] for grade_tuple in grades if isinstance(grade_tuple[0], str) and grade_tuple[0].strip()]
        
        if not valid_grades:
            await query.edit_message_text(text="No grades available at the moment.")
            return

        # Display grades dynamically
        keyboard = [
            [InlineKeyboardButton(grade, callback_data=f"grade_{grade}")] for grade in valid_grades
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["question_type"] = REAL_PAPER
        await query.edit_message_text(text="Choose your grade:", reply_markup=reply_markup)
        
# Primary or Secondary Callback Handler (extended for grade selection)
# Handler for grade selection (now extended to show subjects based on grade)
async def cat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Store selected grade in user_data and extract the grade
    context.user_data["selected_grade"] = query.data.split("grade_")[1]
    selected_grade = context.user_data["selected_grade"]
    grade_id= await get_grade_id(selected_grade)
    
    # Query the database for subjects associated with the selected grade
    subjects = await get_subjects_for_grade(grade_id)
    
    # Extract subject names from tuples
    valid_subjects = [subject_tuple[0] for subject_tuple in subjects if isinstance(subject_tuple[0], str) and subject_tuple[0].strip()]

    # Check if any subjects are available for this grade
    if not valid_subjects:
        await query.edit_message_text(text=f"No subjects available for grade {selected_grade}.")
        return

    # Dynamically generate the inline keyboard with available subjects
    keyboard = [
        [InlineKeyboardButton(subject, callback_data=f"subject_{subject}")] for subject in valid_subjects
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message to the user with the list of available subjects
    await query.edit_message_text(text=f"Choose your subject for grade {selected_grade}:", reply_markup=reply_markup)

# Handling the selected topic and generating questions
async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    #context.user_data["selected_topic"] = query.data  # Save the topic
    context.user_data["selected_subject"] = query.data.split("subject_")[1]
    # Now you can generate the real paper questions based on grade, subject, and topic
    grade = context.user_data.get("selected_grade")
    subject = context.user_data.get("selected_subject")
    grade_id= await get_grade_id(grade)
    subject_id=await get_subject_id(subject)
    
    
    # Simulating question generation - replace this with actual retrieval of questions
    topics = await get_topics_for_grade_and_subject(grade_id, subject_id)
    valid_topics = [topic_tuple[0] for topic_tuple in topics if isinstance(topic_tuple[0], str) and topic_tuple[0].strip()]

    # Check if any subjects are available for this grade
    if not valid_topics:
        await query.edit_message_text(text=f"No topics available for subject {subject}.")
        return

    # Dynamically generate the inline keyboard with available subjects
    keyboard = [
        [InlineKeyboardButton(topic, callback_data=f"topic_{topic}")] for topic in valid_topics
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message to the user with the list of available subjects
    await query.edit_message_text(text=f"Choose your topic for subject {subject}:", reply_markup=reply_markup)
    
# After grade, subject, and topic have been selected
async def generate_questions(update, context):
    query = update.callback_query
    await query.answer()
    grade = context.user_data.get("selected_grade")
    subject = context.user_data.get("selected_subject")
    
    context.user_data["selected_topic"] = query.data.split("topic_")[1]
    topic = context.user_data.get("selected_topic")

    # Fetch random questions from the database
    questions = await get_random_questions(grade, subject, topic)

    # Respond with the questions
    if questions:
        for question, answer in questions:
            formatted_message = f"<b>Question</b>: {question}\n<b>Answer</b>: {answer}"
            await query.message.reply_text(formatted_message, parse_mode=ParseMode.HTML)
    else:
        await query.message.reply_text("No questions found for the selected criteria.")

# Error Handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")
