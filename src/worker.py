import re
import time

from loguru import logger
from win10toast import ToastNotifier

from src.configs import load_configs
from src.telegram import check_tg_account, send_reply, skip_form, wait_bot_response
from src.utils import notify, update_stat
from src.validators import check_about_banwords, check_about_len, check_age, check_promoting


class DVWorker:
    def __init__(self):
        self.bot_name = "leomatchbot"  # Тег бота
        self.client = None  # Клиент тг
        self.toast = ToastNotifier()  # Уведомления

        self.skipped_forms = 0  # Скип
        self.suitable_forms = 0  # Подходящие
        self.all_forms = 0  # Все

        self.config = { }  # Общий конфиг
        self.banwords = []  # Слова для скипа
        self.promotings = []  # Рекламные сообщения

        self.viewed_forms_list = []  # Хеши просмотренных анкет

    async def run(self):
        logger.info("Запуск QueVinchik...")

        await load_configs(self)
        await check_tg_account(self)
        await update_stat(self)

        logger.success("QueVinchik запущен")

        await worker_cycle(self)


async def worker_cycle(self):
    msg = ""

    while True:
        time.sleep(self.config["telegram"]["delay_between_requests"])

        #try:
        msg = await wait_bot_response(self)

        # Чекаем рекламу
        is_promo, reply = check_promoting(self, msg)
        if is_promo:
            logger.warning(f"Скип рекламы - {msg}")
            await send_reply(self, reply)
            continue

        self.all_forms += 1
        await update_stat(self)

        # Парсим анкету
        form = parse_form(msg)
        form_string = f"{form.name} | {form.age}{f" | {form.about}" if form.about != "" else ""}" # <3.11 пайтон сосатьб

        # Возраст
        age, good = check_age(self, form.age, form.about)
        if not good:
            logger.error(f"Скип анкеты - Возраст - {age} | {form_string}")
            await skip_form(self)
            self.skipped_forms += 1
            continue

        # Длина о себе
        about_len, good = check_about_len(self, form.about)
        if not good:
            logger.error(f"Скип анкеты - Длина описания - {about_len} символов | {form_string}")
            await skip_form(self)
            self.skipped_forms += 1
            continue

        # Банворды
        banword, good = check_about_banwords(self, form.about)
        if not good:
            logger.error(f"Скип анкеты - Банворд в описание - {banword} | {form_string}")
            await skip_form(self)
            self.skipped_forms += 1
            continue

        self.suitable_forms += 1
        notify(self)
        await show_form(self, form)

        #except Exception as e:
        #    logger.error(f"Ошибка парсинга анкеты: {msg} - {e}")
        #    await skip_form(self)
        #    continue


class Form:
    def __init__(self, name, age, about):
        self.name = name
        self.age = age
        self.about = about


def parse_form(text):
    name = re.findall(r"([\s\S]+),\s\d{2},", text)[0].strip()
    age = re.findall(r"[\s\S]+,\s(\d{2}),", text)[0].strip()
    about = re.findall(r"[\s\S]+?,\s\d{2},\s[\s\S]+?\s–\s([\s\S]+)", text)
    if len(about) == 0:
        about = ""
    else:
        about = about[0].strip().replace("\n", ". ").capitalize()

    return Form(name=name, age=age, about=about)


async def show_form(self, form):
    logger.success("")
    logger.success("Подходящая анкета найдена")
    logger.success(f"Имя: {form.name}")
    logger.success(f"Возраст: {form.age}")
    logger.success(f"О себе: {form.about}")
    logger.success("")
    logger.success("Нажмите Enter для пропуска")
    input("")
    self.skipped_forms += 1
    await skip_form(self)
