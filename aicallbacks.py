# AI-Generated Questions Callback Handler
import os
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import base64
import aiohttp
import io
from gptapi import send_image_to_openai, chat_with_gpt, answers
from telegram.constants import ParseMode
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AI_GENERATED: Final = "Assesment book questions"
REAL_PAPER: Final = "Past Year Questions"

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
        # Handle cases where update.message might be None
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose an option:", reply_markup=reply_markup)

async def ai_generated_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    

    if query.data == "ai_show_answer":
        current_index = context.user_data.get('current_question_index', 0)
        questions = context.user_data.get('ai_generated_questions', [])
        if current_index < len(questions):
            question = questions[current_index]
            await query.message.reply_text("Generating answer...")
            answer = await answers(question)
            keyboard = [
                [InlineKeyboardButton("Next Question", callback_data="ai_next_question")],
                [InlineKeyboardButton("Back to Start", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(f"<b>Answer:</b>\n{answer}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await query.message.reply_text("No answer available.")
    elif query.data == "ai_next_question":
        current_index = context.user_data.get('current_question_index', 0)
        questions = context.user_data.get('ai_generated_questions', [])
        if current_index + 1 < len(questions):
            current_index += 1
            context.user_data['current_question_index'] = current_index
            current_question = questions[current_index]
            keyboard = [
                [InlineKeyboardButton("Show Answer", callback_data="ai_show_answer")],
                [InlineKeyboardButton("Next Question", callback_data="ai_next_question")],
                [InlineKeyboardButton("Back to Start", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(f"<b>{current_question}</b>", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            keyboard = [
                [InlineKeyboardButton("Back to Start", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("No more questions.", reply_markup=reply_markup)
    elif query.data == "back_to_start":
        await start_command(update, context)


async def ai_generated_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "upload_image":
        context.user_data['awaiting_image'] = True
        context.user_data['awaiting_topic'] = False
        await query.edit_message_text(text="Please upload an image.")
    elif query.data == "type_topic":
        context.user_data['awaiting_topic'] = True
        context.user_data['awaiting_image'] = False
        await query.edit_message_text(text="Please enter a topic for AI-generated questions.")

async def handle_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_image'):
        context.user_data['awaiting_image'] = False
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(file.file_path) as resp:
                if resp.status != 200:
                    await update.message.reply_text("Error downloading image")
                    return
                image_data = await resp.read()

        base64_image = base64.b64encode(image_data).decode('utf-8')
        await update.message.reply_text("Generating AI questions based on the uploaded image...")
        response = await send_image_to_openai(base64_image)
        questions = parse_questions(response)
        if questions:
            context.user_data['ai_generated_questions'] = questions
            context.user_data['current_question_index'] = 0

            current_question = questions[0]
            keyboard = [
                [InlineKeyboardButton("Show Answer", callback_data="ai_show_answer")],
                [InlineKeyboardButton("Next Question", callback_data="ai_next_question")],
                [InlineKeyboardButton("Back to Start", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"<b>{current_question}</b>", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("Sorry, I couldn't generate any questions.")
    else:
        await update.message.reply_text("Please select 'Upload Image' first.")


def parse_questions(text):
    questions = []
    lines = text.strip().split('\n')
    current_question = ''
    is_question = False

    for line in lines:
        line = line.strip()
        if line.startswith('Question '):
            if current_question:
                questions.append(current_question.strip())
                current_question = ''
            is_question = True
        else:
            if is_question:
                current_question += line + '\n'

    if current_question:
        questions.append(current_question.strip())

    return questions

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_topic'):
        context.user_data['awaiting_topic'] = False
        topic = update.message.text
        await update.message.reply_text(f"Generating AI questions for the topic '{topic}'...")
        response = await chat_with_gpt(topic)
        questions = parse_questions(response)
        if questions:
            context.user_data['ai_generated_questions'] = questions
            context.user_data['current_question_index'] = 0

            current_question = questions[0]
            keyboard = [
                [InlineKeyboardButton("Show Answer", callback_data="ai_show_answer")],
                [InlineKeyboardButton("Next Question", callback_data="ai_next_question")],
                [InlineKeyboardButton("Back to Start", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"<b>{current_question}</b>", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("Sorry, I couldn't generate any questions.")
    else:
        await update.message.reply_text("Please select 'Type Topic' first.")
