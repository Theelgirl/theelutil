import discord

import generalconfig as gconf
from .. import util, commands
from ..permissions import Permission


class FeedbackHandler:
    """
    Another weird class to make something easier.
    """

    def __init__(self, **options):
        self.channel = options.get('channel')
        self.type = options.get('type').lower()
        self.trello_list = options.get('trello_list')

    async def send_report(self, ctx, message):
        author = ctx.author
        author_name = str(author)

        trello_link = await util.trello_client.add_card(board_url=gconf.trello_board,
                                                        name=message,
                                                        desc=("Automated %s added by DueUtil\n" % self.type
                                                              + "Author: %s (ID %s)" % (author_name, author.id)),
                                                        list_name=self.trello_list,
                                                        labels=["automated"])
        author_icon_url = author.avatar_url
        if author_icon_url == "":
            author_icon_url = author.default_avatar_url
        report = discord.Embed(color=gconf.DUE_COLOUR)
        report.set_author(name=author_name, icon_url=author_icon_url)
        report.add_field(name=self.type.title(), value="%s\n\n[Trello card](%s)" % (message, trello_link), inline=False)
        report.add_field(name=ctx.server.name, value=ctx.server.id)
        report.add_field(name=ctx.channel.name, value=ctx.channel.id)
        report.set_footer(text="Sent at " + util.pretty_time())
        await util.say(ctx.channel,
                       ":mailbox_with_mail: Sent! You can view your %s here: <%s>" % (self.type, trello_link))
        await util.say(self.channel, embed=report)


bug_reporter = FeedbackHandler(channel=gconf.bug_channel, type="bug report", trello_list="bug reports")
suggestion_sender = FeedbackHandler(channel=gconf.feedback_channel, type="suggestion", trello_list="suggestions")
smh_reporter = FeedbackHandler(channel=gconf.bug_channel, type="suggestion", trello_list="smh x2")

@commands.command(permission=Permission.DUEUTIL_OWNER, args_pattern="PS", aliases=['ar'])
async def answerreport(ctx, player, message, **details):
    """
    [CMD_KEY]answerreport (player) (message)
    Lets bot owners answer bug reports and suggestions.
    [PERM]
    """
    ctx.author = discord.Member(user={"id": player.id})
    ctx.author.server = ctx.server
    await util.say(ctx.author, "%s" % (message))
    await util.say(ctx.channel, "Sent!")


@commands.command(permission=Permission.DISCORD_USER, args_pattern="S")
@commands.ratelimit(cooldown=3600, error=":cold_sweat: You can only bugreport every hour to prevent spam, expect someone else to report soon!")
async def bugreport(ctx, report, **details):
    """
    [CMD_KEY]bugreport (report)
    
    Leaves a bug report on the official DueUtil server and trello.
    [PERM]
    """
    player = details["author"]
    if int(player.id) != 302807237812813824 and int(player.id) != 388310086101106701 and int(player.id) != 356427989095022602:
        await bug_reporter.send_report(ctx, report)
    else:
        await smh_reporter.send_report(ctx, report)

@commands.command(permission=Permission.DISCORD_USER, args_pattern="S")
@commands.ratelimit(cooldown=10800, error=":hushed: You can only suggest every 3 hours to prevent spam!")
async def suggest(ctx, suggestion, **details):
    """
    [CMD_KEY]suggest (suggestion)
    
    Leaves a suggestion on the official server and trello.
    [PERM]
    """
    player = details["author"]
    if int(player.id) != 302807237812813824 and int(player.id) != 388310086101106701 and int(player.id) != 356427989095022602:
        await suggestion_sender.send_report(ctx, suggestion)
    else:
        await smh_reporter.send_report(ctx, suggestion)