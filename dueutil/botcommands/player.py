import discord
import random
import math
import time
import os
import asyncio
import jsonpickle

import dueutil.game.awards as game_awards
import generalconfig as gconf
from ..game import players, customizations
from ..game import stats, game, gamerules
from ..game.helpers import misc, playersabstract, imagehelper
from .. import commands, util, dbconn, stats2
from ..game import emojis as e
from ..game import (
    quests,
    game,
    battles,
    weapons,
    stats,
    awards,
    players,
    teams)

DAILY_AMOUNT = 50
TRAIN_RANGE = (.4,.6)
HARD_TRAIN_RANGE = (.8,1.2)
INSANE_TRAIN_RANGE = (2.4,3.6)

def load_web_player(player_id):
    response = dbconn.get_collection_by_name("dueutiltechusers").find_one({"_id": player_id})
    if response is not None and 'times_visited' in response:
        player_data = response['times_visited']
        return player_data

@commands.command(args_pattern="P?P?")
async def stats(ctx, *args, **details):
    """
    [CMD_KEY]stats (player 1) (player 2)

    Shows all of your stats without the confusingness of the !info page (but with a lot more clutter), and it also shows hidden stats.
    Player 1 and Player 2 arguments are optional, if you use their ID or ping them it'll show their stats in a separate embed.
    [PERM]
    """
    player_1 = details["author"]
    if not hasattr(player_1, "defense"):
        player_1.defense = 1
    if not hasattr(player_1, "item_limit_x2"):
        player_1.item_limit_x2 = 1
    if not hasattr(player_1, "hp_modifier"):
        player_1.hp_modifier = 1
    if not hasattr(player_1, "dummy_chance"):
        player_1.dummy_chance = 1
    if not hasattr(player_1, "prestiges"):
        player_1.prestiges = 0
    if not hasattr(player_1, "prestige_coins"):
        player_1.prestige_coins = 0
    if not hasattr(player_1, "defense"):
        player_1.defense = 1
    if not hasattr(player_1, "slot_increase"):
        player_1.slot_increase = 0
    if not hasattr(player_1, "quest_spawn_boost"):
        player_1.quest_spawn_boost = 1
    if not hasattr(player_1, "education"):
        player_1.education = 1
    if len(args) == 0:
        stat_embed = discord.Embed(title="Your stats!", type="rich", color=gconf.DUE_COLOUR)
        stat_embed.add_field(name="Level:", value=player_1.level)
        stat_embed.add_field(name="Attack:", value=str(int(player_1.attack)))
        stat_embed.add_field(name="Strength:", value=str(int(player_1.strg)))
        stat_embed.add_field(name="Accuracy:", value=str(int(player_1.accy)))
        stat_embed.add_field(name="Base HP:", value=str(int(player_1.level * 10 * player_1.hp_modifier)))
        stat_embed.add_field(name="DUT:", value=str(int(player_1.money)))
        stat_embed.add_field(name="Defense:", value=player_1.defense)
        stat_embed.add_field(name="Item Limit Modifier:", value=player_1.item_limit_x2)
        stat_embed.add_field(name="Dummy Chance Modifier:", value=player_1.dummy_chance)
        stat_embed.add_field(name="Weapon Slot Increases:", value=player_1.slot_increase)
        stat_embed.add_field(name="Quest Spawn Chance Modifier:", value=str(round(player_1.quest_spawn_boost, 3)))
        stat_embed.add_field(name="Prestiges:", value=player_1.prestiges)
        stat_embed.add_field(name="Prestige Coins:", value=player_1.prestige_coins)
        stat_embed.add_field(name="Education:", value=player_1.education)
        await util.say(ctx.channel, embed=stat_embed)
    if len(args) == 1:
        player_2 = args[0]
        if not hasattr(player_2, "defense"):
            player_2.defense = 1
        if not hasattr(player_2, "item_limit_x2"):
            player_2.item_limit_x2 = 1
        if not hasattr(player_2, "hp_modifier"):
            player_2.hp_modifier = 1
        if not hasattr(player_2, "dummy_chance"):
            player_2.dummy_chance = 1
        if not hasattr(player_2, "prestiges"):
            player_2.prestiges = 0
        if not hasattr(player_2, "prestige_coins"):
            player_2.prestige_coins = 0
        if not hasattr(player_2, "defense"):
            player_2.defense = 1
        if not hasattr(player_2, "slot_increase"):
            player_2.slot_increase = 0
        if not hasattr(player_2, "quest_spawn_boost"):
            player_2.quest_spawn_boost = 1
        if not hasattr(player_2, "education"):
            player_2.education = 1
        stat_embed = discord.Embed(title="Your stats!", type="rich", color=gconf.DUE_COLOUR)
        stat_embed.add_field(name="Level:", value=player_1.level)
        stat_embed.add_field(name="Attack:", value=str(int(player_1.attack)))
        stat_embed.add_field(name="Strength:", value=str(int(player_1.strg)))
        stat_embed.add_field(name="Accuracy:", value=str(int(player_1.accy)))
        stat_embed.add_field(name="Base HP:", value=str(int(player_1.level * 10 * player_1.hp_modifier)))
        stat_embed.add_field(name="DUT:", value=str(int(player_1.money)))
        stat_embed.add_field(name="Defense:", value=player_1.defense)
        stat_embed.add_field(name="Item Limit Modifier:", value=player_1.item_limit_x2)
        stat_embed.add_field(name="Dummy Chance Modifier:", value=player_1.dummy_chance)
        stat_embed.add_field(name="Weapon Slot Increases:", value=player_1.slot_increase)
        stat_embed.add_field(name="Quest Spawn Chance Modifier:", value=str(round(player_1.quest_spawn_boost, 3)))
        stat_embed.add_field(name="Prestiges:", value=player_1.prestiges)
        stat_embed.add_field(name="Prestige Coins:", value=player_1.prestige_coins)
        stat_embed.add_field(name="Education:", value=player_1.education)
        stat_embed_2 = discord.Embed(title="Player 1's stats!", type="rich", color=gconf.DUE_COLOUR)
        stat_embed_2.add_field(name="Level:", value=player_2.level)
        stat_embed_2.add_field(name="Attack:", value=str(int(player_2.attack)))
        stat_embed_2.add_field(name="Strength:", value=str(int(player_2.strg)))
        stat_embed_2.add_field(name="Accuracy:", value=str(int(player_2.accy)))
        stat_embed_2.add_field(name="Base HP:", value=str(int(player_2.level * 10 * player_2.hp_modifier)))
        stat_embed_2.add_field(name="DUT:", value=str(int(player_2.money)))
        stat_embed_2.add_field(name="Defense:", value=player_2.defense)
        stat_embed_2.add_field(name="Item Limit Modifier:", value=player_2.item_limit_x2)
        stat_embed_2.add_field(name="Dummy Chance Modifier:", value=player_2.dummy_chance)
        stat_embed_2.add_field(name="Weapon Slot Increases:", value=player_2.slot_increase)
        stat_embed_2.add_field(name="Quest Spawn Chance Modifier:", value=str(round(player_2.quest_spawn_boost, 3)))
        stat_embed_2.add_field(name="Prestiges:", value=player_2.prestiges)
        stat_embed_2.add_field(name="Prestige Coins:", value=player_2.prestige_coins)
        stat_embed_2.add_field(name="Education:", value=player_2.education)
        await util.say(ctx.channel, embed=stat_embed)
        await util.say(ctx.channel, embed=stat_embed_2)
    if len(args) == 2:
        player_2 = args[0]
        if not hasattr(player_2, "defense"):
            player_2.defense = 1
        if not hasattr(player_2, "item_limit_x2"):
            player_2.item_limit_x2 = 1
        if not hasattr(player_2, "hp_modifier"):
            player_2.hp_modifier = 1
        if not hasattr(player_2, "dummy_chance"):
            player_2.dummy_chance = 1
        if not hasattr(player_2, "prestiges"):
            player_2.prestiges = 0
        if not hasattr(player_2, "prestige_coins"):
            player_2.prestige_coins = 0
        if not hasattr(player_2, "defense"):
            player_2.defense = 1
        if not hasattr(player_2, "slot_increase"):
            player_2.slot_increase = 0
        if not hasattr(player_2, "quest_spawn_boost"):
            player_2.quest_spawn_boost = 1
        player_3 = args[1]
        if not hasattr(player_3, "defense"):
            player_3.defense = 1
        if not hasattr(player_3, "item_limit_x2"):
            player_3.item_limit_x2 = 1
        if not hasattr(player_3, "hp_modifier"):
            player_3.hp_modifier = 1
        if not hasattr(player_3, "dummy_chance"):
            player_3.dummy_chance = 1
        if not hasattr(player_3, "prestiges"):
            player_3.prestiges = 0
        if not hasattr(player_3, "prestige_coins"):
            player_3.prestige_coins = 0
        if not hasattr(player_3, "defense"):
            player_3.defense = 1
        if not hasattr(player_3, "slot_increase"):
            player_3.slot_increase = 0
        if not hasattr(player_3, "quest_spawn_boost"):
            player_3.quest_spawn_boost = 1
        if not hasattr(player_3, "education"):
            player_3.education = 1
        stat_embed = discord.Embed(title="Your stats!", type="rich", color=gconf.DUE_COLOUR)
        stat_embed.add_field(name="Level:", value=player_1.level)
        stat_embed.add_field(name="Attack:", value=str(int(player_1.attack)))
        stat_embed.add_field(name="Strength:", value=str(int(player_1.strg)))
        stat_embed.add_field(name="Accuracy:", value=str(int(player_1.accy)))
        stat_embed.add_field(name="Base HP:", value=str(int(player_1.level * 10 * player_1.hp_modifier)))
        stat_embed.add_field(name="DUT:", value=str(int(player_1.money)))
        stat_embed.add_field(name="Defense:", value=player_1.defense)
        stat_embed.add_field(name="Item Limit Modifier:", value=player_1.item_limit_x2)
        stat_embed.add_field(name="Dummy Chance Modifier:", value=player_1.dummy_chance)
        stat_embed.add_field(name="Weapon Slot Increases:", value=player_1.slot_increase)
        stat_embed.add_field(name="Quest Spawn Chance Modifier:", value=str(round(player_1.quest_spawn_boost, 3)))
        stat_embed.add_field(name="Prestiges:", value=player_1.prestiges)
        stat_embed.add_field(name="Prestige Coins:", value=player_1.prestige_coins)
        stat_embed.add_field(name="Education:", value=player_1.education)
        stat_embed_2 = discord.Embed(title="Player 1's stats!", type="rich", color=gconf.DUE_COLOUR)
        stat_embed_2.add_field(name="Level:", value=player_2.level)
        stat_embed_2.add_field(name="Attack:", value=str(int(player_2.attack)))
        stat_embed_2.add_field(name="Strength:", value=str(int(player_2.strg)))
        stat_embed_2.add_field(name="Accuracy:", value=str(int(player_2.accy)))
        stat_embed_2.add_field(name="Base HP:", value=str(int(player_2.level * 10 * player_2.hp_modifier)))
        stat_embed_2.add_field(name="DUT:", value=str(int(player_2.money)))
        stat_embed_2.add_field(name="Defense:", value=player_2.defense)
        stat_embed_2.add_field(name="Item Limit Modifier:", value=player_2.item_limit_x2)
        stat_embed_2.add_field(name="Dummy Chance Modifier:", value=player_2.dummy_chance)
        stat_embed_2.add_field(name="Weapon Slot Increases:", value=player_2.slot_increase)
        stat_embed_2.add_field(name="Quest Spawn Chance Modifier:", value=str(round(player_2.quest_spawn_boost, 3)))
        stat_embed_2.add_field(name="Prestiges:", value=player_2.prestiges)
        stat_embed_2.add_field(name="Prestige Coins:", value=player_2.prestige_coins)
        stat_embed_2.add_field(name="Education:", value=player_2.education)
        stat_embed_3 = discord.Embed(title="Player 2's stats!", type="rich", color=gconf.DUE_COLOUR)
        stat_embed_3.add_field(name="Level:", value=player_3.level)
        stat_embed_3.add_field(name="Attack:", value=str(int(player_3.attack)))
        stat_embed_3.add_field(name="Strength:", value=str(int(player_3.strg)))
        stat_embed_3.add_field(name="Accuracy:", value=str(int(player_3.accy)))
        stat_embed_3.add_field(name="Base HP:", value=str(int(player_3.level * 10 * player_3.hp_modifier)))
        stat_embed_3.add_field(name="DUT:", value=str(int(player_3.money)))
        stat_embed_3.add_field(name="Defense:", value=player_3.defense)
        stat_embed_3.add_field(name="Item Limit Modifier:", value=player_3.item_limit_x2)
        stat_embed_3.add_field(name="Dummy Chance Modifier:", value=player_3.dummy_chance)
        stat_embed_3.add_field(name="Weapon Slot Increases:", value=player_3.slot_increase)
        stat_embed_3.add_field(name="Quest Spawn Chance Modifier:", value=str(round(player_3.quest_spawn_boost, 3)))
        stat_embed_3.add_field(name="Prestiges:", value=player_3.prestiges)
        stat_embed_3.add_field(name="Prestige Coins:", value=player_3.prestige_coins)
        stat_embed_3.add_field(name="Education:", value=player_3.education)
        await util.say(ctx.channel, embed=stat_embed)
        await util.say(ctx.channel, embed=stat_embed_2)
        await util.say(ctx.channel, embed=stat_embed_3)

