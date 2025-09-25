from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class FilmModel(BaseModel):
    """Model for Star Wars film data"""
    episode_id: int = Field(..., description="Episode number of the film")
    title: str = Field(..., description="Title of the film")
    director: str = Field(..., description="Director of the film")
    producer: str = Field(..., description="Producer(s) of the film")
    release_date: str = Field(..., description="Release date of the film")
    opening_crawl: str = Field(..., description="Opening crawl text (truncated)")
    character_count: int = Field(..., description="Number of characters in the film")
    starship_count: int = Field(..., description="Number of starships in the film")
    planet_count: int = Field(..., description="Number of planets in the film")
    vehicle_count: int = Field(..., description="Number of vehicles in the film")
    species_count: int = Field(..., description="Number of species in the film")
    url: str = Field(..., description="SWAPI URL for this film")
    created: str = Field(..., description="Creation timestamp")
    edited: str = Field(..., description="Last edit timestamp")

class CharacterModel(BaseModel):
    """Model for Star Wars character data"""
    name: str = Field(..., description="Name of the character")
    height: str = Field(..., description="Height of the character")
    mass: str = Field(..., description="Mass of the character")
    hair_color: str = Field(..., description="Hair color of the character")
    skin_color: str = Field(..., description="Skin color of the character")
    eye_color: str = Field(..., description="Eye color of the character")
    birth_year: str = Field(..., description="Birth year of the character")
    gender: str = Field(..., description="Gender of the character")
    homeworld_url: str = Field(..., description="URL of the character's homeworld")
    film_count: int = Field(..., description="Number of films the character appears in")
    starship_count: int = Field(..., description="Number of starships piloted by the character")
    vehicle_count: int = Field(..., description="Number of vehicles used by the character")
    species_count: int = Field(..., description="Number of species the character belongs to")
    url: str = Field(..., description="SWAPI URL for this character")
    created: str = Field(..., description="Creation timestamp")
    edited: str = Field(..., description="Last edit timestamp")

class StarshipModel(BaseModel):
    """Model for Star Wars starship data"""
    name: str = Field(..., description="Name of the starship")
    model: str = Field(..., description="Model of the starship")
    manufacturer: str = Field(..., description="Manufacturer of the starship")
    cost_in_credits: str = Field(..., description="Cost of the starship in credits")
    length: str = Field(..., description="Length of the starship")
    max_atmosphering_speed: str = Field(..., description="Maximum atmospheric speed")
    crew: str = Field(..., description="Required crew size")
    passengers: str = Field(..., description="Passenger capacity")
    cargo_capacity: str = Field(..., description="Cargo capacity")
    consumables: str = Field(..., description="Duration of consumables")
    hyperdrive_rating: str = Field(..., description="Hyperdrive class rating")
    MGLT: str = Field(..., description="Speed in megalights per hour")
    starship_class: str = Field(..., description="Class of the starship")
    pilot_count: int = Field(..., description="Number of known pilots")
    film_count: int = Field(..., description="Number of films the starship appears in")
    url: str = Field(..., description="SWAPI URL for this starship")
    created: str = Field(..., description="Creation timestamp")
    edited: str = Field(..., description="Last edit timestamp")

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    count: int = Field(..., description="Number of items returned")
    message: str = Field(..., description="Response message")

class FilmListResponse(BaseResponse):
    """Response model for films endpoint"""
    results: List[FilmModel] = Field(..., description="List of Star Wars films")
    
    class Config:
        schema_extra = {
            "example": {
                "count": 6,
                "message": "Successfully retrieved all films",
                "results": [
                    {
                        "episode_id": 4,
                        "title": "A New Hope",
                        "director": "George Lucas",
                        "producer": "Gary Kurtz, Rick McCallum",
                        "release_date": "1977-05-25",
                        "opening_crawl": "It is a period of civil war...",
                        "character_count": 18,
                        "starship_count": 8,
                        "planet_count": 3,
                        "vehicle_count": 4,
                        "species_count": 5,
                        "url": "https://swapi.dev/api/films/1/",
                        "created": "2014-12-10T14:23:31.880000Z",
                        "edited": "2014-12-20T19:49:45.256000Z"
                    }
                ]
            }
        }

class CharacterListResponse(BaseResponse):
    """Response model for characters endpoint"""
    results: List[CharacterModel] = Field(..., description="List of characters from the film")
    film_id: int = Field(..., description="ID of the film these characters are from")
    
    class Config:
        schema_extra = {
            "example": {
                "count": 3,
                "film_id": 1,
                "message": "Successfully retrieved characters for film 1",
                "results": [
                    {
                        "name": "Luke Skywalker",
                        "height": "172",
                        "mass": "77",
                        "hair_color": "blond",
                        "skin_color": "fair",
                        "eye_color": "blue",
                        "birth_year": "19BBY",
                        "gender": "male",
                        "homeworld_url": "https://swapi.dev/api/planets/1/",
                        "film_count": 4,
                        "starship_count": 2,
                        "vehicle_count": 2,
                        "species_count": 1,
                        "url": "https://swapi.dev/api/people/1/",
                        "created": "2014-12-09T13:50:51.644000Z",
                        "edited": "2014-12-20T21:17:56.891000Z"
                    }
                ]
            }
        }

class StarshipListResponse(BaseResponse):
    """Response model for starships endpoint"""
    results: List[StarshipModel] = Field(..., description="List of starships from the film")
    film_id: int = Field(..., description="ID of the film these starships are from")
    
    class Config:
        schema_extra = {
            "example": {
                "count": 2,
                "film_id": 1,
                "message": "Successfully retrieved starships for film 1",
                "results": [
                    {
                        "name": "X-wing",
                        "model": "T-65 X-wing",
                        "manufacturer": "Incom Corporation",
                        "cost_in_credits": "149999",
                        "length": "12.5",
                        "max_atmosphering_speed": "1050",
                        "crew": "1",
                        "passengers": "0",
                        "cargo_capacity": "110",
                        "consumables": "1 week",
                        "hyperdrive_rating": "1.0",
                        "MGLT": "100",
                        "starship_class": "Starfighter",
                        "pilot_count": 4,
                        "film_count": 3,
                        "url": "https://swapi.dev/api/starships/12/",
                        "created": "2014-12-12T11:19:05.340000Z",
                        "edited": "2014-12-20T21:23:49.886000Z"
                    }
                ]
            }
        }

class ErrorResponse(BaseModel):
    """Response model for errors"""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(..., description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Film with ID 99 not found",
                "status_code": 404,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }