#coding=utf-8
from typing import Optional,List
from fastapi import APIRouter, Header,Depends,HTTPException,status  # Depends 依赖
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel,EmailStr,Field#请求体效验用Field
from passlib.context import CryptContext #密码加密
from jose import JWTError,jwt
from datetime import datetime,timedelta


app06 = APIRouter()

"""OAuth2 密码模式和FastAPI 的 OAuth2PasswordBearer"""

oauth2_schema = OAuth2PasswordBearer(tokenUrl="chapter06/token")

@app06.get("/oauth2_password_bearer")
async def oauth2_password_bearer(token:str=Depends(oauth2_schema)):
    return {"token":token}

"""基于 Password 和 Bearer token 的OAuth2 认证"""

fake_users_db = {
    "john snow" :{
        "username":"john snow",
        "full_name":"Jonhn Snow",
        "email":"jonhnsnow@exqmple.com",
        "heshed_password":"fakehashedsecret",
        "disabled":False
    },
    "alice" :{
        "username":"alice",
        "full_name":"Alice Wonderson",
        "email":"alice@exqmple.com",
        "heshed_password":"fakehashedsecret2",
        "disabled":True
    },
}

def fake_hash_password(password:str):
    return "fakehashed" + password

class User(BaseModel):
    username:str
    email:Optional[str] = None
    full_name:Optional[str] = None
    disabled:Optional[bool] = None

class UserInBD(User):
    heshed_password:str


@app06.post("/token")
async def login(form_data:OAuth2PasswordRequestForm = Depends()):
    user_dict=fake_users_db.get(form_data.username)

    if not user_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="不正确的用户名和密码")
    else:
        user= UserInBD(**user_dict)
        hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.heshed_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不正确的用户名和密码")
    return {"access_token":user.username,"token_type":"bearer"}


def get_user(db,username:str):
    if username in db:
        user_dict = db[username]
        return UserInBD(**user_dict)


def fake_decode_token(token:str):
    user = get_user(fake_users_db,token)
    return user



def get_current_user(token:str = Depends(oauth2_schema)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate":"Bearer"}
        )
    else:
        return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="未激活")
    else:
        return current_user




@app06.get("/users/me")
async def read_users_me(current_user:User = Depends(get_current_active_user)):
    return current_user



"""OAuth2 with Password (and hashing),Bearer with JWT tokens 开发基于 JSON Web """

fake_users_db.update(
    {
    "john snow" :{
            "username":"john snow",
            "full_name":"Jonhn Snow",
            "email":"jonhnsnow@exqmple.com",
            "heshed_password":"$2a$10$1B/WSOkfBLCwrvbo2bkrduyXF1aX1dr3mXECYsjLi.A92UAH9teG2",
            "disabled":False
        }
    }
)

SECRET_KEY = "09b25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256" #算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 访问令牌过期时间

class Token(BaseModel):
    """返回给用户的Token"""
    access_token:str
    token_type:str

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto") #对传入的密码加密

oauth2_schema = OAuth2PasswordBearer(tokenUrl="chapter06/jwt/token")#接受用户名和密码的token接口

#对密码进行效验
def verity_password(plain_password:str,hashed_password:str):
    ''' 对密码进行效验'''
    return pwd_context.verify(plain_password,hashed_password)


def jwt_get_user(db,username:str):
    """获取用户"""
    if username in db:
        user_dict = db[username]
        return UserInBD(**user_dict)



def jwt_authenticate_user(db,username:str,password:str):
    """验证用户"""
    user = jwt_get_user(db=db,username=username)

    if not user:
        return False
    elif not verity_password(plain_password=password,hashed_password=user.heshed_password):
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

@app06.post("/jwt/token",response_model=Token)
async def login_for_access_token(form_data:OAuth2PasswordRequestForm = Depends()):
    user = jwt_authenticate_user(db=fake_users_db,username=form_data.username,password=form_data.password)
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

async def jwt_get_current_user(token:str=Depends(oauth2_schema)):
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
    user = jwt_get_user(db=fake_users_db,username=username)
    if user is None:
        raise credentials_exception
    return user

async def jwt_get_current_active_user(current_user:User=Depends(jwt_get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    else:
        return current_user


@app06.get("/jwt/users/me")
async def jwt_read_users_me(current_user:User = Depends(jwt_get_current_active_user)):
    return current_user