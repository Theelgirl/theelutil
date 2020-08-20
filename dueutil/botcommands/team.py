import discord
import random
import math
import time
import os
import asyncio

import dueutil.game.awards as game_awards
import generalconfig as gconf
from ..game import players, customizations
from ..game import stats, game
from ..game.helpers import misc, playersabstract, imagehelper
from .. import commands, util, dbconn, permissions
from ..permissions import Permission
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

@commands.command(permission=Permission.DUEUTIL_OWNER, args_pattern=None, hidden=True)
async def teamtest(ctx, **details):
    team_values = teams.get_team_test()
    try:
        for value, value_2 in team_values:
            await util.say(ctx.channel, "%s" % (value))
            await util.say(ctx.channel, "%s" % (value_2))
    except:
        try:
            for value in team_values:
                await util.say(ctx.channel, "%s" % (value))
        except:
            await util.say(ctx.channel, "theel you fucked up again")
    team_list = teams.get_all_teams_dict_2()
    for value in team_list:
        await util.say(ctx.channel, "%s" % (value))


@commands.command(args_pattern=None)
async def homeinvite(ctx, **details):
    """
    [CMD_KEY]homeinvite
    Creates an invite to your team's home server so you can play with your teammates.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    if player.team is not None:
        team_name = player.team
    else:
        lan = "You need to be in a team to use this!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team_server = teams.get_team_no_id(player.team.lower())
    if team_server is None:
        lan = "I couldn't find your team!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    server_id_1 = team_server.home_server
    server = util.get_server(server_id_1)
    server_channel = list(util.get_server(server_id_1).channels)[1]
    server_channel_list = list(util.get_server(server_id_1).channels)
    x = len(server_channel_list)
    check = 0
    try:
        if server_channel is not None and server is not None:
            invite = await util.get_client(server.id).create_invite(destination=server_channel, max_uses=1, unique=False)
            invite = str(invite)
            await util.say(ctx.channel, "%s" % (invite))
            check += 1
    except:
        while x > 0:
            try:
                server_channel = list(util.get_server(server_id_1).channels)[x]
                if server_channel is not None and server is not None:
                    invite = await util.get_client(server.id).create_invite(destination=server_channel, max_uses=1, unique=True)
                    invite = str(invite)
                    await util.say(ctx.channel, "%s" % (invite))
                    check += 1
                    break
            except:
                pass
            x -= 1
    if check == 0:
        lan = "I don't seem to have invite creation permissions in this team's home server!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))

@commands.command(args_pattern='P')
async def promote(ctx, player, **details):
    """
    [CMD_KEY]promote (user)
    Promotes a user by one rank in your team.
    You must be a team owner to use this.
    [PERM]
    """
    promoter = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(promoter, "team_rank"):
        promoter.team_rank = None
    if not hasattr(promoter, "team"):
        promoter.team = None
    if promoter.team_rank != "Owner":
        lan = "You need to be the team's owner to promote people!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team_name_1 = promoter.team
    team_name_1 = team_name_1.lower()
    team_name_2 = player.team
    team_name_2 = team_name_2.lower()
    team = teams.get_team_no_id(team_name_1)
    if team is None:
        lan = "I couldn't find your team!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team_2 = teams.get_team_no_id(team_name_2)
    if team != team_2:
        lan = "You need to be in the same team as this player!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if not hasattr(team, "co_leaders"):
        team.co_leaders = []
    if len(team.elders) >= 5 and player.id in team.members:
        lan = "You may only have up to five elders!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if len(team.co_leaders) >= 2 and player.id in team.co_leaders:
        lan = "You may only have up to two co-leaders!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if player.id in team.members:
        team.members.remove(player.id)
        team.elders.append(player.id)
        player.team_rank = "Elder"
        lan = "This player is now an elder!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    elif player.id in team.elders:
        team.elders.remove(player.id)
        team.co_leaders.append(player.id)
        player.team_rank = "Co-Leader"
        lan = "This player is now a co-leader!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    else:
        lan = "This player cannot be promoted further!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    team.save()
    player.save()

@commands.command(args_pattern='P')
async def demote(ctx, player, **details):
    """
    [CMD_KEY]demote (user)
    Demotes a user by one rank in your team.
    You must be a team owner to use this.
    [PERM]
    """
    demoter = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(demoter, "team_rank"):
        demoter.team_rank = None
    if not hasattr(demoter, "team"):
        demoter.team = None
    if demoter.team_rank != "Owner":
        lan = "You need to be the team's owner to demote people!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team_name_1 = demoter.team
    team_name_1 = team_name_1.lower()
    team_name_2 = player.team
    team_name_2 = team_name_2.lower()
    team = teams.get_team_no_id(team_name_1)
    if team is None:
        lan = "I could not find your team!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team_2 = teams.get_team_no_id(team_name_2)
    if team != team_2:
        lan = "You need to be in the same team as this player!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if not hasattr(team, "co_leaders"):
        team.co_leaders = []
    if len(team.elders) >= 5 and player.id in team.co_leaders:
        lan = "You may only have up to 5 elders!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if player.id in team.elders:
        team.elders.remove(player.id)
        team.members.append(player.id)
        player.team_rank = "Member"
        lan = "This player is now a member!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    elif player.id in team.co_leaders:
        team.co_leaders.remove(player.id)
        team.elders.append(player.id)
        player.team_rank = "Elder"
        lan = "This player is now an elder!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    team.save()
    player.save()

@commands.command(args_pattern="S?")
async def teaminfo(ctx, team_name="None", **details):
    """
    [CMD_KEY]teaminfo (optional: team name)
    Shows you some info on your team if you don't include a team name.
    If you do include a tea name, it shows info on the named team.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "team_exp"):
        player.team_exp = 0
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    if team_name == "None":
        team_name = player.team
    if team_name is None:
        lan = "You are not in a team!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team_members_list = []
    team_elders_list = []
    team_co_leaders_list = []
    team_owner_list = []
    lan = "This Team's Stats!"
    lan_2 = "This Team's Members, Elders, Co-Leaders, and Owner!"
    lan_3 = "I couldn't find your team!"
    lan_4 = "Team Name:"
    lan_5 = "Team Level:"
    lan_6 = "Total Team Experience:"
    lan_7 = "Current Team Experience:"
    lan_8 = "Team Description:"
    lan_9 = "Team TopDog Count Since The Last Event:"
    if player.language != "en":
        x = util.translate_9(lan, lan_2, lan_3, lan_4, lan_5, lan_6, lan_7, lan_8, lan_9, player.language)
        lan = x[0]
        lan_2 = x[1]
        lan_3 = x[2]
        lan_4 = x[3]
        lan_5 = x[4]
        lan_6 = x[5]
        lan_7 = x[6]
        lan_8 = x[7]
        lan_9 = x[8]
    team_stats = discord.Embed(title=lan, type="rich", color=gconf.DUE_COLOUR)
    team_members = discord.Embed(title=lan_2, type="rich", color=gconf.DUE_COLOUR)
    team_name = team_name.lower()
    team = teams.get_team_no_id(team_name)
    if team is None:
        raise util.DueUtilException(ctx.channel, "%s" % (lan_3))
    if not hasattr(team, "co_leaders"):
        team.co_leaders = []
    if not hasattr(team, "topdog_count"):
        team.topdog_count = 0
    team.exp = int(team.exp)
    team.total_exp = int(team.total_exp)
    team_stats.add_field(name=lan_4, value=team.name)
    team_stats.add_field(name=lan_5, value=team.level)
    team_stats.add_field(name=lan_6, value=team.total_exp)
    team_stats.add_field(name=lan_7, value=team.exp)    
    team_stats.add_field(name=lan_8, value=team.description)
    team_stats.add_field(name=lan_9, value=team.topdog_count)
    skip = 0
    if len(team.members) == 0:
        skip += 1
    if len(team.elders) == 0:
        skip += 2
    if len(team.co_leaders) == 0:
        skip += 4
    for member in team.members:
        member_2 = "<@!" + str(member) + ">"
        team_members_list.append(member_2)
    for elder in team.elders:
        elder_2 = "<@!" + str(elder) + ">"
        team_elders_list.append(elder_2)
    for co_leader in team.co_leaders:
        co_leader_2 = "<@!" + str(co_leader) + ">"
        team_co_leaders_list.append(co_leader_2)
    for owner in team.owner:
        owner_2 = "<@!" + str(owner) + ">"
        team_owner_list.append(owner_2)
    lan = "No members are in the team yet!"
    lan_2 = "No elders are in the team yet!"
    lan_3 = "No co-leaders are in the team yet!"
    lan_4 = "Team Members:"
    lan_5 = "Team Elders:"
    lan_6 = "Team Co-leaders:"
    lan_7 = "Team Owner:"
    if player.language != "en":
        x = util.translate_7(lan, lan_2, lan_3, lan_4, lan_5, lan_6, lan_7, player.language)
        lan = x[0]
        lan_2 = x[1]
        lan_3 = x[2]
        lan_4 = x[3]
        lan_5 = x[4]
        lan_6 = x[5]
        lan_7 = x[6]
    if skip != 1 and skip != 3 and skip != 5 and skip != 7:
        team_members_list = ', '.join(team_members_list)
        team_members_list = team_members_list.replace('[', ' ')
        team_members_list = team_members_list.replace(']', ' ')
    else:
        team_members_list = lan
    if skip != 2 and skip != 3 and skip != 6 and skip != 7:
        team_elders_list = ', '.join(team_elders_list)
        team_elders_list = team_elders_list.replace('[', ' ')
        team_elders_list = team_elders_list.replace(']', ' ')
    else:
        team_elders_list = lan_2
    if skip < 4 or skip > 7:
        team_co_leaders_list = ', '.join(team_co_leaders_list)
        team_co_leaders_list = team_co_leaders_list.replace('[', ' ')
        team_co_leaders_list = team_co_leaders_list.replace(']', ' ')
    else:
        team_co_leaders_list = lan_3
    team_owner_list = ', '.join(team_owner_list)
    team_owner_list = team_owner_list.replace('[', ' ')
    team_owner_list = team_owner_list.replace(']', ' ')
    team_members.add_field(name=lan_4, value=team_members_list)
    team_members.add_field(name=lan_5, value=team_elders_list)
    team_members.add_field(name=lan_6, value=team_co_leaders_list)
    team_members.add_field(name=lan_7, value=team_owner_list)
    await util.say(ctx.channel, embed=team_stats)
    await util.say(ctx.channel, embed=team_members)


