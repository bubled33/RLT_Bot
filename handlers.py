import json

from aiogram import Router
from aiogram.types import Message

from untils import from_json_format, aggregate_by

router = Router()


@router.message()
async def on_aggregate(message: Message):
    return await message.answer(json.dumps(await aggregate_by(**from_json_format(message.text)))
                                .replace(' ', ''))
