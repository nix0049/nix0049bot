import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

keyboard = [
    ["/ca", "/buy", "/chart"],
    ["/solscan", "/pump", "/volume"],
    ["/social", "/trending", "/off"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Nixcabot 🚀\nSmart gateway to meme coins on Solana.",
        reply_markup=reply_markup
    )

async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ca <token_address>")
        return
    token = context.args[0]
    await update.message.reply_text(f"https://jup.ag/swap/SOL-{token}")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /buy <token_address>")
        return
    token = context.args[0]
    await update.message.reply_text(f"https://jup.ag/swap/SOL-{token}")

async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /chart <token_address>")
        return
    token = context.args[0]
    await update.message.reply_text(f"https://dexscreener.com/solana/{token}")

async def solscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /solscan <token_address>")
        return
    token = context.args[0]
    await update.message.reply_text(f"https://solscan.io/token/{token}")

async def pump(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /pump <token_address>")
        return
    token = context.args[0]
    await update.message.reply_text(f"https://pump.fun/{token}")

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /volume <token_address>")
        return
    token = context.args[0]
    await update.message.reply_text(
        f"Dexscreener: https://dexscreener.com/solana/{token}\n"
        f"Jupiter: https://jup.ag/swap/SOL-{token}"
    )

async def social(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /social <token_address>")
        return
    token = context.args[0]
    await update.message.reply_text(
        f"Links:\n"
        f"📉 Dexscreener: https://dexscreener.com/solana/{token}\n"
        f"🔁 Jupiter: https://jup.ag/swap/SOL-{token}\n"
        f"🧠 Solscan: https://solscan.io/token/{token}"
    )

async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Trending tokens:\nhttps://pump.fun/trending")

async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔕 Updates paused.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ca", ca))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("chart", chart))
app.add_handler(CommandHandler("solscan", solscan))
app.add_handler(CommandHandler("pump", pump))
app.add_handler(CommandHandler("volume", volume))
app.add_handler(CommandHandler("social", social))
app.add_handler(CommandHandler("trending", trending))
app.add_handler(CommandHandler("off", off))

print("Bot is running...")
app.run_polling()
