from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    #Each user can have multiple boards, but every board has only one owner.
    boards = relationship("Board", back_populates="owner")
    #Each user can be assigned many tasks, but each task belongs to only one user.
    tasks = relationship("Task", back_populates="assignee")

class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    #One user can own many boards, But each board has only one owner.
    owner = relationship("User", back_populates="boards")
    #One Board can have many members (users).
    members = relationship("BoardMember", back_populates="board")
    #One Board can have many tasks.
    tasks = relationship("Task", back_populates="board")

class BoardMember(Base):
    __tablename__ = "board_members"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="member")

    board = relationship("Board", back_populates="members")
     #each BoardMember is linked to one Board, and that Board keeps track of all its members through the members relationship.
    user = relationship("User")  #Each BoardMember represents one User.

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="To Do")
    board_id = Column(Integer, ForeignKey("boards.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))

    board = relationship("Board", back_populates="tasks")  #Many tasks belong to one board
    assignee = relationship("User", back_populates="tasks")  #Many tasks can be assigned to one user
    subtasks = relationship("Subtask", back_populates = "task") #1 Task has multiple Subtasks

class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key = True)
    title = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id"))

    task = relationship("Task", back_populates="subtasks") #many subtasks belong to a task