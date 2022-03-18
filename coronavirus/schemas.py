#coding=utf-8
from datetime import datetime
from datetime import date as date_
from pydantic import BaseModel

class CreateData(BaseModel):
    date  : date_
    confirmed : int=0
    deaths : int = 0
    recovered:int = 0

class CreateCity(BaseModel):
    province:str
    country:str
    country_code:str
    country_population:int



class ReadData(CreateData):
    id:int
    city_id:int
    updated_at:datetime
    cretaed_at:datetime
    class Config:
        orm_mode=True


class ReadCity(CreateCity):
    updated_at:datetime
    cretaed_at:datetime
    class Config:
        orm_mode=True

class CreateUser(BaseModel):
    username:str
    user:str
    phone:str
    sex:str = '未知'
    password:str


class ReadUser(CreateUser):
    id:int
    username :str
    user: str
    phone: str
    sex:str
    updated_at: datetime
    cretaed_at: datetime
    class Config:
        orm_mode=True

class Token(BaseModel):
    """返回给用户的Token"""
    access_token:str
    token_type:str