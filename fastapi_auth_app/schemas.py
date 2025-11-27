from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class ShowUser(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class BoardCreate(BaseModel):
    name: str

class ShowBoard(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class ShowBoardWithRole(BaseModel):
    id: int
    name: str
    role: str  # 👈 new field to include user's role on that board
    class Config:
        from_attributes = True

class RoleChange(BaseModel):
    board_id: int
    user_id: int
    new_role: str

class LoginRequest(BaseModel):
    username: str 
    email: EmailStr
    password: str
    login_type:str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    board_id: int
    assignee_id: Optional[int] = None

class ShowTask(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    class Config:
        from_attributes = True

class SubtaskCreate(BaseModel):
    title: str
    task_id: int

class ShowSubtask(BaseModel):
    id: int
    task_id:int
    title: str
    class Config:
        from_attributes =True

class InviteRequest(BaseModel):
    email: EmailStr
    board_id: int