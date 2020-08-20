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

raid_map = DueMap()
active_raid_map = DueMap()
REWARD_TYPES = ["dut", "dup", "teamcash"]
DEFAULT_IMAGE = "http://i.imgur.com/zOIJM9T.png"

class Raid(DueUtilObject, SlotPickleMixin):
    """WIP"""
    __slots__ = ["name", "total_health", "stat_divisor",
                 "b_attack", "b_strg", "b_accy", 
                 "defense", "reward_type", "reward",
                 "home_server", "image_url", "weapon", "no_save"]

    DEFAULT_IMAGE = "http://i.imgur.com/zOIJM9T.png"

    def __init__(self, name, total_health, reward_type, stat_divisor, **extras):
        global REWARD_TYPES
        message = extras.get('ctx', None)
        b_attack = int(total_health / stat_divisor)
        defense = b_attack ** (1/2)
        tier = int(defense / 25) + 1


        if message is not None:
            if message.server in raid_map:
                if name.lower() in raid_map[message.server]:
                    raise util.DueUtilException(message.channel, "A raid with that name already exists!")
            try:
                if (total_health / tier) > 1000000:
                    raise util.DueUtilException(message.channel, "Health/Tier ratio cannot exceed 1,000,000:1!")
            except Exception as e:
                raise util.DueUtilException(message.channel, "Total Health and Tier must be integers! %s" % (str(e)))
            if not reward_type.lower() in REWARD_TYPES:
                raise util.DueUtilException(message.channel, "Reward type must be ``dup``, ``dut``, or ``teamcash``!")
            self.home_server = message.server.id
        else:
            self.home_server = "398778888840544256"
        self.name = name
        super().__init__(self._raid_id(), **extras)
        total_health = int(total_health)
        self.weapon = weapons.NO_WEAPON
        stat_divisor = int(stat_divisor)
        self.total_health = total_health
        self.stat_divisor = stat_divisor
        self.b_attack = int(total_health / stat_divisor)
        self.b_strg = int(total_health / stat_divisor)
        self.b_accy = int(total_health / stat_divisor)    
        self.defense = self.b_attack ** (1/2)
        self.reward_type = reward_type
        if reward_type == "dut":
            self.reward = self.defense * 1000000
        elif reward_type == "teamcash":
            self.reward = self.defense * 100
        else:
            self.reward = self.defense
        self.image_url = extras.get('image_url', Raid.DEFAULT_IMAGE)
        self.no_save = False
        self._add()
        self.save()
            
    def _raid_id(self):
        return self.home_server + '/' + self.name.lower()

    def _add(self):
        global raid_map
        raid_map[self.id] = self

    @property
    def made_on(self):
        return self.home_server

    @property
    def r_id(self):
        return self.id

