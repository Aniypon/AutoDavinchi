import asyncio
import sys

from src.utils import setup_logger
from src.worker import DVWorker


async def main():
    await DVWorker().run()


if __name__ == '__main__':
    try:
        setup_logger()
        asyncio.run(main())
    except Exception as e:
        input(f"Глобальная ошибка: {e}")
        sys.exit()
