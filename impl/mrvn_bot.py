import traceback
from abc import ABC
from typing import Any

from discord import Bot, Message, Interaction, InteractionType, SlashCommand

from api.command.args import element
from api.command.args.arguments import PreparedArguments
from api.command.mrvn_command_context import MrvnCommandContext
from api.command.mrvn_message_context import MrvnMessageContext
from api.event_handler import handler_manager


class MrvnBot(Bot, ABC):
    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        super().dispatch(event_name, *args, *kwargs)

        handler_manager.post(event_name, *args)

    async def on_interaction(self, interaction: Interaction):
        if interaction.type not in (
                InteractionType.application_command,
        ):
            return

        try:
            command = self._application_commands[interaction.data["id"]]
        except KeyError:
            for cmd in self.application_commands:
                if (
                        cmd.name == interaction.data["name"]
                        and interaction.data.get("guild_id", None) in cmd.guild_ids
                ):
                    command = cmd
                    break
            else:
                return self.dispatch("unknown_command", interaction)
        if interaction.type is InteractionType.auto_complete:
            ctx = await self.get_autocomplete_context(interaction)
            ctx.command = command
            return await command.invoke_autocomplete_callback(ctx)

        ctx = MrvnCommandContext(self, interaction)
        ctx.command = command

        await ctx.command.invoke(ctx)

    async def on_message(self, message: Message):
        # Test code for message command support

        if not message.content.startswith("?"):
            return

        args = PreparedArguments(message.content)
        cmd_name = args.next().value[1:].lower()

        for cmd in self.application_commands:
            if (
                    cmd.name == cmd_name
                    and message.guild.id in cmd.guild_ids
                    and isinstance(cmd, SlashCommand)
            ):
                command = cmd
                break
        else:
            return

        ctx = MrvnMessageContext(self, message)
        ctx.command = command

        parsers = []

        for option in command.options:
            parser = element.parsers.get(option.input_type, None)

            if parser is None:
                await ctx.respond(f"Error: could not find parser for slash option type {option.input_type}")

                return

            parsers.append(parser)

        kwargs = {}

        try:
            for i, parser in enumerate(parsers):
                kwargs[command.options[i].name] = parser.parse(ctx, args)
        except RuntimeError:
            await ctx.respond(traceback.format_exc())

            return

        await command(ctx, **kwargs)
