from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=schemas.ShowTask)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    membership = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == task.board_id,
        models.BoardMember.user_id == user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this board")

    # new_task = models.Task(**task.dict())
    new_task = models.Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{board_id}", response_model=list[schemas.ShowTask])
def get_tasks(board_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    membership = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == board_id,
        models.BoardMember.user_id == user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(models.Task).filter(models.Task.board_id == board_id).all()

@router.delete("{task_id}")
def delete_task(task_id:int, 
                db:Session = Depends(get_db), 
                user:models.User = Depends(auth.get_current_user)):
    
    # 1. Check task exists
    task= db.query(models.Task).filter(models.Task.id ==task_id).first()
    if not task:
        raise HTTPException(status_code = 400, detail = "task not found")
    
    # 2. Check membership (user must be member of board)
    membership=(
        db.query(models.BoardMember)
        .filter(models.BoardMember.board_id == task.board_id,
                models.BoardMember.user_id == user.id).first()
    )
    if not membership:
        raise HTTPException(status_code = 400, detail = "You are not a member of this board")
    
    # 3. Delete task
    db.delete(task)
    db.commit()

    return{"message" : "task deleted successfully ", "task_id": task_id} 

