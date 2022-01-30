# Add to Server

Add the Bot to the Server (only Admins can do this!)

Go to https://discord.com/oauth2/authorize?client_id={clientid}&scope=bot&permissions={permission_integer}
client id: 936741085483507712
permission integer: 8589934592

# API Authorization

add a Header:

`Authorization: Bot {token}`

you can get the token from the page of your bot

# Getting Schedules Events

```
$ curl --location --request GET 'http://discordapp.com/api/guilds/906150994843402241/scheduled-events' --header 'Authorization: Bot {token}'

[{"id": "936678965236600862", "guild_id": "906150994843402241", "channel_id": null, "creator_id": "239506007812866050", "name": "Insomni'hack teaser 2022", "description": "Creds in CTF-Note", "image": null, "scheduled_start_time": "2022-01-29T12:00:00+00:00", "scheduled_end_time": "2022-01-30T12:00:00+00:00", "privacy_level": 2, "status": 1, "entity_type": 3, "entity_id": null, "entity_metadata": {"location": "https://insomnihack.ch/contests/"}, "sku_ids": [], "creator": {"id": "239506007812866050", "username": "xTomsko", "avatar": "0c683302b5342530f3cdd5e95c9b3b7f", "discriminator": "0113", "public_flags": 256}}]
```

does not work: don't know why

```
$ curl -H 'Authorization: Bot {token}' -d '{"name": "Test Event", "description": "This is a CURL created Test Event", "scheduled_start_time": 2022-02-01T12:00:00+01:00", "scheduled_end_time": "2022-02-01T14:00:00+01:00"}' 'http://discordapp.com/api/guilds/906150994843402241/scheduled-events'
```