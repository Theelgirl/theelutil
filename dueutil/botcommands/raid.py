import discord
import random
import math
import time
import os
import asyncio
import jsonpickle

import dueutil.game.awards as game_awards
import generalconfig as gconf
from ..game import players, customizations, weapons
from ..game import stats, game
from ..game.helpers import misc, playersabstract, imagehelper
from .. import commands, util, dbconn, permissions
from ..permissions import Permission

from ..game import (
    quests,
    game,
    battles,
    weapons,
    stats,
    awards,
    players,
    teams,
    raids,
    battles_raid)

from ..game import emojis as e


@commands.command(args_pattern='M?')
async def allraids(ctx, page=1, **details):
    """
    [CMD_KEY]allraids

    Shows all the current active raids.

    To see more detailed info, do ``[CMD_KEY]allraids (raid name)``.
    [PERM]
    """
    global e

    @misc.paginator
    def raid_list(raids_embed, raid, **_):
        raids_embed.add_field(name=raid.name_clean,
                               value="Tier: %s\n" % raid.tier
                                     + "HP Left: %s\n" % str(int(raid.hp))
                                     + "Total HP: %s\n" % raid.total_health
                                     + "HP Percentage: %s" % round(((raid.hp / raid.total_health) * 100), 2)
                                     + "%\n"
                                     + "Reward: %s %s" % (raid.reward, raid.reward_type.upper()))
    if type(page) is int:
        page -= 1

        raids_list = raids.get_all_raids_dict_2(list=True, type="active")
        try:
            raids_list.sort(key=lambda raid: raid.defense, reverse=True)
        except Exception as e:
            await util.say(ctx.channel, "raid list did a bad and couldnt be sorted :( %s" % (str(e)))

        # misc.paginator handles all the messy checks.
        raid_list_embed = discord.Embed(title="All DueUtil Raids!", type="rich", color=gconf.DUE_COLOUR)
        raid_list_embed = raid_list(raids_list, page, "All DueUtil Raids",
                                      footer_more="But wait there's more! Do %sallraids %d" % (details["cmd_key"], page+2),
                                      empty_list="There are no raids yet!\nHow sad.")
        raid_list_embed.set_footer(text="Make sure to put the EXACT raid name in! If you need to go to another page, do %sallraids %d!" % (details["cmd_key"], page+2))

        await util.say(ctx.channel, embed=raid_list_embed)
    else:
        raid_info_embed = discord.Embed(type="rich", color=gconf.DUE_COLOUR)
        raid_name = page
        raid_name = raid_name.lower()
        raid = raids.get_raid_no_id(raid_name, type="active")
        if raid is None:
            raise util.DueUtilException(ctx.channel, "Raid not found!")
        raid_info_embed.title = "Raid information for %s " % raid.name_clean
        try:
            raid_info_embed.add_field(name="Base stats", value=((" **Atk/Strg/Accy** - %s \n"
                                                                  + " **Total HP** - %s\n"
                                                                  + " **Defense** - %s\n"
                                                                  + " **Reward** - %s %s\n")
                                                                 % (raid.attack, raid.total_health, round(raid.defense, 2), raid.reward, raid.reward_type.upper())))
        except:
            raise util.DueUtilException(ctx.channel, "Don't forget the parentheses and the number inside of them!")
        if raid.times_attacked == 0:
            dpb = 0
        else:
            dpb = round(((raid.total_health - raid.hp) / int(raid.times_attacked)), 2)
        raid_info_embed.add_field(name="Other attributes", value=(" **Tier** - %s\n"
                                                                   % raid.tier
                                                                   + '**Times Attacked** - %s\n'
                                                                   % raid.times_attacked
                                                                   + " **Stat Multiplier** - %s\n" % round(raid.stat_multiplier, 1)
                                                                   + " **HP Left** - %s\n"
                                                                   % int(raid.hp)
                                                                   + " **HP Percent Left** - %s\n"
                                                                   % round(((raid.hp / raid.total_health) * 100), 2)
                                                                   + "**Average Damage Done Per Battle** - %s" % dpb),
                                   inline=False)
        raid_info_embed.set_thumbnail(url=raid.image_url)
        await util.say(ctx.channel, embed=raid_info_embed)


@commands.command(args_pattern='S', aliases=["rbt"])
@commands.ratelimit(cooldown=600, error="You can't battle raids again for **[COOLDOWN]**! Give others a chance!", save=True)
@commands.imagecommand()
async def raidbattle(ctx, raid_name, **details):
    """
    [CMD_KEY]raidbattle (raid name)
    
    Battle a raid!
    
    Please enter the full name you see on the raid list, including the parentheses.
    [PERM]
    """
    # TODO: Handle draws
    player = details["author"]

    if not hasattr(player, "defense"):
        player.defense = 1

    raid = raids.get_raid_no_id(raid_name, type="active")
    if raid is None:
        raise util.DueUtilException(ctx.channel, "I couldn't find the raid! Use the whole name, including the parentheses!")
    try:
        if raid.tier == 69420:
            raise util.DueUtilException(ctx.channel, "You can't battle this raid!")
    except:
        raise util.DueUtilException(ctx.channel, "Use the full name to battle this raid!")

    try:
        if (player.equipped["weapon"] != weapons.NO_WEAPON_ID and player.weapon != weapons.NO_WEAPON) or not player.equipped["weapon"] is None:
            raise util.DueUtilException(ctx.channel, "No weapons allowed!")
    except:
        pass
    if player.equipped["weapon"] != "STOCK+2|1|0.66/none":
        raise util.DueUtilException(ctx.channel, "No weapons allowed!")
    if ((player.level // 20) + 1) != raid.tier:
        raise util.DueUtilException(ctx.channel, "Your level needs to be between %s and %s to battle this raid!" % (((raid.tier - 1) * 20), (raid.tier * 20)))
    battle_log = battles_raid.get_battle_log(player_one=player, player_two=raid)

    await imagehelper.battle_screen(ctx.channel, player, raid)
    await util.say(ctx.channel, embed=battle_log.embed)
    if battle_log.winner is None:
        # Both players get the draw battle award
        awards.give_award(ctx.channel, player_one, "InconceivableBattle")
        awards.give_award(ctx.channel, player_two, "InconceivableBattle")