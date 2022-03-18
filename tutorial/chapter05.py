#coding=utf-8
from typing import Optional,List
from fastapi import APIRouter, Header,Depends,HTTPException  # Depends 依赖
app05 = APIRouter()

"""Dependencies 创建，导入和声明依赖"""

async def common_parameters(q:Optional[str]=None,page:int=1,limit:int=15):
    return {"q":q,"page":page,"limit":limit}

@app05.get("/dependency01")
async def dependency01(commons:dict = Depends(common_parameters)):
    """Depends 依赖"""
    return commons

"""ClassES as Dependencies 类作为依赖项"""

fake_items_db = [{"item_name":"Foo"},{"item_name":"Foo2"},{"item_name":"Foo3"}]

class CommonQueryParams:

    def __init__(self,q:Optional[str]=None,page:int=1,limit:int=15):
        self.q=q
        self.page = page
        self.limit = limit

@app05.get("/classes_as_dependencies")
async def classes_as_dependencies1(commons:CommonQueryParams = Depends(CommonQueryParams)):
    return commons

@app05.get("/classes_as_dependencies2")
async def classes_as_dependencies2(commons:CommonQueryParams = Depends()):
    return commons

@app05.get("/classes_as_dependencies3")
async def classes_as_dependencies3(commons=Depends(CommonQueryParams)):
    response={}
    if commons.q:
        response.update({"q":commons.q})
        items = fake_items_db[commons.page:commons.page + commons.limit]
        response.update({"items":items})
    return response

"""Sub-dependencies 子依赖"""

def query(q:Optional[str]=None):
    return q

def sub_query(q:str = Depends(query),last_query:Optional[str]=None):
    if not q:
        return last_query
    else:
        return q

@app05.get("/sub_dependency")
async def sub_dependency(final_query:str = Depends(sub_query,use_cache=True)):
    return {"sub_dependency":final_query}


"""Dependencies in path operation decorators 路径操作装饰器中的多依赖"""

async def verify_token(x_token:str=Header(...)):
    """没有返回值的子依赖"""
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=500,detail="X-Token header invalid")
    else:
        return x_token


async def verify_key(x_key:str=Header(...)):
    """有返回值的子依赖，但是返回值不会被调用"""
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=500,detail="X-key header invalid")
    else:
        return x_key

@app05.get("/dependency_in_path_operation",dependencies=[Depends(verify_token),Depends(verify_key)])
async def dependency_in_path_operation():
    return [{"user":"user01"},{"user":"user02"}]


"""Global Dependencies 全局依赖"""

# app05 = APIRouter(dependencies=[Depends(verify_token),Depends(verify_key)])

"""Dependencies with yield 带yield的依赖"""

async def gen_db():
    db = "db_conneton"
    try:
        yield db
    finally:
        db.endswith("db_close")

async def dependncy_a():
    dep_a = "generate_dep_a()"
    try:
        yield dep_a
    finally:
        dep_a.endswith("db_close")

async def dependency_b(dep_a=Depends(dependncy_a)):
    dep_b="generate_dep_b()"
    try:
        yield dep_b
    finally:
        dep_b.endswith(dep_a)

async def dependency_c(dep_b=Depends(dependency_b)):
    dep_c="generate_dep_c()"
    try:
        yield dep_c
    finally:
        dep_c.endswith(dep_b)

