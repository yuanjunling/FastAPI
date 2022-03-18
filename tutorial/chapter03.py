#coding=utf-8
from enum import Enum
from typing import Optional,List
from pydantic import BaseModel,Field#请求体效验用Field
from datetime import date
from fastapi import APIRouter,Path,Query,Cookie,Header #路径参数效验用Path，查询参数效验Query
app03 = APIRouter()

"""Path Parameters and Number Validations 路径参数和数字验证"""
#函数顺序就是路由顺序
@app03.get("/path/parameters")
async def path_params01():
    return {"message":"This is a message"}

@app03.get("/path/{parameters}")
async def path_params01(parameters:str):
    return {"message":parameters}


class CityName(Enum):
    Bejjing = "beijing China"
    Shanghai = "Shanghai China"

@app03.get("/enum/{city}")#枚举类型参数
async def latest(city:CityName):
    if city == CityName.Shanghai:
        return {"city_name":city,"confirmed":1492,"death":7}
    elif city == CityName.Bejjing:
        return {"city_name":city,"confirmed":1588,"death":17}
    else:
        return {"city_name":city,"latest":"unknown"}

@app03.get("/files/{file_path:path}",summary="总结")#通过path parameters传递文件路径
async def filepath(file_path:str):
    return f"The file path is: {file_path}"


@app03.get("/path_test/{num}")
async def path_params_validate(num: int = Path(None,title="Your number",description="不可描述",ge=1,le=10)):
    return num


"""Query Parameters and String Validations 查询参数和字符串验证"""

@app03.get("/query")
def page_linit(page:int=1,limit:Optional[int]=None): #给了默认值就是选填参数
    if limit:
        return {"page":page,"limit":limit}
    else:
        return {"page":page}

@app03.get("/query/bool/conversion")
def type_conversion(param:Optional[bool]=False):#bool类型转换：yes on 1 True
    return {"param":param}

@app03.get("/query/validations")
def query_params_validate(
        value:str=Query(...,min_length=8,max_length=16,regex="^a"),
        values:List[str]=Query(default=["v1","v2","v3"],alias="alias_name")
):#多个查询参数的列表，参数别名
    return {"value":value,"values":values}



"""Request Body and Fields 请求体和字段"""

class CityInfo(BaseModel):
    name:str = Field(...,description='名称')
    country:str
    country_code:Optional[str]=None
    country_population:int=Field(default=800,title="人口数量",description="国家的人口数量",ge=800)
    class Config:
        schema_extra = {
            "example":{
                "name":"Shanghai",
                "country":"China",
                "country_code":"CN",
                "country_population":1400000000
            }
        }


@app03.post("/request_body/city")
def city_info(city:CityInfo):
    print(city.name,city.country)
    return city.dict()

"""Request Body + Path parameters +Query Parameters 多参数混合"""

@app03.put("/request_body/city/{name}")
async def mix_city_info(
        name:str,
        city01:CityInfo,
        city02:CityInfo, #Body 可以定义多个
        confirmed:int = Query(ge=0,description="确诊数",default=0),
        death:int = Query(ge=0,description="死亡人数",default=0)
):
    if name=="shanghai":
        return {
            "Shanghai":{
                "confirmed":confirmed,
                "death":death
            }
        }
    else:
        return city01.dict(),city02.dict()


"""Request Body - Nested Models 数据格式嵌套的请求体"""

class Data(BaseModel):
    city: List[CityInfo]=None #这里就是定义数据格式嵌套的请求体
    date:date #额外的数据类型
    confirmed: int = Field(ge=0, description="确诊数", default=0)
    death: int = Field(ge=0, description="死亡人数", default=0)
    recovered: int = Field(ge=0,description="痊愈数",default=0)


@app03.put("/request_body/nested")
def nested_models(data:Data):
    return data.dict()


"""Cookie 和 Header 参数"""
@app03.get("/cookie")
def cookie(cookie_id:Optional[str]=Cookie(None)):
    return {"cookie_id":cookie_id}

@app03.get("/header")
def header(

        user_agent:Optional[str]=Header(None,convert_underscores=True),
        x_token:List[str]=Header(None,convert_underscores=True)
):
    """注释"""
    return {
        "User_Agent":user_agent,
        "x_token":x_token
    }