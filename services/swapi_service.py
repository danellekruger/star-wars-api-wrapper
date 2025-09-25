import httpx
import asyncio
from typing import List, Dict, Any
import logging
from services.cache_service import CacheService

logger = logging.getLogger(__name__)

class SWAPIService:
    """
    Service class for interacting with the Star Wars API (SWAPI)
    Provides caching, error handling, and data transformation capabilities
    """
    
    BASE_URL = "https://swapi.dev/api"
    TIMEOUT = 30.0
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.client = httpx.AsyncClient(timeout=self.TIMEOUT)
    
    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.get(f"{self.BASE_URL}/{endpoint}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ValueError(f"Resource not found: {endpoint}")
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                if attempt == max_retries - 1:
                    raise
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)  # Wait before retry
    
    async def _fetch_multiple_resources(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch multiple resources concurrently"""
        async def fetch_resource(url: str) -> Dict[str, Any]:
            # Extract endpoint from full URL
            endpoint = url.replace(f"{self.BASE_URL}/", "")
            return await self._make_request(endpoint)
        
        tasks = [fetch_resource(url) for url in urls]
        return await asyncio.gather(*tasks)
    
    async def get_films(self) -> List[Dict[str, Any]]:
        """
        Retrieve all Star Wars films with enhanced data
        Implements caching for optimal performance
        """
        cache_key = "films_all"
        
        # Try cache first
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            logger.info("📦 Retrieved films from cache")
            return cached_result
        
        logger.info("🌐 Fetching films from SWAPI...")
        
        try:
            data = await self._make_request("films/")
            films = data.get("results", [])
            
            # Enhance film data
            enhanced_films = []
            for film in films:
                enhanced_film = {
                    "episode_id": film.get("episode_id"),
                    "title": film.get("title"),
                    "director": film.get("director"),
                    "producer": film.get("producer"),
                    "release_date": film.get("release_date"),
                    "opening_crawl": film.get("opening_crawl", "")[:200] + "...",  # Truncate for API response
                    "character_count": len(film.get("characters", [])),
                    "starship_count": len(film.get("starships", [])),
                    "planet_count": len(film.get("planets", [])),
                    "vehicle_count": len(film.get("vehicles", [])),
                    "species_count": len(film.get("species", [])),
                    "url": film.get("url"),
                    "created": film.get("created"),
                    "edited": film.get("edited")
                }
                enhanced_films.append(enhanced_film)
            
            # Sort by episode_id for consistent ordering
            enhanced_films.sort(key=lambda x: x["episode_id"])
            
            # Cache the result
            await self.cache_service.set(cache_key, enhanced_films)
            logger.info(f"✅ Retrieved and cached {len(enhanced_films)} films")
            
            return enhanced_films
            
        except Exception as e:
            logger.error(f"Failed to fetch films: {e}")
            raise
    
    async def get_film_characters(self, film_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all characters for a specific film
        """
        cache_key = f"film_{film_id}_characters"
        
        # Try cache first
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            logger.info(f"📦 Retrieved characters for film {film_id} from cache")
            return cached_result
        
        logger.info(f"🌐 Fetching characters for film {film_id} from SWAPI...")
        
        try:
            # First, get the film to extract character URLs
            film_data = await self._make_request(f"films/{film_id}/")
            character_urls = film_data.get("characters", [])
            
            if not character_urls:
                return []
            
            # Fetch all characters concurrently
            characters = await self._fetch_multiple_resources(character_urls)
            
            # Enhance character data
            enhanced_characters = []
            for character in characters:
                enhanced_character = {
                    "name": character.get("name"),
                    "height": character.get("height"),
                    "mass": character.get("mass"),
                    "hair_color": character.get("hair_color"),
                    "skin_color": character.get("skin_color"),
                    "eye_color": character.get("eye_color"),
                    "birth_year": character.get("birth_year"),
                    "gender": character.get("gender"),
                    "homeworld_url": character.get("homeworld"),
                    "film_count": len(character.get("films", [])),
                    "starship_count": len(character.get("starships", [])),
                    "vehicle_count": len(character.get("vehicles", [])),
                    "species_count": len(character.get("species", [])),
                    "url": character.get("url"),
                    "created": character.get("created"),
                    "edited": character.get("edited")
                }
                enhanced_characters.append(enhanced_character)
            
            # Sort by name for consistent ordering
            enhanced_characters.sort(key=lambda x: x["name"])
            
            # Cache the result
            await self.cache_service.set(cache_key, enhanced_characters)
            logger.info(f"✅ Retrieved and cached {len(enhanced_characters)} characters for film {film_id}")
            
            return enhanced_characters
            
        except ValueError:
            raise ValueError(f"Film with ID {film_id} not found")
        except Exception as e:
            logger.error(f"Failed to fetch characters for film {film_id}: {e}")
            raise
    
    async def get_film_starships(self, film_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all starships for a specific film
        """
        cache_key = f"film_{film_id}_starships"
        
        # Try cache first
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            logger.info(f"📦 Retrieved starships for film {film_id} from cache")
            return cached_result
        
        logger.info(f"🌐 Fetching starships for film {film_id} from SWAPI...")
        
        try:
            # First, get the film to extract starship URLs
            film_data = await self._make_request(f"films/{film_id}/")
            starship_urls = film_data.get("starships", [])
            
            if not starship_urls:
                return []
            
            # Fetch all starships concurrently
            starships = await self._fetch_multiple_resources(starship_urls)
            
            # Enhance starship data
            enhanced_starships = []
            for starship in starships:
                enhanced_starship = {
                    "name": starship.get("name"),
                    "model": starship.get("model"),
                    "manufacturer": starship.get("manufacturer"),
                    "cost_in_credits": starship.get("cost_in_credits"),
                    "length": starship.get("length"),
                    "max_atmosphering_speed": starship.get("max_atmosphering_speed"),
                    "crew": starship.get("crew"),
                    "passengers": starship.get("passengers"),
                    "cargo_capacity": starship.get("cargo_capacity"),
                    "consumables": starship.get("consumables"),
                    "hyperdrive_rating": starship.get("hyperdrive_rating"),
                    "MGLT": starship.get("MGLT"),
                    "starship_class": starship.get("starship_class"),
                    "pilot_count": len(starship.get("pilots", [])),
                    "film_count": len(starship.get("films", [])),
                    "url": starship.get("url"),
                    "created": starship.get("created"),
                    "edited": starship.get("edited")
                }
                enhanced_starships.append(enhanced_starship)
            
            # Sort by name for consistent ordering
            enhanced_starships.sort(key=lambda x: x["name"])
            
            # Cache the result
            await self.cache_service.set(cache_key, enhanced_starships)
            logger.info(f"✅ Retrieved and cached {len(enhanced_starships)} starships for film {film_id}")
            
            return enhanced_starships
            
        except ValueError:
            raise ValueError(f"Film with ID {film_id} not found")
        except Exception as e:
            logger.error(f"Failed to fetch starships for film {film_id}: {e}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()