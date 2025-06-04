import asyncio
import os
import random
import re
import string
import sys

import re
import emoji
from loguru import logger

from src.configs import load_configs
from src.telegram import check_tg_account, get_bot_response_media, send_reply, skip_form, wait_bot_response, wait_user_action
from src.utils import hash_form_result, notify, save_form, update_stat
from src.validators import check_about_banwords, check_about_len, check_age, check_promoting


class Form:
    def __init__(self, name, age, about):
        self.name = name  # Имя
        self.age = age    # Возраст
        self.about = about  # О себе


def parse_form(text):
    # Парсинг анкеты из текста
    name_match = re.findall(r"([\s\S]+),\s\d{2},", text)
    age_match = re.findall(r"[\s\S]+,\s(\d{1,2}),", text)
    about_match = re.findall(r"[\s\S]+?,\s\d{1,2},\s[\s\S]+?\s–\s([\s\S]+)", text)
    name = name_match[0].strip() if name_match else ""
    age = age_match[0].strip() if age_match else ""
    if not age.isdigit():
        age = "0"
    if len(about_match) == 0:
        about = ""
    else:
        about = about_match[0].strip().replace("\n", ". ").capitalize()
    return Form(name=name, age=age, about=about)


class DVWorker:
    def __init__(self):
        self.bot_name = "leomatchbot"  # Тег бота
        self.client = None  # Клиент Telegram
        self.pool = None

        self.skipped_forms = 0  # Количество пропущенных анкет
        self.suitable_forms = 0  # Количество подходящих анкет
        self.all_forms = 0  # Всего обработано анкет

        self.config = { }  # Общий конфиг
        self.banwords = []  # Бан-слова
        self.promotings = []  # Рекламные сообщения

        self.hash_list = []

    async def run(self):
        logger.info("Запуск QueVinchik...")
        await load_configs(self)
        await check_tg_account(self)
        await update_stat(self)
        logger.success("QueVinchik запущен")
        if self.config["work_mode"] == "search":
            await self.search_cycle()
        elif self.config["work_mode"] == "parse":
            await self.parse_cycle()
        else:
            logger.exception(f"Неправильный режим работы: {self.config['work_mode']}, поддерживаются search и parse")
            sys.exit()

    async def parse_cycle(self):
        msg = ""
        while True:
            await asyncio.sleep(self.config["telegram"]["delay_between_requests"])
            while True:
                rnd_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                save_dir = os.path.join(self.config["parse"]["save_dir"], rnd_id)
                if os.path.exists(save_dir):
                    continue
                else:
                    break
            try:
                msg = await wait_bot_response(self)
                is_promo, reply = check_promoting(self, msg)
                if is_promo:
                    logger.warning(f"Скип рекламы - {msg}")
                    await send_reply(self, reply)
                    continue
                photo_msgs, video_msgs = await get_bot_response_media(self)
                self.all_forms += 1
                await update_stat(self)
                form = parse_form(msg)
                form_string = f"{form.name} | {form.age}{f' | {form.about}' if form.about != '' else ''}"
                safe_name = re.sub(r'[^\w_. -]', '', form.name)
                rnd_id = f"{safe_name}_{form.age}_{rnd_id}"
                md5, sha256, raw = hash_form_result(form)
                if form.about != "":
                    if md5 in self.hash_list:
                        logger.error(f"Скип анкеты - Дубликат | {form_string}")
                        await skip_form(self)
                        self.skipped_forms += 1
                        continue
                    self.hash_list.append(md5)
                age, good = check_age(self, form.age, form.about)
                if not good:
                    logger.error(f"Скип анкеты - Возраст - {age} | {form_string}")
                    await skip_form(self)
                    self.skipped_forms += 1
                    continue
                about_len, good = check_about_len(self, form.about)
                if not good:
                    logger.error(f"Скип анкеты - Длина описания - {about_len} символов | {form_string}")
                    await skip_form(self)
                    self.skipped_forms += 1
                    continue
                banword, good = check_about_banwords(self, form.about)
                if not good:
                    logger.error(f"Скип анкеты - Банворд в описание - {banword} | {form_string}")
                    await skip_form(self)
                    self.skipped_forms += 1
                    continue
                save_task = asyncio.create_task(save_form(self, form, rnd_id, photo_msgs, video_msgs, None))
                await save_task
                logger.success(form_string)
            except Exception as e:
                logger.error(f"Ошибка парсинга анкеты: {msg} - {e}")
            await skip_form(self)

    async def search_cycle(self):
        msg = ""
        while True:
            await asyncio.sleep(self.config["telegram"]["delay_between_requests"])
            try:
                msg = await wait_bot_response(self)
                is_promo, reply = check_promoting(self, msg)
                if is_promo:
                    logger.warning(f"Скип рекламы - {msg}")
                    await send_reply(self, reply)
                    continue
                self.all_forms += 1
                await update_stat(self)
                form = parse_form(msg)
                form_string = f"{form.name} | {form.age}{f' | {form.about}' if form.about != '' else ''}"
                age, good = check_age(self, form.age, form.about)
                if not good:
                    logger.error(f"Скип анкеты - Возраст - {age} | {form_string}")
                    await skip_form(self)
                    self.skipped_forms += 1
                    continue
                about_len, good = check_about_len(self, form.about)
                if not good:
                    logger.error(f"Скип анкеты - Длина описания - {about_len} символов | {form_string}")
                    await skip_form(self)
                    self.skipped_forms += 1
                    continue
                banword, good = check_about_banwords(self, form.about)
                if not good:
                    logger.error(f"Скип анкеты - Банворд в описание - {banword} | {form_string}")
                    await skip_form(self)
                    self.skipped_forms += 1
                    continue
                photo_msgs, video_msgs = await get_bot_response_media(self)
                # Показываем форму и ждем действие пользователя
                await self.show_form(form, photo_msgs, video_msgs)
            except Exception as e:
                logger.error(f"Ошибка парсинга анкеты: {msg} - {e}")
                await skip_form(self)

    async def show_form(self, form, photo_msgs=None, video_msgs=None):
        logger.success("")
        logger.success("Подходящая анкета найдена")
        logger.success(f"Имя: {form.name}")
        logger.success(f"Возраст: {form.age}")
        logger.success(f"О себе: {form.about}")
        logger.success("")
        
        # Уведомляем пользователя если включено
        if self.config["search"]["forms"]["notify"]["enabled"]:
            notify(self)
        
        # Если включен мониторинг действий пользователя
        if self.config["search"]["auto_continue"]["monitor_user_actions"]:
            logger.success("Ожидание действия пользователя в Telegram...")
            
            # Ждем действие пользователя в Telegram
            user_liked = await wait_user_action(self)
            
            if user_liked:
                logger.success("Пользователь лайкнул анкету!")
                
                # Сохраняем анкету если разрешено в конфиге
                if self.config["search"]["allow_save"] and photo_msgs is not None and video_msgs is not None:
                    safe_name = re.sub(r'[^\w_. -]', '', form.name)
                    rnd_id = f"{safe_name}_{form.age}_{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}"
                    await save_form(self, form, rnd_id, photo_msgs, video_msgs, None)
                    logger.success("Анкета сохранена!")
                
                self.suitable_forms += 1
            else:
                logger.info("Пользователь пропустил анкету")
                self.skipped_forms += 1
            
            await update_stat(self)
            logger.info("Продолжаем поиск...")
        else:
            # Режим без мониторинга - показываем анкету и ждем ручного действия пользователя
            logger.success("Анкета показана. Примите решение в Telegram вручную.")
            logger.info("Нажмите Enter для продолжения после того, как примете решение в Telegram...")
            
            # Ждем ввод от пользователя в консоли
            input()
            
            # Сохраняем анкету если разрешено в конфиге
            if self.config["search"]["allow_save"] and photo_msgs is not None and video_msgs is not None:
                safe_name = re.sub(r'[^\w_. -]', '', form.name)
                rnd_id = f"{safe_name}_{form.age}_{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}"
                await save_form(self, form, rnd_id, photo_msgs, video_msgs, None)
                logger.success("Анкета сохранена!")
            
            self.suitable_forms += 1
            await update_stat(self)
            logger.info("Продолжаем поиск...")
            # НЕ вызываем skip_form() - пользователь сам принял решение в Telegram
