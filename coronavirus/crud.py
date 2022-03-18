#coding=utf-8
from sqlalchemy.orm import Session
from coronavirus import models,schemas

def get_city(db:Session,city_id:int):
    '''根据城市ID查询城市'''
    return db.query(models.City).filter(models.City.id==city_id).first()

def get_city_by_name(db:Session,name:str):
    '''根据名称查询城市'''
    return db.query(models.City).filter(models.City.province==name).first()

def get_cities(db:Session,skip:int=0,limit:int=10):
    '''查询城市'''
    return db.query(models.City).offset(skip).limit(limit).all()


def create_city(db:Session,city:schemas.CreateCity):
    '''创建城市'''
    db_city = models.City(**city.dict())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

def get_data(db:Session,city:str=None,skip:int=0,limit:int=10):
    '''查询数据'''
    if city:
        return db.query(models.Data).filter(models.Data.city.has(province=city)).all()
    else:
        return db.query(models.Data).offset(skip).limit(limit).all()


def create_city_data(db:Session,data:schemas.CreateData,city_id:int):
    '''创建数据'''
    db_data=models.Data(**data.dict(),city_id=city_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def create_user(db:Session,user:schemas.CreateUser):
    """新建用户"""
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()#提交保存数据库中
    db.refresh(db_user)
    return db_user

def get_user_by_name(db:Session,name:str):
    '''根据用户名查询用户'''
    return db.query(models.User).filter(models.User.username==name).first()




