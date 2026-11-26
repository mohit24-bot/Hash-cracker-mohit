import logging
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
        f"👋 Namaste, {user.first_name}!\n\n"
        "🔓 Hash Cracker Lab Bot mein swagat hai.\n\n"
        "Yeh bot tumhe hashing aur dictionary attack ka concept sikhayega.\n"
        "Neeche menu se tool chuno:"
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
        "/start - Menu kholo\n"
        "/help - Yeh message\n"
        "/hash <text> - MD5, SHA1, SHA256 banao\n"
        "/identify <hash> - Hash type batao\n"
        "/crack <hash> - Dictionary attack chalao\n\n"
        "⚠️ Sirf apne khud ke hashes pe test karo."
    )
    await update.message.reply_text(help_text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "hash_gen":
        await query.edit_message_text(
            "🔐 Hash Generator\n\n"
            "Use karo: /hash <text>\n"
            "Example: /hash hello",
        )
    elif query.data == "hash_id":
        await query.edit_message_text(
            "🔍 Hash Identifier\n\n"
            "Use karo: /identify <hash>\n"
            "Example: /identify 5d41402abc4b2a76b9719d911017c592",
        )
    elif query.data == "hash_crack":
        await query.edit_message_text(
            "🔓 Hash Cracker\n\n"
            "Use karo: /crack <hash>\n"
            "Example: /crack 5d41402abc4b2a76b9719d911017c592\n\n"
            "⚠️ Sirf apne khud ke hashes pe test karo!",
        )
    elif query.data == "help":
        await query.edit_message_text(
            "📖 Commands ke liye /help type karo.\n\n"
            "Ya /start se menu kholo.",
        )


def main() -> None:
    if BOT_TOKEN == "YAHAN_NEW_TOKEN_PASTE_KARO":
        raise ValueError("Bhai token daalna bhool gaye!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()