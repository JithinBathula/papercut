from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import AsyncOpenAI
import base64
import aiohttp
import io
import pymysqlx

## telegram token
TOKEN: Final = "7414557591:AAEOPbw0RXdSwX3cBtBPJR_sqDmpc5WKKo8"
BOT_USERNAME: Final = "@Trialpapercutbot"

## api key for open ai
OPENAI_API_KEY = "sk-proj-GNPuVdrlqOqw7o8ScVGJT3BlbkFJrJFbcN1QhVfB8FHC92jt"

AI_GENERATED: Final = "Assesment book questions"
REAL_PAPER: Final = "Past Year Questions"

# Start Command Handler
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


##--------

import psycopg2
import random

# Database connection details
DATABASE = {
    'database': 'paper_cut',  # Changed from 'dbname' to 'database'
    'user': 'root',
    'password': '1212',
    'host': '127.0.0.1',
    'port': '3306',
}

# Connect to the PostgreSQL database
def connect_to_db():
    conn = pymysql.connect(
        host=DATABASE['host'],
        user=DATABASE['user'],
        password=DATABASE['password'],
        database=DATABASE['database'],  # Use 'database' instead of 'dbname'
        port=int(DATABASE['port'])
    )
    return conn

# Function to retrieve random questions from the database
def get_random_questions(grade, subject, subtopic, limit=4):
    conn = connect_to_db()
    cur = conn.cursor()

    query = """
    SELECT q.question_text, q.answer_text
    FROM Questions q
    JOIN Grades g ON q.grade_id = g.id
    JOIN Subjects s ON q.subject_id = s.id
    JOIN Subtopics st ON q.subtopic_id = st.id
    WHERE g.grade_name = %s
      AND s.subject_name = %s
      AND st.subtopic_name = %s
      AND st.grade_id = g.id
    ORDER BY RAND()
    LIMIT %s;
    """
    cur.execute(query, (grade, subject, subtopic, limit))
    questions = cur.fetchall()

    cur.close()
    conn.close()
    return questions

# After grade, subject, and subtopic have been selected
async def generate_questions(update, context):
    grade = context.user_data["grade"]
    subject = context.user_data["subject"]
    subtopic = context.user_data["subtopic"]

    # Fetch random questions from the database
    questions = get_random_questions(grade, subject, subtopic)

    # Respond with the questions
    if questions:
        for question, answer in questions:
            formatted_message = f"**Question**: {question}\n**Answer**: {answer}"
            await update.message.reply_text(formatted_message)
    else:
        await update.message.reply_text("No questions found for the selected criteria.")

##-----



# AI-Generated Questions Callback Handler
async def ai_generated_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "upload_image":
        await query.edit_message_text(text="Please upload an image.")
    elif query.data == "type_topic":
        await query.edit_message_text(text="Please enter a topic for AI-generated questions.")

# Image Upload Handler
async def handle_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]  # Get the highest resolution image
    file = await context.bot.get_file(photo.file_id)
    
    # Download the image
    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as resp:
            if resp.status != 200:
                await update.message.reply_text("Error downloading image")
                return
            image_data = await resp.read()

    # Convert image to base64
    base64_image = base64.b64encode(image_data).decode('utf-8')

    # Send the image to OpenAI's API
    response = await send_image_to_openai(base64_image)
    
    # Return the questions generated by OpenAI
    await update.message.reply_text(response)

async def send_image_to_openai(base64_image):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    prompt = """
Based on the image, you must:
1. Read all the questions in the image and identify the overall topic, difficulty level, and question structure (e.g., multiple-choice, short-answer, long-answer).
2. Generate 4 new questions on the same topic and difficulty level, ensuring that the new questions follow the exact same structure and format as the questions in the image.
3. Ensure the questions are coherent, make sense, and align with the Singapore syllabus. Do not generate random or irrelevant questions.
4. After creating the 4 new questions, provide the answers for each question along with a short explanation.

Important: Do not output any additional analysis such as the overall topic, difficulty level, or structure to the student. Only provide the questions and their corresponding answers. Keep the format clean and simple, with no special characters like `**` or `##`.
"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",  # Using gpt-4o-mini as per the documentation
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt  
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "auto"  # You can change this to "low" or "high" if needed
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Text Message Handler
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_type = context.user_data.get("question_type")

    if question_type == AI_GENERATED:
        topic = update.message.text
        await update.message.reply_text(f"Generating AI questions for the topic '{topic}'...")
        response = await chat_with_gpt(topic)
        await update.message.reply_text(response)

async def chat_with_gpt(text):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal:paper-cut:A0VCkgl2",
        messages=[
            {
                "role": "system",
                "content": "You are an experienced educator for Singapore students. Based on the Grade, Subject and Topic provided, create 3 questions covering the topics within the subject for students in grade. Ensure the questions vary in difficulty and format, including multiple-choice, short-answer, and essay-type questions. Align the questions with the Singaporean curriculum standards and provide clear instructions and context for each question. After giving the questions, you must also give them answers."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content

# Error Handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")

# Main function
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start_command))

    # Callback Query Handlers
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^ai_generated|real_paper$"))
    app.add_handler(CallbackQueryHandler(cat_callback, pattern="^primary|secondary$"))
    app.add_handler(CallbackQueryHandler(grade_callback, pattern="^P[1-6]|Sec[1-3]$"))
    app.add_handler(CallbackQueryHandler(subject_callback, pattern="^Math|Science|English$"))
    app.add_handler(CallbackQueryHandler(subtopic_callback, pattern="^Algebra|Geometry|Numbers|Photosynthesis|Cells|Forces$"))
    app.add_handler(CallbackQueryHandler(ai_generated_callback, pattern="^upload_image|type_topic$"))

    # Message Handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_image_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Error Handler
    app.add_error_handler(error)

    # Run the bot
    print("Starting bot...")
    app.run_polling(poll_interval=0.5)