class ActiveRaid(DueUtilObject, SlotPickleMixin):
    __slots__ = ["name", "total_health", "hp", 
                 "attack", "strg", "accy", "stat_multiplier",
                 "defense", "reward_type", "reward", "times_attacked",
                 "attackers", "tier", "image_url", "home_server", "attackable", "weapon",
                 "level", "no_save"]
    def __init__(self, base_raid_name, stat_multiplier, **extras):
        global DEFAULT_IMAGE
        message = extras.get('ctx', None)
        base_raid = get_raid_no_id(base_raid_name)
        x = 0

        if not base_raid is None:
            if message is not None:
                self.home_server = message.server.id
            else:
                x = 1

        if base_raid is None and x == 0:
            if message is not None:
                raise util.DueUtilException(message.channel, "Unable to find a base raid to create!")
            else:
                x = 1
        elif not base_raid is None and x == 0:
            try:
                name = str(base_raid_name) + "(" + str(len(get_all_raids_dict_2(list=True, type="active"))) + ")"
                self.attackable = True
            except:
                name = "Placeholder Raid"
                self.attackable = False
            self.name = name
            super().__init__(self._raid_id(), **extras)
            total_health = int(base_raid.total_health)
            self.total_health = total_health
            self.hp = total_health
            stat_multiplier = round(stat_multiplier ** 1.5, 5)
            self.stat_multiplier = stat_multiplier
            rand = float(random.uniform(.7, 1.3))
            self.attack = int(base_raid.b_attack * stat_multiplier * rand)
            self.strg = int(base_raid.b_strg * stat_multiplier * rand)
            self.accy = int(base_raid.b_accy * stat_multiplier * rand)
            self.level = int(self.get_level_from_stats())
            self.weapon = weapons.NO_WEAPON
            self.save()
            self.defense = round(self.level ** (2/3), 3)
            self.reward_type = base_raid.reward_type
            reward_type = self.reward_type
            self.tier = int(self.level / 20) + 1
            if reward_type == "dut":
                self.reward = int((self.defense * 100000) / self.tier * random.uniform(.5, 1.5))
            elif reward_type == "teamcash":
                self.reward = int((self.defense * 100) / self.tier * random.uniform(.5, 1.5))
            else:
                self.reward = int(self.defense / self.tier * random.uniform(.5, 1.5))
            self.times_attacked = 0
            self.attackers = []
            self.image_url = extras.get('image_url', DEFAULT_IMAGE)
            if self.attackable == False:
                self.tier = 69420
            self.no_save = False
            self._add()
            self.save()

    def get_level_from_stats(self):
        total_stats = int(self.attack + self.strg + self.accy)
        exp = total_stats * 100
        level = 0
        exp_next_level = gamerules.raid_get_exp_for_next_level(level)
        while exp >= exp_next_level:
            level += 1
            exp -= exp_next_level
            exp_next_level = gamerules.raid_get_exp_for_next_level(level)
            no = 42069.69420 ** 20
            if level >= 100:
                return level
                break
        return level

    def _raid_id(self):
        return self.home_server + '/' + self.name.lower()

    def _add(self):
        global active_raid_map
        active_raid_map[self.id] = self

    def weapon_hit(self):
        return random.random() < .86

    @property
    def made_on(self):
        return self.home_server

    @property
    def r_id(self):
        return self.id

def get_server_raid_list(server: discord.Server) -> Dict[str, Raid]:
    return raid_map[server]

def get_raid(server: discord.Server, raid_name: str) -> Raid:
    return raid_map[server.id + "/" + raid_name.lower()]

def get_raid_no_id(raid_name: str, type="base") -> Raid:
    raid_name = str(raid_name)
    raid_name = raid_name.lower()
    dbconn_raids = []
    if type == "base":
        for raid in dbconn.get_collection_for_object(Raid).find():
            loaded_raid = jsonpickle.decode(raid['data'])
            dbconn_raids.append(raid_map[loaded_raid.id])
    else:
        for raid in dbconn.get_collection_for_object(ActiveRaid).find():
            loaded_raid = jsonpickle.decode(raid['data'])
            dbconn_raids.append(active_raid_map[loaded_raid.id])
    raid_list = get_all_raids_dict_2(list=True)
    try:
        raid_list_2 = get_all_raids_dict().values()
    except:
        raid_list_2 = []
    try:
        for raid_3 in dbconn_raids:
            raid_name_3 = raid_3.name
            raid_name_3 = str(raid_name_3)
            raid_name_3 = raid_name_3.lower()
            if raid_name_3.lower() == raid_name.lower():
                return raid_3
    except:
        pass
    try:
        for raid_2 in raid_list:
            raid_name_2 = raid_2.name
            raid_name_2 = str(raid_name_2)
            raid_name_2 = raid_name_2.lower()
            if raid_name_2.lower() == raid_name.lower():
                return raid_2
    except:
        pass
    try:
        for raid_4 in raid_list_2:
            raid_name_4 = raid_4.name
            raid_name_4 = str(raid_name_4)
            raid_name_4 = raid_name_4.lower()
            if raid_name_4.lower() == raid_name.lower():
                return raid_4
    except:
        pass
    return None

