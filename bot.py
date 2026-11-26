import logging
import hashlib
import requests
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
        "Choose a tool from the menu below:"
    )
    keyboard = [
        [InlineKeyboardButton("🔐 Hash Generator", callback_data="hash_gen")],
        [InlineKeyboardButton("🔍 Hash Identifier", callback_data="hash_id")],
        [InlineKeyboardButton("🔓 Hash Cracker", callback_data="hash_crack")],
        [InlineKeyboardButton("🕵️‍♂️ OSINT Lookup", callback_data="osint")],
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
        "/search <username> - Find username across platforms\n"
        "/crack <hash> - Run dictionary attack\n\n"
        "⚠️ Only test on your own data."
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


async def identify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /identify <hash>\nExample: /identify 5d41402abc4b2a76b9719d911017c592"
        )
        return

    hash_str = context.args[0].strip()
    length = len(hash_str)
    is_hex = all(c in "0123456789abcdefABCDEF" for c in hash_str)

    if not is_hex:
        await update.message.reply_text("❌ This is not a valid hash. Hashes only contain hexadecimal characters.")
        return

    if length == 32:
        hash_type = "MD5"
    elif length == 40:
        hash_type = "SHA1"
    elif length == 64:
        hash_type = "SHA256"
    elif length == 128:
        hash_type = "SHA512"
    else:
        hash_type = "Unknown"

    response = (
        f"Input Hash: `{hash_str}`\n\n"
        f"Length: {length} characters\n"
        f"Identified Type: **{hash_type}**"
    )

    await update.message.reply_text(response, parse_mode="Markdown")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /search <username>\nExample: /search elonmusk"
        )
        return

    username = context.args[0].strip()
    msg = await update.message.reply_text(f"🕵️‍♂️ Searching for '{username}' across platforms...")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    results = []

    try:
        res = requests.get(f"https://github.com/{username}", headers=headers, timeout=5)
        if res.status_code == 200:
            results.append(f"✅ GitHub: https://github.com/{username}")
    except:
        pass

    try:
        res = requests.get(f"https://www.instagram.com/{username}/", headers=headers, timeout=5)
        if res.status_code == 200:
            results.append(f"✅ Instagram: https://instagram.com/{username}")
    except:
        pass

    try:
        res = requests.get(f"https://www.reddit.com/user/{username}/", headers=headers, timeout=5)
        if res.status_code == 200:
            results.append(f"✅ Reddit: https://reddit.com/user/{username}")
    except:
        pass

    try:
        res = requests.get(f"https://twitter.com/{username}", headers=headers, timeout=5)
        if res.status_code == 200:
            results.append(f"✅ Twitter (X): https://twitter.com/{username}")
    except:
        pass

    if results:
        final_text = f"🕵️‍♂️ OSINT Results for **{username}**:\n\n" + "\n".join(results)
        final_text += "\n\n⚠️ *Note: If a platform has strict privacy, it might not show up here.*"
    else:
        final_text = f"❌ No public profiles found for **{username}** on the checked platforms."
    
    await msg.edit_text(final_text, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "hash_gen":
        await query.edit_message_text("🔐 Hash Generator\n\nUsage: /hash <text>\nExample: /hash hello")
    elif query.data == "hash_id":
        await query.edit_message_text("🔍 Hash Identifier\n\nUsage: /identify <hash>\nExample: /identify 5d41402abc4b2a76b9719d911017c592")
    elif query.data == "hash_crack":
        await query.edit_message_text("🔓 Hash Cracker\n\nUsage: /crack <hash>\nExample: /crack 5d41402abc4b2a76b9719d911017c592\n\n⚠️ Only test on your own hashes!")
    elif query.data == "osint":
        await query.edit_message_text("🕵️‍♂️ OSINT Lookup\n\nUsage: /search <username>\nExample: /search elonmusk")
    elif query.data == "help":
        await query.edit_message_text("📖 Type /help to see all commands.\n\nOr use /start to open the menu.")


def main() -> None:
    if BOT_TOKEN == "YAHAN_APNA_TOKEN_PASTE_KARO":
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hash", hash_command))
    app.add_handler(CommandHandler("identify", identify_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()