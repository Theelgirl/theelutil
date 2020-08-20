import json
import os
import re
import subprocess
import random
import math
from io import StringIO
from collections import defaultdict

import discord
import objgraph
import asyncio
import time

import generalconfig as gconf
import dueutil.permissions
from ..game.helpers import imagehelper
from ..permissions import Permission
from .. import commands, util, events
from ..game import customizations, awards, leaderboards, game, weapons, players, shields
from ..game import emojis


@commands.command(args_pattern="S?")
@commands.require_cnf(warning="This will **__permanently__** reset your user and give prestige coins!")
async def prestige(ctx, cnf="", **details):
    """
    [CMD_KEY]prestige
    
    Resets all your stats & any customization, and grants you prestige coins to help you level up faster.
    This cannot be reversed! Use !prestigecheck if you want to see how many coins you'll get without actually prestiging.
    Each prestige coin gives a small bonus to the max amount of stats gained from a quest, and the quest reward.
    Every 100 prestige coins gives you 1 extra teamcash per quest if you're in a team, starting at 50 prestige coins.
    You keep all your teamcash, purchases made with teamcash, quests beaten, and wagers won.
    [PERM]
    """

    player = details["author"]
    if not hasattr(player, "prestiges"):
        player.prestiges = 0
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    if not hasattr(player, "item_limit_x2"):
        player.item_limit_x2 = 1
    if not hasattr(player, "team"):
        player.team = 0
    if not hasattr(player, "team_money"):
        player.team_money = 0
    if not hasattr(player, "defense"):
        player.defense = 1
    if not hasattr(player, "dummy_chance"):
        player.dummy_chance = 1
    if not hasattr(player, "hp_modifier"):
        player.hp_modifier = 1
    if not hasattr(player, "bot"):
        player.bot = 0
    if not hasattr(player, "counts"):
        player.counts = 0
    if not hasattr(player, "topdog_time"):
        player.topdog_time = 0
    if not hasattr(player, "topdog_time_elapsed"):
        player.topdog_time_elapsed = 0
    if not hasattr(player, "quest_spawn_boost"):
        player.quest_spawn_boost = 1
    if not hasattr(player, "slot_increase"):
        player.slot_increase = 0
    if not hasattr(player, "opt_topdog"):
        player.opt_topdog = 0
    if not hasattr(player, "teams_created"):
        player.teams_created = 0
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "dummy_prestige"):
        player.dummy_prestige = 1
    teams = player.teams_created
    team_rank = player.team_rank
    team = player.team
    a = player.prestiges
    b = player.prestige_coins
    if player.team_money >= 2:
        i = player.team_money / 2
    else:
        i = player.team_money
    if player.defense >= 2:
        j = player.defense / 2
    else:
        j = player.defense
    if player.item_limit_x2 >= 2:
        k = player.item_limit_x2 / 2
    else:
        k = player.item_limit_x2
    if player.dummy_chance >= 2:
        l = player.dummy_chance / 2
    else:
        l = player.dummy_chance
    if player.hp_modifier >= 2:
        m = player.hp_modifier / 2
    else:
        m = player.hp_modifier
    if player.quest_spawn_boost > 2:
        r = player.quest_spawn_boost / 2
    else:
        r = player.quest_spawn_boost
    if player.slot_increase > 2:
        s = int(player.slot_increase / 2)
    else:
        s = (player.slot_increase)
    if player.dummy_prestige > 2:
        u = int(player.dummy_prestige / 2)
    else:
        u = (player.dummy_prestige)
    p = player.topdog_time
    q = player.topdog_time_elapsed
    t = player.opt_topdog
    z = (player.strg / 59049)
    try:
        if z < 1:
            z = 1.0001
        c = z ** (player.level / 25 * (player.item_limit_x2 * 1.69))
    except OverflowError:
        c = 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
    try:
        d = (.60266 / math.log((player.strg / 2), z)) + 1.2
    except ValueError:
        d = 1.3
    if d < 1.3:
        d = 1.3
    if d > 3.5:
        d = 3.5
    e = int(math.log(c, d))
    if player.level >= 80:
        player.prestiges += 1
        player.prestige_coins += e
        player.level = 1
        player.exp = 0
        player.total_exp = 0
        player.attack = 1
        player.strg = 1
        player.accy = 1
        player.hp = 10
        player.money = 100
        player.quests = []
        DEFAULT_FACTORIES = {"equipped": lambda: "default", "inventory": lambda: ["default"]}
        player.equipped = defaultdict(players.Player.DEFAULT_FACTORIES["equipped"],
                                    weapon=weapons.NO_WEAPON_ID,
                                    banner="discord blue",
                                    theme="default",
                                    background="default",
                                    shield=shields.NO_SHIELD_ID)
        player.inventory = defaultdict(players.Player.DEFAULT_FACTORIES["inventory"],
                                     weapons=[],
                                     themes=["default"],
                                     backgrounds=["default"],
                                     banners=["discord blue"],
                                     shields=[])
        player.shield = shields.NO_SHIELD_ID
        player.shields = []
        player.team_money = i
        player.defense = j
        player.item_limit_x2 = k
        player.dummy_chance = l
        player.hp_modifier = m
        player.topdog_time = p
        player.topdog_time_elapsed = q
        player.slot_increase = s
        player.quest_spawn_boost = r
        player.opt_topdog = t
        player.teams_created = teams
        player.team_rank = team_rank
        player.team = team
        player.dummy_prestige = u
        player.save()
        language = player.language
        message = "Your user has been reset and you gained **" + str(e) + "** DUP!"
        message2 = "Any team-bought items/boosts that you own have been halved (because you now earn teamcash faster). However, you can still buy more."
        if language != "en":
            x = util.translate_2(message, message2, language)
            message = x[0]
            message2 = x[1]
        await util.say(ctx.channel, "%s %s" % (message, message2))
    else:
        language = player.language
        message = "You need to be level 80 to prestige."
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    player.save()

   
@commands.command(args_pattern=None, aliases=['ps'])
async def prestigecoins(ctx, **details):
    """
    [CMD_KEY]prestigecoins

    Tells you how many prestige coins you currently have and how much the quest stat bonus you recieve from them is.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    if not hasattr(player, "prestiges"):
        player.prestiges = 0
    if not hasattr(player, "dummy_prestige"):
        player.dummy_prestige = 1
    a = player.prestige_bonus()
#    z = (player.strg / 59049)
#    try:
#        b = (.60266 / math.log((player.strg / 2), z)) + 1.2
#    except ValueError:
#        b = 1.4
#    if b < 1.3:
#        b = 1.3
#    if b > 3.5:
#        b = 3.5
#    if player.prestige_coins <= 0:
#        c = 1
#    else:
#        try:
#            c = 1 + round(((((math.log(player.prestige_coins, b) / 10) + (player.prestige_coins / (180 / player.prestiges)))) * player.dummy_prestige), 2)
#        except ZeroDivisionError:
#            c = 1 + round(((((math.log(player.prestige_coins, b) / 10) + (player.prestige_coins / 180))) * player.dummy_prestige), 2)
    language = player.language
    message = "You have **" + str(int(player.prestige_coins)) + "** DUP."
    message2 = "Those give a bonus of **" + str(a) + "** to quest stats and experience."
    message3 = "When you beat a quest, your prestige bonus may go up or down depending on your stat gain."
#    message4 = "If this number is not the same as your bonus, there is definitely a problem with your prestige coins, and the dev will try and fix it: " + str(c)
    if language != "en":
#        x = util.translate_4(message, message2, message3, message4, language)
        x = util.translate_3(message, message2, message3, language)
        message = x[0]
        message2 = x[1]
        message3 = x[2]
#        message4 = x[3]
    await util.say(ctx.channel, "%s %s %s" % (message, message2, message3)) #%s" % (message, message2, message3, message4))


@commands.command(args_pattern=None, aliases=['pc'])
async def prestigecheck(ctx, **details):
    """
    [CMD_KEY]prestigecheck

    Tells you how many prestige coins you can gain by using !prestige.
    [PERM]
    """

    player = details["author"]
    if not hasattr(player, "prestiges"):
        player.prestiges = 0
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    if not hasattr(player, "item_limit_x2"):
        player.item_limit_x2 = 1
    if not hasattr(player, "dummy_prestige"):
        player.dummy_prestige = 1
    z = (player.strg / 59049)
    try:
        if z < 1:
            z = 1.0001
        a = z ** (player.level / 25 * (player.item_limit_x2 * 1.69))
    except OverflowError:
        a = 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
    try:
        b = (.60266 / math.log((player.strg / 2), z)) + 1.2
    except ValueError:
        b = 1.3
    if b < 1.3:
        b = 1.3
    if b > 3.5:
        b = 3.5
    c = int(math.log(a, b))
    if (player.prestige_coins + c) <= 0:
        a = 1
    else:
        a = player.prestige_bonus(prestige=True, bonus=c)
        e = 1 + round((((math.log((player.prestige_coins + c), b) / 10) + ((player.prestige_coins + c) / (180 / (player.prestiges + 1)))) * player.dummy_prestige), 2)
    if player.level >= 80:
        language = player.language
        message = "You can prestige for " + str(c) + " prestige coins. You'll get a " + str(a) + " bonus on quest exp and max stats from it."
#        message2 = "If this number is not the same as your bonus, there is definitely a problem with your prestige coins, and the dev will try and fix it: " + str(c)
        if language != "en":
#            x = util.translate_2(message, message2, language)
            message = util.translate(message, language)
#            message = x[0]
#            message2 = x[1]
        await util.say(ctx.channel, "%s" % (message)) #%s" % (message, message2))
    else:
        language = player.language
        message = "You need to be level 80 to prestige."
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))

@commands.command(args_pattern="M")
async def prestigeshop(ctx, *args, **details):
    """
    [CMD_KEY]prestigeshop (page/item name)
    Use a number for page, and the name of the item in quotes if you want an item.
    Remember, on mobile, you need to hold down the double quotes and select the vertical double quotes (not curvy ones) to encase it in proper quotes for Due.
    At the moment, **You have to write the exact name** of the item you want. The name is shown in the page, and it is not caps-sensitive.
    Use !prestigebuy to buy stuff.
    [PERM]
    """
    player = details["author"]
    shop_embed = discord.Embed(title="DueUtil's Prestigeshop", type="rich", color=gconf.DUE_COLOUR)
    shop_logo = 'https://cdn.discordapp.com/attachments/411657988776919050/563757792809189376/due_pfp.png'
    a = str(args[0])
    shop_embed.set_thumbnail(url=shop_logo)
    language = player.language
    if a in "1" or a in "2":
        page = int(args[0])
        if a in "1":
            message = "Showing items 1-3 in the DueUtil Prestige Shop."
            message2 = "4% Toil Raid Reward Increase"
            message3 = "2% Toil Raid Cooldown Decrease"
            message4 = "Learning Stop"
            message5 = "This costs 10 DUP."
            message6 = "This costs 15 DUP."
            message7 = "This costs 100 DUP."
            if language != "en":
                x = util.translate_7(message, message2, message3, message4, message5, message6, message7, language)
                message = x[0]
                message2 = x[1]
                message3 = x[2]
                message4 = x[3]
                message5 = x[4]
                message6 = x[5]
                message7 = x[6]
            shop_embed.description = message
            shop_embed.add_field(name=message2, value=message5)
            shop_embed.add_field(name=message3, value=message6)
            shop_embed.add_field(name=message4, value=message7)
        await util.say(ctx.channel, embed=shop_embed)
    else:
        item_1 = str(a.lower())
        if item_1 in "4% toil raid reward increase":
            message = "4% Toil Raid Reward Increase"
            message2 = "This item will permanently multiply the percentage of other players' toils you recieve on a successful raid by 1.04, and it costs 10 DUP."
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            shop_embed.add_field(name=message, value=message2)
        elif item_1 in "2% toil raid cooldown decrease":
            message = "2% Toil Raid Cooldown Decrease"
            message2 = "This item will permanently decrease the cooldown of your toil raids by 2%, and it costs 15 DUP."
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            shop_embed.add_field(name=message, value=message2)
        elif item_1 in "learning stop" or item_1 in "learning" or item_1 in "stop":
            message = "Learning Stop"
            message2 = "This item will stop your learning at any point, and costs 100 DUP."
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            shop_embed.add_field(name=message, value=message2)
        else:
            message = "What do you want to buy?"
            message2 = "We couldn't find this item! View the help page for this command for fixing problems!"
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            shop_embed.add_field(name=message, value=message2)
        await util.say(ctx.channel, embed=shop_embed)


@commands.command(args_pattern='CI?', aliases=["pb"])
async def prestigebuy(ctx, amount, number=1, **details):
    """
    [CMD_KEY]prestigebuy (item #) (# of items)

    Gives you stats based on the item number and # of items bought, you can view the item details with ``!prestigeshop``.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "prestiges"):
       player.prestiges = 0
    if not hasattr(player, "toil_raid_reward_increase"):
       player.toil_raid_reward_increase = 1
    if not hasattr(player, "toil_raid_cooldown_decrease"):
       player.toil_raid_cooldown_decrease = 1
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    language = player.language
    if amount == 1:
        if player.prestige_coins >= (number * 10):
            player.toil_raid_reward_increase += (number * .04)
            player.toil_raid_reward_increase = round(player.toil_raid_reward_increase, 2)
            player.prestige_coins -= number * 10
            language = player.language
            message = "Your toil raid reward has been increased to " + str(player.toil_raid_reward_increase) + "x!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
        else:
            message = "You need " + str(number * 10) + "prestige coins to buy this upgrade!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
    elif amount == 2:
        if player.prestige_coins >= (number * 15):
            player.toil_raid_cooldown_decrease += (number * .02)
            player.toil_raid_cooldown_decrease = round(player.toil_raid_cooldown_decrease, 2)
            player.prestige_coins -= number * 10
            language = player.language
            message = "Your toil raid cooldown has been decreased to " + str(player.toil_raid_cooldown_increase) + "x!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
        else:
            message = "You need " + str(number * 15) + "prestige coins to buy this upgrade!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
    elif amount == 3:
        if player.prestige_coins >= (number * 100):
            player.learning = False
            player.prestige_coins -= number * 100
            language = player.language
            message = "Your learning has been stopped!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
        else:
            message = "You need " + str(number * 100) + "prestige coins to buy this item!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
    else:
        language = player.language
        message = "This item does not exist yet! Check the prestige shop for all the items!"
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))