@commands.command(args_pattern='S')
@commands.ratelimit(cooldown=60,
                    error="You can change your team again in **[COOLDOWN]**!",
                    save=True)
async def jointeam(ctx, team_name, **details):
    """
    [CMD_KEY]jointeam <team name>
    A list of teams can be found with ``!allteams <page number>``
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "team_exp"):
        player.team_exp = 0
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    team_to_join_list = list(teams.get_all_teams_dict().values())
    team_to_join = teams.get_all_teams_dict()
    if player.team_rank != None:
        lan = "You can't join a team if you're already in another team! Delete or leave it first!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team_name_2 = team_name
    team_name = str(team_name)
    team_name = team_name.lower()
    if teams.get_team_no_id(team_name) is not None:
        team_name = str(team_name)
        team_name = team_name.lower()    
        team = teams.get_team_no_id(team_name.lower())
        if team is None:
            lan = "This team does not exist!"
            if player.language != "en":
                lan = util.translate(lan, player.language)
            raise util.DueUtilException(ctx.channel, "%s" % (lan))
        if team.join_req > player.level:
            lan = "You aren't a high enough level to join this team!"
            if player.language != "en":
                lan = util.translate(lan, player.language)
            raise util.DueUtilException(ctx.channel, "%s" % (lan))
        team.members.append(player.id)
        player.team = team_name
        player.team_rank = "Member"
        await util.say(ctx.channel, "You joined Team **%s**!" % (team_name_2))
    else:
        lan = "This team does not exist!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    team.save()
    player.save()

@commands.command(args_pattern=None)
async def leaveteam(ctx, **details):
    """
    [CMD_KEY]leaveteam
    Makes you leave your current team.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    team_to_leave_list = list(teams.get_all_teams_dict().values())
    if player.team_rank == "Owner":
        lan = "You can't leave a team if you're its owner! Delete it first!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if player.team is not None:
        team_name = player.team.lower()
        team = teams.get_team_no_id(team_name)
    else:
        lan = "You aren't in a team!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if team is not None:
        try:
            team.members.remove(player.id)
        except:
            try:
                team.elders.remove(player.id)
            except:
                lan = "You're the team's owner! Delete the team instead!"
                if player.language != "en":
                    lan = util.translate(lan, player.language)
                raise util.DueUtilException(ctx.channel, "%s" % (lan))
        player.team = None
        player.team_rank = None
        lan = "You left your team!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        await util.say(ctx.channel, "%s" % (lan))
    else:
        lan = "You aren't in a team!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    player.save()
    team.save()

