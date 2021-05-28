import discord
from discord.ext import commands
import random
from datetime import datetime
import config as cfg
import embedded as emb
import cooldown as cd

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
    if cfg.user_coll.count_documents({'_id': id_user }, limit = 1) != 1:
        user = {
        "_id" : id_user,
        "name" : name_user,
        "points" : 0,
        "agents" : [],
        "cooldowns" : {},
        "weapons" : [],
        "teams_comp" : []
        }
        cfg.user_coll.insert_one(user)
        cd.set_default_cooldown(ctx)
        await ctx.send("Sucessfully Registered")
    else :
        await ctx.send("Already Registered")

@bot.command()
async def profile(ctx):
    id_user = ctx.message.author.id
    data_user = cfg.user_coll.find_one({"_id" : id_user})
    data_user_cooldowns = data_user['cooldowns'] 
    if data_user == None:
        await ctx.send("You must register first!")
    else:
        namauser = data_user['name']
        point = data_user['points']
        id_user = data_user['_id']
        
        author_ava = ctx.message.author.avatar_url
        embed = emb.makeembeduser(ctx, namauser, author_ava, point, data_user_cooldowns)
        await ctx.send(embed=embed)

@bot.command()
async def gacha(ctx):
    id_user = ctx.message.author.id
    data_user_query = cfg.user_coll.find_one({"_id" : id_user})
    time_now = datetime.utcnow()
    if data_user_query == None:
        await ctx.send("You must register first!, `?register`")
    else:
        data_user_cooldowns = data_user_query['cooldowns']   
        # for i in data_user_cooldowns:
        #     if i == "gacha" :
        #         time_diff = (time_now - data_user_cooldowns[i]).total_seconds()
        #         if time_diff<86400 :
        #             await ctx.send("Still in Cooldown, Wait " + str(int(24 - time_diff/3600)) + " hours " + str(int((60 - time_diff/60)%60)) + " minutes")
        #             return
        cd.set_cooldown_now(ctx, "gacha", data_user_cooldowns)
        roll = random.randint(1,100)
        if roll > 80: # Rolled an agent
            print("Rolled agent!")
            judul_data = cfg.collection.aggregate([{"$sample":{"size":1}}])
            rating = random.randint(0,20)
            for result in judul_data :
                judul = result['name']
                ava_url = result['ava_URL']
                tipe = result['type']
            rank = 0
            embed = emb.makeembedagent(ctx, judul, ava_url, rating, tipe, rank)
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
                embed_dupe = emb.make_embed_dupe(ctx, judul, ava_url, data_user_new[agent_idx]["rating"], tipe, data_user_new[agent_idx]["rank"])
                if data_user_new[agent_idx]["rank"] < 7:
                    data_user_new[agent_idx]["rank"] += 1 
                    embed_dupe.description = "Congratulations! Your " + judul + " has ranked \nup to " + cfg.ranks[data_user_new[agent_idx]["rank"]] + "."
                else:
                    embed_dupe.description = "Congratulations! Your " + judul + " has already \nreached the highest rank.\n (kasih vp atau apa gitu idk)."
                await ctx.send(embed=embed_dupe)
            cfg.user_coll.update_one({'_id': id_user}, { "$set": {"agents": data_user_new}})
        else: # Rolled a weapon
            print("Rolled weapon!")
            add_weapon = True
            data_weapon_new = data_user_query['weapons']
            weapon_type = cfg.weapons.aggregate([{"$sample":{"size":1}}])
            weapon_type = list(weapon_type)[0]
            weapon, rarity = get_random_weapon(weapon_type)
            weapon_data = {
                "_id" : weapon_type["_id"],
                "name" : weapon ["name"],
                "rarity" : rarity
            }
            for i in range(len(data_weapon_new)):
                if data_weapon_new[i]["name"] == weapon_data['name']:
                    add_weapon = False
                    break
            if add_weapon :
                cfg.user_coll.update_one({'_id' : id_user}, {'$push' : {"weapons" : weapon_data}}, upsert=True)
                embed_weapon = emb.make_embed_weapon(ctx, weapon_type["_id"], weapon["name"],weapon["img_url"],rarity)
                await ctx.send(embed=embed_weapon)
            else :
                point_random_dupe = random.randint(3, 10)
                point_user = data_user_query["points"]
                new_point = point_user + point_random_dupe
                cfg.user_coll.update_one({'_id': id_user}, { "$set": {"points": new_point}})
                await ctx.send("`Found duplicated weapon`, converted to " + str(point_random_dupe) + " points. Current points : " + str(new_point))
                
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

