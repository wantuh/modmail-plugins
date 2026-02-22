import re
import discord
from discord.ext import commands

class LogURLFixer(commands.Cog):
    """A plugin to fix the log URL generation by intercepting the hardcoded /logs/ segment."""
    
    def __init__(self, bot):
        self.bot = bot
        
        self._original_msg_send = discord.abc.Messageable.send
        self._original_wh_send = discord.Webhook.send
        
        _plugin_self = self
        
        self.url_pattern = re.compile(r"(/logs/[^/]+)/logs/")
        
        async def custom_msg_send(messageable_self, *args, **kwargs):
            args, kwargs = _plugin_self._clean_payload(args, kwargs)
            return await self._original_msg_send(messageable_self, *args, **kwargs)

        async def custom_wh_send(webhook_self, *args, **kwargs):
            args, kwargs = _plugin_self._clean_payload(args, kwargs)
            return await self._original_wh_send(webhook_self, *args, **kwargs)

        discord.abc.Messageable.send = custom_msg_send
        discord.Webhook.send = custom_wh_send

    def _clean_payload(self, args, kwargs):
        """Finds and replaces the bad URL pattern in message content and embeds."""
        if args and isinstance(args[0], str):
            args = (self.url_pattern.sub(r"\1/", args[0]),) + args[1:]
            
        if 'content' in kwargs and isinstance(kwargs['content'], str):
            kwargs['content'] = self.url_pattern.sub(r"\1/", kwargs['content'])
            
        if 'embed' in kwargs and kwargs['embed']:
            self._fix_embed(kwargs['embed'])
            
        if 'embeds' in kwargs and kwargs['embeds']:
            for e in kwargs['embeds']:
                self._fix_embed(e)
                
        return args, kwargs

    def _fix_embed(self, embed):
        """Helper function to find and replace the bad URL inside Discord embeds."""
        try:
            if isinstance(embed.url, str):
                embed.url = self.url_pattern.sub(r"\1/", embed.url)
            if isinstance(embed.description, str):
                embed.description = self.url_pattern.sub(r"\1/", embed.description)
            if isinstance(embed.title, str):
                embed.title = self.url_pattern.sub(r"\1/", embed.title)
            
            if getattr(embed.author, 'url', None) and isinstance(embed.author.url, str):
                embed.set_author(
                    name=embed.author.name, 
                    url=self.url_pattern.sub(r"\1/", embed.author.url), 
                    icon_url=embed.author.icon_url
                )
                
            for i, field in enumerate(embed.fields):
                if isinstance(field.value, str):
                    embed.set_field_at(
                        i, 
                        name=field.name, 
                        value=self.url_pattern.sub(r"\1/", field.value), 
                        inline=field.inline
                    )
        except Exception:
            pass

    def cog_unload(self):
        discord.abc.Messageable.send = self._original_msg_send
        discord.Webhook.send = self._original_wh_send

async def setup(bot):
    await bot.add_cog(LogURLFixer(bot))