@commands.command(args_pattern='S?')
@commands.require_cnf(warning="This will **__permanently__** delete your team, and kick everyone out!")
async def deleteteam(ctx, cnf="", **details):
    """
    [CMD_KEY]deleteteam (cnf)
    Deletes your team permanently. You will be permanently unable to make another team.
    DO NOT DO THIS IF YOU'RE UNSURE ABOUT WHETHER TO DO IT.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    if player.team_rank != "Owner":
        lan = "You can't delete a team if you aren't a team owner!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    teams.remove_team(player.team)
    player.team = None
    player.team_rank = None
    lan = "Your team was deleted!"
    if player.language != "en":
        lan = util.translate(lan, player.language)
    await util.say(ctx.channel, "%s" % (lan))
    player.save()


@commands.command(args_pattern='SI?')
async def createteam(ctx, *args, **_):
    """
    [CMD_KEY]createteam (name) (optional: minimum level)
    Creates a team for you.
    Every team needs a home server for bot events and such, so if your team's server is deleted, please set another server as the home server.
    [PERM]
    """
    client = util.shard_clients[0]
    player = players.find_player(ctx.author.id)
    extras = {"idk": "idk"}
    if not hasattr(player, "teams_created"):
        player.teams_created = 0
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "team_exp"):
        player.team_exp = 0
    if not hasattr(player, "team_money"):
        player.team_money = 0
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    if len(args) == 1:
        name = args[0]
        requirements = 1
    elif len(args) == 2:
        name = args[0]
        requirements = args[1]
    member = discord.Member(user={"id": player.id})
    if player.teams_created >= 1 and not permissions.has_permission(member, permissions.Permission.DUEUTIL_OWNER):
        lan = "You've created a team already! Even if it has been deleted, you can't make another!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if player.team_money < 50:
        lan = "You now need 50 teamcash to create a team. Join a pre-existing team and beat quests or do dailies to earn teamcash first!"
        if player.language != "en":
            lan = util.translate(lan, player.language)
        raise util.DueUtilException(ctx.channel, "%s" % (lan))
    if requirements > 100:
        raise util.DueUtilException(ctx.channel, "Minimum level can't be over 100!")
    try:
        name = int(name)
        raise util.DueUtilException(ctx.channel, "Your team name can't be a number!")
    except:
        pass
    if player.team != None:
        raise util.DueUtilException(ctx.channel, "You can't create a team while you're in a team! Leave your team first!")
    if teams.get_team_no_id(name.lower()) != None:
        raise util.DueUtilException(ctx.channel, "A team with this name already exists!")
    if teams.get_team_no_id(name) != None:
        raise util.DueUtilException(ctx.channel, "A team with this name already exists!")
    new_team = teams.Team(name=name, requirement=requirements, **extras, ctx=ctx)
    await util.say(ctx.channel, "Team **%s** has been created, with you as owner!" % (new_team.name_clean))
    player.team = name.lower()
    player.team_rank = "Owner"
    player.teams_created += 1
    player.team_money -= 100
    player.save()

@commands.command(args_pattern='SS*')
@commands.extras.dict_command(optional={"level": "I", "description": "S", "homeserver": "S"})
async def editteam(ctx, name, updates, **details):
    """
    [CMD_KEY]editteam name (property)+

    Any number of properties can be set at once.

    Properties:
        __level__, __description__, __homeserver__

    More coming soon! Also, level is the minimum level to join the team, not the actual team level ;)
    
    Homeserver MUST be the new home server's ID, or you can enter "here" to set the homeserver to where the command is used.

    Example usage:

        [CMD_KEY]editteam "Team Champions" description "For the best of the best!"

        [CMD_KEY]editteam "Team Ban" level 69

        [CMD_KEY]editteam "Team Neon" homeserver 398778888840544256
    
    You can only edit a team if you're the owner!
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "team_rank"):
        player.team_rank = None
    if not hasattr(player, "team"):
        player.team = None
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    client = util.shard_clients[0]
    name = name.lower()
    team = teams.get_team_no_id(name)
    if team is None:
        raise util.DueUtilException(ctx.channel, "You need to use the correct team name to edit it!")
    if player.id not in team.owner:
        raise util.DueUtilException(ctx.channel, "You need to be team owner to edit it!")
    for team_property, value in updates.items():
        if team_property in ("level", "min level", "minimum level"):
            if value >= 1 and value <= 100:
                team.join_req = value
                await util.say(ctx.channel, "Minimum level set to %s." % (value))
            else:
                raise util.DueUtilException(ctx.channel, "The minimum level must be at least 1, and less than or equal to 100!")
            continue
        elif team_property in ("desc", "description"):
            if len(list(value)) >= 100:
                raise util.DueUtilException(ctx.channel, "Description can only be up to 100 characters long!")
            team.description = value
            await util.say(ctx.channel, "Description set to %s!" % (value))
            continue
        elif team_property in ("homeserver", "home_server", "home server"):
            value = value.lower()
            if str(value) == "here":
                value = str(ctx.server.id)
            server = util.get_server(value)
            if server is None:
                raise util.DueutilException(ctx.channel, "I'm not in this server!")
            team.home_server = value
            await util.say(ctx.channel, "Home server changed!")
            continue
        else:
            await util.say(ctx.channel, "Use a valid update name!")
    team.save()

