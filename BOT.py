import os
import threading
from flask import Flask
import discord
from discord.ext import commands

# -------------------
# WEB STATUS PAGE
# -------------------

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Discord Bot Status</title>
    </head>
    <body style="font-family: Arial; text-align:center; margin-top:100px;">
        <h1>🟢 Bot Online</h1>
        <p>The Discord bot is running successfully.</p>
    </body>
    </html>
    """

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# -------------------
# DISCORD BOT
# -------------------

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# -------------------
# START BOTH
# -------------------

threading.Thread(target=run_web, daemon=True).start()

bot.run(TOKEN)