@commands.command(args_pattern=None)
@commands.ratelimit(cooldown=86400, error="You can't collect your daily reward again for **[COOLDOWN]**!", save=True)
async def daily(ctx, **details):
    """
    [CMD_KEY]daily

    ¤50! Your daily DUT/teamcash!

    You can use this command once every 24 hours!
    [PERM]
    """

    player = details["author"]
    if not hasattr(player, "streak"):
        player.streak = 0
    if not hasattr(player, "streak_check"):
        player.streak_check = 0
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "team_money"):
        player.team_money = 0
    if not hasattr(player, "web_visits"):
        player.web_visits = 0
    a = float(time.time()) - player.streak_check
    if a >= 129600:
        player.streak = 1
        message = "Your streak was reset for not collecting daily after 36 hours! (12 hour grace period)"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    message3 = "Your streak has gone up by one!"
    if a >= 86400:
        player.streak += 1
        player.streak_check = time.time()
    else:
        message3 = "It has not been 24 hours since you last used ``!daily`` or ``!vote``, so your streak stayed the same!"
    player.streak_check = time.time()
    times_visited = load_web_player(player.id) 
    if times_visited is None:
        times_visited = 0       
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    b = int(.1 * player.level * player.streak) + 1
    try:
        if times_visited >= (int(player.web_visits) + 3):
            DAILY_AMOUNT_2 = DAILY_AMOUNT * 3
            b = b * 4
            player.web_visits = times_visited
            await util.say(ctx.channel, "Your daily was quadrupled for visiting ``https://dueutil.org/``! Thank you so much!")
        else:
            DAILY_AMOUNT_2 = DAILY_AMOUNT
            if random.random() <= .33:
                await util.say(ctx.channel, "Your daily could be quadrupled by visiting https://dueutil.org/ 3 times or more since your last daily!")
    except:
        player.web_visits = 0
        if times_visited >= (int(player.web_visits) + 3):
            DAILY_AMOUNT_2 = DAILY_AMOUNT * 3
            b = b * 4
            player.web_visits = times_visited
            await util.say(ctx.channel, "Your daily was quadrupled for visiting ``https://dueutil.org/``! Thank you so much")
        else:
            DAILY_AMOUNT_2 = DAILY_AMOUNT
            if random.random() <= .33:
                await util.say(ctx.channel, "Your daily could be quadrupled by visiting https://dueutil.org/ 3 times or more since your last daily!")
    if player.team != None:
        player.team_money += b
    BALANCED_AMOUNT = DAILY_AMOUNT * player.level * player.streak
    player.money += BALANCED_AMOUNT
    player.streak += 1
    player.save()
    c = player.streak - 1
    if player.team is None:
        message = str(player) + " collected their daily " + str(BALANCED_AMOUNT) + " DUT!"
        message2 = "You have a " + str(c) + " day streak!"
        language = player.language
        if language != "en":
            x = util.translate_3(message, message2, message3, language)
            message = x[0]
            message2 = x[1]
            message3 = x[2]
        await util.say(ctx.channel, e.DUT + " %s %s %s" % (message, message2, message3))
    if player.team != None:
        message = str(player) + " collected their daily " + str(BALANCED_AMOUNT) + " DUT, and " + str(b) + " teamcash!"
        message2 = "You have a " + str(c) + " day streak!"
        language = player.language
        if language != "en":
            x = util.translate_3(message, message2, message3, language)
            message = x[0]
            message2 = x[1]
            message3 = x[2]
        await util.say(ctx.channel, e.DUT + " %s %s %s" % (message, message2, message3))

