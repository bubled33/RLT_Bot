import asyncio

from aiogram import Bot, Dispatcher

from config import Config
from database import init_database
from handlers import router
from contextlib import suppress


async def main():
    config = Config('settings.toml')

    bot = Bot(token=config['Bot']['token'])
    dispatcher = Dispatcher()

    dispatcher.include_router(router)

    await init_database(config=config)

    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
