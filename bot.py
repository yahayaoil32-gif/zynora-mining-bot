import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⛏️ Welcome to Zynora Mining!\n\n"
        "Start mining, complete tasks, invite friends and earn Zynora points. 🚀\n\n"
        "Use /mine to start mining."
    )

async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⛏️ Mining started!\n\n"
        "Your Zynora mining session is now active."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Zynora Mining Help\n\n"
        "/mine - Start or check mining\n"
        "/balance - Check balance\n"
        "/daily - Daily bonus\n"
        "/referral - Invite friends\n"
        "/tasks - Complete tasks\n"
        "/profile - View profile\n"
        "/withdraw - Request withdrawal"
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mine", mine))
    app.add_handler(CommandHandler("help", help_command))

    print("Zynora Mining Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
