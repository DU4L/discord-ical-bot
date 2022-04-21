from discord.ext.commands import Bot
from cogs.calendar import Calendar


class MyBot(Bot):
    def __init__(
        self,
        token: str,
        guild: str,
        iCal_url: str,
        command_prefix: str,
        **options
    ) -> None:
        super().__init__(command_prefix, **options)
        self.token = token
        self.guild = guild
        self.iCal_url = iCal_url

    async def on_ready(
        self
    ) -> None:
        """
        Called when bot is ready to be used.
        """
        print("Logged in as " + self.user.name)
        cal = Calendar(self)
        print(await cal.getGuildEvents())
        await cal.createEvent()
