from discord.ext import commands
from core.thread import Thread

class LogURLFixer(commands.Cog):
    """A plugin to fix the log URL generation by removing the hardcoded /logs/ segment."""
    
    def __init__(self, bot):
        self.bot = bot
        
        self._original_log_url = Thread.log_url
        
        @property
        def custom_log_url(thread_self):
            prefix = thread_self.bot.config.get('log_url_prefix', '').strip('/')
            
            if not prefix or prefix == 'NONE':
                return ''
                
            return f"{prefix}/{thread_self.key}"

        Thread.log_url = custom_log_url

    def cog_unload(self):
        Thread.log_url = self._original_log_url


async def setup(bot):
    await bot.add_cog(LogURLFixer(bot))