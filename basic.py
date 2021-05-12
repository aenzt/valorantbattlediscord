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

cluster = MongoClient(mongosrv, tls=True, tlsAllowInvalidCertificates=True)
db = cluster['ValorantBot']
collection = db['agent']
user_coll = db['user']

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
async def register(ctx):
    id_user = ctx.message.author.id
    name_user = ctx.message.author.name
    if user_coll.count_documents({'_id': id_user }, limit = 1) != 1:
        post = {
        "_id" : id_user,
        "name" : name_user,
        "points" : 0,
        "agents" : []
        }
        user_coll.insert_one(post)
        await ctx.send("Sucessfully Registered")
    else :
        await ctx.send("Already Registered")

@bot.command()
async def profile(ctx):
    id_user = ctx.message.author.id
    data_user = user_coll.find_one({"_id" : id_user})
    if data_user == None:
        await ctx.send("You must register first!")
    else:
        namauser = data_user['name']
        point = data_user['points']
        id_user = data_user['_id']
        
        author_ava = ctx.message.author.avatar_url
        embed = makeembeduser(ctx, namauser, author_ava, point)
        await ctx.send(embed=embed)

@bot.command()
async def gacha(ctx):
    id_user = ctx.message.author.id
    data_user_query = user_coll.find_one({"_id" : id_user})
    if data_user_query == None:
        await ctx.send("You must register first!")
    else:
        judul_data = collection.aggregate([{"$sample":{"size":1}}])
        rating = random.randint(0,20)
        for result in judul_data :
            judul = result['name']
            ava_url = result['ava_URL']
            rating = rating
            tipe = result['type']
        rarity = getRarity()
        embed = makeembedagent(ctx, judul, ava_url, rating, tipe, rarity)
        data_user_query = user_coll.find_one({"_id" : id_user})
        data_user_new = data_user_query["agents"]
        add_agent = True
        for i in data_user_new:
            if i[0] == result['name']:
                add_agent = False
                break
        if add_agent:
            data_user_new.append([result['name'],rating, rarity])
        else:
            await ctx.send("udah punya idk nanti nanya kalau mau replace atau kgk")
        user_coll.update_one({'_id': id_user}, { "$set": {"agents": data_user_new}})
        await ctx.send(embed=embed)

def getRarity():
    rarity_int = random.randint(1,1000)
    if rarity_int == 1000:
        rarity = "Symshini"
    elif rarity_int > 995:
        rarity = "Radiant"
    elif rarity_int > 970:
        rarity = "Immortal"
    elif rarity_int > 900:
        rarity = "Diamond"
    elif rarity_int > 800:
        rarity = "Platinum"
    elif rarity_int > 640:
        rarity = "Gold"
    elif rarity_int > 460:
        rarity = "Silver"
    elif rarity_int > 260:
        rarity = "Bronze"
    else:
        rarity = "Iron"
    return rarity

def makeembedagent(ctx, judul, ava_url, rating, tipe, rarity):
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
    embed.add_field(name='Rarity', value=rarity, inline=True)
    embed.add_field(name='Type', value=tipe, inline=True)
    return embed

def makeembeduser(ctx, name, user_url, point):
    embed = discord.Embed(
        title=name,
        colour = discord.Colour.blue()
    )
    author = ctx.message.author.name
    author_ava = ctx.message.author.avatar_url
    id_user = ctx.message.author.id
    user_agents = user_coll.find_one({"_id" : id_user})["agents"]
    owned_agents = ""
    if len(user_agents) > 0:
        for i in user_agents:    
            owned_agents += i[0] + " [" + str(i[1]) + "] " + "`" + i[2] + "`\n"
    else: 
        owned_agents = "This user has no agents!"

    embed.set_footer(text="©Valorant BattleBot")
    embed.set_image(url=user_url)
    embed.set_author(name=author, icon_url=author_ava)
    embed.add_field(name='Point', value=point, inline=True)
    embed.add_field(name='Owned', value=owned_agents, inline=False)
    embed.add_field(name='Cooldown 1', value="Not Found", inline=True)
    embed.add_field(name='Cooldown 2', value="Not Found", inline=True)
    embed.add_field(name='Cooldown 3', value="Not Found", inline=True)
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