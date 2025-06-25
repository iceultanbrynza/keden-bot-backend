import os
import redis.asyncio as redis

redis_client = redis.Redis(
    host=os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'],
    decode_responses=True,
    username="default",
    password=os.environ['REDIS_PASSWORD']
)
