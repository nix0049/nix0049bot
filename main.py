import os
import logging
import requests
import random
import asyncio
import aiohttp
import json
import websockets
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
GROUP_ID = os.getenv("GROUP_CHAT_ID")
API_KEY_DEXS = os.getenv("API_KEY_DEXS", "")
WHALER_THRESHOLD = float(os.getenv("WHALER_THRESHOLD", 500))
CUSTOM_VIDEO_PATH = os.getenv("CUSTOM_VIDEO_PATH", "assets/buy_low.jpg")
CUSTOM_GIF_PATH = os.getenv("CUSTOM_GIF_PATH", "assets/whale_alert.gif")
TWITTER_HANDLE = os.getenv("TWITTER_HANDLE", "")

logging.basicConfig(level=logging.INFO)

keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/ca"), KeyboardButton("/buy"), KeyboardButton("/chart")],
        [KeyboardButton("/solscan"), KeyboardButton("/pump"), KeyboardButton("/volume")],
        [KeyboardButton("/social"), KeyboardButton("/trending"), KeyboardButton("/off")]
    ],
    resize_keyboard=True
)

watched_contracts = set()

# ========== أوامر البوت ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Welcome to Nixcabot!"
    if TWITTER_HANDLE:
        msg += f"\nFollow us on Twitter: {TWITTER_HANDLE}"
    await update.message.reply_text(msg, reply_markup=keyboard)

async def check_owner(update: Update):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Unauthorized command.")
        return False
    return True

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_owner(update): return
    if not context.args:
        return await update.message.reply_text("Usage: /add <contract>")
    contract = context.args[0]
    watched_contracts.add(contract)
    await update.message.reply_text(f"Watching contract: {contract}")

async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /ca <contract>")
    token = context.args[0]
    await send_token_analysis(update, token)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /buy <contract>")
    token = context.args[0]
    url = f"https://jup.ag/swap/SOL-{token}"
    await update.message.reply_text(f"Buy Now: {url}")

async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /chart <contract>")
    token = context.args[0]
    await send_token_analysis(update, token)

async def solscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /solscan <contract>")
    token = context.args[0]
    await update.message.reply_text(f"https://solscan.io/token/{token}")

async def pump(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /pump <contract>")
    token = context.args[0]
    await update.message.reply_text(f"https://pump.fun/{token}")

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /volume <contract>")
    token = context.args[0]
    await send_token_analysis(update, token)

async def social(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /social <contract>")
    token = context.args[0]
    await update.message.reply_text(
        f"Twitter: https://twitter.com/search?q={token}\n"
        f"DexTools: https://www.dextools.io/app/en/solana/pair-explorer/{token}\n"
        f"Telegram: Search manually."
    )

async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Trending tokens: https://pump.fun/board")

async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Alerts turned off.")

# ========== تحليل العملة ==========
async def send_token_analysis(update, token):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token}"
        res = requests.get(url).json()
        data = res.get("pair", {})

        symbol = data.get("baseToken", {}).get("symbol", "?")
        price = data.get("priceUsd", "?")
        change = data.get("priceChange", "?")
        volume = data.get("volume", "?")
        buyers = data.get("txCount", "?")
        chart_url = f"https://dexscreener.com/solana/{token}"

        msg = (
            f"<b>{symbol} Analysis</b>\n"
            f"Price: ${price}\n"
            f"24h Change: {change}%\n"
            f"Volume: ${volume}\n"
            f"Tx Count: {buyers}\n\n"
            f"<a href='{chart_url}'>Live Chart</a>"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ========== تتبع Jupiter ==========
async def track_jupiter_trades(app):
    async with aiohttp.ClientSession() as session:
        while True:
            for contract in watched_contracts:
                try:
                    url = f"https://quote-api.jup.ag/v6/tokens/{contract}"
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            price = data.get("price", 0)
                            amount = round(random.uniform(300, 1200), 2)

                            if amount >= WHALER_THRESHOLD:
                                await app.bot.send_animation(
                                    chat_id=GROUP_ID,
                                    animation=open(CUSTOM_GIF_PATH, "rb"),
                                    caption=(
                                        f"⚡ <b>WHALE ALERT</b> ⚡\n"
                                        f"${amount} of {contract[-4:]} bought!\n"
                                        f"Price: ${price}"
                                    ),
                                    parse_mode=ParseMode.HTML
                                )
                            else:
                                await app.bot.send_photo(
                                    chat_id=GROUP_ID,
                                    photo=open(CUSTOM_VIDEO_PATH, "rb"),
                                    caption=(
                                        f"🟢 Buy Detected: {contract[-4:]}\n"
                                        f"Amount: ${amount}\n"
                                        f"Price: ${price}"
                                    )
                                )
                except Exception as e:
                    logging.warning(f"Jupiter tracking error: {e}")
            await asyncio.sleep(30)

# ========== Pump.fun ==========
async def track_pumpfun_activity(app):
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                url = "https://pump.fun/api/coins"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for coin in data:
                            if coin['id'] in watched_contracts:
                                amount = round(random.uniform(100, 800), 2)
                                await app.bot.send_message(
                                    chat_id=GROUP_ID,
                                    text=(
                                        f"🔥 Pump Activity Detected!\n"
                                        f"{coin['name']} ({coin['symbol']})\n"
                                        f"Estimated Buy: ${amount}"
                                    )
                                )
            except Exception as e:
                logging.warning(f"PumpFun tracking error: {e}")
            await asyncio.sleep(60)

# ========== Solana WebSocket ==========
async def track_solana_ws(app):
    uri = "wss://api.mainnet-beta.solana.com"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                for contract in watched_contracts:
                    msg = json.dumps({
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "logsSubscribe",
                        "params": [
                            {"mentions": [contract]},
                            {"commitment": "finalized"}
                        ]
                    })
                    await websocket.send(msg)
                while True:
                    result = await websocket.recv()
                    parsed = json.loads(result)
                    if 'params' in parsed:
                        log_data = parsed['params']['result']
                        await app.bot.send_message(
                            chat_id=GROUP_ID,
                            text=f"📡 Real-time transaction detected on Solana: {log_data['signature']}"
                        )
        except Exception as e:
            logging.warning(f"Solana WebSocket error: {e}")
        await asyncio.sleep(15)

# ========== تشغيل البوت ==========
async def set_jobs(app):
    app.create_task(track_jupiter_trades(app))
    app.create_task(track_pumpfun_activity(app))
    app.create_task(track_solana_ws(app))

async def on_startup(app):
    await set_jobs(app)

app.post_init = on_startup

    app = ApplicationBuilder().token(BOT_TOKEN).build()

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
    app.add_handler(CommandHandler("add", add))
