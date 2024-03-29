from pydantic import BaseModel
import typing as t


# Valves
class ValveBase(BaseModel):
    name: str
    is_active: bool = True
    is_up: bool = True
    last_changed: str
    state: str

class AuditLogBase(BaseModel):
    created: str
    type: str
    user: str
    name: str
    action: str
    description: str

class LogCreate(AuditLogBase):
    type: str
    user: str
    name: str
    action: str
    description: str

    class Config:
        orm_mode = True


class ValveOut(ValveBase):
    pass


class ValveCreate(ValveBase):
    name: str

    class Config:
        orm_mode = True


class ValveEdit(ValveBase):
    name: t.Optional[str] = None

    class Config:
        orm_mode = True


class Valve(ValveBase):
    name: str

    class Config:
        orm_mode = True


# auditLog
class AuditBase(BaseModel):
    name: str
    is_active: bool = True
    is_up: bool = True
    last_changed: str
    state: str


class ValveOut(ValveBase):
    pass


class ValveCreate(ValveBase):
    name: str

    class Config:
        orm_mode = True


class ValveEdit(ValveBase):
    name: t.Optional[str] = None

    class Config:
        orm_mode = True


class Valve(ValveBase):
    name: str

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_superuser: bool = False
    first_name: str = None
    last_name: str = None


class UserOut(UserBase):
    pass


class UserCreate(UserBase):
    password: str

    class Config:
        orm_mode = True


class UserEdit(UserBase):
    password: t.Optional[str] = None

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None
    permissions: str = "user"
