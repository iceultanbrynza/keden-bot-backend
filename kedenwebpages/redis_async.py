import os
import redis.asyncio as redis
from kedenbot.settings import (REDIS_HOST,
                               REDIS_PORT,
                               REDIS_PASSWORD)
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    decode_responses=True,
    username="default",
    password=REDIS_PASSWORD
)