@commands.command(args_pattern='I?S?')
async def allteams(ctx, page=1, sort="members", **details):
    """
    [CMD_KEY]allteams (page) (sort)
    Shows all the current teams and a bit of info on them.
    Sort lets you choose whether to order teams by "level", "exp", "topdog", or number of "members".
    Use "level", "exp", "topdog", or "members", anything else will result in a default of number of members.
    Ordering by topdog gives back the teams in order of highest topdog count to lowest, not which team is currently topdog.
    [PERM]
    """
    @misc.paginator
    def team_list(teams_embed, team, **_):
        teams_embed.add_field(name=team.name_clean,
                               value="**Minimum Level:** %s\n" % team.join_req
                                     + "**Team Level:** %s\n" % team.level
                                     + "**Description:** %s\n" % team.description
                                     + "**Members:** %s" % (len(team.members) + len(team.elders) + len(team.co_leaders) + 1))
    if type(page) is int:
        page -= 1

        teams_list = teams.get_all_teams_dict_2()
        for team in teams_list:
            if not hasattr(team, "topdog_count"):
                team.topdog_count = 0
        if sort.lower() == "members":
            try:
                teams_list.sort(key=lambda team: (len(team.members) + len(team.elders) + len(team.co_leaders)), reverse=True)
            except Exception as e:
                await util.say(ctx.channel, "team list did a bad and couldnt be sorted :(")
        elif sort.lower() == "level":
            try:
                teams_list.sort(key=lambda team: team.level, reverse=True)
            except Exception as e:
                await util.say(ctx.channel, "team list did a bad and couldnt be sorted :(")
        elif sort.lower() == "exp":
            try:
                teams_list.sort(key=lambda team: team.total_exp, reverse=True)
            except Exception as e:
                await util.say(ctx.channel, "team list did a bad and couldnt be sorted :(")
        elif sort.lower() == "topdog" or sort.lower() == "topdog count":
            try:
                teams_list.sort(key=lambda team: team.topdog_count, reverse=True)
            except Exception as e:
                await util.say(ctx.channel, "team list did a bad and couldnt be sorted :(")
        else:
            await util.say(ctx.channel, "Use a valid sort type next time, valid ones can be found in the help page! Sort has defaulted to members now.")
            try:
                teams_list.sort(key=lambda team: (len(team.members) + len(team.elders) + len(team.co_leaders)), reverse=True)
            except Exception as e:
                await util.say(ctx.channel, "team list did a bad and couldnt be sorted :(")
        # misc.paginator handles all the messy checks.
        team_list_embed = discord.Embed(title="All DueUtil Teams!", type="rich", color=gconf.DUE_COLOUR)
        team_list_embed = team_list(teams_list, page, "All DueUtil Teams",
                                      footer_more="But wait there's more! Do %sallteams %d" % (details["cmd_key"], page+2),
                                      empty_list="There are no teams yet!\nHow sad.")

        await util.say(ctx.channel, embed=team_list_embed)

