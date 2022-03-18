#coding = UTF-8
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List,Optional
app = FastAPI()

class CityInfo(BaseModel):
    province:str
    country:str
    is_affected:Optional[bool]=None

@app.get('/')
async def fastapi_test():
    return {"code": "200","success": "true"}

@app.get('/city/{city}')
async def result(city:str,name:Optional[str]=None,query_string:Optional[str]=None):
    return {'city':city,'name':name,'query_string':query_string}

@app.put('/city/{city}')
async def result(city:str,city_info:CityInfo):
    return {'city':city,'country':city_info.country,'is_affected':city_info.is_affected,'province':city_info.province}


 #启动命令：uvicorn 文件名 :app --reload
