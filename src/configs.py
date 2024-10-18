import json
import sys

from loguru import logger


def read_file_to_list(path) -> list:
    logger.info(f"Загрузка конфига из {path}")
    try:
        with open(path, mode="r", encoding="utf-8", errors="ignore") as f:
            return list(set([line.strip().lower() for line in f.readlines() if not line.startswith("#")]))
    except Exception as e:
        logger.error(f"Ошибка загрузки конфига из {path}: {e}")
        return []


def read_json(path) -> dict:
    # Я ебу Алибабу валидируй головой сам
    logger.info(f"Загрузка конфига из {path}")
    try:
        with open(path, mode="r", encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Ошибка загрузки конфига из {path}: {e}")
        input()
        sys.exit()


async def load_configs(self) -> None:
    self.banwords = read_file_to_list("configs/banwords.txt")
    self.promotings = read_file_to_list("configs/promotings.txt")
    self.config = read_json("configs/main_config.json")
