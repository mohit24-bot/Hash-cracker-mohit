import logging
import hashlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = "9296265397:AAEBe4iP1NmAS8DpmT4BFcLLsdaic3sVdSk"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome = (
        f"👋 Hello, {user.first_name}!\n\n"
        "🔓 Welcome to the Hash Cracker Lab Bot.\n\n"
        "This bot will teach you the concepts of hashing and dictionary attacks.\n"
        "Choose a tool from the menu below:"
    )
    keyboard = [
        [InlineKeyboardButton("🔐 Hash Generator", callback_data="hash_gen")],
        [InlineKeyboardButton("🔍 Hash Identifier", callback_data="hash_id")],
        [InlineKeyboardButton("🔓 Hash Cracker", callback_data="hash_crack")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 Commands:\n\n"
        "/start - Open menu\n"
        "/help - Show this message\n"
        "/hash <text> - Generate MD5, SHA1, SHA256\n"
        "/identify <hash> - Identify hash type\n"
        "/crack <hash> - Run dictionary attack\n\n"
        "⚠️ Only test on your own hashes."
    )
    await update.message.reply_text(help_text)


async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /hash <text>\nExample: /hash hello"
        )
        return

    text = " ".join(context.args)
    text_bytes = text.encode('utf-8')

    md5_hash = hashlib.md5(text_bytes).hexdigest()
    sha1_hash = hashlib.sha1(text_bytes).hexdigest()
    sha256_hash = hashlib.sha256(text_bytes).hexdigest()

    response = (
        f"Input Text: {text}\n\n"
        f"MD5:\n`{md5_hash}`\n\n"
        f"SHA1:\n`{sha1_hash}`\n\n"
        f"SHA256:\n`{sha256_hash}`"
    )

    await update.message.reply_text(response, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "hash_gen":
        await query.edit_message_text(
            "🔐 Hash Generator\n\n"
            "Usage: /hash <text>\n"
            "Example: /hash hello",
        )
    elif query.data == "hash_id":
        await query.edit_message_text(
            "🔍 Hash Identifier\n\n"
            "Usage: /identify <hash>\n"
            "Example: /identify 5d41402abc4b2a76b9719d911017c592",
        )
    elif query.data == "hash_crack":
        await query.edit_message_text(
            "🔓 Hash Cracker\n\n"
            "Usage: /crack <hash>\n"
            "Example: /crack 5d41402abc4b2a76b9719d911017c592\n\n"
            "⚠️ Only test on your own hashes!",
        )
    elif query.data == "help":
        await query.edit_message_text(
            "📖 Type /help to see all commands.\n\n"
            "Or use /start to open the menu.",
        )


def main() -> None:
    if BOT_TOKEN == "YAHAN_APNA_TOKEN_PASTE_KARO":
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hash", hash_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()