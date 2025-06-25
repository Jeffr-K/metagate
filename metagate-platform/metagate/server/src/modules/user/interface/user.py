from typing import List, Union

from fastapi import APIRouter
from fastapi.params import Depends

from src.infrastructure.utils.response_model import BusinessResponse, SuccessResponse, ErrorResponse
from src.modules.user.core.command import UserRegisterUseCase, UserUpdateUseCase, UserDeleteUseCase
from src.modules.user.core.entity import User
from src.modules.user.core.query import UsersPaginationQueryUseCase, UserQueryUseCase
from src.modules.user.interface.adapter import UserRegisterAdapter, UserUpdateAdapter, UserDeleteAdapter

users = APIRouter(prefix="/users", tags=["user"])


@users.get("/", response_model=Union[SuccessResponse[List[User]], ErrorResponse])
async def get_users(
    usecase: UsersPaginationQueryUseCase = Depends(UsersPaginationQueryUseCase)
) -> Union[SuccessResponse[List[User]], ErrorResponse]:
    try:
        result = await usecase.execute()
        return BusinessResponse.success(200, result, "Users retrieved successfully")
    except Exception as e:
        return BusinessResponse.failure(500, str(e), "Failed to retrieve users")


@users.get("/{user_id}", response_model=Union[SuccessResponse[User], ErrorResponse])
async def get_user(
    user_id: int, usecase: UserQueryUseCase = Depends(UserQueryUseCase)
) -> Union[SuccessResponse[User], ErrorResponse]:
    try:
        user = await usecase.execute(user_id=user_id)
        return BusinessResponse.success(200, user, "User retrieved successfully")
    except ValueError as e:
        return BusinessResponse.failure(404, str(e), "User not found")
    except Exception as e:
        return BusinessResponse.failure(500, str(e), "Failed to retrieve user")


@users.post("/", response_model=Union[SuccessResponse[User], ErrorResponse])
async def register(
    adapter: UserRegisterAdapter,
    usecase: UserRegisterUseCase = Depends(UserRegisterUseCase)
) -> Union[SuccessResponse[User], ErrorResponse]:
    try:
        result = await usecase.execute(adapter=adapter)
        return BusinessResponse.success(201, result, "User registered successfully")
    except ValueError as e:
        return BusinessResponse.failure(400, str(e), "Registration failed")
    except Exception as e:
        return BusinessResponse.failure(500, str(e), "Internal server error")


@users.put("/{user_id}", response_model=Union[SuccessResponse[User], ErrorResponse])
async def edit(
    user_id: int,
    adapter: UserUpdateAdapter,
    usecase: UserUpdateUseCase = Depends(UserUpdateUseCase)
) -> ErrorResponse | SuccessResponse[bool]:
    try:
        result = await usecase.execute(adapter=adapter)
        return BusinessResponse.success(200, result, "User updated successfully")
    except ValueError as e:
        return BusinessResponse.failure(400, str(e), "Update failed")
    except Exception as e:
        return BusinessResponse.failure(500, str(e), "Internal server error")


@users.delete("/{user_id}", response_model=Union[SuccessResponse[dict], ErrorResponse])
async def drop(
    user_id: int,
    adapter: UserDeleteAdapter,
    usecase: UserDeleteUseCase = Depends(UserDeleteUseCase)
) -> Union[SuccessResponse[dict], ErrorResponse]:
    try:
        await usecase.execute(adapter=adapter)
        return BusinessResponse.success(200, {}, "User deleted successfully")
    except ValueError as e:
        return BusinessResponse.failure(400, str(e), "Delete failed")
    except Exception as e:
        return BusinessResponse.failure(500, str(e), "Internal server error")