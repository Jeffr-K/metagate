from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    username: str = Field(nullable=False)

    @classmethod
    async def register(cls, email: str, password: str, username: str) -> "User":
        user = cls(email=email, password=password, username=username)
        return user