import json
import os
import re
import subprocess
import random
import math
from io import StringIO

import discord
import objgraph
import asyncio
import time

import generalconfig as gconf
import dueutil.permissions
from ..game.helpers import imagehelper
from ..permissions import Permission
from .. import commands, util, events
from ..game import customizations, awards, leaderboards, game, weapons, players, quests
from ..game import emojis


@commands.command(permission=Permission.DUEUTIL_OWNER, args_pattern=None, hidden=True)
async def stopbot(ctx, **_):
    await util.say(ctx.channel, ":wave: Stopping DueUtil!")
    await util.duelogger.concern("DueUtil shutting down!")
    os._exit(0)


@commands.command(permission=Permission.DUEUTIL_OWNER, args_pattern=None, aliases=["rb"], hidden=True)
async def restartbot(ctx, **_):
    await util.say(ctx.channel, ":ferris_wheel: Restarting DueUtil!")
    await util.duelogger.concern("DueUtil restarting!!")
    os._exit(1)

