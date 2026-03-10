from collections import namedtuple
import asyncio

    
Message = namedtuple('Message', ['chat_id', 'text'])

class TelegramSender():

    def __init__(self, bot):
        self.bot = bot

    async def send_one(self, msg: Message):
        await self.bot.send_message(chat_id=msg.chat_id, text=msg.text)

    async def send_batch(self, data: list[Message]):
        tasks = [self.send_one(msg) for msg in data]
        await asyncio.gather(*tasks)