from pydantic import BaseModel,Field

class CityCreate(BaseModel):
    name:str=Field(min_length=2,max_length=50)
    state:str=Field(min_length=2,max_length=50)

class CityResponse(BaseModel):
    id:int
    name:str
    state:str