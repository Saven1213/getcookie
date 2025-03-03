from aiogram import Bot, Dispatcher
import asyncio
from Key import KEY
import logging
from handlers import router


async def main():
    bot = Bot(token=KEY)
    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    except:
        await dp.stop_polling()
        await bot.session.close()



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())