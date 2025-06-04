import asyncio
import sys

import emoji
import os
import emoji
from loguru import logger
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


async def check_tg_account(self):
    # Авторизация в Telegram
    logger.info("Проверка аккаунта Telegram...")
    try:
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            raise ValueError("TELEGRAM_API_ID и TELEGRAM_API_HASH должны быть установлены в .env файле")
        
        self.client = TelegramClient('QueVinchik', api_id=int(api_id), api_hash=api_hash)
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


async def wait_user_action(self):
    """
    Ожидание действия пользователя (лайк/дизлайк) в чате с ботом
    Возвращает True если пользователь сделал лайк, False если дизлайк
    """
    # Получаем ID последнего сообщения перед началом ожидания
    initial_messages = await self.client.get_messages(self.bot_name, limit=10)
    last_msg_id = initial_messages[0].id if initial_messages else 0
    
    logger.info("Ожидание действия пользователя (лайк/дизлайк)...")
    
    while True:
        await asyncio.sleep(0.5)
        
        # Получаем новые сообщения
        messages = await self.client.get_messages(self.bot_name, limit=10)
        
        # Ищем новые сообщения от пользователя
        for msg in messages:
            # Пропускаем старые сообщения
            if msg.id <= last_msg_id:
                continue
                
            sender = await msg.get_sender()
            me = await self.client.get_me()
            
            # Если сообщение от нас
            if sender.id == me.id and msg.text:
                # Проверяем эмодзи в сообщении
                if "❤️" in msg.text:
                    logger.success("Обнаружен лайк пользователя")
                    return True
                elif "👎" in msg.text:
                    logger.info("Обнаружен дизлайк пользователя")
                    return False
                else:
                    # Обновляем ID последнего сообщения для игнорирования служебных команд
                    last_msg_id = msg.id
                    continue
