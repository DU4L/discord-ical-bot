from icalevents.icalevents import events
from discord.ext.commands import Cog
from aiocron import crontab
from aiohttp import ClientSession
from json import loads, dumps
# import time


class Calendar(Cog, name="Calendar"):
    def __init__(self, bot) -> None:
        """
        Initializes the Calendar cog
        :param bot: Bot that the cog shall attach to
        """
        self.bot = bot
        self.base_api_url = "https://discord.com/api/v8"
        self.auth_headers = {
            "Authorization": f"Bot {bot.token}",
            "User-Agent": "DiscordBot Python/3.9 aiohttp/3.8.1",
            "Content-Type": "application/json",
        }
        self.event_url = f"{self.base_api_url}/guilds/{bot.guild}/scheduled-events"
        print("Calendar cog loaded")

    # crontab that runs every 3 days
    # @crontab('* * */3 * *')
    async def createEvent(self) -> None:
        """
        Creates events in the guild if they don't exist based on an iCal.
        S
        """
        print("Creating event")
        iCalEvents = events(self.bot.iCal_url)
        serverEvents = await self.getGuildEvents()
        for iEvent in iCalEvents:
            print(f"{iEvent}, {serverEvents}")
            if iEvent.summary not in [event["name"] for event in serverEvents]:
                await self.create_guild_event(
                    event_name=iEvent.summary,
                    event_description=iEvent.description,
                    event_start_time=str(iEvent.start),
                    event_end_time=str(iEvent.end),
                    event_channel_id="966745318702059571",
                    event_metadata={"location": iEvent.location},
                )
            else:
                print("Event already exists")

    async def getGuildEvents(self) -> list[dict]:
        """Returns a list of dictionary of events in the guild."""
        async with ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.get(self.event_url) as response:
                    response.raise_for_status()
                    response_list = loads(await response.read())
            except Exception as e:
                print(f"EXCEPTION: {e}")
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
        event_privacy_level=2,
    ) -> None:
        """
        Creates a guild event using the supplied arguments.

        :param event_name: Name of the event
        :param event_description: Description of the event
        :param event_start_time: %Y-%m-%dT%H:%M:%S - Start time of the event
        :param event_end_time: %Y-%m-%dT%H:%M:%S - End time of the event
        :param event_metadata: event_metadata={'location': 'YOUR_LOCATION_NAME'} - Dictionary of metadata for the event
        :param event_channel_id: ID of the channel the event takes place in
        """
        event_data = dumps(
            {
                "name": event_name,
                "privacy_level": event_privacy_level,
                "scheduled_start_time": event_start_time,
                "scheduled_end_time": event_end_time,
                "description": event_description,
                "channel_id": event_channel_id,
                "entity_metadata": event_metadata,
                "entity_type": 3,
            }
        )

        async with ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.post(self.event_url, data=event_data) as response:
                    response.raise_for_status()
                    if response.status != 200:
                        raise Exception(f"Response status code: {response.status}")
            except Exception as e:
                print(f"EXCEPTION: {e}")
            finally:
                await session.close()
