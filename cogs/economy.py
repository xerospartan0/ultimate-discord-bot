import os, sqlite3, random
import discord
from discord.ext import commands
from discord import app_commands

DB = os.path.join("data","economy.db")
os.makedirs("data", exist_ok=True)
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS wallets (user_id INTEGER PRIMARY KEY, balance INTEGER)""")
con.commit()

def ensure_account(user_id):
    cur.execute("SELECT balance FROM wallets WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO wallets(user_id,balance) VALUES(?,?)", (user_id, 100))
        con.commit()

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ensure_account(interaction.user.id)
        cur.execute("SELECT balance FROM wallets WHERE user_id=?", (interaction.user.id,))
        bal = cur.fetchone()[0]
        await interaction.followup.send(f"Your balance: {bal} coins")

    @app_commands.command(name="daily", description="Claim daily reward")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ensure_account(interaction.user.id)
        amount = random.randint(50,150)
        cur.execute("UPDATE wallets SET balance=balance+? WHERE user_id=?", (amount, interaction.user.id))
        con.commit()
        await interaction.followup.send(f"You claimed {amount} coins!")

    @app_commands.command(name="give", description="Give coins to another user")
    async def give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await interaction.response.defer()
        ensure_account(interaction.user.id)
        ensure_account(member.id)
        cur.execute("SELECT balance FROM wallets WHERE user_id=?", (interaction.user.id,))
        bal = cur.fetchone()[0]
        if bal < amount or amount <= 0:
            await interaction.followup.send("Insufficient funds or invalid amount.")
            return
        cur.execute("UPDATE wallets SET balance=balance-? WHERE user_id=?", (amount, interaction.user.id))
        cur.execute("UPDATE wallets SET balance=balance+? WHERE user_id=?", (amount, member.id))
        con.commit()
        await interaction.followup.send(f"Gave {amount} coins to {member.display_name}.")

async def setup(bot):
    await bot.add_cog(Economy(bot))
