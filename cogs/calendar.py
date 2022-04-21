from icalevents.icalevents import events
from discord.ext.commands import Cog
from aiocron import crontab
from aiohttp import ClientSession
from json import loads, dumps
from environs import Env


class Calendar(Cog, name="Calendar"):
    def __init__(self, bot) -> None:
        """
        Initializes the Calendar cog
        :param bot: Bot that the cog shall attach to
        """
        env = Env()
        env.read_env()
        self.bot = bot
        self.channel_id = env("CHANNEL_ID")
        self.base_api_url = "https://discord.com/api/v8"
        self.auth_headers = {
            "Authorization": f"Bot {bot.token}",
            "User-Agent": "DiscordBot Python/3.9 aiohttp/3.8.1",
            "Content-Type": "application/json",
        }
        self.event_url = f"{self.base_api_url}/guilds/{bot.guild}/scheduled-events"

    # crontab that runs daily
    @crontab("0 0 * * *")
    async def createEvent(self) -> None:
        """
        Creates events in the guild if they don't exist based on an iCal.
        S
        """
        iCalEvents = events(self.bot.iCal_url)
        serverEvents = await self.getGuildEvents()
        for iEvent in iCalEvents:
            if iEvent.summary not in [event["name"] for event in serverEvents]:
                if iEvent.location == "Discord":
                    event_type = 2
                    if iEvent.summary == "DU4L Jour-Fixe":
                        time_adjustment = "+01"
                    else:
                        time_adjustment = "+00"
                else:
                    event_type = 3
                    time_adjustment = "+00"

                await self.create_guild_event(
                    event_name=iEvent.summary,
                    event_description=iEvent.description,
                    event_start_time=iEvent.start.strftime(
                        "%Y-%m-%dT%H:%M:%S" + time_adjustment
                    ),
                    event_end_time=iEvent.end.strftime(
                        "%Y-%m-%dT%H:%M:%S" + time_adjustment
                    ),
                    event_channel_id=self.channel_id,
                    event_type=event_type,
                    event_metadata={"location": iEvent.location},
                )
            else:
                print("Event already exists")

    async def getGuildEvents(self) -> list:
        """Returns a list of dictionaries that represent events in the guild."""
        async with ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.get(self.event_url) as response:
                    response.raise_for_status()
                    response_list = loads(await response.read())
            finally:
                await session.close()
        return response_list

    async def create_guild_event(
        self,
        event_name: str,
        event_description: str,
        event_start_time: str,
        event_end_time: str,
        event_metadata: dict,
        event_channel_id: str,
        event_type: int,
        event_privacy_level=2,
    ) -> None:
        """
        Creates a guild event using the supplied arguments.

        :param event_name: Name of the event
        :param event_description: Description of the event
        :param event_start_time: %Y-%m-%dT%H:%M:%S.000Z - Start time of the event
        :param event_end_time: %Y-%m-%dT%H:%M:%S.000Z - End time of the event
        :param event_metadata: event_metadata={'location': 'YOUR_LOCATION_NAME'} - Dictionary of metadata for the event
        :param event_channel_id: ID of the channel the event takes place in
        :param event_type: Type of event (2 = Voice Event, 3 = External Event)
        :param event_privacy_level: Privacy level of the event 2 = default
        """
        event_data = {
            "name": event_name,
            "description": event_description,
            "scheduled_start_time": event_start_time,
            "privacy_level": event_privacy_level,
        }

        if event_type == 1:
            event_data["entity_type"] = 1
        elif event_type == 2:
            event_data["entity_type"] = 2
            event_data["channel_id"] = event_channel_id
        else:
            event_data["entity_type"] = 3
            event_data["scheduled_end_time"] = event_end_time
            event_data["entity_metadata"] = event_metadata

        print(event_data)
        async with ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.post(
                    self.event_url, data=dumps(event_data)
                ) as response:
                    response.raise_for_status()
            finally:
                await session.close()
