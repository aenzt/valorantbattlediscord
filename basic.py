# This example requires the 'members' privileged intents

import discord
from discord import colour
from discord.activity import Activity
from discord.ext import commands
import random
import pymongo
from pymongo import MongoClient 
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('auth', 'discordtoken')
mongosrv = config.get('auth', 'mongosrv')

cluster = MongoClient(mongosrv, tls=True, tlsAllowInvalidCertificates=True)
db = cluster['ValorantBot']
collection = db['agent']
user_coll = db['user']
weapons = db['weapons']
ranks = ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Immortal', 'Radiant']

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

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
        user = {
        "_id" : id_user,
        "name" : name_user,
        "points" : 0,
        "agents" : []
        }
        user_coll.insert_one(user)
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
        await ctx.send("You must register first!, `?register`")
    else:
        roll = random.randint(1,100)
        if roll > 80: # Rolled an agent
            print("Rolled agent!")
            judul_data = collection.aggregate([{"$sample":{"size":1}}])
            rating = random.randint(0,20)
            for result in judul_data :
                judul = result['name']
                ava_url = result['ava_URL']
                tipe = result['type']
            rank = 0
            embed = makeembedagent(ctx, judul, ava_url, rating, tipe, rank)
            data_user_new = data_user_query["agents"]
            add_agent = True
            agent_idx = 0
            for i in range(len(data_user_new)):
                if data_user_new[i]["name"] == result['name']:
                    agent_idx = i
                    add_agent = False
                    break
            if add_agent:
                await ctx.send(embed=embed)
                data_user_new.append({"name": result['name'],"rating": rating, "rank": rank})
            else:
                embed_dupe = make_embed_dupe(ctx, judul, ava_url, data_user_new[agent_idx]["rating"], tipe, data_user_new[agent_idx]["rank"])
                if data_user_new[agent_idx]["rank"] < 7:
                    data_user_new[agent_idx]["rank"] += 1 
                    embed_dupe.description = "Congratulations! Your " + judul + " has ranked \nup to " + ranks[data_user_new[agent_idx]["rank"]] + "."
                else:
                    embed_dupe.description = "Congratulations! Your " + judul + " has already \nreached the highest rank.\n (kasih vp atau apa gitu idk)."
                await ctx.send(embed=embed_dupe)
            user_coll.update_one({'_id': id_user}, { "$set": {"agents": data_user_new}})
        else: # Rolled a weapon
            print("Rolled weapon!")
            weapon_type = weapons.aggregate([{"$sample":{"size":1}}])
            weapon_type = list(weapon_type)[0]
            weapon, rarity = get_random_weapon(weapon_type)
            embed_weapon = make_embed_weapon(ctx, weapon_type["_id"], weapon["name"],weapon["img_url"],rarity)
            await ctx.send(embed=embed_weapon)

def get_random_weapon(weapon_type):
    rarity_int = random.randint(1,100)
    if rarity_int > 98 and weapon_type["Exclusive"] != None:
        return random.choice(weapon_type["Exclusive"]), "Exclusive"
    elif rarity_int > 93:
        return random.choice(weapon_type["Ultra"]), "Ultra"
    elif rarity_int > 85:
        return random.choice(weapon_type["Premium"]), "Premium"
    elif rarity_int > 70:
        return random.choice(weapon_type["Deluxe"]), "Deluxe"
    elif rarity_int > 50:
        return random.choice(weapon_type["Select"]), "Select"
    else:
        return weapon_type["Default"][0], "Default"

def make_embed_weapon(ctx, weapon_type, weapon_name, img_url, rarity):
    embed = discord.Embed(
        title=weapon_type,
        colour = discord.Colour.blue()
    )
    author = ctx.message.author.name
    author_ava = ctx.message.author.avatar_url

    embed.set_footer(text="©Valorant BattleBot")
    embed.set_image(url=img_url)
    embed.set_author(name=author, icon_url=author_ava)
    embed.add_field(name='Skin', value=weapon_name, inline=True)
    embed.add_field(name='Rarity', value=rarity, inline=True)
    return embed

def make_embed_dupe(ctx, judul, ava_url, rating, tipe, rank):
    embed=discord.Embed(title=judul+"\n`(Duplicate Received)`",colour = discord.Colour.blue())
    embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    embed.set_image(url = ava_url)
    embed.set_footer(text="©Valorant BattleBot")
    #tiga line di bawah untuk nampilin stats agent nya menurut gw mending gk usah tapi idk
    #embed.add_field(name='Rating', value=rating)
    #embed.add_field(name='Rank', value=ranks[rank])
    #embed.add_field(name='Type', value=tipe)
    return embed

def makeembedagent(ctx, judul, ava_url, rating, tipe, rank):
    embed = discord.Embed(
        title=judul,
        colour = discord.Colour.blue()
    )
    author = ctx.message.author.name
    author_ava = ctx.message.author.avatar_url
    rank_string = ranks[rank]

    embed.set_footer(text="©Valorant BattleBot")
    embed.set_image(url=ava_url)
    embed.set_author(name=author, icon_url=author_ava)
    embed.add_field(name='Rating', value=rating, inline=True)
    embed.add_field(name='Rank', value=rank_string, inline=True)
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
            owned_agents += i["name"] + " [" + str(i["rating"]) + "] " + "`" + ranks[i["rank"]] + "`\n"
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