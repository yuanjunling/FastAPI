#coding=utf-8
from enum import Enum
from typing import Optional,List,Union
from pydantic import BaseModel,EmailStr,Field#请求体效验用Field
from datetime import date
from fastapi import APIRouter,Path,Query,Cookie,Header,status,Form,File,UploadFile,HTTPException#路径参数效验用Patj，查询参数效验Query


app04 = APIRouter()


"""Response Model 响应模型"""


class UserIn(BaseModel):
    username:str
    password:str
    email:EmailStr
    mobile:str="10086"
    address:str=None
    full_name:Optional[str] = None
    s_out: str = None

class UserOut(BaseModel):
    username: str
    email: EmailStr  #EmailStr 需要pip install pydantic[email]
    mobile: str = "10086"
    address: str = None
    full_name: Optional[str] = None


users = {
    "user01":{"username":"user01","password":"123456","email":"user01@qq.com"},
    "user02":{"username":"user02","password":"123456","email":"user02@qq.com","mobile":"110","s_out":"abc"}
}

@app04.post("/response_model",response_model=UserOut,response_model_exclude_unset=False)
async def resopnse_model(user:UserIn):
    print(user.password)
    return users["user02"]

@app04.post(
    "/response_model/attributes",response_model=Union[UserIn,UserOut],
    #response_model=List[UserOut]
    # response_model_include = ["username"],  #一点要返回的数据
    response_model_exclude = ["mobile"] #不需要返回的数据
) #Union 联合数据
async def reponse_model_attributes(user:UserIn):
    """response_model_include 列出需要在返回结果中包含的字段
       response_model_exclude 列出需要在返回结果中排除的字段
    """
    del user.password
    return user
    # return [user,user]


"""Response Status Code 响应状态码"""

@app04.post("/status_code",status_code=200)
async def status_code():
    return {"status_code":200}

@app04.post("/status_codes",status_code=status.HTTP_200_OK)
async def status_attribute():
    print(type(status.HTTP_200_OK))
    return {"status_code":status.HTTP_200_OK}


"""Form Data 表单数据处理"""
@app04.post("/login")
async def login(user:str=Form(...),password:str=Form(...)):#定义表单参数
    """用Form类需要pip install python-multipart"""
    return {"username":user}

"""Request Files 单文件，多文件上传的参数详解"""
#单文件
@app04.post("/file")
async def file_(file:bytes = File(...)):
    """使用File类 文件内容会以bytes的形式读入内存，适合上传小文件"""
    return {"file_size":len(file)}

#多文件
@app04.post("/files")
async def file_(files:List[bytes] = File(...)):
    """使用File类 文件内容会以bytes的形式读入内存，适合上传小文件"""
    return {"files_size":len(files)}

#上传大文件
@app04.post("/upload_files")
async def upload_files(files:List[UploadFile]=File(...)):
    """
    上传单个文件只需去掉List[]
    1.文件存储在内存中，使用的内存达到阈值后，将保存在磁盘中
    2.适合于图片，视频文件
    3.可以获取上传的文件的元数据，如文件名，创建时间等
    4.有文件对象的异步接口
    5.上传的文件是python对象，可以使用write(),read(),seek(),close()操作
    """
    for file in files:
        contents = await file.read()
        print(contents)
    return {"filename":files[0].filename,"content_type":files[0].content_type}


"""Path Operation Configuration 路径操作配置"""
@app04.post(
    "/path_operation_configuration",
    response_model=UserOut,
    # tags=['Path',"Operation","Configuration"],
    summary="This is summary",
    description="This is description",
    response_description="This is response descriptioin",
    #deprecated=True,#表示接口已经废弃了
    status_code=status.HTTP_200_OK
)
async def path_operation_configuration(user:UserIn):
    """Path Operaton Configuration 路径操作配置"""
    return user.dict()


""""Handling Error 错误处理"""

@app04.get("/http_exception")
async def http_exceptinon(city:str):
    if city != "Beijing":
        raise HTTPException(status_code=404,detail="错误的数据",headers={"X-Error":"ERROR"})
    else:
        return {"city":city}

@app04.get("/http_exception/{city_id}")
async def override_http_http_exceptinon(city_id:int):
    if city_id ==1:
        raise HTTPException(status_code=418,detail="错误的数据")
    else:
        return {"city":city_id}
