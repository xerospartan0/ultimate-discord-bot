import os
import sqlite3
import discord
from discord.ext import commands, tasks
from discord import app_commands

DB = os.path.join("data","levels.db")
os.makedirs("data", exist_ok=True)
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS xp (user_id INTEGER PRIMARY KEY, xp INTEGER, level INTEGER)""")
con.commit()

def add_xp(user_id, amount=10):
    cur.execute("SELECT xp, level FROM xp WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO xp(user_id,xp,level) VALUES(?,?,?)", (user_id, amount, 1))
        con.commit()
        return 1, amount
    xp, level = row
    xp += amount
    new_level = level
    while xp >= new_level * 100:
        xp -= new_level * 100
        new_level += 1
    cur.execute("UPDATE xp SET xp=?, level=? WHERE user_id=?", (xp, new_level, user_id))
    con.commit()
    return new_level, xp

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        level, xp = add_xp(message.author.id, 10)
        if xp < 10:
            try:
                await message.channel.send(f"🎉 {message.author.mention} leveled up to level {level}!")
            except: pass

    @app_commands.command(name="rank", description="Show your rank/level")
    async def rank(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cur.execute("SELECT xp, level FROM xp WHERE user_id=?", (interaction.user.id,))
        row = cur.fetchone()
        if not row:
            await interaction.followup.send("You have no XP yet.")
            return
        xp, level = row
        await interaction.followup.send(f"Level: {level} | XP: {xp}")

    @app_commands.command(name="leaderboard", description="Show top users by level")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cur.execute("SELECT user_id, level, xp FROM xp ORDER BY level DESC, xp DESC LIMIT 10")
        rows = cur.fetchall()
        desc = ""
        for r in rows:
            user = interaction.guild.get_member(r[0])
            desc += f"{user.display_name if user else r[0]} — Level {r[1]} XP {r[2]}\\n"
        await interaction.followup.send(desc or "No data.")

async def setup(bot):
    await bot.add_cog(Leveling(bot))