def remove_raid(raid_name: str, type="base"):
    if type == "base":
        raid = get_raid_no_id(raid_name, type="base")
        raid_id = raid.home_server + "/" + raid_name.lower()
        del raid_map[raid_id]
        dbconn.get_collection_for_object(Raid).remove({'_id': raid_id})
    else:
        raid = get_raid_no_id(raid_name, type="active")
        raid_id = raid.home_server + "/" + raid_name.lower()
        dbconn.get_collection_for_object(ActiveRaid).remove({'_id': raid_id})    

def get_random_raid():
    oshit_list = []
    for raid in dbconn.get_collection_for_object(Raid).find():
        loaded_raid = jsonpickle.decode(raid['data'])
        oshit_list.append(raid_map[loaded_raid.id])
    if 0 <= len(oshit_list) < 1:
        return None
    number = random.randint(0, len(oshit_list) - 1)
    return oshit_list[number]

def get_raid_from_id(raid_id: str) -> Raid:
    return raid_map[raid_id]

def get_all_raids_dict(type="base"):
    a = 0
    raid_list = []
    oshit = None
    if type != "active":
        for client in util.shard_clients:
            for server in client.servers:
                server_raids = get_server_raid_list(server)
                if not server_raids is None:
                    raid_list.append(server_raids)
                    a += 1
                if a > 1:
                    oshit = {**raid_list[0], **raid_list[1]}
    return oshit

def get_all_raids_dict_2(list=False, type="base"):
    a = 0
    b = 0
    raid_list = []
    oshit = None
    while len(util.shard_clients) > b:
        client = util.shard_clients[b]
        if type != "active":
            for server in client.servers:
                server_raids = get_server_raid_list(server)
                if not server_raids is None:
                    raid_list.append(server_raids)
                    a += 1
                if a == 1:
                    if not server_raids is None:
                        oshit = server_raids
                if a > 1:
                    try:
                        oshit = {**raid_list[0], **raid_list[1]}
                    except:
                        if not server_raids is None:
                            oshit = server_raids
        b += 1
    if a == 0:
        oshit = None
    oshit_list = []
    if type != "active":
        for raid in dbconn.get_collection_for_object(Raid).find():
            loaded_raid = jsonpickle.decode(raid['data'])
            oshit_list.append(raid_map[loaded_raid.id])
        if len(oshit_list) == 1 and list == False:
            oshit = raid_map[loaded_raid.id]
        if len(oshit_list) == 1 and list == True:
            oshit = oshit_list
        if len(oshit_list) >= 1:
            oshit = oshit_list
    if type == "active":
        for raid in dbconn.get_collection_for_object(ActiveRaid).find():
            loaded_raid = jsonpickle.decode(raid['data'])
            oshit_list.append(loaded_raid)
        if len(oshit_list) == 1 and list == False:
            oshit = loaded_raid
        if len(oshit_list) == 1 and list == True:
            oshit = oshit_list
        if len(oshit_list) >= 1:
            oshit = oshit_list
    return oshit

REFERENCE_BASE_RAID = Raid("test", 10000000, "dut", 10, no_save=True)
REFERENCE_ACTIVE_RAID = ActiveRaid("test", 10, no_save=True)

def _load():
    for raid in dbconn.get_collection_for_object(Raid).find():
        loaded_raid = jsonpickle.decode(raid['data'])
        raid_map[loaded_raid.id] = util.load_and_update(REFERENCE_BASE_RAID, loaded_raid)
    util.logger.info("Loaded %s raid options", len(raid_map))

def _load2():
    for raid in dbconn.get_collection_for_object(ActiveRaid).find():
        loaded_raid = jsonpickle.decode(raid['data'])
        active_raid_map[loaded_raid.id] = util.load_and_update(REFERENCE_ACTIVE_RAID, loaded_raid)
#    util.load_and_update(REFERENCE_ACTIVE_RAID, REFERENCE_ACTIVE_RAID)
    util.logger.info("Loaded %s active raids", len(raid_map))
    

_load()
_load2()
