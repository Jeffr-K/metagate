from passlib.context import CryptContext

from src.infrastructure.security.token import Token, TokenType
from src.modules.user.core.entity import User
from src.modules.user.core.repository import SQLModelUserRepository
from src.modules.user.interface.adapter import UserRegisterAdapter, UserUpdateAdapter, UserDeleteAdapter, \
    UserLogoutAdapter, UserLoginAdapter


class UserRegisterUseCase:
    def __init__(self):
        pass

    @classmethod
    async def execute(cls, adapter: UserRegisterAdapter):
        repository = SQLModelUserRepository()
        if repository.exists_by_email(adapter.email):
            raise ValueError("already exists with this email address.")
        hashed_password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(adapter.password)
        user = await User.register(email=adapter.email, password=hashed_password, username=adapter.username)
        await repository.save(user)


class UserUpdateUseCase:

    def __init__(self):
        pass

    @classmethod
    async def execute(cls, adapter: UserUpdateAdapter) -> bool:
        repository = SQLModelUserRepository()
        await repository.update(user_id=adapter.user_id)
        return True


class UserDeleteUseCase:

    def __init__(self):
        pass

    @classmethod
    async def execute(cls, adapter: UserDeleteAdapter) -> bool:
        repository = SQLModelUserRepository()
        await repository.delete(adapter.user_id)
        return True


class UserLoginUseCase:
    def __init__(self):
        pass

    @classmethod
    async def execute(cls, adapter: UserLoginAdapter) -> dict:
        access_token = Token.generate(adapter.email, token_type=TokenType.ACCESS)
        refresh_token = Token.generate(adapter.email, token_type=TokenType.REFRESH)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }


class UserLogoutUseCase:
    def __init__(self):
        pass

    @classmethod
    async def execute(cls, adapter: UserLogoutAdapter) -> dict:
        pass