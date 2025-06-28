from typing import Union

from fastapi import APIRouter, Depends

from src.infrastructure.utils.response_model import BusinessResponse, SuccessResponse, ErrorResponse
from src.modules.user.core.command import UserLoginUseCase, UserLogoutUseCase
from src.modules.user.interface.adapter import UserLoginAdapter, UserLogoutAdapter

auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.post("/login", response_model=None)
async def login(
    adapter: UserLoginAdapter,
    usecase: UserLoginUseCase = Depends()
) -> Union[SuccessResponse[dict], ErrorResponse]:
    try:
        result = await usecase.execute(adapter)
        return BusinessResponse[dict].success(200, result)
    except Exception as e:
        return BusinessResponse.failure(500, e)


@auth.post("/logout")
async def logout(
    adapter: UserLogoutAdapter,
    usecase: UserLogoutUseCase = Depends()
) -> Union[SuccessResponse[dict], ErrorResponse]:
    try:
        result = await usecase.execute(adapter)
        return await BusinessResponse[dict].success(200, result)
    except Exception as e:
        return await BusinessResponse.failure(500, e)



@auth.post("/")
async def reset_password():
    pass

