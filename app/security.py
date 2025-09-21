# app/security.py
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth import get_current_user

# HTTP Bearer scheme for Swagger UI
bearer_scheme = HTTPBearer(description="Paste your JWT token here, starting with 'Bearer '")

# Dependency for routes
async def get_current_user_from_bearer(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    token = credentials.credentials  # raw JWT
    return await get_current_user(token)
