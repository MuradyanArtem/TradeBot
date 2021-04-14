import os

import aiogram

from . import app, modules


HTTP_TIMEOUT = 3


tg_token: str = os.getenv("TELEGRAM_TOKEN")
if not tg_token:
    print("Need to set TELEGRAM_TOKEN env")
    exit(1)


api_url: str = os.getenv("API_URL")
if not api_url:
    print("Need to set API_URL env")
    exit(1)


dispatcher: aiogram.Dispatcher = aiogram.Dispatcher(aiogram.Bot(tg_token))
application: app.Application = app.Application(
    modules.TradeClient(api_url, HTTP_TIMEOUT),
    modules.Auth(),
    modules.Template(),
    modules.Scheme(),
)


@dispatcher.message_handler(commands=["start", "help"])
async def usage(msg: aiogram.types.Message) -> None:
    await msg.answer(application.usage)


@dispatcher.message_handler(commands=["transaction"])
async def transaction(msg: aiogram.types.Message) -> None:
    await msg.answer(
        await application.transaction(msg["from"]["username"], msg["text"])
    )


@dispatcher.message_handler(commands=["register"])
async def register(msg: aiogram.types.Message) -> None:
    await msg.answer(await application.register(msg["from"]["username"], msg["text"]))


@dispatcher.message_handler(commands=["wallet"])
async def get_wallet(msg: aiogram.types.Message) -> None:
    await msg.answer(await application.get_wallet(msg["from"]["username"]))


@dispatcher.message_handler(commands=["login"])
async def login(msg: aiogram.types.Message) -> None:
    await msg.answer(await application.login(msg["from"]["username"], msg["text"]))


@dispatcher.message_handler(commands=["logout"])
async def logout(msg: aiogram.types.Message) -> None:
    await msg.answer(await application.logout(msg["from"]["username"]))


if __name__ == "__main__":
    aiogram.executor.start_polling(dispatcher, skip_updates=True)
