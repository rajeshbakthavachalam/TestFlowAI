import redis
import json
from typing import Optional
from src.test_pilot.state.sdlc_state import CustomEncoder, SDLCState
from upstash_redis import Redis
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


# Initialize Redis client

## Upstash Redis Client Configuraion
# REDIS_URL = os.getenv("REDIS_URL")
# REDIS_TOKEN = os.getenv("REDIS_TOKEN")
# redis_client = redis = Redis(url=REDIS_URL, token=REDIS_TOKEN)

## For testing locally with docker
redis_client = redis.Redis(
    host='localhost',  # Replace with your Redis host
    port=6379,         # Replace with your Redis port
    db=0               # Replace with your Redis database number
)

def save_state_to_redis(task_id: str, state: SDLCState):
    """Save the state to Redis."""
    state = json.dumps(state, cls=CustomEncoder)
    redis_client.set(task_id, state)

    # Set expiration for 24 hours
    redis_client.expire(task_id, 86400)

def get_state_from_redis(task_id: str) -> Optional[SDLCState]:
    """ Retrieves the state from redis """
    state_json = redis_client.get(task_id)
    if not state_json:
        return None
    
    state_dict = json.loads(state_json)[0]
    return SDLCState(**state_dict)

def delete_from_redis(task_id: str):
    """ Delete from redis """
    redis_client.delete(task_id)

def flush_redis_cache():
    """ Flushes the whole cache"""

    # Clear all keys in all databases
    redis_client.flushall()

    logger.info("--- Redis cache cleared ---")