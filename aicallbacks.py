import os
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import base64
import aiohttp
from gptapi import send_image_to_openai, chat_with_gpt, answers
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_GENERATED: Final = "Assessment book questions"
REAL_PAPER: Final = "Past Year Questions"

# Start Command Handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Assessment book questions", callback_data="ai_generated")],
        [InlineKeyboardButton("Past Year Questions", callback_data="real_paper")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    else:
        # Handle cases where update.message might be None
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Choose an option:",
            reply_markup=reply_markup,
        )

# Callback Query Handler for Main Menu
async def main_menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai_generated":
        keyboard = [
            [InlineKeyboardButton("Upload Image", callback_data="upload_image")],
            [InlineKeyboardButton("Type Topic", callback_data="type_topic")],
            [InlineKeyboardButton("Back to Start", callback_data="back_to_start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Choose how you want to generate AI questions:",
            reply_markup=reply_markup,
        )
    elif query.data == "real_paper":
        # Implement functionality for past year questions
        await query.edit_message_text(text="Past Year Questions feature is under development.")
    elif query.data == "back_to_start":
        await start_command(update, context)
    else:
        await query.edit_message_text(text="Unknown option selected.")

# Callback Query Handler for AI-Generated Questions
async def ai_generated_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai_show_answer":
        current_question = context.user_data.get("current_question")
        if current_question:
            await query.message.reply_text("Generating answer...")
            answer = await answers(current_question)
            keyboard = [
                [InlineKeyboardButton("Next Question", callback_data="ai_next_question")],
                [InlineKeyboardButton("Back to Start", callback_data="back_to_start")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                f"<b>Answer:</b>\n{answer}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
            )
        else:
            await query.message.reply_text("No question available to show the answer.")
    elif query.data == "ai_next_question":
        generation_mode = context.user_data.get("generation_mode")
        if generation_mode == "image":
            image_data = context.user_data.get("image_data")
            if not image_data:
                await query.message.reply_text("No image data found. Please upload an image again.")
                return
            question = await send_image_to_openai(image_data)
        elif generation_mode == "topic":
            topic = context.user_data.get("topic")
            if not topic:
                await query.message.reply_text("No topic found. Please enter a topic again.")
                return
            question = await chat_with_gpt(topic)
        else:
            await query.message.reply_text("Invalid generation mode.")
            return

        if question:
            context.user_data["current_question"] = question
            keyboard = [
                [InlineKeyboardButton("Show Answer", callback_data="ai_show_answer")],
                [InlineKeyboardButton("Next Question", callback_data="ai_next_question")],
                [InlineKeyboardButton("Back to Start", callback_data="back_to_start")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                f"<b>Question:</b>\n{question}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
            )
        else:
            await query.message.reply_text("Sorry, I couldn't generate a question.")
    elif query.data == "back_to_start":
        await start_command(update, context)
    else:
        await query.edit_message_text(text="Unknown option selected.")

# Callback Query Handler for Image or Topic Selection
async def ai_generated_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "upload_image":
        context.user_data["awaiting_image"] = True
        context.user_data["awaiting_topic"] = False
        await query.edit_message_text(text="Please upload an image.")
    elif query.data == "type_topic":
        context.user_data["awaiting_topic"] = True
        context.user_data["awaiting_image"] = False
        await query.edit_message_text(text="Please enter a topic for AI-generated questions.")
    else:
        await query.edit_message_text(text="Unknown option selected.")

# Handle Image Upload
async def handle_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_image"):
        context.user_data["awaiting_image"] = False
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        async with aiohttp.ClientSession() as session:
            async with session.get(file.file_path) as resp:
                if resp.status != 200:
                    await update.message.reply_text("Error downloading image.")
                    return
                image_data = await resp.read()

        base64_image = base64.b64encode(image_data).decode("utf-8")
        context.user_data["image_data"] = base64_image
        context.user_data["generation_mode"] = "image"

        await update.message.reply_text("Image received. Generating the first AI question...")
        await generate_and_send_question(update, context)
    else:
        await update.message.reply_text("Please select 'Upload Image' first.")

# Handle Text Message for Topic
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_topic"):
        context.user_data["awaiting_topic"] = False
        topic = update.message.text.strip()
        if not topic:
            await update.message.reply_text("Topic cannot be empty. Please enter a valid topic.")
            return
        context.user_data["topic"] = topic
        context.user_data["generation_mode"] = "topic"

        await update.message.reply_text(f"Topic '{topic}' received. Generating the first AI question...")
        await generate_and_send_question(update, context)
    else:
        await update.message.reply_text("I didn't understand that. Please use the provided buttons to navigate.")

# Function to Generate and Send a Question
async def generate_and_send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    generation_mode = context.user_data.get("generation_mode")
    if generation_mode == "image":
        image_data = context.user_data.get("image_data")
        if not image_data:
            await update.message.reply_text("No image data found. Please upload an image again.")
            return
        question = await send_image_to_openai(image_data)
    elif generation_mode == "topic":
        topic = context.user_data.get("topic")
        if not topic:
            await update.message.reply_text("No topic found. Please enter a topic again.")
            return
        question = await chat_with_gpt(topic)
    else:
        await update.message.reply_text("Invalid generation mode.")
        return

    if question:
        context.user_data["current_question"] = question
        keyboard = [
            [InlineKeyboardButton("Show Answer", callback_data="ai_show_answer")],
            [InlineKeyboardButton("Next Question", callback_data="ai_next_question")],
            [InlineKeyboardButton("Back to Start", callback_data="back_to_start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"<b>Question:</b>\n{question}",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text("Sorry, I couldn't generate a question.")
