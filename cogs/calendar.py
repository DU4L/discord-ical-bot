from icalevents.icalevents import events
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from aiohttp import ClientSession, ClientResponseError
from json import loads, dumps
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging


class Calendar(Cog, name="iCal Creator"):

    TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
    TIME_ZONE = "+00"

    def __init__(self, bot, iCal_url: str, channel_id: str) -> None:
        """
        Summary:
        Initializes the Calendar cog

        Args:
            bot: The bot the cog shall attach to, needs attributes: token, guild_id
            iCal_url: The url of the iCal feed
            channel_id: The channel id of the voice channel the events shall take place in
        """
        self.bot = bot
        self.channel_id = channel_id
        self.base_api_url = "https://discord.com/api/v8"
        self.auth_headers = {
            "Authorization": f"Bot {bot.token}",
            "User-Agent": "DiscordBot Python/3.9 aiohttp/3.8.1",
            "Content-Type": "application/json",
        }
        self.iCal_url = iCal_url
        self.event_url = f"{self.base_api_url}/guilds/{bot.guild}/scheduled-events"
        self.create_event.start()

    # Runs every five minutes
    @loop(minutes=5)
    async def create_event(self) -> None:
        """
        Summary:
        Creates events in the guild, if they don't exist based on an iCal feed.
        """
        try:
            iCal_events = events(
                url=self.iCal_url,
                start=datetime.now(),
                end=datetime.now() + relativedelta(days=+7),
            )
        finally:
            logging.info("Fetched iCal events")
        server_events = await self.get_guild_events()
        for iEvent in iCal_events:
            if iEvent.summary not in [event["name"] for event in server_events]:
                if iEvent.location is None or iEvent.location.lower() == "discord" or iEvent.location == "":
                    event_type = 2
                else:
                    event_type = 3

                logging.info("Creating event %s", iEvent.summary)
                await self.create_guild_event(
                    name=iEvent.summary,
                    description=iEvent.description,
                    start_time=iEvent.start.strftime(self.TIME_FORMAT + self.TIME_ZONE),
                    end_time=iEvent.end.strftime(self.TIME_FORMAT + self.TIME_ZONE),
                    channel_id=self.channel_id,
                    type_id=event_type,
                    metadata={"location": iEvent.location or "¯\\_(ツ)_/¯"},
                )
            else:
                logging.info("Event already exists")

    @create_event.before_loop
    async def before_printer(self) -> None:
        logging.info("waiting for bot to be ready")
        await self.bot.wait_until_ready()

    async def get_guild_events(self) -> list:
        """
        Fetches all events in the guild

        Returns:
            list: List of dicts that represent events in the guild
        """
        async with ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.get(self.event_url) as response:
                    response.raise_for_status()
                    response_list = loads(await response.read())
                    logging.info("Fetched server events successfully")
            except ClientResponseError:
                logging.error("Failed to fetch events from the guild")
            finally:
                await session.close()
        return response_list

    async def create_guild_event(
        self,
        name: str,
        description: str,
        start_time: str,
        end_time: str,
        metadata: dict,
        channel_id: str,
        type_id: int,
        privacy_level=2,
    ) -> None:
        """
        Summary:
        Creates a guild event using the supplied arguments.

        Args:
            name: Name of the event
            description: Description of the event
            start_time: %Y-%m-%dT%H:%M:%S.000Z - Start time of the event
            end_time: %Y-%m-%dT%H:%M:%S.000Z - End time of the event
            metadata: metadata={'location': 'YOUR_LOCATION_NAME'} - Dictionary of metadata for the event
            channel_id: ID of the channel the event takes place in
            type_id: Type of event (2 = Voice Event, 3 = External Event)
            privacy_level: Privacy level of the event 2 = default
        """
        event_data = {
            "name": name,
            "description": description,
            "scheduled_start_time": start_time,
            "privacy_level": privacy_level,
            "entity_type": type_id,
        }

        if type_id == 2:
            event_data["channel_id"] = channel_id
        elif type_id == 3:
            event_data["scheduled_end_time"] = end_time
            event_data["entity_metadata"] = metadata

        async with ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.post(
                    self.event_url, data=dumps(event_data)
                ) as response:
                    logging.info(response)
                    response.raise_for_status()
                    logging.info("Created event successfully")

            except ClientResponseError:
                logging.error("Failed to create event.")
            finally:
                await session.close()
