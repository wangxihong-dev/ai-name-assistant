from sqlalchemy.ext.asyncio import  create_async_engine
from settings import DB_URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData


engine = create_async_engine(
    DB_URL,
    #将输出所有执行SQL的日志
    echo=True,
    #连接池大小（默认是5个）
    pool_size=10,
    #允许连接池最大的连接数（默认是10个2）
    max_overflow=20,
    #获取连接超时时间（默认是30秒）
    pool_timeout=10,
    #连接回收时间（默认是-1，代表永不回收）
    pool_recycle=3600,
    #连接是否检查（默认是false）
    pool_pre_ping=True,
)


AsyncSessionFactory = sessionmaker(
    #Engine或者其子类对象（这里是AsyncEngine）
    bind=engine,
    #Session类的代替（默认是Session类）
    class_=AsyncSession,
    #是否在查找之前执行flush操作（默认为True）
    autoflush=True,
    #是否在执行commit操作后Session就过期（默认是Ture）
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        #ix：index 索引
        "ix": "ix_%(column_0_label)s",
        #uq：unique 唯一索引
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        #ck：check，检查索引
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        #fk：外键约束
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        #pk：primary key，主键约束
        "pk": "pk_%(table_name)s",
    })

from . import user