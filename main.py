from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
from services.swapi_service import SWAPIService
from services.cache_service import CacheService
from models.responses import FilmListResponse, CharacterListResponse, StarshipListResponse
import logging
from contextlib import asynccontextmanager

# Logging needs to be configurated
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)