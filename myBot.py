from discord.ext.commands import Bot
import logging


class MyBot(Bot):
    def __init__(
        self, token: str, guild: str, iCal_url: str, command_prefix: str, **options
    ) -> None:
        """
        Summary:
        Initialize the bot.

        Args:
            token: bot token
            guild: server id the bot should interact with
            iCal_url: url to the iCal feed
            command_prefix: [$,!,>,etc.] prefix for commands
            **options:
        """
        super().__init__(command_prefix, **options)
        self.token = token
        self.guild = guild
        self.iCal_url = iCal_url

    async def on_ready(self) -> None:
        """
        Summary:
        Called when bot is ready to be used.
        """
        logging.info(f"Logged in as {self.user}")
