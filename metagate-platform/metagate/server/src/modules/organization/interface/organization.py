from typing import Union, List

from fastapi import APIRouter, Depends

from src.infrastructure.utils.response_model import BusinessResponse, SuccessResponse, ErrorResponse
from src.modules.organization.core.command import OrganizationCreateUseCase, OrganizationDeleteUseCase, \
    OrganizationUpdateUseCase
from src.modules.organization.core.entity import Organization
from src.modules.organization.core.query import OrganizationQueryUseCase, OrganizationsQueryUseCase
from src.modules.organization.interface.adapter import OrganizationCreateAdapter, OrganizationUpdateAdapter, \
    OrganizationPaginationQuery, OrganizationQuery

organizations = APIRouter(prefix="/organizations", tags=["organization"])

@organizations.get("/")
async def organizations(
    query: OrganizationPaginationQuery,
    usecase: OrganizationsQueryUseCase = Depends(OrganizationsQueryUseCase),
) -> Union[BusinessResponse, SuccessResponse, ErrorResponse]:
    try:
        result = await usecase.execute(query)
        return BusinessResponse[List[Organization]].success(200, result)
    except Exception as e:
        return BusinessResponse[List[None]].failure(500, e)


@organizations.get("/{organization_id}")
async def organization(
    query: OrganizationQuery,
    usecase: OrganizationQueryUseCase = Depends(OrganizationQueryUseCase)
) -> Union[BusinessResponse, SuccessResponse, ErrorResponse]:
    try:
        result = await usecase.execute(query)
        return BusinessResponse[Organization].success(200, result)
    except Exception as e:
        return BusinessResponse[Organization].failure(500, e)


@organizations.post("/")
async def create_organization(
    adapter: OrganizationCreateAdapter,
    usecase: OrganizationCreateUseCase = Depends(OrganizationCreateUseCase)
) -> Union[SuccessResponse[bool], ErrorResponse]:
    try:
        result = await usecase.execute(adapter)
        return BusinessResponse[bool].success(201, result)
    except Exception as e:
        return BusinessResponse[bool].failure(500, e)


@organizations.delete("/{organization_id}")
async def delete_organization(
    organization_id: int,
    usecase: OrganizationDeleteUseCase = Depends(OrganizationDeleteUseCase)
) -> Union[SuccessResponse[bool], ErrorResponse]:
    try:
        result = await usecase.execute(organization_id)
        return BusinessResponse[bool].success(204, result)
    except Exception as e:
        return BusinessResponse[bool].failure(500, e)


@organizations.put("/{organization_id}")
async def update_organization(
    organization_id: int,
    adapter: OrganizationUpdateAdapter,
    usecase: OrganizationUpdateUseCase = Depends(OrganizationUpdateUseCase)
) -> Union[SuccessResponse[bool], ErrorResponse]:
    try:
        result = await usecase.execute(organization_id, adapter)
        return BusinessResponse[bool].success(204, result)
    except Exception as e:
        return BusinessResponse[bool].failure(500, e)