@bot.command()
async def daily(ctx):
    id_user = ctx.message.author.id
    data_user_query = cfg.user_coll.find_one({"_id" : id_user})
    time_now = datetime.utcnow()
    if data_user_query == None:
        await ctx.send("You must register first!, `?register`")
    else:
        data_user_cooldowns = data_user_query['cooldowns']   
        for i in data_user_cooldowns:
            if i == "daily" :
                time_diff = (time_now - data_user_cooldowns[i]).total_seconds()
                if time_diff<86400 :
                    await ctx.send("Still in Cooldown, Wait " + str(int(24 - time_diff/3600)) + " hours " + str(int((60 - time_diff/60)%60)) + " minutes")
                    return
        cd.set_cooldown_now(ctx, "daily", data_user_cooldowns)
        point_user = data_user_query["points"]
        random_point = random.randint(1, 5)
        new_point_user = point_user + random_point
        cfg.user_coll.update_one({'_id': id_user}, { "$set": {"points": new_point_user}})
        await ctx.send("Successfully claimed daily reward, got " + str(random_point) + " .Current point : " + str(new_point_user))

@bot.command()
async def agentlist(ctx):
    embed_agent_list = emb.makeembedagentlist(ctx)
    await ctx.send(embed=embed_agent_list)

@bot.command()
async def weaponlist(ctx):
    embed_weapon_list = emb.makeembedweaponlist(ctx)
    await ctx.send(embed=embed_weapon_list)

@bot.command()
async def team(ctx):
    id_user = ctx.message.author.id
    data_user = cfg.user_coll.find_one({"_id" : id_user})
    data_user_teams = data_user['teams_comp']
    if data_user_teams == [] :
        await ctx.send("No team yet, made one via `?maketeam`")

@bot.command()
async def maketeam(ctx):
    id_user = ctx.message.author.id
    data_user = cfg.user_coll.find_one({"_id" : id_user})
    data_user_teams = data_user['teams_comp']
    if data_user == None :
        await ctx.send("You must register first!, `?register`")
    else:
        if data_user_teams != [] :
            await ctx.send("You already formed a team, edit your team via `?editteam`")
        else:
            embed_weapon_team_list, count_ag = emb.makeembedagentlist_1(ctx)
            await ctx.send(embed=embed_weapon_team_list)
            valid = False
            id_count =0
            while valid == False :    
                def check(m):
                    return ctx.author == m.author #To make sure it is the only message author is getting
                msg = await bot.wait_for('message', timeout=60.0, check=check)
                msg = str(msg.content.lower())
                msg = msg.split(",")
                if len(msg) > 5 :
                    await ctx.send("Max Agent is 5, input again")
                elif len(msg) > count_ag :
                    await ctx.send("Agent not owned, input again")
                else:
                    valid = True
            if valid == True :
                for i in msg :
                    user_agents = cfg.user_coll.find_one({"_id" : id_user})["agents"][int(i)]
                    data_input = {
                        "_id" : id_count,
                        "name" : user_agents['name'],
                        "rating" : user_agents['rating'],
                        "rank" : user_agents['rank'],
                    }
                    id_count+=1
                    cfg.user_coll.update_one({'_id' : id_user}, {'$push' : {'teams_comp': data_input}})
                await ctx.send("Succesfully made your team")    

bot.run(cfg.token)