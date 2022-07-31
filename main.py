import discord
from discord.ext import commands
import os

from music_cog import music_cog

bot = commands.Bot(command_prefix="/")

bot.add_cog(music_cog(bot))

bot.run(os.getenv("farsi"))