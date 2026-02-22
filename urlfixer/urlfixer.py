from discord.ext import commands
from core.models import Log

class LogURLFixer(commands.Cog):
    """A plugin to fix the log URL generation by removing the hardcoded /logs/ segment."""
    
    def __init__(self, bot):
        self.bot = bot
        
        self._original_log_url = Log.url
        
        bot_instance = self.bot
        
        @property
        def custom_log_url(log_self):
            prefix = bot_instance.config.get('log_url_prefix', '').strip('/')
            
            if not prefix or prefix == 'NONE':
                return ''
                
            return f"{prefix}/{log_self.key}"

        Log.url = custom_log_url

    def cog_unload(self):
        Log.url = self._original_log_url


async def setup(bot):
    await bot.add_cog(LogURLFixer(bot))