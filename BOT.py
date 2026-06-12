import os
import discord
from discord.ext import commands
from flask import Flask
import threading

# ---------------- WEB ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "🟢 Bot Online"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# ---------------- BOT ----------------

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1514929528194207764

ROLE_MAP = {
    1514928475906244669: 1514345512101216306,  # VALORANT
    1514928326303809589: 1514928778785198240,  # ROBLOX
    1514928148062404703: 1514345509706273079,  # CS
    1514928010023927910: 1514928927083204618,  # FIVEM
    1514927916419518555: 1514929046054633565,  # GTA
}

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_MESSAGE_ID = None


@bot.event
async def on_ready():
    global ROLE_MESSAGE_ID

    print(f"Logged in as {bot.user}")

    channel = await bot.fetch_channel(CHANNEL_ID)

    # שולח הודעה פעם אחת בכל ריסטארט (פשוט ויעיל)
    embed = discord.Embed(
        title="🎮 Game Roles",
        description=(
            "<:VALORANT:1514928475906244669> Valorant\n"
            "<:ROBLOX:1514928326303809589> Roblox\n"
            "<:CS:1514928148062404703> CS\n"
            "<:FIVEM:1514928010023927910> FiveM\n"
            "<:GTA:1514927916419518555> GTA V\n\n"
            "React to get roles"
        )
    )

    msg = await channel.send(embed=embed)
    ROLE_MESSAGE_ID = msg.id

    print("Role message sent:", ROLE_MESSAGE_ID)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id != ROLE_MESSAGE_ID:
        return

    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)

    role_id = ROLE_MAP.get(payload.emoji.id)
    if role_id:
        role = guild.get_role(role_id)
        if role:
            await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != ROLE_MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)

    role_id = ROLE_MAP.get(payload.emoji.id)
    if role_id:
        role = guild.get_role(role_id)
        if role:
            await member.remove_roles(role)


bot.run(TOKEN)
