from datetime import datetime

from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient


class Payment(Document):
    value: int
    dt: datetime

    class Settings:
        name = 'sample_collection'


async def init_database(config):
    if config['MongoDB']['is_localhost']:

        client = AsyncIOMotorClient(f"mongodb://localhost:{config['MongoDB']['port']}")
    else:
        client = AsyncIOMotorClient(f'mongodb://{config["MongoDB"]["username"]}:{config["MongoDB"]["password"]}@{config["MongoDB"]["host"]}:{config["MongoDB"]["port"]}/{config["MongoDB"]["database"]}?authSource=admin&directConnection=true')
    await init_beanie(database=client[config['MongoDB']['database']], document_models=[Payment])
