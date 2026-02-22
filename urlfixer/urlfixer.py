import json
import re
from discord.ext import commands

class LogURLFixer(commands.Cog):
    """A plugin to fix the log URL generation by intercepting raw HTTP requests to Discord."""
    
    def __init__(self, bot):
        self.bot = bot
        
        self._original_request = bot.http.request
        
        self.url_pattern = re.compile(r"(/logs/[^/]+)/logs/")
        
        async def custom_request(*args, **kwargs):
            if 'json' in kwargs and kwargs['json']:
                try:
                    payload_str = json.dumps(kwargs['json'])
                    
                    if '/logs/' in payload_str:
                        cleaned_str = self.url_pattern.sub(r"\1/", payload_str)
                        kwargs['json'] = json.loads(cleaned_str)
                except Exception:
                    pass 
                    
            return await self._original_request(*args, **kwargs)

        bot.http.request = custom_request

    def cog_unload(self):
        self.bot.http.request = self._original_request


async def setup(bot):
    await bot.add_cog(LogURLFixer(bot))