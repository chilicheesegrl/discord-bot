from aiohttp import web
import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands, Interaction, ui

QUEUE_CHANNEL_ID = 1375995539929436182
ALLOWED_COMMAND_ROLES = {1152160525862567947, 1360108467230216494, 1326116500930695258, 1397408159945064538}
ALLOWED_STATUS_ROLES = {1152160525862567947, 1360108467230216494}

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class StatusDropdown(ui.Select):
    def __init__(self, message: discord.Message):
        self.message = message
        options = [
            discord.SelectOption(label="noted", emoji="<:A_bow:1326422864085389393>", value="noted"),
            discord.SelectOption(label="pending", emoji="<:A_bow:1326422864085389393>", value="pending"),
            discord.SelectOption(label="completed", emoji="<:A_bow:1326422864085389393>", value="completed"),
        ]
        super().__init__(placeholder="status ♡", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        if not any(role.id in ALLOWED_STATUS_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to change the status.", ephemeral=True)
            return

        content = self.message.content
        new_status = self.values[0]
        updated = content.rsplit("\n", 1)[0] + f"\n**◟ ♡order status : {new_status} <a:stars:1337150744251334719>**"
        await self.message.edit(content=updated, view=self.view)
        await interaction.response.defer()

class StatusView(ui.View):
    def __init__(self, message: discord.Message):
        super().__init__(timeout=None)
        self.add_item(StatusDropdown(message))

@bot.tree.command(name="q", description="add an order to the queue ♡")
@app_commands.describe(
    user="user the order is for",
    order="order details",
    priority="yes/no",
    quantity="quantity of the order"
)
async def q(interaction: Interaction, user: discord.Member, order: str, priority: str, quantity: str):
    if not any(role.id in ALLOWED_COMMAND_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)

    queue_channel = interaction.guild.get_channel(QUEUE_CHANNEL_ID)
    if queue_channel is None:
        await interaction.followup.send("Queue channel not found.")
        return

    message_content = (
        f"**◟ ♡ user ! <a:stars:1337150744251334719>**\n"
        f"**<:Untitled152_20250711124024:1393285849839435786> ୨୧┇{user.mention}  °｡ﾟ** \n\n"
        f"**◟ ♡order ! <a:stars:1337150744251334719>**\n"
        f"**<:Untitled152_20250711124024:1393285849839435786> ୨୧┇{order}  °｡ﾟ** \n\n"
        f"**◟ ♡ priority ! <a:stars:1337150744251334719>**\n"
        f"**<:Untitled152_20250711124024:1393285849839435786> ୨୧┇{priority} °｡ﾟ** \n\n"
        f"**◟ ♡quantity ! <a:stars:1337150744251334719>**\n"
        f"**<:Untitled152_20250711124024:1393285849839435786> ୨୧┇{quantity}  °｡ﾟ** \n\n"
        f"**◟ ♡order status : ... <a:stars:1337150744251334719>**"
    )

    message = await queue_channel.send(content=message_content)
    await message.edit(view=StatusView(message))

    await interaction.followup.send("**order added to queue!** <a:151517:1391877314614267935>")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

async def handle(request):
    return web.Response(text="Bot is running")

port = int(os.getenv("PORT", 8080))
app = web.Application()
app.add_routes([web.get('/', handle)])

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server running on port {port}")

    await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())