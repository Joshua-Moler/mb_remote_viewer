from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import typing as t
import datetime
from app.core.security import *
from app.core.Utils import *
from . import models, schemas




#### ***** LOGS ***** #####
def get_logs_data (c):
    return get_data(config.EVENTS, None)

def get_logs_data_by_id (run_id, c):
    print ({'run_id': run_id})
    return get_data(config.LOGS, {'run_id': run_id})





# error message
def error_message(e):
    try:
        if isinstance(e.orig, UniqueViolation):
            return e.orig
        else:
            return str(e)
    except Exception as ee:
        return str(e)

    # id = Column(Integer, primary_key=True, index=True)
    # created = Column(DateTime, default=datetime.datetime.utcnow)
    # type = Column(String)
    # user = Column(String) ## Column(Integer, ForeignKey(User.id))
    # name = Column(String)
    # action = Column(String)
    # description = Column(String)

def save_logs(db:Session, current_user, type = None, name = None, action = None, description = None):
    log_msg = models.Audit(
        created=datetime.now(),
        type=type,
        user=current_user.id,
        name=name,
        action=action,
        description=description
    )
    db.add(log_msg)
    db.commit()
    db.refresh(log_msg)
    return log_msg
  

# Audit Logs
def get_logs():
    pass

# get_log by event
def get_log():
    pass
# Valves
def get_valve(db: Session, name: str):
    valve = db.query(models.Valve).filter(models.Valve.name == name).first()
    if not valve:
        raise HTTPException(status_code=404, detail="Valve not found")
    return valve


# def get_user_by_email(db: Session, email: str) -> schemas.UserBase:
#     return db.query(models.User).filter(models.User.email == email).first()


def get_valves(
    db: Session, skip: int = 0, limit: int = 100
) -> t.List[schemas.ValveOut]:
    return db.query(models.Valve).offset(skip).limit(limit).all()


def create_valve(db: Session, valve: schemas.ValveCreate):
    db_valve = models.Valve(
        name=valve.name,
        is_active=valve.is_active,
        is_up=valve.is_up,
        last_changed="test",
        state="open"
    )
    try:
        db.add(db_valve)
        db.commit()
        db.refresh(db_valve)
    except Exception as e:
        print (f"error - {e}")
        print (f"aaa - {e.orig} {type(e.orig)}")
        raise HTTPException(status_code=400, detail=error_message(e))
    return db_valve


def delete_valve(db: Session, name: str):
    valve = get_valve(db, name)
    if not valve:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Valve not found")
    db.delete(valve)
    db.commit()
    return valve


def edit_valve(
    db: Session, name: str, valve: schemas.ValveEdit
) -> schemas.Valve:
    db_valve = get_valve(db, name)
    if not db_valve:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Valve not found")
    update_data = valve.dict(exclude_unset=True)

    # if "password" in update_data:
    #     update_data["hashed_password"] = get_password_hash(user.password)
    #     del update_data["password"]

    for key, value in update_data.items():
        setattr(db_valve, key, value)

    db.add(db_valve)
    db.commit()
    db.refresh(db_valve)
    return db_valve


# Users
def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_email(db: Session, email: str) -> schemas.UserBase:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100
) -> t.List[schemas.UserOut]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return user


def edit_user(
    db: Session, user_id: int, user: schemas.UserEdit
) -> schemas.User:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = user.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(user.password)
        del update_data["password"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


