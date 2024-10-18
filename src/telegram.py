import asyncio
import sys
import time

import emoji
from loguru import logger
from telethon import TelegramClient


async def check_tg_account(self):
    logger.info("Проверка аккаунта Telegram...")

    try:
        self.client = TelegramClient('QueVinchik', api_id=self.config["telegram"]["api_id"], api_hash=self.config["telegram"]["api_hash"])
        await self.client.start()
        logger.success("@" + (await self.client.get_me()).username)
        await self.client.send_message(self.bot_name, emoji.emojize(":thumbs_down:"))
        logger.info("Аккаунт Telegram подключен")
    except Exception as e:
        logger.exception(f"Ошибка авторизации в Telegram: {e}")
        input()
        sys.exit()


async def wait_bot_response(self):
    """
    Ожидает сообщение от бота в чате и возвращает его текст.
    """

    while True:
        messages = await self.client.get_messages(self.bot_name, limit=1)
        if messages:
            msg = messages[0]
            sender = await msg.get_sender()

            if sender.username == self.bot_name:
                messages = await self.client.get_messages(self.bot_name, limit=5)
                for msg in messages:
                    if msg.text:
                        return msg.text


        await asyncio.sleep(0.25)


async def skip_form(self):
    await self.client.send_message(self.bot_name, emoji.emojize(":thumbs_down:"))


async def send_reply(self, text):
    await self.client.send_message(self.bot_name, text)
