Posting giveaways from a Discord bot
====================================

This cog for `discord.py <https://discordpy.readthedocs.io>`_ 2.x posts every new Epic Games
Store giveaway in one channel.

.. code-block:: python

   import asyncio
   import logging

   import discord
   from discord.ext import commands

   from gamerpower import GamerPower, Giveaway, Platform

   CHANNEL_ID = 123456789012345678  # replace with your announcement channel


   def make_embed(g: Giveaway) -> discord.Embed:
       embed = discord.Embed(
           title=g.title,
           url=g.open_giveaway_url,
           description=f"{g.description[:300]}\n\n[Free games via GamerPower](https://www.gamerpower.com)",
       )
       if g.thumbnail:
           embed.set_thumbnail(url=g.thumbnail)
       if g.worth is not None:
           embed.add_field(name="Worth", value=f"${g.worth:.2f}")
       if g.end_date:
           embed.add_field(name="Ends", value=f"{g.end_date:%Y-%m-%d %H:%M}")
       return embed


   class FreeGames(commands.Cog):
       def __init__(self, bot: commands.Bot) -> None:
           self.bot = bot
           self.gp = GamerPower()
           self.task: asyncio.Task | None = None

       async def cog_load(self) -> None:
           self.task = asyncio.create_task(self.announce())

       async def cog_unload(self) -> None:
           if self.task:
               self.task.cancel()
           await self.gp.close()

       async def announce(self) -> None:
           await self.bot.wait_until_ready()
           channel = self.bot.get_channel(CHANNEL_ID)
           if not isinstance(channel, discord.TextChannel):
               return
           async for g in self.gp.watch(platform=Platform.EPIC_GAMES_STORE):
               try:
                   await channel.send(embed=make_embed(g))
               except discord.HTTPException:
                   logging.exception("could not post giveaway %s", g.id)


   async def setup(bot: commands.Bot) -> None:
       await bot.add_cog(FreeGames(bot))

Things to know
--------------

- **Attribution.** GamerPower's terms ask for an active hyperlink back to GamerPower.com. Embed
  descriptions render Markdown links, which is why the example ends with one. A footer would not
  work, since footer text is not clickable. See :doc:`/terms`.
- **Claim button.** ``open_giveaway_url`` is the link to send people to. It redirects to the
  store page.
- **Times.** ``end_date`` is a naive datetime, the API does not state its timezone. The example
  shows it as plain text instead of a Discord timestamp for that reason.
- **Restarts.** The watcher forgets what it has posted when the bot stops. To keep that across
  restarts, see :ref:`the database recipe <watching-db>` in :doc:`watching`.
- **One channel per server.** The cog above posts to one fixed channel. For a public bot, store
  a channel per guild and call ``channel.send`` for each of them from the same ``async for``
  loop, so every server shares a single watcher and a single stream of requests.
