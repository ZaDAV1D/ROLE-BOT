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

# ---------------- BOT CONFIG ----------------

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1514929528194207764

ROLE_MAP = {
    "valorant": 1514345512101216306,
    "roblox": 1514928778785198240,
    "cs": 1514345509706273079,
    "fivem": 1514928927083204618,
    "gta": 1514929046054633565,
}

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_MESSAGE_ID = None


# ---------------- CONFIRM REMOVE VIEW ----------------

class ConfirmRemoveView(discord.ui.View):
    def __init__(self, member, role):
        super().__init__(timeout=30)
        self.member = member
        self.role = role

    @discord.ui.button(label="Yes, remove", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.member:
            await interaction.response.send_message("❌ זה לא שלך.", ephemeral=True)
            return

        await self.member.remove_roles(self.role)

        await interaction.response.edit_message(
            content=f"❌ Removed role: **{self.role.name}**",
            view=None
        )

        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.member:
            await interaction.response.send_message("❌ זה לא שלך.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content="👍 פעולה בוטלה",
            view=None
        )

        self.stop()


# ---------------- ROLE VIEW (MAIN BUTTONS) ----------------

class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle_role(self, interaction: discord.Interaction, role_key: str):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(ROLE_MAP[role_key])

        if role is None:
            await interaction.response.send_message("❌ Role not found", ephemeral=True)
            return

        # אם יש רול → שואל לפני הסרה
        if role in member.roles:
            view = ConfirmRemoveView(member, role)

            await interaction.response.send_message(
                f"❓ אתה בטוח שאתה רוצה להסיר את **{role.name}**?",
                view=view,
                ephemeral=True
            )
        else:
            await member.add_roles(role)

            await interaction.response.send_message(
                f"✅ Added role: **{role.name}**",
                ephemeral=True
            )

    @discord.ui.button(label="Valorant", style=discord.ButtonStyle.green)
    async def valorant(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "valorant")

    @discord.ui.button(label="Roblox", style=discord.ButtonStyle.blurple)
    async def roblox(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "roblox")

    @discord.ui.button(label="CS", style=discord.ButtonStyle.red)
    async def cs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "cs")

    @discord.ui.button(label="FiveM", style=discord.ButtonStyle.gray)
    async def fivem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "fivem")

    @discord.ui.button(label="GTA", style=discord.ButtonStyle.green)
    async def gta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "gta")


# ---------------- BOT READY ----------------

@bot.event
async def on_ready():
    global ROLE_MESSAGE_ID

    print(f"Logged in as {bot.user}")

    channel = await bot.fetch_channel(CHANNEL_ID)

    embed = discord.Embed(
        title="🎮 Game Roles",
        description="לחץ על כפתור כדי לקבל או להסיר Role"
    )

    view = RoleView()

    msg = await channel.send(embed=embed, view=view)
    ROLE_MESSAGE_ID = msg.id

    print("Role button panel sent")


# ---------------- RUN BOT ----------------

bot.run(TOKEN)
