import asyncio
import datetime
import functools
from typing import Optional

import discord
from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from api.translation.translator import Translator
from extensions.statistics import plot
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsDailyGuildChannelMessages

PLOT_DAYS_COUNT = 30


async def get_monthly_messages(guild_id: int) -> tuple[list[str], dict[str, list[int]]]:
    messages = {}

    for day in reversed(range(PLOT_DAYS_COUNT)):
        date = datetime.date.today() - datetime.timedelta(days=day)

        entries = await StatsDailyGuildChannelMessages.filter(guild_id=guild_id, date=date)

        messages[f"{date.day}-{date.month}"] = sum([x.count for x in entries])

    return list(messages.keys()), {"": list(messages.values())}


async def get_messages_stats_file(guild: discord.Guild, tr: Translator) -> discord.File:
    dates, counts = await get_monthly_messages(guild.id)

    legend_text = tr.format("statistics_command_messages_legend", guild.name)

    result = await asyncio.get_event_loop().run_in_executor(None, functools.partial(plot.get_plot, dates, counts,
                                                                                    legend_text))

    return File(result, filename="Chart_Messages.png")


@stats.stats_group.command(description=Translatable("statistics_command_messages_desc"), name="messages")
async def messages_command(ctx: MrvnCommandContext):
    await ctx.defer()

    await ctx.respond(file=await get_messages_stats_file(ctx.guild, ctx))
