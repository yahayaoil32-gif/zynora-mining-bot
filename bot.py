import os
import sqlite3
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
DB_FILE = "zynora.db"

MINING_RATE = 1
MINING_DURATION = 24 * 60 * 60


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            mining_start INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def get_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id, username, balance, mining_start FROM users WHERE user_id = ?",
        (user_id,)
    )
    user = cur.fetchone()

    if user is None:
        cur.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username or "")
        )
        conn.commit()

        cur.execute(
            "SELECT user_id, username, balance, mining_start FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = cur.fetchone()

    conn.close()
    return user


def update_user(user_id, balance=None, mining_start=None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    if balance is not None:
        cur.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (balance, user_id)
        )

    if mining_start is not None:
        cur.execute(
            "UPDATE users SET mining_start = ? WHERE user_id = ?",
            (mining_start, user_id)
        )

    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user.id, user.username)

    await update.message.reply_text(
        "⛏️ Welcome to Zynora Mining!\n\n"
        "Start mining, complete tasks, invite friends and earn Zynora points. 🚀\n\n"
        "⛏️ /mine - Start mining\n"
        "💰 /balance - Check balance\n"
        "👤 /profile - View profile"
    )


async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user(user.id, user.username)

    mining_start = data[3]
    now = int(time.time())

    if mining_start > 0:
        elapsed = now - mining_start

        if elapsed < MINING_DURATION:
            remaining = MINING_DURATION - elapsed
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60

            await update.message.reply_text(
                f"⛏️ Your mining session is active!\n\n"
                f"💰 Rate: {MINING_RATE} Zynora/hour\n"
                f"⏳ Time remaining: {hours}h {minutes}m"
            )
            return

        earned = MINING_RATE * 24
        new_balance = data[2] + earned

        update_user(
            user.id,
            balance=new_balance,
            mining_start=now
        )

        await update.message.reply_text(
            f"🎉 Mining session completed!\n\n"
            f"⛏️ Earned: +{earned} Zynora\n"
            f"💰 New balance: {new_balance:.2f} Zynora\n\n"
            f"⛏️ A new mining session has started!"
        )
        return

    update_user(user.id, mining_start=now)

    await update.message.reply_text(
        "⛏️ Mining started!\n\n"
        "💰 Rate: 1 Zynora/hour\n"
        "⏳ Duration: 24 hours\n\n"
        "Come back after 24 hours to claim your mining reward. 🚀"
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user(user.id, user.username)

    await update.message.reply_text(
        f"💰 Your Zynora Balance\n\n"
        f"🪙 Balance: {data[2]:.2f} Zynora"
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user(user.id, user.username)

    username = f"@{user.username}" if user.username else "No username"

    await update.message.reply_text(
        f"👤 Zynora Profile\n\n"
        f"🆔 User ID: {user.id}\n"
        f"👤 Username: {username}\n"
        f"💰 Balance: {data[2]:.2f} Zynora"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Zynora Mining Help\n\n"
        "⛏️ /mine - Start/check mining\n"
        "💰 /balance - Check balance\n"
        "👤 /profile - View profile\n"
        "ℹ️ /help - Show help"
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mine", mine))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("help", help_command))

    print("Zynora Mining Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
