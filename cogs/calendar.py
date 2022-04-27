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

    iCal_events: list
    server_events: list

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

    @loop(minutes=5)
    async def main_loop(self):
        await self.create_event()
        self.server_events = await self.get_guild_events()
        await self.delete_event()
        self.server_events = await self.get_guild_events()
        await self.update_event()

    @main_loop.before_loop()
    async def before_main_loop(self) -> None:
        """
        Summary:
        Runs before the main_loop starts and fetches the iCal and server events
        """
        logging.info("Checking if bot is ready")
        await self.bot.wait_until_ready()
        self.iCal_events = await self.get_iCal_events(
            start=datetime.now(), end=datetime.now() + relativedelta(days=+7)
        )
        self.server_events = await self.get_guild_events()

    async def create_event(self) -> None:
        """
        Summary:
        Creates events in the guild, if they don't exist based on an iCal feed.
        """
        for iEvent in self.iCal_events:
            if iEvent.summary not in [event["name"] for event in self.server_events]:
                if iEvent.location in ["Discord", "discord"]:
                    event_type = 2
                else:
                    event_type = 3

                logging.info(f"Creating event {iEvent.summary}")
                await self.create_guild_event(
                    name=iEvent.summary,
                    description=iEvent.description,
                    start_time=iEvent.start.strftime(self.TIME_FORMAT + self.TIME_ZONE),
                    end_time=iEvent.end.strftime(self.TIME_FORMAT + self.TIME_ZONE),
                    channel_id=self.channel_id,
                    type_id=event_type,
                    metadata={"location": iEvent.location},
                )
            else:
                logging.info("Event already exists")

    async def delete_event(self) -> None:
        """
        Summary:
        Deletes events in the guild, if they don't exist based on an iCal feed.
        """
        for event in self.server_events:
            if event["name"] not in [iEvent.summary for iEvent in self.iCal_events]:
                logging.info(f"Deleting event {event['name']}")
                await self.delete_guild_event(event)

    async def update_event(self) -> None:
        """
        Summary:
        Updates event information in the guild based on iCal feed.
        """
        for iEvent in self.iCal_events:
            for event in self.server_events:

                update_data = {}

                if iEvent.summary == event["name"]:
                    if iEvent.location != event["metadata"]["location"]:
                        update_data["metadata"] = {"location": iEvent.location}

                    if iEvent.start != event["scheduled_start_time"]:
                        update_data["scheduled_start_time"] = iEvent.start

                    if iEvent.end != event["scheduled_end_time"]:
                        update_data["scheduled_end_time"] = iEvent.end

                    if iEvent.description != event["description"]:
                        update_data["description"] = iEvent.description

                    logging.info(f"Updating the event: {iEvent.summary}")
                    await self.update_guild_event(event["id"], update_data)

    async def get_iCal_events(self, start=None, end=None) -> list:
        """
        Summary:
        Fetches the events from the iCal feed

        Returns:
            list: A list of iCal events
        """
        try:
            logging.info("trying to get iCal events")
            return events(
                url=self.iCal_url,
                start=start,
                end=end,
            )
        finally:
            logging.info("Fetched iCal events")

    async def get_guild_events(self) -> list:
        """
        Summary:
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
                    response.raise_for_status()
                    logging.info("Created event successfully")

            except ClientResponseError:
                logging.error("Failed to create event.")
            finally:
                await session.close()

    async def delete_guild_event(self, event: dict) -> None:
        """
        Summary:
        Deletes an event in Discord.

        Args:
            event: dict: Event to delete
        """
        async with ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.delete(self.event_url + event["id"]) as response:
                    response.raise_for_status()
                    logging.info("Deleted event successfully")

            except ClientResponseError:
                logging.error("Failed to delete event.")
            finally:
                await session.close()

    async def update_guild_event(self, eventId: str, update_data: dict) -> None:
        """
        Summary:
        Updates the provided information for a specific event.
        Args:
            eventId: str: Event that should be updated
            update_data: dict: Information that needs to be updated
        """
        if update_data != {}:
            async with ClientSession(headers=self.auth_headers) as session:
                try:
                    async with session.patch(
                        self.event_url + eventId, data=dumps(update_data)
                    ) as response:
                        response.raise_for_status()
                        logging.info("Updated event successfully")

                except ClientResponseError:
                    logging.error("Failed to update event.")
                finally:
                    await session.close()
