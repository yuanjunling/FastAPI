#coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:admin@890903@localhost:3306/test_01"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    encoding='utf-8',
    echo=True,

)

SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False,expire_on_commit=True)

#创建基本的映射类
Base = declarative_base(bind=engine,name='Base')