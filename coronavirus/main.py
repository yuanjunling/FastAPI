#coding=utf-8
from typing import Optional,List
import requests
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request,status
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from coronavirus import crud, schemas
from coronavirus.database import engine, Base, SessionLocal
from coronavirus.models import City, Data,User
from passlib.context import CryptContext #密码加密
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

from jose import JWTError,jwt
from datetime import datetime,timedelta

application=APIRouter()

templates = Jinja2Templates(directory='E://fastapi_tutorial//coronavirus//templates')

Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = "09b25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256" #算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 访问令牌过期时间

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto") #对传入的密码加密

oauth2_schema = OAuth2PasswordBearer(tokenUrl="coronavirus/jwt/user/token")#接受用户名和密码的token接口

#对密码进行效验
def verity_password(plain_password:str,hashed_password:str):
    ''' 对密码进行效验'''
    return pwd_context.verify(plain_password,hashed_password)

#对密码进行加密
def get_password_hash(password:str):
    return pwd_context.hash(password)



#新建用户
@application.post('/create_user',response_model=schemas.ReadUser,summary="注册用户")
async def create_user(user:schemas.CreateUser,db:Session=Depends(get_db)):
    db_user =crud.get_user_by_name(db=db,name=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='您输入的用户已存在')
    try:
        user.password = get_password_hash(user.password)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='密码加密失败')
    try:
        user = crud.create_user(db=db, user=user)
        return user
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='注册失败')

def jwt_authenticate_user(db,username:str,password:str):
    """验证用户"""
    user = crud.get_user_by_name(db=db,name=username)

    if not user:
        return False
    elif not verity_password(plain_password=password,hashed_password=user.password):
        return False
    else:
        return user

def created_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(claims=to_encode,key=SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt

@application.post("/jwt/user/token",response_model=schemas.Token,summary="生成token")
async def login_for_access_token(db:Session=Depends(get_db),form_data:OAuth2PasswordRequestForm = Depends()):
    user = jwt_authenticate_user(db=db,username=form_data.username,password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    else:
        #token过期时间
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = created_access_token(
            data={"sub":user.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token":access_token,
            "token_type":"bearer"
        }

async def jwt_get_current_user(db:Session=Depends(get_db),token:str=Depends(oauth2_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not Validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token=token,key=SECRET_KEY,algorithms=[ALGORITHM])
        username =payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_name(db=db,name=username)
    if user is None:
        raise credentials_exception
    return user

@application.get("/jwt/users/me")
async def jwt_read_users_me(current_user:User = Depends(jwt_get_current_user)):
    return current_user


@application.post("/create_city",response_model=schemas.ReadCity)
def create_city(city:schemas.CreateCity,db:Session=Depends(get_db),User:str = Depends(jwt_get_current_user)):
    '''添加城市数据'''
    db_city = crud.get_city_by_name(db=db,name=city.province)
    if db_city:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='您输入的城市已存在')
    else:
        return crud.create_city(db=db,city=city)


@application.get("/get_city/{city}",response_model=schemas.ReadCity)
def get_city(city:str,db:Session=Depends(get_db)):
    '''根据城市名称查询数据'''
    db_city = crud.get_city_by_name(db=db,name=city)
    if db_city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='您输入的数据不存在')
    else:
        return db_city


@application.get('/get_cities',response_model=List[schemas.ReadCity])
def get_cities(skip:int=0,limit:int=15,db:Session = Depends(get_db)):
    '''根据页数批量查询'''
    cities = crud.get_cities(db=db,skip=skip,limit=limit)
    return cities

@application.post("/create_data",response_model=schemas.ReadData)
def create_data_for_city(city:str,data:schemas.CreateData,db:Session = Depends(get_db)):
    '''添加数据'''
    db_city = crud.get_city_by_name(db=db,name=city)
    data = crud.create_city_data(db=db,data=data,city_id=db_city.id)
    return data


@application.get("/get_data")
def get_data(city:str=None, skip:int=0, limit:int=10, db:Session = Depends(get_db)):
    '''查询数据'''
    data = crud.get_data(db=db,city=city,skip=skip,limit=limit)
    return data

def bg_task(url: HttpUrl, db: Session):
    """这里注意一个坑，不要在后台任务的参数中db: Session = Depends(get_db)这样导入依赖"""
    coronavirus_data = requests.get(url=f"{url}?source=jhu&country_code=CN&timelines=true")

    if 200 == coronavirus_data.status_code:
        db.query(Data).delete()
        for city in coronavirus_data.json()["locations"]:
            db_city = crud.get_city_by_name(db=db, name=city["province"])
            for date, confirmed in city["timelines"]["confirmed"]["timeline"].items():
                data = {
                    "date": date.split("T")[0],  # 把'2020-12-31T00:00:00Z' 变成 ‘2020-12-31’
                    "confirmed": confirmed,
                    "deaths": city["timelines"]["deaths"]["timeline"][date],
                    "recovered": 0  # 每个城市每天有多少人痊愈，这种数据没有
                }
                # 这个city_id是city表中的主键ID，不是coronavirus_data数据里的ID
                crud.create_city_data(db=db, data=schemas.CreateData(**data), city_id=db_city.id)

    city_data = requests.get(url=f"{url}?source=jhu&country_code=CN&timelines=false")

    if 200 == city_data.status_code:
        db.query(City).delete()  # 同步数据前先清空原有的数据
        for location in city_data.json()["locations"]:
            city = {
                "province": location["province"],
                "country": location["country"],
                "country_code": "CN",
                "country_population": location["country_population"]
            }
            crud.create_city(db=db, city=schemas.CreateCity(**city))



@application.get("/sync_coronavirus_data/jhu")
def sync_coronavirus_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """从Johns Hopkins University同步COVID-19数据"""
    background_tasks.add_task(bg_task, "http://coronavirus-tracker-api.herokuapp.com/v2/locations", db)
    return {"message": "正在后台同步数据..."}

@application.get("/home")
def coronavirus(request: Request, city: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_data(db, city=city, skip=skip, limit=limit)
    return templates.TemplateResponse("home.html",{
        "request": request,
        "data": data,
        "sync_data_url": "/coronavirus/sync_coronavirus_data/jhu"
    })
