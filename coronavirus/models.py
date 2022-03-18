#coding=utf-8
from sqlalchemy import Column, String,Integer,BigInteger,Date,DateTime,ForeignKey,func,Enum
from sqlalchemy.orm import relationship

from.database import Base

class City(Base):
    __tablename__ = 'city'#数据库的表名
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    province = Column(String(100),unique=True,nullable=False,comment='省/直辖市')
    country = Column(String(100),nullable=False,comment='国家')
    country_code = Column(String(100), nullable=False, comment='国家代码')
    country_population = Column(BigInteger, nullable=False, comment='国家人口')
    data = relationship('Data',back_populates='city')
    cretaed_at = Column(DateTime,server_default=func.now(),comment='创建时间')
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),comment='更新时间')

    __mapper_args__ = {"order_by":country_code.desc()}#数据排序

    def __repr__(self):
        return f'{self.country}_{self.province}'

class Data(Base):
    __tablename__ = 'data'  # 数据库的表名
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city_id = Column(Integer,ForeignKey('city.id'),comment='所属省/直辖市')
    date = Column(Date,nullable=False,comment='数据日期')
    confirmed = Column(BigInteger,default=0,nullable=False,comment='确诊数量')
    deaths = Column(BigInteger, default=0, nullable=False, comment='死亡数量')
    recovered = Column(BigInteger, default=0, nullable=False, comment='痊愈数量')
    city = relationship('City',back_populates='data')#类名加上自己的表名

    cretaed_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __mapper_args__ = {"order_by": date.desc()}  # 数据排序

    def __repr__(self):
        return f'{repr(self.date)}: 确诊{self.confirmed}例'

class User(Base):
    __tablename__ = 'user'  # 数据库的表名
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100),nullable=False,unique=True,comment='账户信息')
    user = Column(String(100), nullable=False,  comment='用户名')
    phone = Column(String(100), nullable=False, unique=True, comment='手机号码')
    sex = Column(String(5), nullable=False,  comment='性别')
    password = Column(String(100),nullable=False,comment='用户密码')
    cretaed_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __mapper_args__ = {"order_by": id.desc()}  # 数据排序

    def __repr__(self):
        return f'{repr(self.date)}: 注册{self.username}'