@commands.command(args_pattern=None, aliases=["t"])
@commands.ratelimit(cooldown=14400,
                    error="You've done all the training you can for now! You can train again in **[COOLDOWN]**!",
                    save=True)
async def train(ctx, **details):
    """
    [CMD_KEY]train

    Train to get a little exp to help you with quests.

    This will never give you much exp! But should help you out with quests early on!

    You can use this command once every 4 hours!
    [PERM]
    """

    player = details["author"]

    attack_increase = random.uniform(*TRAIN_RANGE) * player.level
    strg_increase = random.uniform(*TRAIN_RANGE) * player.level
    accy_increase = random.uniform(*TRAIN_RANGE) * player.level
        
    player.progress(attack_increase, strg_increase, accy_increase,
                    max_exp=200000, max_attr=2000)
    progress_message = players.STAT_GAIN_FORMAT % (attack_increase, strg_increase, accy_increase)
    await game.check_for_level_up(ctx, player)
    player.save()
    language = player.language
    message = "training complete"
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "**%s** %s!\n%s" % (player, message, progress_message))


@commands.command(args_pattern=None, aliases=["ht"])
@commands.ratelimit(cooldown=28800,
                    error="You've done all the training you can for now! You can train again in **[COOLDOWN]**!",
                    save=True)
