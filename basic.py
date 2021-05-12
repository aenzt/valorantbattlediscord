# This example requires the 'members' privileged intents

import discord
from discord import colour
from discord.activity import Activity
from discord.ext import commands
import random
import pymongo
from pymongo import MongoClient
import configparser

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('auth', 'discordtoken')
mongosrv = config.get('auth', 'mongosrv')

cluster = MongoClient(mongosrv)
db = cluster['ValorantBot']
collection = db['agent']

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=5, name="Life"))

@bot.command()
async def gacha(ctx):
    judul_data = collection.aggregate([{"$sample":{"size":1}}])
    for result in judul_data :
        judul = result['name']
        ava_url = result['ava_URL']
        rating = result['rating']
        tipe = result['type']
    embed = makeembed(ctx, judul, ava_url, rating, tipe)

    await ctx.send(embed=embed)

def makeembed(ctx, judul, ava_url, rating, tipe):
    embed = discord.Embed(
        title=judul,
        colour = discord.Colour.blue()
    )
    author = ctx.message.author.name
    author_ava = ctx.message.author.avatar_url

    embed.set_footer(text="©Riot Games")
    embed.set_image(url=ava_url)
    embed.set_author(name=author, icon_url=author_ava)
    embed.add_field(name='Rating', value=rating, inline=True)
    embed.add_field(name='Type', value=tipe, inline=True)
    return embed

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return
    except discord.ext.commands.errors.MissingRequiredArgument:
        await ctx.send('Error no argument')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send('rolled {0}'.format(result))

@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))

@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

bot.run(token)