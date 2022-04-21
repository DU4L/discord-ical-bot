from myBot import MyBot
from environs import Env
from cogs.calendar import Calendar


def main() -> None:
    """Main function."""
    env = Env()
    env.read_env()
    token = env.str("BOT_TOKEN")
    guild_id = env.str("GUILD_ID")
    iCal_url = env.str("ICAL_URL")

    bot = MyBot(token=token, guild=guild_id, iCal_url=iCal_url, command_prefix="$")
    bot.add_cog(Calendar(bot))
    bot.run(token)


if __name__ == "__main__":
    main()
