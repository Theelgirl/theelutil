import json
import random
from collections import defaultdict, namedtuple
from typing import Dict, List
import math
import asyncio

import discord
import jsonpickle

from ..util import SlotPickleMixin
from .. import dbconn
from .. import util
from ..game import players
from ..game import weapons
from ..game.helpers.misc import DueUtilObject, DueMap
from .players import Player
from . import gamerules

#BAD_WORDS = ['fuck', 'bitch', 'cunt', 'nigger', 'nigga', 'pussy']

team_map = DueMap()

class Team(DueUtilObject, SlotPickleMixin):
    """WIP"""
    __slots__ = ["name", "level", "total_exp", "exp",
                 "join_req", "description", "home_server",
                 "owner", "co_leaders", "elders", "members",
                 "topdog_count"]

    def __init__(self, name, requirement, **extras):
        message = extras.get('ctx', None)
        self.description = extras.get('description', 'None specified!')

        if message is not None:
            if message.server in team_map:
                if name.lower() in team_map[message.server]:
                    raise util.DueUtilException(message.channel, "A team with that name already exists on this server! Go to another server to make this team!")
            self.home_server = message.server.id
            self.owner = []
            self.owner.append(message.author.id)
        else:
            self.home_server = extras.get('server_id', "DEFAULT")
            self.owner = []
        self.name = name
        self.join_req = requirement
        super().__init__(self._team_id(), **extras)
        self.level = 1
        self.total_exp = 0
        self.exp = 0
        self.co_leaders = []
        self.elders = []
        self.members = []
        self.topdog_count = 0
        self._add()
        self.save()

    def _team_id(self):
        return self.home_server + '/' + self.name.lower()

    def _add(self):
        global team_map
        if self.home_server != "":
            team_map[self.id] = self

    @property
    def made_on(self):
        return self.home_server

    @property
    def t_id(self):
        return self.id

def get_server_team_list(server: discord.Server) -> Dict[str, Team]:
    return team_map[server]

def get_team(server: discord.Server, team_name: str) -> Team:
    return team_map[server.id + "/" + team_name.lower()]

def get_team_test():
    dbconn_teams = []
    for team in dbconn.get_collection_for_object(Team).find():
        loaded_team = jsonpickle.decode(team['data'])
        dbconn_teams.append(team_map[loaded_team.id])
    team_list = get_all_teams_dict().values()
    if len(dbconn_teams) != len(team_list):
        number = random.randint(1, 2)
        if number == 1:
            return team_list
        elif number == 2:
            return dbconn_teams
    return team_list, dbconn_teams
#    for team in team_list:
#        return team.name.lower()
#    return "None found!"

def get_team_no_id(team_name: str) -> Team:
    team_name = str(team_name)
    team_name = team_name.lower()
    dbconn_teams = []
    for team in dbconn.get_collection_for_object(Team).find():
        loaded_team = jsonpickle.decode(team['data'])
        dbconn_teams.append(team_map[loaded_team.id])
    team_list = get_all_teams_dict_2(list=True)
    team_list_2 = get_all_teams_dict().values()
    for team_3 in dbconn_teams:
        team_name_3 = team_3.name
        team_name_3 = str(team_name_3)
        team_name_3 = team_name_3.lower()
        if team_name_3.lower() == team_name.lower():
            return team_3
    for team_4 in team_list_2:
        team_name_4 = team_4.name
        team_name_4 = str(team_name_4)
        team_name_4 = team_name_4.lower()
        if team_name_4.lower() == team_name.lower():
            return team_4
    for team_2 in team_list:
        team_name_2 = team_2.name
        team_name_2 = str(team_name_2)
        team_name_2 = team_name_2.lower()
        if team_name_2.lower() == team_name.lower():
            return team_2
    for team in dbconn.get_collection_for_object(Team).find():
        if not team_map[loaded_team.id] is None:
            team_name = team_name.lower()
            team_name_2 = team_map[loaded_team.id].name.lower()
            if team_name == team_name_2:
                return team_map[loaded_team.id]
    return None
#    team_list = get_all_teams_dict()
#    try:
#        team = team_list[team_name.lower()]
#        return team
#    except:
#        return None
#    return team_list.get(team_name.lower(), None)

def remove_team(team_name: str):
    team = get_team_no_id(team_name)
    try:
        for player in team.members:
            player.team = None
            player.team_rank = None
            player.save()
    except:
        for member in team.members:
            player = players.find_player(member)
            player.team = None
            player.team_rank = None
            player.save()
    try:
        for player in team.elders:
            player.team = None
            player.team_rank = None
            player.save()
    except:
        for member in team.elders:
            player = players.find_player(member)
            player.team = None
            player.team_rank = None
            player.save()
    try:
        for player in team.co_leaders:
            player.team = None
            player.team_rank = None
            player.save()
    except:
        for member in team.co_leaders:
            player = players.find_player(member)
            player.team = None
            player.team_rank = None
            player.save()
    team_id = team.home_server + "/" + team_name.lower()
    del team_map[team_id]
    dbconn.get_collection_for_object(Team).remove({'_id': team_id})

def get_team_from_id(team_id: str) -> Team:
    return team_map[team_id]

def does_team_exist(name):
    team_dict = get_all_teams_dict_2()
    return team_dict.get(name, False)
#    try:
#        team = team_dict[name]
#        return team
#    except:
#        return False

def get_all_teams():
    a = 0
    team_list = []
    client = util.shard_clients[0]
    for server in client.servers:
        server_teams = get_server_team_list(server)
        if not server_teams is None:
            team_list.append(server_teams)
            a += 1
        if a > 1:
            oshit = {**team_list[0], **team_list[1]}
            team_list.clear()
            team_list.append(oshit)
    return team_list

def get_all_teams_dict():
    a = 0
    team_list = []
    for client in util.shard_clients:
        for server in client.servers:
            server_teams = get_server_team_list(server)
            if not server_teams is None:
                team_list.append(server_teams)
                a += 1
            if a > 1:
                oshit = {**team_list[0], **team_list[1]}
    return oshit

def get_all_teams_dict_2(list=False):
    a = 0
    b = 0
    team_list = []
    while len(util.shard_clients) > b:
        client = util.shard_clients[b]
        for server in client.servers:
            server_teams = get_server_team_list(server)
            if not server_teams is None:
                team_list.append(server_teams)
                a += 1
            if a == 1:
                if not server_teams is None:
                    oshit = server_teams
            if a > 1:
                try:
                    oshit = {**team_list[0], **team_list[1]}
                except:
                    if not server_teams is None:
                        oshit = server_teams
        b += 1
    if a == 0:
        oshit = None
    oshit_list = []
    for team in dbconn.get_collection_for_object(Team).find():
        loaded_team = jsonpickle.decode(team['data'])
        oshit_list.append(team_map[loaded_team.id])
    if len(oshit_list) == 1 and list == False:
        oshit = team_map[loaded_team.id]
    if len(oshit_list) == 1 and list == True:
        oshit = oshit_list
    if len(oshit_list) >= 1:
        oshit = oshit_list
    return oshit

REFERENCE_TEAM = Team("Default Team", 1, home_server="", no_save=True)

def _load():
    for team in dbconn.get_collection_for_object(Team).find():
        loaded_team = jsonpickle.decode(team['data'])
        team_map[loaded_team.id] = util.load_and_update(REFERENCE_TEAM, loaded_team)
    util.logger.info("Loaded %s teams", len(team_map))


_load()
