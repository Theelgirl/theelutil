import json
import os
import re
import random
import subprocess
import math
import time
from decimal import Decimal
from io import StringIO

import discord
import objgraph
import asyncio

import generalconfig as gconf
import dueutil.permissions
from ..game.helpers import imagehelper
from ..permissions import Permission
from .. import commands, util, events
from ..game import customizations, awards, leaderboards, game, players, battles
from ..game import emojis


@commands.command(args_pattern="P?S?", aliases=['tr'])
@commands.imagecommand()
async def toilraid(ctx, *args, **details):
    """
    [CMD_KEY]toilraid (player) (optional: currency)
    Use this to attempt to take another player's unclaimed toil rewards.
    Currency defaults to DUT, however it can also be Strg, Atk, Accy, or DUP.
    [PERM]
    """
    raider = details["author"]
    if len(args) == 0:
        x = game.criminals
        criminals_embed = discord.Embed(title="Criminals:", type="rich", color=gconf.DUE_COLOUR)
        if len(x) > 0:            
            y = '>, <@!'.join(x)
            y = str(y)
            y = "<@!" + y
            y = y + ">"
            y = y.replace('[', ' ')
            y = y.replace(']', ' ')
            criminals_embed.add_field(name="List of Tax-Evaders to raid:", value=y)
        else:
            criminals_embed.add_field(name="There's nobody to raid!", value="Wait a bit for someone to not pay their taxes!")
        await util.say(ctx.channel, embed=criminals_embed)
    elif len(args) >= 1:
        player = args[0]
        if not hasattr(raider, "toil_raid_reward_increase"):
           raider.toil_raid_reward_increase = 1
        if not hasattr(raider, "toil_raid_cooldown_decrease"):
           raider.toil_raid_cooldown_decrease = 1
        if not hasattr(raider, "toil_raid_cooldown"):
           raider.toil_raid_cooldown = 0
        if not hasattr(raider, "toil_raids"):
           raider.toil_raids = 0
        if not hasattr(player, "job"):
           player.job = []
        if raider.id == player.id:
            raise util.DueUtilException(ctx.channel, "You can't raid yourself!")
        if not (-1 * 30) < (raider.level - player.level) < 15:
            raise util.DueUtilException(ctx.channel, "You can't raid someone more than 15 levels below you or 30 above!")
        if raider.toil_raid_cooldown > int(time.time()):
            cooldown = util.display_time(raider.toil_raid_cooldown - int(time.time()))
            raise util.DueUtilException(ctx.channel, "You can't raid someone else for **%s**!" % (cooldown))
        if not player.id in game.criminals:
            raise util.DueUtilException(ctx.channel, "You can't raid someone who has filed their taxes or doesn't have a job!")
        if len(player.job) == 0:
            raise util.DueUtilException(ctx.channel, "You can't raid someone who doesn't have a job!")
        battle_log = battles.get_battle_log(player_one=raider, player_two=player)
        winner = battle_log.winner
        loser = battle_log.loser

        a = ((raider.level - player.level) + 30) / 100

        if winner == raider:
            if not hasattr(raider, "job"):
                raider.job = []
            if not hasattr(player, "education"):
                player.education = 1
            if not hasattr(raider, "job_level"):
                raider.job_level = 1
            if not hasattr(player, "last_work"):
               player.last_work = time.time()
            if len(args) == 1:
                currency = "dut"
                for i in player.job:
                    try:
                        job_number = int(gconf.JOBS.index(i) + 1)
                    except:
                        raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon!")
                if player.education >= 2:
                    x = int(((time.time() - player.last_work) / 2) * (job_number / 2) * math.log(player.education, 2)) * (a * raider.toil_raid_reward_increase)
                else:
                    x = int(((time.time() - player.last_work) / 2) * (job_number / 2)) * (a * raider.toil_raid_reward_increase)
                raider.money += x
                y = (int(time.time()) - player.last_work) * (a * raider.toil_raid_reward_increase)
                z = a * raider.toil_raid_reward_increase * 100
                z = round(z, 2)
                player.last_work = (int(time.time()) - y)
                x = int(x)
                x = str(x)
                await util.say(ctx.channel, "You got %s DUT/DUP, which was %s percent of the the reward available!" % (x, z))
            if len(args) == 2:
                currency = args[1]
                if currency == "atk" or currency == "strg" or currency == "accy":
                    for i in player.job:
                        try:
                            job_number = int(gconf.JOBS.index(i) + 1)
                        except:
                            raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon!")
                    if player.education >= 2:
                        x = int(((time.time() - player.last_work) / 864) * (job_number / 2) * math.log(player.education, 2)) * (a * raider.toil_raid_reward_increase)
                    else:
                        x = int(((time.time() - player.last_work) / 864) * (job_number / 2)) * (a * raider.toil_raid_reward_increase)
                    if currency == "atk":
                        raider.attack += x
                    elif currency == "strg":
                        raider.strg += x
                    elif currency == "accy":
                        raider.accy += x
                    y = (int(time.time()) - player.last_work) * (a * raider.toil_raid_reward_increase)
                    z = a * raider.toil_raid_reward_increase * 100
                    z = round(z, 2)
                    player.last_work = (int(time.time()) - y)
                    x = round(x, 1)
                    x = str(x)
                    await util.say(ctx.channel, "You got %s of the stat you picked, which was %s percent of the the reward available!" % (x, z))
                elif currency == "dup":
                    if not hasattr(raider, "prestige_coins"):
                        raider.prestige_coins = 0
                    for i in player.job:
                        try:
                            job_number = int(gconf.JOBS.index(i) + 1)
                        except:
                            raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon!")
                    if player.education >= 2:
                        x = int(((time.time() - player.last_work) / 129600) * (job_number / 2) * math.log(player.education, 2)) * (a * raider.toil_raid_reward_increase)
                    else:
                        x = int(((time.time() - player.last_work) / 129600) * (job_number / 2)) * (a * raider.toil_raid_reward_increase)
                    raider.prestige_coins += x
                    y = (int(time.time()) - player.last_work) * (a * raider.toil_raid_reward_increase)
                    z = a * raider.toil_raid_reward_increase * 100
                    z = round(z, 2)
                    player.last_work = (int(time.time()) - y)
                    x = round(x, 1)
                    x = str(x)
                    await util.say(ctx.channel, "You got %s DUT, %s percent of the the reward available!" % (x, z))
                else:
                    await util.say(ctx.channel, "Please use a valid currency! Valid currencies are DUP, Atk, Strg, or Accy. Don't specify a currency if you want DUT.")
            raider.toil_raids += 1
        else:
            await imagehelper.battle_screen(ctx.channel, raider, player)
            await util.say(ctx.channel, embed=battle_log.embed)
            raider.toil_raid_cooldown = int(time.time()) + (a * 120)
            await util.say(ctx.channel, "You lost!")
        raider.save()
        player.save()

