#coding = UTF-8
from datetime import datetime,date
from pydantic import BaseModel,ValidationError,constr
from typing import List,Optional
from pathlib import Path
from sqlalchemy import Column,Integer,String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

class User(BaseModel):
    id :int # 没默认值是必填字段
    name : str = "john" #有默认值，选填字段
    signup_ts : Optional[datetime] = None
    friends: List[int] = [] #列表中元素是int类型或者可以直接转换成int类型

external_data = {
    "id":"123",
    "signup_ts" : "2022-2-16 13:49",
    "friends" : [1,2,"3"]
}

if __name__ == '__main__':
    user = User(**external_data)
    print(user.id,user.name,user.friends)
    print(repr(user.signup_ts))
    print(user.dict())
    print(User.parse_obj(obj=external_data))

    try:
        User(id = 1,signup_ts=datetime.today(),friends = [1,2,"not number"])
    except ValidationError as e:
        print(e.json())

    path = Path('pydantic_tutorial.json')
    path.write_text('{"id": 123, "name": "john", "signup_ts": "2022-2-16 13:49", "friends": [1, 2, 3]}')
    print(User.parse_file(path))
    print(user.schema())
    print(user.schema_json())
    # user_data = '{"id": "error", "name": "john", "signup_ts": "2022-2-16 13:49", "friends": [1, 2, 3]}'
    # print(User.construct(**user_data))

    print(User.__fields__.keys())

class Sound(BaseModel):
    sound:str

class Dog(BaseModel):
    birthday:date
    weigth: Optional[float]=None
    sound:List[Sound]

dogs = Dog(birthday=date.today(),weight=6.66,sound=[{"sound":"wang wang"},{"sound":"ying ying"}])
print(dogs.json())



Base = declarative_base()

class CompanyOrm(Base):
    __tablename__='companies'
    id = Column(Integer,primary_key=True,nullable=False)
    public_key = Column(String(20),index=True,nullable=False,unique=True)
    name = Column(String(63),unique=True)
    domains = Column(ARRAY(String(255)))

class CompanyMode(BaseModel):
    id:int
    public_key:constr(max_length=20)
    name:constr(max_length=63)
    domains:List[constr(max_length=255)]

    class Config:
        orm_mode = True

co_orm = CompanyOrm(
    id = 123,
    public_key='foobar',
    name='xiaoming',
    domains=['baidu.com','xiaomi.com']
)

print(CompanyMode.from_orm(co_orm))