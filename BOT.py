import os
import discord
from discord.ext import commands
from flask import Flask
import threading
import json

# ---------------- WEB ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "🟢 Bot Online"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# ---------------- CONFIG ----------------

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {"role_message_id": None}

def save_config(data):
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

# ---------------- DISCORD ----------------

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1514929528194207764

ROLE_MAP = {
    1514928475906244669: 1514345512101216306,
    1514928326303809589: 1514928778785198240,
    1514928148062404703: 1514345509706273079,
    1514928010023927910: 1514928927083204618,
    1514927916419518555: 1514929046054633565,
}

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    global config

    channel = await bot.fetch_channel(CHANNEL_ID)

    # אם כבר יש הודעה שמורה → לא שולח שוב
    if config["role_message_id"]:
        print("Role message already exists:", config["role_message_id"])
        return

    embed = discord.Embed(
        title="🎮 Game Roles",
        description="React to get roles"
    )

    msg = await channel.send(embed=embed)

    config["role_message_id"] = msg.id
    save_config(config)

    print("Created role message:", msg.id)


@bot.event
async def on_raw_reaction_add(payload):
    if config["role_message_id"] is None:
        return

    if payload.message_id != config["role_message_id"]:
        return

    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)

    role_id = ROLE_MAP.get(payload.emoji.id)
    if not role_id:
        return

    role = guild.get_role(role_id)
    if role:
        await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    if config["role_message_id"] is None:
        return

    if payload.message_id != config["role_message_id"]:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)

    role_id = ROLE_MAP.get(payload.emoji.id)
    if not role_id:
        return

    role = guild.get_role(role_id)
    if role:
        await member.remove_roles(role)


bot.run(TOKEN)
