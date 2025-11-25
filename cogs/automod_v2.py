import re, json, os, asyncio, time
import discord
from discord.ext import commands, tasks

CONFIG = os.path.join(os.getcwd(), 'data', 'automod_config.json')
WARN_DB = os.path.join(os.getcwd(), 'data', 'warnings.db')
LINK_REGEX = re.compile(r'https?://\S+')

default_conf = {'bad_words': ['spamword'], 'link_whitelist_roles': []}

def ensure_config():
    if not os.path.exists(CONFIG):
        with open(CONFIG, 'w') as f:
            json.dump(default_conf, f)

class AutoModV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_config()

    def load_conf(self):
        with open(CONFIG) as f:
            return json.load(f)

    def add_warning(self, user_id, guild_id, reason):
        conn = sqlite3.connect(WARN_DB)
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS warns(user_id INTEGER, guild_id INTEGER, reason TEXT, time INTEGER)')
        cur.execute('INSERT INTO warns VALUES(?,?,?,?)', (user_id, guild_id, reason, int(time.time())))
        conn.commit(); conn.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot: return
        conf = self.load_conf()
        lowered = message.content.lower()
        if any(b in lowered for b in conf.get('bad_words', [])):
            try:
                await message.delete()
                await message.channel.send(f'⚠️ {message.author.mention}, that language is not allowed.')
                self.add_warning(message.author.id, message.guild.id, 'bad_language')
            except Exception:
                pass
            return
        if LINK_REGEX.search(message.content):
            # check role whitelist
            allowed = False
            for role_name in conf.get('link_whitelist_roles', []):
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role and role in message.author.roles:
                    allowed = True; break
            if not allowed and not message.author.guild_permissions.manage_messages:
                try:
                    await message.delete()
                    await message.channel.send(f'🔗 {message.author.mention}, links are not allowed here.')
                    self.add_warning(message.author.id, message.guild.id, 'link_posting')
                except Exception:
                    pass

    @commands.command(name='warnings')
    @commands.has_permissions(manage_guild=True)
    async def warnings(self, ctx, member: discord.Member=None):
        member = member or ctx.author
        conn = sqlite3.connect(WARN_DB); cur = conn.cursor()
        cur.execute('SELECT reason, time FROM warns WHERE user_id=? AND guild_id=?', (member.id, ctx.guild.id))
        rows = cur.fetchall(); conn.close()
        if not rows:
            return await ctx.send('No warnings.')
        embed = discord.Embed(title=f'Warnings for {member}', description='Most recent first')
        for reason, t in rows[-10:]:
            embed.add_field(name=reason, value=time.ctime(t), inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    import sqlite3, time
    bot.add_cog(AutoModV2(bot))
