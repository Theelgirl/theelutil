import os
import time
from .. import commands, util, loader

@commands.command(args_pattern="S?", hidden=True)
#@commands.require_cnf(warning="This will restart the whole bot! Be careful!")
async def restartbot(ctx, cnf="", **details):
    player = details["author"]
    if str(player.id) == "376166105917554701":
        await util.say(ctx.channel, ":ferris_wheel: Restarting DueUtil!")
        await util.duelogger.concern("DueUtil restarting!!")
        os._exit(1)

@commands.command(args_pattern=None, hidden=True)
async def reloadcommands(ctx, **details):
#    await util.say(ctx.channel, "python -m compileall <file>.py")
#    await util.say(ctx.channel, ":ferris_wheel: Reloading commands!")
#    await util.duelogger.concern("DueUtil commands reloading!!")
#    raise util.DueReloadException(ctx.channel)
    player = details["author"]
    time.sleep(1)
    if str(player.id) == "376166105917554701":
        loader.theel_load()
#    loader.reload_modules()
#    loader.reload_module(module_name='dueutil.botcommands')
#    loader.module_refresh(module_name='dueutil.botcommands')
#    loader.reload_module(module_name='dueutil.game')
#    loader.module_refresh(module_name='dueutil.game')