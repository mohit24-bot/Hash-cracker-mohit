import logging
import hashlib
import requests
import os
import exifread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
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
        "🔓 Welcome to the Hacker Lab Bot.\n\n"
        "Choose a tool from the menu below:"
    )
    keyboard = [
        [InlineKeyboardButton("🔐 Hash Tools", callback_data="hash_tools")],
        [InlineKeyboardButton("🕵️‍♂️ OSINT Lookup", callback_data="osint")],
        [InlineKeyboardButton("🖼️ Image EXIF Spy", callback_data="exif")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 Commands:\n\n"
        "/start - Open menu\n"
        "/hash <text> - Generate MD5, SHA1, SHA256\n"
        "/identify <hash> - Identify hash type\n"
        "/search <username> - OSINT Lookup\n\n"
        "🖼️ To extract EXIF data, send an image as a FILE (Document)."
    )
    await update.message.reply_text(help_text)


async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /hash <text>\nExample: /hash hello")
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
        await update.message.reply_text("Usage: /identify <hash>\nExample: /identify 5d41402abc4b2a76b9719d911017c592")
        return

    hash_str = context.args[0].strip()
    length = len(hash_str)
    is_hex = all(c in "0123456789abcdefABCDEF" for c in hash_str)

    if not is_hex:
        await update.message.reply_text("❌ This is not a valid hash.")
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

    response = f"Input Hash: `{hash_str}`\n\nLength: {length} chars\nIdentified Type: **{hash_type}**"
    await update.message.reply_text(response, parse_mode="Markdown")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /search <username>\nExample: /search elonmusk")
        return

    username = context.args[0].strip()
    msg = await update.message.reply_text(f"🕵️‍♂️ Searching for '{username}'...")

    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15"}
    results = []
    
    platforms = [
        {"name": "GitHub", "url": f"https://github.com/{username}"},
        {"name": "Twitter (X)", "url": f"https://twitter.com/{username}"},
        {"name": "Telegram", "url": f"https://t.me/{username}"},
        {"name": "Pinterest", "url": f"https://pinterest.com/{username}"},
        {"name": "GitLab", "url": f"https://gitlab.com/{username}"},
        {"name": "YouTube", "url": f"https://youtube.com/@{username}"}
    ]

    for p in platforms:
        try:
            res = requests.get(p["url"], headers=headers, timeout=5, allow_redirects=False)
            if res.status_code == 200:
                results.append(f"✅ {p['name']}: {p['url']}")
        except Exception:
            pass

    if results:
        final_text = f"🕵️‍♂️ OSINT Results for **{username}**:\n\n" + "\n".join(results)
    else:
        final_text = f"❌ No public profiles found for **{username}**."
    
    await msg.edit_text(final_text, parse_mode="Markdown")


def convert_to_degrees(value):
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.document:
        file_id = update.message.document.file_id
    elif update.message.photo:
        await update.message.reply_text("⚠️ Please send the image as a **File (Document)**, not a Photo. Telegram deletes the hidden data from normal photos!")
        return
    else:
        return

    msg = await update.message.reply_text("🕵️‍♂️ Extracting EXIF Metadata...")
    
    new_file = await context.bot.get_file(file_id)
    temp_path = "temp_image.jpg"
    await new_file.download_to_drive(temp_path)

    try:
        with open(temp_path, 'rb') as f:
            tags = exifread.process_file(f)

        if not tags:
            await msg.edit_text("❌ No EXIF data found in this image. (Maybe it's a screenshot or WhatsApp image).")
            return

        make = tags.get('Image Make', 'Unknown')
        model = tags.get('Image Model', 'Unknown')
        date_time = tags.get('Image DateTime', 'Unknown')
        
        response = (
            f"🖼️ **EXIF Data Found!**\n\n"
            f"📱 **Device:** {make} {model}\n"
            f"📅 **Date/Time:** {date_time}\n"
        )

        lat = tags.get('GPS GPSLatitude')
        lat_ref = tags.get('GPS GPSLatitudeRef')
        lon = tags.get('GPS GPSLongitude')
        lon_ref = tags.get('GPS GPSLongitudeRef')

        if lat and lon:
            lat_deg = convert_to_degrees(lat)
            lon_deg = convert_to_degrees(lon)
            
            if lat_ref and lat_ref.values[0] != 'N':
                lat_deg = -lat_deg
            if lon_ref and lon_ref.values[0] != 'E':
                lon_deg = -lon_deg

            gmap_link = f"https://www.google.com/maps?q={lat_deg},{lon_deg}"
            response += f"\n📍 **Location Found!**\n[Click to view on Google Maps]({gmap_link})"
        else:
            response += "\n📍 **Location:** GPS data not available."

        await msg.edit_text(response, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        await msg.edit_text(f"❌ Error extracting data: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "hash_tools":
        await query.edit_message_text("🔐 **Hash Tools**\n\n/hash <text> - Generate hashes\n/identify <hash> - Identify hash")
    elif query.data == "osint":
        await query.edit_message_text("🕵️‍♂️ **OSINT Lookup**\n\nUsage: /search <username>")
    elif query.data == "exif":
        await query.edit_message_text("🖼️ **Image EXIF Spy**\n\nSend me any image as a **File (Document)** to extract its hidden camera and GPS data!\n\n*(Note: Do not send as Photo).*")
    elif query.data == "help":
        await query.edit_message_text("📖 Type /help to see all commands.")


def main() -> None:
    if BOT_TOKEN == "YAHAN_APNA_TOKEN_PASTE_KARO":
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hash", hash_command))
    app.add_handler(CommandHandler("identify", identify_command))
    app.add_handler(CommandHandler("search", search_command))
    
    app.add_handler(MessageHandler(filters.Document.IMAGE | filters.PHOTO, handle_image))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Hacker Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()