async def hardtrain(ctx, **details):
    """
    [CMD_KEY]hardtrain

    Train to get a bit of exp to help you with quests.

    This will only give you a bit of exp! But should help you out with quests early on!

    You can use this command once every 12 hours!
    [PERM]
    """

    player = details["author"]

    attack_increase = random.uniform(*HARD_TRAIN_RANGE) * player.level
    strg_increase = random.uniform(*HARD_TRAIN_RANGE) * player.level
    accy_increase = random.uniform(*HARD_TRAIN_RANGE) * player.level
        
    player.progress(attack_increase, strg_increase, accy_increase,
                    max_exp=400000, max_attr=4000)
    progress_message = players.STAT_GAIN_FORMAT % (attack_increase, strg_increase, accy_increase)
    await game.check_for_level_up(ctx, player)
    player.save()
    language = player.language
    message = "training complete"
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "**%s** %s!\n%s" % (player, message, progress_message))



@commands.command(args_pattern=None, aliases=["it"])
@commands.ratelimit(cooldown=86400,
                    error="You've done all the training you can for now! You can train again in **[COOLDOWN]**!",
                    save=True)
async def insanetrain(ctx, **details):
    """
    [CMD_KEY]insanetrain

    Train to get a bunch of exp to help you with quests.

    This will give a lot of exp! But it will mostly help you out with quests early on!

    You can use this command once every 24 hours!
    [PERM]
    """

    player = details["author"]

    attack_increase = random.uniform(*INSANE_TRAIN_RANGE) * player.level
    strg_increase = random.uniform(*INSANE_TRAIN_RANGE) * player.level
    accy_increase = random.uniform(*INSANE_TRAIN_RANGE) * player.level
        
    player.progress(attack_increase, strg_increase, accy_increase,
                    max_exp=1200000, max_attr=12000)
    progress_message = players.STAT_GAIN_FORMAT % (attack_increase, strg_increase, accy_increase)
    await game.check_for_level_up(ctx, player)
    player.save()
    language = player.language
    message = "training complete"
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "**%s** %s!\n%s" % (player, message, progress_message))


