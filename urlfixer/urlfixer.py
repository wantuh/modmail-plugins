import discord
from discord.ext import commands

class LogURLFixer(commands.Cog):
    """A plugin to fix the log URL generation by intercepting and replacing the hardcoded /logs/ segment."""
    
    def __init__(self, bot):
        self.bot = bot
        
        self._original_send = discord.abc.Messageable.send
        
        _bot = self.bot
        _plugin_self = self
        
        async def custom_send(messageable_self, *args, **kwargs):
            try:
                prefix = _bot.config.get('log_url_prefix', '').strip('/')
            except Exception:
                prefix = ''
                
            if prefix and prefix != 'NONE':
                bad_str = f"{prefix}/logs/"
                good_str = f"{prefix}/"
                
                if args and isinstance(args[0], str) and bad_str in args[0]:
                    args = (args[0].replace(bad_str, good_str),) + args[1:]
                    
                if 'content' in kwargs and isinstance(kwargs['content'], str) and bad_str in kwargs['content']:
                    kwargs['content'] = kwargs['content'].replace(bad_str, good_str)
                    
                if 'embed' in kwargs and kwargs['embed']:
                    _plugin_self._fix_embed(kwargs['embed'], bad_str, good_str)
                    
                if 'embeds' in kwargs and kwargs['embeds']:
                    for e in kwargs['embeds']:
                        _plugin_self._fix_embed(e, bad_str, good_str)

            return await self._original_send(messageable_self, *args, **kwargs)

        discord.abc.Messageable.send = custom_send

    def _fix_embed(self, embed, bad_str, good_str):
        """Helper function to find and replace the bad URL inside Discord embeds."""
        try:
            if isinstance(embed.url, str) and bad_str in embed.url:
                embed.url = embed.url.replace(bad_str, good_str)
            if isinstance(embed.description, str) and bad_str in embed.description:
                embed.description = embed.description.replace(bad_str, good_str)
            if isinstance(embed.title, str) and bad_str in embed.title:
                embed.title = embed.title.replace(bad_str, good_str)
            
            if getattr(embed.author, 'url', None) and isinstance(embed.author.url, str) and bad_str in embed.author.url:
                embed.set_author(
                    name=embed.author.name, 
                    url=embed.author.url.replace(bad_str, good_str), 
                    icon_url=embed.author.icon_url
                )
                
            for i, field in enumerate(embed.fields):
                if isinstance(field.value, str) and bad_str in field.value:
                    embed.set_field_at(
                        i, 
                        name=field.name, 
                        value=field.value.replace(bad_str, good_str), 
                        inline=field.inline
                    )
        except Exception:
            pass

    def cog_unload(self):
        discord.abc.Messageable.send = self._original_send


async def setup(bot):
    await bot.add_cog(LogURLFixer(bot))