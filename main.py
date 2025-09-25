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

# Setup for the rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize services from the services folder
cache_service = CacheService()
swapi_service = SWAPIService(cache_service)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Star Wars API Wrapper starting up...")
    yield
    # Shutdown
    logger.info("🛑 Star Wars API Wrapper shutting down...")
    await cache_service.close()

# Create FastAPI app with enhanced metadata
app = FastAPI(
    title="Star Wars API Wrapper",
    description="""
    An outstanding API wrapper for the Star Wars API (SWAPI) with advanced caching, 
    rate limiting, and comprehensive error handling.
    
    ## Features
    * ⚡ Lightning-fast response times with intelligent caching
    * 🛡️ Built-in rate limiting and error handling
    * 📊 Automatic API documentation
    * 🚀 Async processing for optimal performance
    """,
    version="1.0.0",
    contact={
        "name": "Danelle Kruger",
        "email": "kruger.danelle2829@gmail.com",
    },
    license_info={
        "name": "dkSWAPI",
    },
    lifespan=lifespan
)

# Add CORS middleware, security mechanism for FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "🌟 Welcome to the Star Wars API Wrapper!",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "films": "/films",
            "film_characters": "/films/{id}/characters",
            "film_starships": "/films/{id}/starships"
        },
        "may_the_force_be_with_you": True
    }

@app.get("/films", response_model=FilmListResponse, tags=["Films"])
@limiter.limit("30/minute")
async def get_films(request: Request = None):
    """
    🎬 Retrieve all Star Wars films
    
    Returns a comprehensive list of all Star Wars films with detailed information
    including title, episode number, director, release date, and more.
    """
    try:
        films = await swapi_service.get_films()
        return FilmListResponse(
            count=len(films),
            results=films,
            message="Successfully retrieved all films"
        )
    except Exception as e:
        logger.error(f"Error fetching films: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve films")

@app.get("/films/{film_id}/characters", response_model=CharacterListResponse, tags=["Characters"])
@limiter.limit("30/minute")
async def get_film_characters(film_id: int, request: Request = None):
    """
    👥 Retrieve all characters from a specific film
    
    Get detailed information about all characters that appeared in the specified film,
    including their names, species, homeworld, and other character details.
    """
    try:
        characters = await swapi_service.get_film_characters(film_id)
        return CharacterListResponse(
            count=len(characters),
            results=characters,
            film_id=film_id,
            message=f"Successfully retrieved characters for film {film_id}"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching characters for film {film_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve characters")

@app.get("/films/{film_id}/starships", response_model=StarshipListResponse, tags=["Starships"])
@limiter.limit("30/minute")
async def get_film_starships(film_id: int, request: Request = None):
    """
    🚀 Retrieve all starships from a specific film
    
    Get comprehensive information about all starships that appeared in the specified film,
    including technical specifications, crew capacity, and performance metrics.
    """
    try:
        starships = await swapi_service.get_film_starships(film_id)
        return StarshipListResponse(
            count=len(starships),
            results=starships,
            film_id=film_id,
            message=f"Successfully retrieved starships for film {film_id}"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching starships for film {film_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve starships")

@app.get("/health", tags=["System"])
async def health_check():
    """🏥 Health check endpoint"""
    cache_status = await cache_service.health_check()
    return {
        "status": "healthy",
        "cache": cache_status,
        "timestamp": cache_service.get_current_time()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )