from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger

if TYPE_CHECKING:
    from bot import ModmailBot

info_json = Path(__file__).parent.resolve() / "info.json"
with open(info_json, encoding="utf-8") as f:
    __plugin_info__ = json.loads(f.read())

__plugin_name__ = __plugin_info__["name"]
__version__ = __plugin_info__["version"]
__description__ = "\n".join(__plugin_info__["description"])

logger = getLogger(__name__)


class ConfigRefresh(commands.Cog, name=__plugin_name__):
    """Re-fetches the bot configuration from the database without a restart."""

    def __init__(self, bot: ModmailBot):
        self.bot: ModmailBot = bot

    @commands.command(name="configrefresh", aliases=["reloadconfig"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def config_refresh(self, ctx: commands.Context):
        """
        Re-fetches the bot configuration from the database.

        Overwrites the in-memory config cache with the latest values stored in MongoDB.
        Useful when the database has been edited externally and you want the changes
        to take effect without restarting the bot.

        Requires permission level: **Administrator (4)**.
        """
        await self.bot.config.refresh()
        logger.info("Config manually refreshed by %s (%s).", ctx.author, ctx.author.id)

        embed = discord.Embed(
            title="Config Refreshed",
            color=self.bot.main_color,
            description="Successfully re-fetched the configuration from the database.",
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        return await ctx.send(embed=embed)


async def setup(bot: ModmailBot):
    await bot.add_cog(ConfigRefresh(bot))