@commands.command(args_pattern="PI", aliases=["dep"])
@commands.ratelimit(cooldown=172800, error="You can't deposit money again for **[COOLDOWN]**!", save=True)
async def deposit(ctx, player, amount, **_):
    """
    [CMD_KEY]deposit (player) (amount)

    The first command that Theel made, kept for sentimental reasons.
    [PERM]
    """
    if amount>= 10000001 or amount<= 999:
        raise util.DueUtilException(ctx.channel, "You can't deposit more than 10,000,000 DUT, less than 1,000, or more than what you have!")
    elif amount>= player.money:
        raise util.DueUtilException(ctx.channel, "You can't deposit more than 10,000,000 DUT, less than 1,000, or more than what you have!")
    else:
        interest_amount = amount * .25
        player.money += interest_amount
        await util.say(ctx.channel, "Interest was recieved! We hope to see you in another two days!")


@commands.command(args_pattern=None, aliases=["lim"])
async def mylimit(ctx, **details):
    """
    [CMD_KEY]mylimit

    Shows the weapon price you're limited to.
    [PERM]
    """

    player = details["author"]

    if not hasattr(player, "item_limit_x2"):
        player.item_limit_x2 = 1
    if not hasattr(player, "dummy_limit"):
        player.dummy_limit = 1
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0

    if player.item_limit_x2 < 1:
        player.item_limit_x2 = 1
    if player.dummy_limit >= 10:
        player.dummy_limit = 2
        await util.say(ctx.channel, "Your dummy limit was reset to normal because it there was a big bug in the code that made some people's limit 10x higher than it should have been!")

    precise_level = player.level + player.exp / gamerules.get_exp_for_next_level(player.level)
    x = int(10 * (math.pow(precise_level, 1.8) / 3
                  + 0.4 * math.pow(precise_level + 1, 1.75) * precise_level))
    y = util.format_number(x, money=True, full_precision=True)
    z = round((player.item_value_limit / x), 2)

    await util.say(ctx.channel, ("You're currently limited to weapons with a value up to **%s**!\n"
                                 + "Your base limit is **%s**, and your limit multiplier is %s.\n")
                   % (util.format_number(player.item_value_limit, money=True, full_precision=True), y, z))


