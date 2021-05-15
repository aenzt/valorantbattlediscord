import discord
from datetime import datetime
import config as cfg

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
    rank_string = cfg.ranks[rank]

    embed.set_footer(text="©Valorant BattleBot")
    embed.set_image(url=ava_url)
    embed.set_author(name=author, icon_url=author_ava)
    embed.add_field(name='Rating', value=rating, inline=True)
    embed.add_field(name='Rank', value=rank_string, inline=True)
    embed.add_field(name='Type', value=tipe, inline=True)
    return embed

def makeembeduser(ctx, name, user_url, point, data_user_cooldown):
    embed = discord.Embed(
        title=name,
        colour = discord.Colour.blue()
    )
    author = ctx.message.author.name
    author_ava = ctx.message.author.avatar_url
    id_user = ctx.message.author.id
    time_now = datetime.utcnow()
    time_diff_gacha = (time_now - data_user_cooldown["gacha"]).total_seconds()
    time_diff_daily = (time_now - data_user_cooldown["daily"]).total_seconds()
    if time_diff_gacha > 86400 :
        time_diff_gacha_string = "`READY`"
    else :
        time_diff_gacha_string = str(int(24 - time_diff_gacha/3600)) + "h" + str(int((60 - time_diff_gacha/60)%60)) + "m"
    if time_diff_daily > 86400 :
        time_diff_daily_string = "`READY`"
    else :
        time_diff_daily_string = str(int(24 - time_diff_gacha/3600)) + "h" + str(int((60 - time_diff_gacha/60)%60)) + "m"
    user_agents = cfg.user_coll.find_one({"_id" : id_user})["agents"]
    owned_agents = ""
    if len(user_agents) > 0:
        for i in user_agents:    
            owned_agents += i["name"] + " [" + str(i["rating"]) + "] " + "`" + cfg.ranks[i["rank"]] + "`\n"
    else: 
        owned_agents = "This user has no agents!"

    embed.set_footer(text="©Valorant BattleBot")
    embed.set_image(url=user_url)
    embed.set_author(name=author, icon_url=author_ava)
    embed.add_field(name='Point', value=point, inline=True)
    embed.add_field(name='Owned', value=owned_agents, inline=False)
    embed.add_field(name='Cooldowns',value="Gacha \t: " + time_diff_gacha_string + "\nDaily \t:" + time_diff_daily_string, inline=False)
    return embed