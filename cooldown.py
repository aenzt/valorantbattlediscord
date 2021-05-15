from datetime import datetime
import config as cfg

def set_default_cooldown(ctx):
    id_user = ctx.message.author.id
    default_time = datetime(1970,1,1)
    coolkids = {
        "gacha" : default_time,
        "daily" : default_time
    }
    cfg.user_coll.update_one({'_id': id_user}, { "$set": {"cooldowns": coolkids}})

def set_cooldown_now(ctx, cooldown_type, data_user_cooldown):
    id_user = ctx.message.author.id
    for i in data_user_cooldown:
        if i == cooldown_type:
            data_user_cooldown[i] = datetime.utcnow()
    cfg.user_coll.update_one({'_id': id_user}, { "$set": {"cooldowns": data_user_cooldown}})