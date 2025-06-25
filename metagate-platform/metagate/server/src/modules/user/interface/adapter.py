from typing import Optional

from pydantic import BaseModel


class UserPaginationQuery(BaseModel):
    pass


class UserQueryAdapter(BaseModel):
    pass


class UserRegisterAdapter(BaseModel):
    email: str
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "example@gmail.com",
                "username": "example_user",
                "password": "example_password"
            }
        }


class UserUpdateAdapter(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "example@gmail.com",
                "username": "example_user",
                "password": "example_password"
            }
        }


class UserDeleteAdapter(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "example@gmail.com"
            }
        }