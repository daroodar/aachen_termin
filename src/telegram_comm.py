import asyncio
import os

from dotenv import load_dotenv
import telegram


async def send_telegram_message(text: str):
    bot = telegram.Bot(os.environ.get("TELEGRAM_TOKEN"))
    async with bot:
        print(
            await bot.send_message(
                text=text, chat_id=os.environ.get("TELEGRAM_CHAT_ID")
            )
        )


if __name__ == "__main__":
    load_dotenv()
    # Test
    asyncio.run(send_telegram_message("Hi, it's me!"))
