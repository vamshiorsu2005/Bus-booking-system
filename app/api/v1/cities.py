from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import APIRouter
from app.schemas.cities import CityResponse,CityCreate
router=APIRouter()

cities = [
    {"id": 1, "name": "Hyderabad", "state": "Telangana"},
    {"id": 2, "name": "Bangalore", "state": "Karnataka"},
    {"id": 3, "name": "Chennai", "state": "Tamil Nadu"},
    {"id": 4, "name": "Mumbai", "state": "Maharashtra"}
]

@router.get("/{city_id}")
async def get_city_by_id(city_id:int):
    for city in cities:
        if city["id"]==city_id:
            return city
    raise HTTPException(
         status_code=404,
         detail="City Not found"
    )

@router.get("/")
async def get_city_by_state(state: str=None):
    if state == None:
         return cities
    filtered_cities=[]
    for city in cities:
            if city["state"]==state:
                filtered_cities.append(city)
    
    return filtered_cities

@router.post("/",response_model=CityResponse,status_code=201)
async def create_city(city:CityCreate):
     new_id = max(c["id"] for c in cities) + 1
     new_city={
          "id":new_id,
          "name":city.name,
          "state":city.state
     }
     cities.append(new_city)
     return new_city

     