@commands.command(args_pattern="S?", aliases=["bn"])
async def battlename(ctx, name="", **details):
    """
    [CMD_KEY]battlename (name)
    
    Sets your name in DueUtil.
    To reset your name to your discord name, run the command with no arguments.
    [PERM]
    """

    player = details["author"]
    if "[" in name or ";" in name or "\\" in name or "/" in name:
        raise util.DueUtilException(ctx.channel, "No semicolons, backslashes, forward slashes or, [ please!")
        util.logger.info("%s tried to make their name have a ; or [ or /.")
    else:
        if name != "":
            name_len_range = players.Player.NAME_LENGTH_RANGE
            if len(name) not in name_len_range:
                raise util.DueUtilException(ctx.channel, "Battle name must be between **%d-%d** characters long!"
                                                         % (min(name_len_range), max(name_len_range)))
            player.name = name
        else:
            player.name = details["author_name"]

    player.save()
    await util.say(ctx.channel, "Your battle name has been set to **%s**!" % player.name_clean)


@commands.command(args_pattern=None, aliases=["mi"])
@commands.imagecommand()
async def myinfo(ctx, **details):
    """
    [CMD_KEY]myinfo
    
    Shows your info!
    [PERM]
    """

    await imagehelper.stats_screen(ctx.channel, details["author"])


def player_profile_url(player_id):
    private_record = dbconn.conn()["public_profiles"].find_one({"_id": player_id})

    if private_record is None or private_record["private"]:
        return None
    return "https://dueutil.org/player?id=%s" % player_id


@commands.command(args_pattern=None)
async def myprofile(ctx, **details):
    """
    [CMD_KEY]myprofile

    Gives the link to your dueutil.org profile
    [PERM]
    """

    profile_url = player_profile_url(details["author"].id)

    if profile_url is None:
        await util.say(ctx.channel, (":lock: Your profile is currently set to private!\n"
                                     + "If you want a public profile login to <https://dueutil.org/>"
                                     + " and make your profile public in the settings. Use !info to view your stats."))
    else:
        await util.say(ctx.channel, "Your profile is at %s" % profile_url)


@commands.command(args_pattern='P')
async def profile(ctx, player, **_):
    """
    [CMD_KEY]profile @player

    Gives a link to a player's profile!
    [PERM]
    """

    profile_url = player_profile_url(player.id)

    if profile_url is None:
        await util.say(ctx.channel, ":lock: **%s** profile is private! Use !info to view your stats." % player.get_name_possession_clean())
    else:
        await util.say(ctx.channel, "**%s** profile is at %s" % (player.get_name_possession_clean(), profile_url))


@commands.command(args_pattern='P', aliases=["in"])
@commands.imagecommand()
async def info(ctx, player, **details):
    """
    [CMD_KEY]info @player
    
    Shows the info of another player!
    [PERM]
    """

    await imagehelper.stats_screen(ctx.channel, player)


async def show_awards(ctx, player, page=0):
    # Always show page 1 (0)
    if page != 0 and page * 5 >= len(player.awards):
        raise util.DueUtilException(ctx.channel, "Page not found")

    await imagehelper.awards_screen(ctx.channel, player, page,
                                    is_player_sender=ctx.author.id == player.id)


@commands.command(args_pattern='C?')
@commands.imagecommand()
async def myawards(ctx, page=1, **details):
    """
    [CMD_KEY]myawards (page number)
    
    Shows your awards!
    [PERM]
    """

    await show_awards(ctx, details["author"], page - 1)


@commands.command(args_pattern='PC?')
@commands.imagecommand()
async def awards(ctx, player, page=1, **_):
    """
    [CMD_KEY]awards @player (page number)
    
    Shows a players awards!
    [PERM]
    """

    await show_awards(ctx, player, page - 1)


