from datetime import datetime
from typing import Optional,Literal
from pydantic import BaseModel,Field
TaskStatus=Literal["todo","in_progress","done"]
class TaskCreate(BaseModel):
    title:str=Field(min_length=1,max_length=200); description:Optional[str]=None
class TaskUpdate(BaseModel):
    title:Optional[str]=Field(default=None,min_length=1,max_length=200); description:Optional[str]=None; status:Optional[TaskStatus]=None
class TaskResponse(BaseModel):
    id:int; title:str; description:Optional[str]; status:str; created_at:datetime
    class Config: from_attributes=True
