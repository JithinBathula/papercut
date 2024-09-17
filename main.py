from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import AsyncOpenAI
import base64
import aiohttp
import io
import os
import pymysql
from dotenv import load_dotenv
from realquestionshandlers import back_to_start, menu_callback, start_command, cat_callback, topic_callback, generate_questions, show_answer, new_question, error
from aicallbacks import ai_generated_callback, handle_image_upload, handle_text_message
load_dotenv()

## telegram token
TOKEN: Final = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME: Final = "@Trialpapercutbot"

# Main function
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start_command))

    # Callback Query Handlers
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^(ai_generated|real_paper|back_to_start)$"))
    app.add_handler(CallbackQueryHandler(cat_callback, pattern="^(grade_.*|back_to_grades)$"))
    app.add_handler(CallbackQueryHandler(topic_callback, pattern="^(subject_.*|back_to_subjects|back_to_grades)$"))
    app.add_handler(CallbackQueryHandler(generate_questions, pattern="^(topic_.*|back_to_topics|show_answer|new_question)$"))
    app.add_handler(CallbackQueryHandler(show_answer, pattern="^show_answer$"))
    app.add_handler(CallbackQueryHandler(new_question, pattern="^new_question$"))
    app.add_handler(CallbackQueryHandler(ai_generated_callback, pattern="^upload_image|type_topic$"))

    # Message Handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_image_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Error Handler
    app.add_error_handler(error)

    # Run the bot
    print("Starting bot...")
    app.run_polling(poll_interval=0.5)