@commands.command(args_pattern=None)
async def learntime(ctx, **details):
    """
    [CMD_KEY]learntime
    Tells you how much time you have left to learn.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "learning"):
        player.learning = False
    if not hasattr(player, "education"):
        player.education = 1
    if player.learning == True:
        time_1 = player.learning_end - int(time.time())
        time_2 = util.display_time(time_1)
        language = player.language
        message = "You have " + str(time_2) + " left of learning time! Your current education tier is " + str(player.education) + "!"
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    else:
        language = player.language
        message = "You are not learning, and your current education tier is " + str(player.education) + "!"
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))

@commands.command(args_pattern="S?")
@commands.require_cnf(warning="You will have a half chance to gain quests for 24 hours times your current education tier!")
async def learn(ctx, cnf="", **details):
    """
    [CMD_KEY]learn
    Ranks up your education tier so you can get better jobs.
    You will have only half the chance to get quests for 24 hours times the tier you're trying to level to.
    Having teacher as your job means you get 3 education every 2 learning periods, instead of 2 education over 2 learning periods.
    Having head teacher in addition to teacher gives you 4 education every 2 learning periods.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "learning"):
        player.learning = False
    if not hasattr(player, "education"):
        player.education = 1
    if not hasattr(player, "learning_end"):
        player.learning_end = time.time()
    if not player.learning:
        player.learning = True
        player.learning_end = int(time.time() + (86400 * player.education))
        language = player.language
        message = "Learning started! You'll be at tier " + str(player.education + 1) + " when you're finished if you don't have the teacher job! I'll DM you when it's done!"
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    else:
        language = player.language
        message = "Wait for your current learning to finish!"
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    player.save()

