# Discord-ical-Bot

This Discord bot should serve the simple purpose of getting an ical-url and adding those events to a discord server.

## Usage

```
docker run -e "ICAL_URL=https://example.com/calendar.ics" -e "BOT_TOKEN=xxx" -e "GUILD_ID=xx" -e "CHANNEL_ID=xx" ghcr.io/du4l/discord-ical
```

You can get the bot token from the discord developer portal. The Guild ID is the Discord Server ID. You can get it by enabling developer settings in discord and right clicking on the server. The CHANNEL_ID should be the ID of the voicechannel where the events will be held.

By default only events in the next 7 days will be added to the calendar.

The bot will update the events every 5 minutes.

## Adding the bot to a Server

Add the Bot to the Server (only Admins can do this!)

Go to https://discord.com/oauth2/authorize?client_id={clientid}&scope=bot&permissions=8589934592

where the clientid is the id of the bot.