@commands.command(args_pattern="M")
async def teamshop(ctx, *args, **details):
    """
    [CMD_KEY]teamshop (page/item name)
    Use a number for page, and the name of the item in quotes if you want an item.
    Remember, on mobile, you need to hold down the double quotes and select the vertical double quotes (not curvy ones) to encase it in proper quotes for Due.
    At the moment, **You have to write the exact name** of the item you want. The name is shown in the page, and it is not caps-sensitive.
    The description for the first item, double max daily quests, is broken, and we are working on a fix at the moment.
    Use !teambuy to buy stuff.
    [PERM]
    """
    player = details["author"]
    shop_embed = discord.Embed(title="DueUtil's Teamshop", type="rich", color=gconf.DUE_COLOUR)
    shop_logo = 'https://cdn.discordapp.com/attachments/411657988776919050/563757792809189376/due_pfp.png'
    a = str(args[0])
    shop_embed.set_thumbnail(url=shop_logo)
    language = player.language
    if a in "1" or a in "2":
        page = int(args[0])
        if a in "1":
            message = "Showing items 1-5 in the DueUtil Team Shop."
            message2 = "1. Double Maximum Daily Quests"
            message3 = "2. Daily Quest Cooldown Reset"
            message4 = "3. 5% Limit Increase"
            message5 = "4. 3% Defense Increase"
            message6 = "5. Maximum Dummy Limit Increase"
            message7 = "This costs 500 team cash."
            message8 = "This costs 200 team cash."
            message9 = "This costs 75 team cash, and goes to a maximum of 5x normal limit."
            message10 = "This costs 75 team cash, and increases damage resistance by 3%."
            message11 = "This costs 75 team cash, and maxes out at a 25 dummy max."
            if language != "en":
                x = util.translate_11(message, message2, message3, message4, message5, message6, message7, message8, message9, message10, message11, language)
                message = x[0]
                message2 = x[1]
                message3 = x[2]
                message4 = x[3]
                message5 = x[4]
                message6 = x[5]
                message7 = x[6]
                message8 = x[7]
                message9 = x[8]
                message10 = x[9]
                message11 = x[10]
            shop_embed.description = message
            shop_embed.add_field(name=message2, value=message7)
            shop_embed.add_field(name=message3, value=message8)
            shop_embed.add_field(name=message4, value=message9)
            shop_embed.add_field(name=message5, value=message10)
            shop_embed.add_field(name=message6, value=message11)
        if a in "2":
            message = "Showing items 6-9 in the DueUtil Team Shop."
            message2 = "6. Dummy Spawn Chance Increase"
            message3 = "7. Weapon Slot Increase"
            message4 = "8. Quest Spawn Chance Increase"
            message5 = "9. Quest Prediction Accuracy Increase"
            message6 = "This costs 50 team cash, and maxes out at 3x normal chance."
            message7 = "This costs 400 team cash, and maxes out at 10 total weapon slots."
            message8 = "This costs 500 team cash for a 5% increase, and maxes out at 2x normal chance."
            message9 = "This costs 250 team cash for a 5% accuracy increase, and maxes out at 90% accuracy."
            message10 = "More items coming soon!"
            if language != "en":
                x = util.translate_10(message, message2, message3, message4, message5, message6, message7, message8, message9, message10, language)
                message = x[0]
                message2 = x[1]
                message3 = x[2]
                message4 = x[3]
                message5 = x[4]
                message6 = x[5]
                message7 = x[6]
                message8 = x[7]
                message9 = x[8]
                message10 = x[9]
            shop_embed.description = message
            shop_embed.add_field(name=message2, value=message6)
            shop_embed.add_field(name=message3, value=message7)
            shop_embed.add_field(name=message4, value=message8)
            shop_embed.add_field(name=message5, value=message9)
            shop_embed.set_footer(text=message10)
        await util.say(ctx.channel, embed=shop_embed)
    else:
        item = str(a.lower())
        if item in "double maxmimum daily quests":
            message = "Double Maximum Daily Quests"
            message2 = "This item will permanently double the maximum amount of daily quests you can do, and it costs 300 teamcash."
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            shop_embed.add_field(name=message, value=message2)
        else:
            if item in "daily quest cooldown reset":
                message = "Daily Quest Cooldown Reset"
                message2 = "If you've done your maximum quests and it hasn't reset yet, you can buy this to let you complete another 100 (or 200) quests before your cooldown resets. This costs 200 team cash."
                if language != "en":
                    x = util.translate_2(message, message2, language)
                    message = x[0]
                    message2 = x[1]
                shop_embed.add_field(name=message, value=message2)
            else:
                if item in "1000 dut":
                    message = "This item is no longer available."
                    message2 = "Use ``!exchange`` for inter-currency conversions."
                    if language != "en":
                        x = util.translate_2(message, message2, language)
                        message = x[0]
                        message2 = x[1]
                    shop_embed.add_field(name=message, value=message2)
                else:
                    if item in "5% limit increase":
                        message = "5% Limit Increase"
                        message2 = "Increases your **base** limit by 5%. For example, if your base limit is 1000 DUT, and you already have a 50% boost so you have a limit of 1500 DUT, then this upgrade will boost limit by 50 DUT, or 5% of 1000 DUT. If you hit the max of 5x limit increase from this, you can still earn limit elsewhere. This costs 75 team cash."
                        if language != "en":
                            x = util.translate_2(message, message2, language)
                            message = x[0]
                            message2 = x[1]
                        shop_embed.add_field(name=message, value=message2)
                    else:
                        if item in "3% defense increase":
                            message = "3% Defense Increase"
                            message2 = "Increases your **base** defense by 3%. This way, each time you buy it, you recieve less damage in PvP battles and quests. This costs 75 team cash."
                            if language != "en":
                                x = util.translate_2(message, message2, language)
                                message = x[0]
                                message2 = x[1]
                            shop_embed.add_field(name=message, value=message2)
                        else:
                            if item in "maximum dummy limit increase":
                                message = "Maximum Dummy Limit Increase"
                                message2 = "Lets you hold 1 additional dummy at a time, starting at 10, but going up to 25 dummies. This costs 75 team cash."
                                if language != "en":
                                    x = util.translate_2(message, message2, language)
                                    message = x[0]
                                    message2 = x[1]
                                shop_embed.add_field(name=message, value=message2)
                            else:
                                if item in "dummy spawn chance increase":
                                    message = "Dummy Spawn Chance Increase"
                                    message2 = "Increases the chance you have to get a dummy from a quest by 20% every time you purchase it, up to a maximum of 200%. This costs 50 team cash."
                                    if language != "en":
                                        x = util.translate_2(message, message2, language)
                                        message = x[0]
                                        message2 = x[1]
                                    shop_embed.add_field(name=message, value=message2)
                                else:
                                    if item in "weapon slot increase":
                                        message = "Weapon Slot Increase"
                                        message2 = "Increases your maximum inventory weapon slots by 1 each time used, up to a maximum of 11 slots, or 5 usages. This costs 400 team cash."
                                        if language != "en":
                                            x = util.translate_2(message, message2, language)
                                            message = x[0]
                                            message2 = x[1]
                                        shop_embed.add_field(name=message, value=message2)
                                    else:
                                        if item in "quest spawn chance increase":
                                            message = "Quest Spawn Chance Increase"
                                            message2 = "Increases your chance to spawn quests by 5% each time bought, up to a maximum of a 100% (double normal) increase. This is by far the most important upgrade you can buy, so it costs 500 teamcash each time."
                                            if language != "en":
                                                x = util.translate_2(message, message2, language)
                                                message = x[0]
                                                message2 = x[1]
                                            shop_embed.add_field(name=message, value=message2)
                                        else:
                                            if item in "quest prediction accuracy increase":
                                                message = "Quest Prediction Accuracy Increase"
                                                message2 = "This costs 250 teamcash for a 5% accuracy increase, and maxes out at 90% accuracy. This upgrade does not reset with prestiges."
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