@commands.command(args_pattern="P?")
async def joblist(ctx, *args, **details):
    """
    [CMD_KEY]joblist (optional: other player)

    Shows a list of all jobs, and your/their current job(s).
    [PERM]
    """
    if len(args) == 0:
        player = details["author"]
    else:
        player = args[0]
    job_embed = discord.Embed(title="Job data!", type="rich", color=gconf.DUE_COLOUR)
    if not hasattr(player, "job"):
        player.job = []
    if not hasattr(player, "education"):
        player.education = 1
    jobs = gconf.CAPITALIZED_JOBS
    job_buffs = gconf.CAPITALIZED_JOB_BUFFS
    job_list = []
    available_job_list = []
    a = 0
    b = 0
    for i in jobs:
        job_list.append(i)
        b += 1
    for i in job_list:
        try:
            job_list.insert(((2 * a) + 1), job_buffs[a])
        except:
            try:
                job_list.append(job_buffs[a])
            except:
                pass
        a = a + 1
    try:
        available_job_list = job_list[0:(2 * int(player.education - 1))]
    except:
        available_job_list = job_list[0:(len(job_list) - 1)]
    available_job_list = iter(available_job_list)
    available_job_list = [job+next(available_job_list, '') for job in available_job_list]
    y = '**, '.join(available_job_list)
    y = str(y)
    y = y.replace('[', ' ')
    y = y.replace(']', ' ')
    if y == "":
        y = "You can't equip any jobs right now! You need to learn to equip some!"
    if player.language != "en":
        y = util.translate(y, player.language)
    job_embed.add_field(name="Job/Buff Pairs That You Can Equip:", value=y)
    job_list = iter(job_list)
    job_list = [job+next(job_list, '') for job in job_list]
    x = '**, '.join(job_list)
    x = str(x)
    x = x.replace('[', ' ')
    x = x.replace(']', ' ')
    job_embed.add_field(name="All Job/Buff Pairs:", value=x)
    if len(player.job) > 0:
        x = 0
        for i in player.job:
            try:
                job_number = int(gconf.JOBS.index(player.job[x]) + 1)
                z = "One of your/their jobs:"
                if player.language != "en":
                    z = util.translate(z, player.language)
                job_embed.add_field(name=z, value=player.job[x])
            except Exception as e:
                raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon! **%s**" % (e))
            x += 1
    else:
        z = "You don't have any jobs!"
        if player.language != "en":
            z = util.translate(z, player.language)
        job_embed.set_footer(text=z)
    max_job = jobs[int(player.education) - 2]
    if int(player.education) - 2 < 0:
        max_job = "None"
    if (int(player.education) - 1) > 0:
        lan = "The highest job you can get right now is " + str(max_job) + "!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        job_embed.set_footer(text=lan)
    else:
        lan = "You can't get any jobs right now!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        job_embed.set_footer(text=lan)
    await util.say(ctx.channel, embed=job_embed)
    job_list.clear()
    available_job_list.clear()


@commands.command(args_pattern=None)
async def filetaxes(ctx, **details):
    """
    [CMD_KEY]filetaxes
    Files your taxes for you so the Duevernment doesn't take it.
    The higher your job tier is, the more you pay in taxes.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "job"):
        player.job = []
    if not hasattr(player, "tax_filing"):
        player.tax_filing = time.time()
    if not hasattr(player, "tax_status"):
        player.tax_status = True
    if len(player.job) > 0:
        x = 0
        for i in player.job:
            try:
                job_number = int(gconf.JOBS.index(player.job[x]) + 1)
            except:
                raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon!")
            if (player.money - (((int((int(time.time()) - int(player.tax_filing)))) + (job_number ** 1.5)))) < 10000:
                if player.money >= 10000:
                    a = player.money - 10000
                    player.money = 10000
                else:
                    player.tax_filing = int(time.time())
                    lan = "You don't have to pay taxes if you have less than 10k DUT!"
                    if player.language != "en":
                        lan = util.translate(lan, player.language)
                    raise util.DueUtilException(ctx.channel, "%s" % (lan))
            else:
                player.money -= int(((int(time.time()) - int(player.tax_filing)) + (job_number ** 1.5)))
                a = int(((int(time.time()) - int(player.tax_filing)) + (job_number ** 1.5)))
            x += 1
        player.tax_status = True
        player.tax_filing = int(time.time())
        if player.id in game.criminals:
            game.criminals.remove(player.id)
        lan = "You paid your taxes for one of your jobs! **" + str(a) + "** DUT has been taken from your balance. Make sure to file again within 24 hours, or people will be able to toilraid you!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    else:
        lan = "You don't have a job!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    player.save()

@commands.command(args_pattern=None)
async def leavejobs(ctx, **details):
    """
    [CMD_KEY]leavejobs
    Leaves your job(s).
    Try to only use it if you can't remember to pay taxes, as jobs are a big benefit.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "job"):
        player.job = []
    if not hasattr(player, "last_work"):
        player.last_work = time.time()
    if not hasattr(player, "tax_status"):
        player.tax_status = False
    if not hasattr(player, "tax_filing"):
        player.tax_filing = time.time()
    if len(player.job) > 0:
        player.job = []
        player.tax_status = False
        player.tax_filing = time.time()
        x = (player.level ** 2) * 10
        player.money -= x
        lan = "You left all your jobs, and had to pay **" + str(x) + "** DUT in paperwork fees!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    else:
        lan = "You're not in a job!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    player.save()

