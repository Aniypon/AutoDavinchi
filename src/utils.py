import hashlib
import os
import random
import string
import subprocess
import sys
import json

from loguru import logger


async def update_stat(self):
    try:
        os.system(f'title "QueVinchik - Подходящие {self.suitable_forms} | Скип {self.skipped_forms} | Всего {self.all_forms}"')
    except:
        pass


def notify(self):
    if self.config["search"]["notify"]["move_on_top"]:
        try:
            process = subprocess.Popen(["xdotool", "getactivewindow"], stdout=subprocess.PIPE)
            window_id, _ = process.communicate()
            subprocess.Popen(["wmctrl", "-i", "-r", window_id.strip(), "-b", "add,above"])
        except:
            pass


def setup_logger():
    logger.add(sys.stdout, colorize=True, enqueue=True, backtrace=True, diagnose=True)
    logger.remove(0)


def hash_form_result(form):
    # Генерирует MD5 и SHA256 хеши для анкеты
    raw = f"{form.age}{form.name}{form.about}"
    md5 = hashlib.md5(raw.encode()).hexdigest()
    sha256 = hashlib.sha256(raw.encode()).hexdigest()
    return md5, sha256, raw


async def save_form(self, form, rnd_id, photo_msgs, video_msgs, _):
    try:
        save_dir = os.path.join(self.config["parse"]["save_dir"], rnd_id)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # Сохраняем текстовое описание
        desc_path = os.path.join(save_dir, "desc.txt")
        with open(desc_path, "w", errors="ignore", encoding="utf-8") as f:
            f.write(f"Имя: {form.name}\nВозраст: {form.age}\nО себе: {form.about}")
        # Считаем хеши и исходную строку
        md5, sha256, raw = hash_form_result(form)
        # Сохраняем md5 для обратной совместимости
        hash_path = os.path.join(save_dir, "hash.txt")
        with open(hash_path, "w", errors="ignore", encoding="utf-8") as f:
            f.write(md5)
        # Сохраняем все данные анкеты в JSON
        json_path = os.path.join(save_dir, "form.json")
        data = {
            "raw": raw,  # Исходная строка для хеширования
            "name": form.name,
            "age": form.age,
            "about": form.about,
            "md5": md5,
            "sha256": sha256
        }
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, indent=2)
        # Сохраняем все медиафайлы
        for msg in photo_msgs:
            filename = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4)) + ".jpg"
            await msg.download_media(os.path.join(save_dir, filename))
        for msg in video_msgs:
            filename = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4)) + ".mp4"
            await msg.download_media(os.path.join(save_dir, filename))
    except Exception as e:
        logger.error(f"Save form error: {e}")
