import yaml
import sqlite3
from fastapi import HTTPException, Request, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Load API configuration
with open("configs/api_config.yaml", "r") as f:
    api_config = yaml.safe_load(f)

# Initialize SQLite database
conn = sqlite3.connect(api_config["auth"]["database_path"])
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        key TEXT PRIMARY KEY,
        user_id TEXT NOT NULL
    )
""")
conn.commit()

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Admin Key header
admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

# Rate limiting storage
rate_limit_storage: Dict[str, Dict[str, float]] = {}

def verify_api_key(api_key: str):
    if not api_config["auth"]["enabled"]:
        return True
    
    cursor.execute("SELECT user_id FROM api_keys WHERE key = ?", (api_key,))
    result = cursor.fetchone()
    return result is not None

def verify_admin_key(admin_key: str):
    return admin_key == api_config["auth"]["admin_key"]

def check_rate_limit(api_key: str):
    if not api_config["rate_limit"]["enabled"]:
        logger.debug("Rate limiting is disabled")
        return True
    
    current_time = time.time()
    user_limits = rate_limit_storage.get(api_key, {"requests": [], "last_reset": current_time})
    
    # Reset if it's been more than a minute
    if current_time - user_limits["last_reset"] > 60:
        logger.debug(f"Resetting rate limit for API key: {api_key}")
        user_limits["requests"] = []
        user_limits["last_reset"] = current_time
    
    # Remove requests older than 1 minute
    user_limits["requests"] = [t for t in user_limits["requests"] if current_time - t <= 60]
    
    # Check if user has exceeded rate limit
    if len(user_limits["requests"]) >= api_config["rate_limit"]["requests_per_minute"]:
        # Allow burst up to the burst limit
        if len(user_limits["requests"]) < api_config["rate_limit"]["burst_limit"]:
            logger.warning(f"Burst limit used for API key: {api_key}. Current request count: {len(user_limits['requests'])}")
        else:
            logger.warning(f"Rate limit exceeded for API key: {api_key}. Current request count: {len(user_limits['requests'])}")
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
    
    # Add current request timestamp
    user_limits["requests"].append(current_time)
    rate_limit_storage[api_key] = user_limits
    logger.debug(f"Current request count for API key {api_key}: {len(user_limits['requests'])}")
    return True

async def auth_middleware(request: Request, api_key: str = Depends(api_key_header)):
    if not api_key:
        logger.warning("API Key is missing")
        raise HTTPException(status_code=400, detail="API Key is missing")
    if not verify_api_key(api_key):
        logger.warning(f"Invalid API Key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    check_rate_limit(api_key)
    request.state.api_key = api_key

async def admin_auth_middleware(request: Request, admin_key: str = Depends(admin_key_header)):
    if not admin_key:
        logger.warning("Admin Key is missing")
        raise HTTPException(status_code=400, detail="Admin Key is missing")
    if not verify_admin_key(admin_key):
        logger.warning("Invalid Admin Key")
        raise HTTPException(status_code=403, detail="Invalid Admin Key")

def add_api_key_to_db(user_id: str, api_key: str):
    try:
        cursor.execute("INSERT INTO api_keys (key, user_id) VALUES (?, ?)", (api_key, user_id))
        conn.commit()
        logger.info(f"Added new API key for user: {user_id}")
    except sqlite3.IntegrityError:
        logger.warning(f"Attempted to add duplicate API key for user: {user_id}")
        raise HTTPException(status_code=400, detail="API key already exists")
    except Exception as e:
        logger.error(f"Error adding API key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding API key: {str(e)}")

def reset_rate_limit(api_key: str):
    if api_key in rate_limit_storage:
        logger.info(f"Manually resetting rate limit for API key: {api_key}")
        rate_limit_storage[api_key] = {"requests": [], "last_reset": time.time()}
    else:
        logger.warning(f"Attempted to reset rate limit for non-existent API key: {api_key}")