@commands.command(args_pattern="S")
async def joinjob(ctx, job_name, **details):
    """
    [CMD_KEY]joinjob (job name)
    Lets you join a job (choices viewed with !jobs).
    Each day, you need to file taxes with ``!filetaxes``. 
    If you don't file your taxes for 48 hours, the Duevernment will fine you 2 DUT every second.
    To start working, use !toil.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "job"):
        player.job = []
    if not hasattr(player, "education"):
        player.education = 1
    if not hasattr(player, "tax_status"):
        player.tax_status = False
    if not hasattr(player, "tax_filing"):
        player.tax_filing = time.time()
    job_name = job_name.lower()
    jobs = gconf.JOBS
    if player.education > (len(gconf.JOBS) - 1):
        player.education = len(gconf.JOBS) - 1
    education = player.education
    if len(player.job) <= int(player.education * .25):
        if job_name in player.job:
            lan = "You already have this job!"
            if player.language != "en":
                lan = util.translate(lan, player.language)
            raise util.DueUtilException(ctx.channel, "%s" % (lan))
        elif job_name in jobs[0:(int(player.education) - 1)]:
            player.job.append(job_name)
            player.tax_status = True
            player.tax_filing = int(time.time())
            lan = "Your job is now " + str(job_name) + "!"
            if player.language != "en":
                lan = util.translate(lan, player.language)
            await util.say(ctx.channel, "%s" % (lan))
        else:
            lan = "Either your education isn't high enough for this job, or this job doesn't exist!"
            if player.language != "en":
                lan = util.translate(lan, player.language)
            await util.say(ctx.channel, "%s" % (lan))
    else:
        lan = "You already have the max jobs for your education level!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    player.save()

@commands.command(args_pattern="S?")
async def jobstats(ctx, job_name="376166105917554701", **details):
    """
    [CMD_KEY]jobstats (job name)
    Tells you the rewards you'd get for a job.
    [PERM]
    """
    player = details["author"]
    lan = "Job data!"
    if player.language != "en":
        lan = util.translate(lan, player.language)
    job_embed = discord.Embed(title=lan, type="rich", color=util.random_embed_color_decimal())
    if not hasattr(player, "last_work"):
        player.last_work = time.time()
    if not hasattr(player, "education"):
        player.education = 1
    job_name = job_name.lower()
    jobs = gconf.JOBS
    if job_name == "376166105917554701":
        if len(player.job) <= 0:
            raise util.DueUtilException(ctx.channel, "You don't have any jobs!")
        else:
            a = 0
            b = 0
            c = 0
            d = 0
            for i in player.job:
                try:
                    job_number = int(gconf.JOBS.index(i) + 1)
                except:
                    raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon!")
                if player.education >= 2:
                    a += int(((time.time() - player.last_work) / 2) * (job_number / 2) * math.log(player.education, 2))
                    b += int(((time.time() - player.last_work) / 129600) * (job_number / 2) * math.log(player.education, 2))
                    c += int(((time.time() - player.last_work) / 864) * (job_number / 2) * math.log(player.education, 2))
                    d += int(((time.time() - player.last_work) / 86400) * player.education)
                else:
                    a += int(((time.time() - player.last_work) / 2) * (job_number / 2))
                    b += int(((time.time() - player.last_work) / 129600) * (job_number / 2))
                    c += int(((time.time() - player.last_work) / 864) * (job_number / 2))
                    d += int(((time.time() - player.last_work) / 86400) * player.education)
            a = str(a)
            b = str(b)
            c = str(c)
            d = str(d)
            job_embed.add_field(name="DUT Reward For All Your Jobs", value=a)
            job_embed.add_field(name="DUP Reward For All Your Jobs", value=b)
            job_embed.add_field(name="ATK/STRG/ACCY Reward For All Your Jobs", value=c)
            job_embed.add_field(name="Job Level Reward For All Your Jobs", value=d)
    max_job = jobs[int(player.education) - 2]
    if int(player.education) - 2 < 0:
        max_job = "None"
    if job_name in jobs:
        job_number = jobs.index(job_name) + 1
        if player.education >= 2:
            a = str(int(((time.time() - player.last_work) / 2) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
            b = str(int(((time.time() - player.last_work) / 172800) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
            c = str(int(((time.time() - player.last_work) / 864) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
            d = str(int(((time.time() - player.last_work) / 86400) * player.education))
        else:
            a = str(int(((time.time() - player.last_work) / 2) * (job_number / 4)))
            b = str(int(((time.time() - player.last_work) / 172800) * (job_number / 4)))
            c = str(int(((time.time() - player.last_work) / 864) * (job_number / 4)))
            d = str(int(((time.time() - player.last_work) / 86400) * player.education))
        lan = "DUT Reward:"
        lan_2 = "DUP Reward:"
        lan_3 = "Attack/Strength/Accuracy Reward:"
        lan_4 = "Job Level Reward:"
        lan_5 = "You need at least 2 education for job level to affect your earnings. The highest job you can get right now is " + str(max_job) + ". Your current job level is " + str(player.job_level) + "."
        lan_6 = "You need at least 2 education for job level to affect your earnings. The highest job you can get right now is " + str(max_job) + "."
        if player.language != "en":
            x = util.translate_6(lan, lan_2, lan_3, lan_4, lan_5, lan_6, player.language)
            lan = x[0]
            lan_2 = x[1]
            lan_3 = x[2]
            lan_4 = x[3]
            lan_5 = x[4]
            lan_6 = x[5]
        job_embed.add_field(name=lan, value=a)
        job_embed.add_field(name=lan_2, value=b)
        job_embed.add_field(name=lan_3, value=c)
        job_embed.add_field(name=lan_4, value=d)
        try:
            job_embed.set_footer(text=lan_5)
        except:
            job_embed.set_footer(text=lan_6)
    else:
        lan = "This Job Does Not Exist!"
        lan_2 = "Read The Above Sentence!"
        if player.language != "en":
            x = util.translate(lan, player.language)
            lan = x[0]
            lan_2 = x[1]
        await util.say(ctx.channel, "%s" % (lan))
        job_embed.add_field(name=lan, value=lan_2)
    await util.say(ctx.channel, embed=job_embed)


@commands.command(args_pattern="SS?")
async def toil(ctx, currency, job="", **details):
    """
    [CMD_KEY]toil (currency/stat for rewards) (job you want to toil with)
    Basically a work command, but named different so it doesn't interfere with other bots.
    Higher job level means more rewards from toiling.
    Currency or Stat can be:
    DUT (normal money)
    DUP (prestige coins)
    Atk (attack stat)
    Accy (accuracy stat)
    Strg (strength stat)
    Level (job level)
    You have to enter DUT, DUP, Atk, Accy, Strg, or Level for it to work.
    [PERM]
    """
    player = details["author"]
    currency == currency.lower()
    if not hasattr(player, "job"):
        player.job = []
    if not hasattr(player, "last_work"):
        player.last_work = time.time()
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    if not hasattr(player, "education"):
        player.education = 1
    if not hasattr(player, "job_level"):
        player.job_level = 3
    currency = currency.lower()
    try:
        job = job.lower()
    except:
        job = ""
    a = 0
    if player.job_level < 3:
        player.job_level = 3
    b = len(player.job)
    if len(player.job) > 0 and job == "":
        x = []
        for i in player.job:
#            if a == 1:
#                break
            try:
                job_number = int(gconf.JOBS.index(i) + 1)
            except:
                raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon!")
            if currency == "dut":
                if player.education >= 2:
                    x.append(int(((time.time() - player.last_work) / 2) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
                else:
                    x.append(int(((time.time() - player.last_work) / 2) * (job_number / 4)))
                if b == (a + 1):
                    player.last_work = time.time()
            elif currency == "dup":
                if player.education >= 2:
                    x.append(int(((time.time() - player.last_work) / 172800) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
                else:
                    x.append(int(((time.time() - player.last_work) / 172800) * (job_number / 4)))
                if b == (a + 1):
                    player.last_work = time.time()
            elif currency == "atk":
                if player.education >= 2:
                    x.append(int(((time.time() - player.last_work) / 864) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
                else:
                    x.append(int(((time.time() - player.last_work) / 864) * (job_number / 4)))
                if b == (a + 1):
                    player.last_work = time.time()
            elif currency == "accy":
                if player.education >= 2:
                    x.append(int(((time.time() - player.last_work) / 864) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
                else:
                    x.append(int(((time.time() - player.last_work) / 864) * (job_number / 4)))
                if b == (a + 1):
                    player.last_work = time.time()
            elif currency == "strg":
                if player.education >= 2:
                    x.append(int(((time.time() - player.last_work) / 864) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3)))
                else:
                    x.append(int(((time.time() - player.last_work) / 864) * (job_number / 4)))
                if b == (a + 1):
                    player.last_work = time.time()
            elif currency == "level":
                x.append(int(((time.time() - player.last_work) / 86400) * player.education))
                if b == (a + 1):
                    player.last_work = time.time()
            else:
                await util.say(ctx.channel, "The reward you wanted was not valid! See the help page for a list of valid rewards.")
                return
            a += 1
            y = 0
        z = int(sum(Decimal(i) for i in x))
        await util.say(ctx.channel, "Your %s increased by %s, from %s jobs!" % (currency, z, a))
        if currency == "dut":
            currency = "money"
        elif currency == "dup":
            currency = "prestige_coins"
        elif currency == "atk":
            currency = "attack"
        elif currency == "level":
            currency = "job_level"
        bal = getattr(player, currency)
        bal = int(bal)
        setattr(player, currency, (z + bal))
    elif len(player.job) > 0 and job != "":
        for i in player.job:
#            if a == 1:
#                break
            try:
                job_number = int(gconf.JOBS.index(i) + 1)
            except:
                raise util.DueUtilException(ctx.channel, "There's a problem with your job! The problem has been reported, and a fix should come soon!")
            if currency == "dut":
                if player.education >= 2:
                    x = int(((time.time() - player.last_work) / 2) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3))
                else:
                    x = int(((time.time() - player.last_work) / 2) * (job_number / 4))
                player.money += x
                if b == (a + 1):
                    player.last_work = time.time()
                x = str(x)
                await util.say(ctx.channel, "You got %s DUT!" % (x))
            elif currency == "dup":
                if player.education >= 2:
                    x = int(((time.time() - player.last_work) / 172800) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3))
                else:
                    x = int(((time.time() - player.last_work) / 172800) * (job_number / 4))
                player.prestige_coins += x
                if b == (a + 1):
                    player.last_work = time.time()
                x = str(x)
                await util.say(ctx.channel, "You got %s DUP!" % (x))
            elif currency == "atk":
                if player.education >= 2:
                    x = int(((time.time() - player.last_work) / 864) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3))
                else:
                    x = int(((time.time() - player.last_work) / 864) * (job_number / 4))
                player.attack += x
                if b == (a + 1):
                    player.last_work = time.time()
                x = str(x)
                await util.say(ctx.channel, "You got %s Attack!" % (x))
            elif currency == "accy":
                if player.education >= 2:
                    x = int(((time.time() - player.last_work) / 864) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3))
                else:
                    x = int(((time.time() - player.last_work) / 864) * (job_number / 4))
                player.accy += x
                if b == (a + 1):
                    player.last_work = time.time()
                x = str(x)
                await util.say(ctx.channel, "You got %s Accuracy!" % (x))
            elif currency == "strg":
                if player.education >= 2:
                    x = int(((time.time() - player.last_work) / 864) * (job_number / 4) * math.log(player.education, 3) * math.log(player.job_level, 3))
                else:
                    x = int(((time.time() - player.last_work) / 864) * (job_number / 4))
                player.strg += x
                if b == (a + 1):
                    player.last_work = time.time()
                x = str(x)
                await util.say(ctx.channel, "You got %s Strength!" % (x))
            elif currency == "level":
                x = int(((time.time() - player.last_work) / 86400) * player.education)
                player.job_level += x
                if b == (a + 1):
                    player.last_work = time.time()
                x = str(x)
                await util.say(ctx.channel, "Your job level increased by %s!" % (x))
            else:
                lan = "The reward you wanted was not valid! See the help page for a list of valid rewards."
                if player.language != "en":
                    lan = util.translate(lan, player.language)
                await util.say(ctx.channel, "%s" % (lan))
            a += 1
    else:
        lan = "You don't have a job!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    player.save()
