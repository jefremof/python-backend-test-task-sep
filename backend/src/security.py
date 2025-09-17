from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY")

if API_KEY is None:
    raise ValueError("API_KEY environment variable is not set.")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key is None or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to validate the api key",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
    return api_key

