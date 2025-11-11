import json
import re
import requests
from urllib.parse import quote_plus
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "7549965981:AAH4gvaz18_bkUhJHaHffKfkabABJXm-ATk")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "https://t.me/Owner_By_Rose")
CHANNEL_JOIN_URL = os.getenv("CHANNEL_JOIN_URL", "https://t.me/stangerboy")

WELCOME_IMAGE = "https://i.ibb.co/ccV44ZRS/STRANGER-BOY.jpg"
WELCOME_TEXT = (
"╔══════════════════════════════╗\n"
"║ 🔥 Welcome to Rose-X Bot🔥 \n"
"╠══════════════════════════════╣\n"
"║ Select an option below to search 💥\n"
"╠═══════════════════════════════╣                            \n"
"║  🛠️ Developed By: @Ros3_Zii 💝  \n"
"╚═══════════════════════════════╝"
)

MOBILE_API = "https://number-to-information.vercel.app/fetch?key=NO-LOVE&num="
AADHAR_API = "https://rose-x-tool.vercel.app/fetch?key=@Ros3_x&aadhaar="
VEHICLE_API = "https://vehicle-2-info.vercel.app/rose-x?vehicle_no="
PAK_API = "https://seller-ki-mkc.taitanx.workers.dev/?aadhar="

BLOCKED_NUMBERS = {
    "8859772859": "Ooh Rose Ka Number Ka Info Chahiye 😁😆",
}

DEVELOPER_CONTACT_URL = "https://t.me/h4ck3rspybot"
DEVELOPER_TAG = "Developer ➜ @h4ck3rspybot"

USER_PENDING_TYPE = {}

def main_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("👭👬 Enter Aadhar to Family", callback_data="aadhar")],
        [InlineKeyboardButton("📞 Enter Mobile Number", callback_data="mobile")],
        [InlineKeyboardButton("🧍🏻 Enter Aadhar Number", callback_data="pak")],
        [InlineKeyboardButton("🚗 Enter Vehicle Number", callback_data="vehicle")],
        [InlineKeyboardButton("🪪 Developer Contact", url=DEVELOPER_CONTACT_URL)],
    ]
    return InlineKeyboardMarkup(keyboard)

def result_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("↩️ Back to Main Menu", callback_data="main_menu")],
        [InlineKeyboardButton("🪪 Developer Contact", url=DEVELOPER_CONTACT_URL)],
    ]
    return InlineKeyboardMarkup(keyboard)

def join_channel_markup():
    keyboard = [[InlineKeyboardButton("✅ Join Our Channel", url=CHANNEL_JOIN_URL)]]
    return InlineKeyboardMarkup(keyboard)

def clean_number(number: str) -> str:
    return re.sub(r"[^\d+]", "", number or "")

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

async def check_and_block_if_not_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    is_joined = await check_subscription(user.id, context)
    if not is_joined:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ ACCESS DENIED ⚠️\n\nYou must join our channel to use this bot. Press /start after joining.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=join_channel_markup()
        )
        return False
    return True

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_and_block_if_not_joined(update, context):
        return
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=main_inline_keyboard(),
    )

async def process_number(chat_id: int, number_type: str, number: str, context: ContextTypes.DEFAULT_TYPE):
    number_clean = clean_number(number)
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Processing...", parse_mode=ParseMode.HTML)
    api_url = {
        "mobile": MOBILE_API + quote_plus(number_clean),
        "aadhar": AADHAR_API + quote_plus(number_clean),
        "vehicle": VEHICLE_API + quote_plus(number_clean),
        "pak": PAK_API + quote_plus(number_clean),
    }[number_type]

    try:
        resp = requests.get(api_url, timeout=15)
        data = resp.json()
    except Exception as e:
        data = {"error": str(e)}

    final_text = f"<b>Result for {number_type.capitalize()}:</b>\n<pre>{json.dumps(data, indent=2)}</pre>\n\n{DEVELOPER_TAG}"
    try:
        await context.bot.edit_message_text(chat_id=chat_id, message_id=loading_msg.message_id, text=final_text, parse_mode=ParseMode.HTML, reply_markup=result_inline_keyboard())
    except:
        await context.bot.send_message(chat_id=chat_id, text=final_text, parse_mode=ParseMode.HTML, reply_markup=result_inline_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not await check_and_block_if_not_joined(update, context):
        return
    if query.data in ["aadhar", "mobile", "pak", "vehicle"]:
        USER_PENDING_TYPE[user_id] = query.data
        prompts = {
            "aadhar": "Please enter your 12-digit Aadhar number:",
            "mobile": "Please enter your 10-digit mobile number:",
            "pak": "Please enter your 12-digit Aadhar number:",
            "vehicle": "Please enter the IFSC CODE:"
        }
        await query.message.reply_text(prompts[query.data])
    elif query.data == "main_menu":
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=WELCOME_IMAGE, caption=WELCOME_TEXT, parse_mode=ParseMode.HTML, reply_markup=main_inline_keyboard())

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_and_block_if_not_joined(update, context):
        return
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    if user_id in USER_PENDING_TYPE:
        number_type = USER_PENDING_TYPE.pop(user_id)
        await process_number(update.effective_chat.id, number_type, text, context)
        return
    await update.message.reply_text("Please select an option from the menu below.", reply_markup=main_inline_keyboard())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
