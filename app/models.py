from datetime import datetime
from sqlalchemy import Column,DateTime,Integer,String,Text
from .database import Base
class Task(Base):
    __tablename__="tasks"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(200),nullable=False)
    description=Column(Text,nullable=True)
    status=Column(String(30),nullable=False,default="todo")
    created_at=Column(DateTime,default=datetime.utcnow,nullable=False)
