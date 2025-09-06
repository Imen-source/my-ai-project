from pydantic import BaseModel, Field,EmailStr
from typing import List, Optional
# ---------- User Schemas ----------
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: EmailStr | None = None
    avatar: str | None = None
    bio: str | None = None

class UserRead(BaseModel):
    username: str
    full_name: str | None
    email: EmailStr | None
    avatar: str | None
    bio: str | None

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

# ---------- Task Schemas ----------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = Field(default="medium", regex="^(low|medium|high)$")  # enforce allowed values
    tags: Optional[List[str]] = []  # list of strings

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    completed: bool
    owner_id: int
    class Config:
        orm_mode = True
