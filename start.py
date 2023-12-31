import os
import dotenv
import logging
import signal

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, Application, ContextTypes

dotenv.load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)

# Define the start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text='Bot started!')

    print(f"\n\n\nChat ID: {chat_id}\n\n")

    os.kill(os.getpid(), signal.SIGINT)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Unknown command. Please use /start to begin.")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(os.getenv("TOKEN")).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()

if __name__ == '__main__':
    main()