@commands.command(args_pattern=None, aliases=["tc"])
async def teamcash(ctx, **details):
    """
    [CMD_KEY]teamcash

    Shows you how much team money you have!
    [PERM]
    """

    player = details["author"]

    if not hasattr(player, "team_money"):
        player.team_money = 0

    player.team_money = int(player.team_money)
    await util.say(ctx.channel, "You have **%s** teamcash!" % (player.team_money))


@commands.command(args_pattern='CI?', aliases=["tb"])
async def teambuy(ctx, amount, number=1, **details):
    """
    [CMD_KEY]teambuy (item #) (# of items)

    Gives you stats based on the item number and the # of items bought, you can view the item details with ``!teamshop``.
    The only items that the # of items can be greater than 1 on are 5, 6 and 7, but it defaults to one item bought for everything.
    [PERM]
    """

    player = details["author"]

    if not hasattr(player, "team_money"):
        player.team_money = 0

    if not hasattr(player, "item_limit_x2"):
        player.item_limit_x2 = 1

    if not hasattr(player, "dummy_max"):
        player.dummy_max = 10

    if not hasattr(player, "dummy_chance"):
        player.dummy_chance = 1

    if not hasattr(player, "dummies"):
        player.dummies = 0

    if not hasattr(player, "defense"):
        player.defense = 1

    if not hasattr(player, "quest_spawn_boost"):
        player.quest_spawn_boost = 1

    if not hasattr(player, "slot_increase"):
        player.slot_increase = 0

    if not hasattr(player, "donor"):
        player.donor = False

    if not hasattr(player, "prediction_accy"):
        player.prediction_accy = 0.75

    if amount == 1:
        if not hasattr(player, "double_quests"):
            player.double_quests = False
        if player.team_money >= 500:
            player.team_money -= 500
            if player.double_quests is False:
                language = player.language
                message = "bought x2 daily quests!"
                if language != "en":
                    message = util.translate(message, language)
                player.double_quests = True
                await util.say(ctx.channel, "**%s** %s" % (player.name_clean, message))
            else:
                language = player.language
                message = "You already have double daily quests!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "You need 500 team cash!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))

    elif amount == 2:
        if player.team_money >= 200:
            player.team_money -= 200
            player.quests_completed_today = 0
            player.quest_day_start = time.time()
            language = player.language
            message = "Your quest time has been reset!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "You need 200 team cash!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))

    elif amount == 3:
        if player.team_money >= 75:
            if player.item_limit_x2 < 5:
                player.team_money -= 75
                player.item_limit_x2 += .05
                player_item_limit_x2 = player.item_limit_x2
                player.item_limit_x2 = round(player_item_limit_x2, 3)
                language = player.language
                message = "Your limit multiplier has been increased by .05x to"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s **%s**x!" % (message, player.item_limit_x2))
            else:
                language = player.language
                message = "You can't upgrade limit over 5x!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "You need 75 team cash!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))

    elif amount == 4:
        if player.team_money >= 75:
            if player.defense < 3:
                player.team_money -= 75
                player.defense += .03
                player_defense = player.defense
                player.defense = round(player_defense, 3)
                language = player.language
                message = "Your defense has multiplied by 1.03, to " + str(player.defense) + "x!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, ("%s")
                               % (message))
            else:
                language = player.language
                message = "Defense maxes out at 3x!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "You need 75 team cash!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))

    elif amount == 5:
        if 1 <= number <= 50:
            a = round(int(number * 75), 1)
            b = number + player.dummy_max
            if player.team_money >= a:
                if player.dummy_max <= 50 and b <= 50:
                    player.dummy_max += int(number)
                    player.team_money -= a
                    c = round(player.dummy_max, 1)
                    language = player.language
                    message = "You increased your training dummy max to:"
                    if language != "en":
                        message = util.translate(message, language)
                    await util.say(ctx.channel, "%s **%s**!" % (message, player.dummy_max))
                else:
                    language = player.language
                    message = "Your training dummy max cannot increase past 50!"
                    if language != "en":
                        message = util.translate(message, language)
                    await util.say(ctx.channel, "%s" % (message))
            else:
                language = player.language
                message = "Your team cash needs to be:"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s **%s**" % (message, a))
        else:
            language = player.language
            message = "The number has to be greater than 0 and less than 51!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))

    elif amount == 6:
        a = int(number * 50)
        b = (number * .1)
        player.dummy_chance = float(player.dummy_chance)
        player.dummy_chance = round(float(player.dummy_chance), 2)
        c = (number * .1) + player.dummy_chance
        if player.team_money >= a:
            if c <= 3:
                player.team_money -= a
                player.dummy_chance += b
                d = round(player.dummy_chance, 4)
                language = player.language
                message = "Your training dummy spawn chance multiplier is now:"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s **%s**!" % (message, d))
            else:
                language = player.language
                message = "Your training dummy spawn chance multiplier can't increase above 3!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "Your team cash needs to be:"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s **%s**" % (message, a))

    elif amount == 7:
        a = int(number * 400)
        b = number
        c = b + player.slot_increase
        if player.team_money >= a:
            if c <= 6:
                player.team_money -= a
                player.slot_increase += b
                language = player.language
                message = "Your max weapon slot bonus increased to:"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s %s" % (message, c))
            else:
                language = player.language
                message = "Your total inventory weapon slots cannot increase past 11!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "Your team cash needs to be"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s **%s**" % (message, a))

    elif amount == 8:
        a = int(number * 500)
        b = number
        c = (b * .05) + player.quest_spawn_boost
        if player.team_money >= a:
            if c <= 2:
                player.team_money -= a
                player.quest_spawn_boost += (b * .05)
                c = round(player.quest_spawn_boost, 2)
                player.quest_spawn_boost = c
                language = player.language
                message = "Your quest chance multiplier has now increased to:"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s **%s**" % (message, c))
            else:
                language = player.language
                message = "You maxed out your quest chance multiplier at 2x normal!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "Your team cash needs to be"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s **%s**" % (message, a))

    elif amount == 9:
        a = int(number * 250)
        b = number
        c = player.prediction_accy - (b * .05) 
        if player.team_money >= a:
            if c >= .1:
                player.team_money -= a
                player.prediction_accy = player.prediction_accy - round((b * .05), 2)
                c = int((1 - player.prediction_accy) * 100)
                language = player.language
                message = "Your quest prediction accuracy has now increased to:"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s **%s**" % (message, c))
            else:
                language = player.language
                message = "You maxed out your quest prediction accuracy at 90!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            language = player.language
            message = "Your team cash needs to be"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s **%s**" % (message, a))

    else:
        language = player.language
        message = "This item does not exist yet! Check the team shop for all the items!"
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))


