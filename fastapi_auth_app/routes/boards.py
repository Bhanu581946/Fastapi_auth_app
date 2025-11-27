from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/boards", tags=["Boards"])

# -------------------------------------------------------
# 1. CREATE A NEW BOARD
# -------------------------------------------------------
@router.post("/", response_model=schemas.ShowBoardWithRole)
def create_board(
    board: schemas.BoardCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    # Step 1: Create the board
    new_board = models.Board(name=board.name, owner_id=user.id)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    # Step 2: Add the user as a board member with role = 'owner'
    new_member = models.BoardMember(board_id=new_board.id, user_id=user.id, role="owner")
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    # Step 3: Return both board info + role
    return {
        "id": new_board.id,
        "name": new_board.name,
        "role": new_member.role
    }

# -------------------------------------------------------
# 2. GET SINGLE BOARD (ONLY IF USER IS OWNER)
# -------------------------------------------------------
@router.get("/one/{board_id}")
def get_one_board(
    board_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    
    # Check if board exists and belongs to the logged-in user
    board= db.query(models.Board).filter(models.Board.owner_id== user.id).first()
    if not board:
        raise HTTPException(status_code= 200, detail= "Board not found")
    return({"id": board_id, "name": board.name})


# -------------------------------------------------------
# 3. GET ALL BOARDS WHERE USER IS MEMBER
# -------------------------------------------------------
@router.get("/all", response_model=list[schemas.ShowBoardWithRole])
def get_boards(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):

    # Join BoardMember table to include boards where user is a member
    boards = (
        db.query(models.Board, models.BoardMember.role)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(models.BoardMember.user_id == user.id)
        .all()
    )

    # Convert results into list of dicts
    result = [
        {"id": b.Board.id, "name": b.Board.name, "role": b.role}
        for b in boards
    ]
    return result

# -------------------------------------------------------
# 4. CHANGE MEMBER ROLE (ONLY OWNER CAN DO THIS)
# -------------------------------------------------------
@router.put("/role")
def change_member_role(
    data: schemas.RoleChange,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    
    #Step 1.Valid role check
    
    vaild_roles = ["Viewer","Owner", "Member"] 
    if data.new_role not in vaild_roles:
        raise HTTPException(status_code=400, detail="Invalid role")  
    
    # Step 2.Check Board exists?
    
    board = db.query(models.Board).filter(models.Board.id== data.board_id).first()
    if not board: 
        raise HTTPException(status_code = 404, detail ="Board not found")   
    
    #Step 3.Current user Owner or only Owner can change roles

    membership =(
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id == data.board_id,
            models.BoardMember.user_id == current_user.id,
            models.BoardMember.role == "owner"
        ).first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail= "only owner can change roles")


    #Step 4.find user whose role will be changed
    target_member = (
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id == data.board_id,
            models.BoardMember.user_id == data.user_id
        ).first()
    )
    if not target_member:
        raise HTTPException(status_code=404, detail= "user is not a member pof this board")  

    #Step 5.update Role
    target_member.role= data.new_role
    db.commit()

    return{
        "message": "Updated Role",
        "user_id": data.user_id,
        "board_id": data.board_id,
        "new_role": target_member.role
    }                          

@router.post("/invite-member") 
def invite_member(data:schemas.InviteRequest,
                  db:Session =Depends(get_db),
                  user:models.User = Depends(auth.get_current_user)):

    #Step 1. Only owner can invite
    membership = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == data.board_id,
        models.BoardMember.user_id == user.id,
        models.BoardMember.role=="owner").first()
    if not membership:
        raise HTTPException(status_code = 400, detail = "Only owner can invite members")
    
    #Step 2. Check Email
    user_to_invite= db.query(models.User).filter(models.User.email== data.email).first()
    if not user_to_invite:
        raise HTTPException(status_code=400, detail="email not found")
    
    #Step 3. Check duplicate Membership
    exists = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == data.board_id,
        models.BoardMember.user_id == user_to_invite.id
    ).first()
    if exists:
        raise HTTPException(status_code = 400, detail = "User already a member")
    
    #Step 4. Create member
    new_member = models.BoardMember(
        user_id=user_to_invite.id,
        board_id=data.board_id,
        role="member"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return{"message":"Invitation Successul",
           "added_user": user_to_invite.email}
    
    

    
               