@commands.command(args_pattern="S?")
@commands.require_cnf(warning="This will **__permanently__** reset your user, including prestige coins!")
async def resetme(ctx, cnf="", **details):
    """
    [CMD_KEY]resetme
    
    Resets all your stats & any customization.
    This cannot be reversed!
    [PERM]
    """

    player = details["author"]
    if not hasattr(player, "teams_created"):
        player.teams_created = 0
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    teams = player.teams_created
    team_rank = player.team_rank
    team = player.team
    rate_limits = player.command_rate_limits
    player.reset(ctx.author)
    player.teams_created = teams
    player.team_rank = team_rank
    player.team = team
    player.command_rate_limits = rate_limits
    player.save()
    util.logger.info("%s reset themself." % (player.id))
    await util.say(ctx.channel, "Your user has been reset, with the exception of your team information.")


@commands.command(args_pattern='PCS?', aliases=["sc"])
async def sendcash(ctx, receiver, transaction_amount, message="", **details):
    """
    [CMD_KEY]sendcash @player amount (optional message)
    
    Sends some cash to another player.
    Note: The maximum amount someone can receive is ten times their limit.
    
    Example usage:
    
    [CMD_KEY]sendcash @MacDue 1000000 "for the lit bot fam"
    
    or
    
    [CMD_KEY]sendcash @MrAwais 1
    [PERM]
    """

    sender = details["author"]
    amount_string = util.format_number(transaction_amount, money=True, full_precision=True)


    if not hasattr(sender, "item_limit_x2"):
        sender.item_limit_x2 = 1

    if receiver.id == sender.id:
        raise util.DueUtilException(ctx.channel, "There is no reason to send money to yourself!")

    if sender.money - transaction_amount < 0:
        if sender.money > 0:
            await util.say(ctx.channel, ("You do not have **" + amount_string + "**!\n"
                                                                                "The maximum you can transfer is **"
                                         + util.format_number(sender.money, money=True, full_precision=True) + "**"))
        else:
            await util.say(ctx.channel, "You do not have any money to transfer!")
        return

    max_receive = int(receiver.item_value_limit * 10)
    if transaction_amount > max_receive:
        await util.say(ctx.channel, ("**" + amount_string
                                     + "** is more than ten times **" + receiver.name_clean
                                     + "**'s limit!\nThe maximum **" + receiver.name_clean
                                     + "** can receive is **"
                                     + util.format_number(max_receive, money=True, full_precision=True) + "**!"))
        return

    sender.money -= transaction_amount
    receiver.money += transaction_amount

    sender.save()
    receiver.save()

#    stats.increment_stat(stats.Stat.MONEY_TRANSFERRED, int(transaction_amount))
    if transaction_amount >= 50:
        await game_awards.give_award(ctx.channel, sender, "SugarDaddy", "Sugar daddy!")

    transaction_log = discord.Embed(title=e.DUT_WITH_WINGS + " Transaction complete!", type="rich",
                                    color=gconf.DUE_COLOUR)
    transaction_log.add_field(name="Sender:", value=sender.name_clean)
    transaction_log.add_field(name="Recipient:", value=receiver.name_clean)
    transaction_log.add_field(name="Transaction amount (DUT):", value=amount_string, inline=False)
    if message != "":
        transaction_log.add_field(name=":pencil: Attached note:", value=message, inline=False)
    transaction_log.set_footer(text="Please keep this receipt for your records.")
    await util.say(ctx.channel, embed=transaction_log)

@commands.command(hidden=True, args_pattern=None)
async def benfont(ctx, **details):
    """
    [CMD_KEY]benfont 
    
    Shhhhh...
    [PERM]
    """

    player = details["author"]
    player.benfont = not player.benfont
    player.save()
    if player.benfont:
        await util.get_client(ctx.server.id).send_file(ctx.channel, 'assets/images/nod.gif')
        await game_awards.give_award(ctx.channel, player, "BenFont", "ONE TRUE *type* FONT")


"""
WARNING: Setter & my commands use decorators to be lazy

Setters just return the item type & inventory slot. (could be done without
the decorators but setters must be fucntions anyway to be commands)

This is part of my quest in finding lazy ways to do things I cba.
"""


