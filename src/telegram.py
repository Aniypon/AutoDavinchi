import asyncio
import sys

import emoji
from loguru import logger
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto


async def check_tg_account(self):
    # Авторизация в Telegram
    logger.info("Проверка аккаунта Telegram...")
    try:
        self.client = TelegramClient('QueVinchik', api_id=self.config["telegram"]["api_id"], api_hash=self.config["telegram"]["api_hash"])
        await self.client.start()
        logger.success("@" + (await self.client.get_me()).username)
        await self.client.send_message(self.bot_name, emoji.emojize(":thumbs_down:"))
        logger.info("Аккаунт Telegram подключен")
    except Exception as e:
        logger.exception(f"Ошибка авторизации в Telegram: {e}")
        sys.exit()


async def wait_bot_response(self):
    """
    Ожидание сообщения от бота в чате и возврат его текста
    """
    while True:
        messages = await self.client.get_messages(self.bot_name, limit=1)
        if messages:
            msg = messages[0]
            sender = await msg.get_sender()
            if sender.username == self.bot_name:  # Сообщение должно быть от бота
                messages = await self.client.get_messages(self.bot_name, limit=5)
                for msg in messages:
                    if msg.text:
                        return msg.text
        await asyncio.sleep(0.2)


async def get_bot_response_media(self):
    # Получение медиафайлов из последних сообщений бота
    raw_messages = await self.client.get_messages(self.bot_name, limit=5)
    msgs = []
    for msg in raw_messages:
        sender = await msg.get_sender()
        if sender.username == self.bot_name:
            msgs.append(msg)
        else:
            break
    return [msg for msg in msgs if type(msg.media) == MessageMediaPhoto], [msg for msg in msgs if type(msg.media) == MessageMediaDocument]


async def skip_form(self):
    # Пропуск анкеты (отправка дизлайка)
    await self.client.send_message(self.bot_name, emoji.emojize(":thumbs_down:"))


async def send_reply(self, text):
    # Отправка текстового ответа боту
    text = text.capitalize()
    logger.info(f"Отправка ответа: {text}")
    await self.client.send_message(self.bot_name, text)
