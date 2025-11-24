from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix= "/subtasks", tags=["Subtask"])

# Create subtask
@router.post("/", response_model = schemas.ShowSubtask)
def create_subtask(data: schemas.SubtaskCreate,
                   db: Session = Depends(get_db),
                   user: models.User = Depends(auth.get_current_user)
):

    # 1. check task exist:
    task= db.query(models.Task).filter(models.Task.id == data.task_id).first()

    if not task:
        raise HTTPException(status_code= 400, detail= "task is not exist")

    # 2. check membership exist
    membership = (
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id==task.board_id,
            models.BoardMember.user_id== user.id
        ).first()
    )

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this board")

    # 3. Allow only owner or member to create subtasks
    if membership.role.lower() == "viewer":
        raise HTTPException(status_code= 400, detail= "viewer can not create subtasks")

    # 4. Create subtask
    new_subtask = models.Subtask(task_id=data.task_id, title= data.title)
    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)
    return new_subtask

@router.get("/{task_id}", response_model= list[schemas.ShowSubtask])
def get_subtask(board_id: int,
                task_id:int,
                db:Session = Depends(get_db),
                user:models.User = Depends(auth.get_current_user)):
    
    # 1. Check membership
    membership = (
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id == board_id,
            models.BoardMember.user_id == user.id).first()
    )

    if not membership:
        raise HTTPException(status_code= 400, detail= "Access denied")
    
    # 2. Check task belongs to this board
    task = db.query(models.Task).filter(
         models.Task.id==task_id,
         models.Task.board_id==board_id
     )
    if not task:
        raise HTTPException(status_code=400, detail="task is not found in this board")
    
     # 3. Return subtasks for this task
    return( db.query(models.Subtask).filter(models.Subtask.task_id == task_id).all())
    

    

              
