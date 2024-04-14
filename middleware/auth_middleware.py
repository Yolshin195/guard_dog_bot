from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from settings import BOT_USER_ID


class AuthMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id != BOT_USER_ID:
            # Логика обработки для неавторизованных пользователей
            print(f"Доступ запрещен для пользователя с ID {event.from_user.id}")
            return  # Прерываем обработку, не вызывая handler
        return await handler(event, data)