# Think about clean up & reuse
@commands.command(args_pattern='M?')
@playersabstract.item_preview
def mythemes(player):
    """
    [CMD_KEY]mythemes (optional theme name)
    
    Shows the amazing themes you can use on your profile.
    If you use this command with a theme name you can get a preview of the theme!
    """

    return {"thing_type": "theme",
            "thing_list": list(player.get_owned_themes().values()),
            "thing_lister": theme_page,
            "my_command": "mythemes",
            "set_command": "settheme",
            "thing_info": theme_info,
            "thing_getter": customizations.get_theme}


@commands.command(args_pattern='S')
@playersabstract.item_setter
def settheme():
    """
    [CMD_KEY]settheme (theme name)
    
    Sets your profile theme
    """

    return {"thing_type": "theme", "thing_inventory_slot": "themes"}


@commands.command(args_pattern='M?', aliases=("mybackgrounds", "backgrounds"))
@playersabstract.item_preview
def mybgs(player):
    """
    [CMD_KEY]mybgs (optional background name)
    
    Shows the backgrounds you've bought!
    """

    return {"thing_type": "background",
            "thing_list": list(player.get_owned_backgrounds().values()),
            "thing_lister": background_page,
            "my_command": "mybgs",
            "set_command": "setbg",
            "thing_info": background_info,
            "thing_getter": customizations.get_background}


@commands.command(args_pattern='S', aliases=["setbackground"])
@playersabstract.item_setter
def setbg():
    """
    [CMD_KEY]setbg (background name)
    
    Sets your profile background
    """

    return {"thing_type": "background", "thing_inventory_slot": "backgrounds"}


@commands.command(args_pattern='M?')
@playersabstract.item_preview
def mybanners(player):
    """
    [CMD_KEY]mybanners (optional banner name)
    
    Shows the banners you've bought!
    """
    return {"thing_type": "banner",
            "thing_list": list(player.get_owned_banners().values()),
            "thing_lister": banner_page,
            "my_command": "mybanners",
            "set_command": "setbanner",
            "thing_info": banner_info,
            "thing_getter": customizations.get_banner}


@commands.command(args_pattern='S')
@playersabstract.item_setter
def setbanner():
    """
    [CMD_KEY]setbanner (banner name)
    
    Sets your profile banner
    """

    return {"thing_type": "banner", "thing_inventory_slot": "banners"}


# Part of the shop buy command
@misc.paginator
def theme_page(themes_embed, theme, **extras):
    price_divisor = extras.get('price_divisor', 1)
    themes_embed.add_field(name=theme["icon"] + " | " + theme["name"], value=(theme["description"] + "\n ``"
                                                                              + util.format_number(
        theme["price"] // price_divisor, money=True, full_precision=True) + "``"))


@misc.paginator
def background_page(backgrounds_embed, background, **extras):
    price_divisor = extras.get('price_divisor', 1)
    backgrounds_embed.add_field(name=background["icon"] + " | " + background["name"],
                                value=(background["description"] + "\n ``"
                                       + util.format_number(background["price"] // price_divisor, money=True,
                                                            full_precision=True) + "``"))


@misc.paginator
def banner_page(banners_embed, banner, **extras):
    price_divisor = extras.get('price_divisor', 1)
    banners_embed.add_field(name=banner.icon + " | " + banner.name,
                            value=(banner.description + "\n ``"
                                   + util.format_number(banner.price // price_divisor,
                                                        money=True, full_precision=True) + "``"))


def theme_info(theme_name, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    theme = details.get('theme', customizations.get_theme(theme_name))
    embed.title = str(theme)
    embed.set_image(url=theme["preview"])
    embed.set_footer(text="Buy this theme for " + util.format_number(theme["price"] // price_divisor, money=True,
                                                                     full_precision=True))
    return embed


def background_info(background_name, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    background = customizations.get_background(background_name)
    embed.title = str(background)
    embed.set_image(url="https://dueutil.org/duefiles/backgrounds/" + background["image"])
    embed.set_footer(
        text="Buy this background for " + util.format_number(background["price"] // price_divisor, money=True,
                                                             full_precision=True))
    return embed


def banner_info(banner_name, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    banner = customizations.get_banner(banner_name)
    embed.title = str(banner)
    if banner.donor:
        embed.description = ":star2: This is a __donor__ banner!"
    embed.set_image(url="https://dueutil.org/duefiles/banners/" + banner.image_name)
    embed.set_footer(text="Buy this banner for " + util.format_number(banner.price // price_divisor, money=True,
                                                                      full_precision=True))
    return embed

