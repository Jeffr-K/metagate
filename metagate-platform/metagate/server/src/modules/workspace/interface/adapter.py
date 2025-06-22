from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.modules.workspace.core.value import WorkspaceStatus


class WorkspaceCreateSchema(BaseModel):
    name: str = Field(
        ...,
        description="워크스페이스 이름",
        min_length=1,
        max_length=100,
        example="새로운 프로젝트",
    )
    description: str = Field(
        ...,
        description="워크스페이스 설명",
        min_length=1,
        max_length=500,
        example="이 프로젝트는 새로운 기능을 개발하는 워크스페이스입니다.",
    )
    start_date: datetime = Field(
        ..., description="워크스페이스 시작 날짜 및 시간", example="2024-01-01T00:00:00"
    )
    end_date: datetime = Field(
        ...,
        description="워크스페이스 종료 날짜 및 시간 (시작 날짜보다 이후여야 함)",
        example="2024-12-31T23:59:59",
    )
    workspace_status: WorkspaceStatus = Field(
        default=WorkspaceStatus.ACTIVE,
        description="워크스페이스 상태 (기본값: ACTIVE)",
        example=WorkspaceStatus.ACTIVE,
    )
    owner_id: str = Field(
        ..., description="워크스페이스 소유자 ID", min_length=1, example="user_123456"
    )
    team_id: str = Field(
        ..., description="워크스페이스 담당 팀 ID", min_length=1, example="team_789"
    )
    client_id: str = Field(
        ...,
        description="워크스페이스 클라이언트 ID",
        min_length=1,
        example="client_456",
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "새로운 프로젝트",
                "description": "이 프로젝트는 새로운 기능을 개발하는 워크스페이스입니다.",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "workspace_status": "ACTIVE",
                "owner_id": "user_123456",
                "team_id": "team_789",
                "client_id": "client_456",
            }
        }


class WorkspaceUpdateSchema(BaseModel):
    name: Optional[str] = Field(
        None,
        description="워크스페이스 이름 (수정 시에만 제공)",
        min_length=1,
        max_length=100,
        example="수정된 프로젝트명",
    )
    description: Optional[str] = Field(
        None,
        description="워크스페이스 설명 (수정 시에만 제공)",
        min_length=1,
        max_length=500,
        example="수정된 프로젝트 설명입니다.",
    )
    start_date: Optional[datetime] = Field(
        None,
        description="워크스페이스 시작 날짜 및 시간 (수정 시에만 제공)",
        example="2024-01-01T00:00:00",
    )
    end_date: Optional[datetime] = Field(
        None,
        description="워크스페이스 종료 날짜 및 시간 (수정 시에만 제공, 시작 날짜보다 이후여야 함)",
        example="2024-12-31T23:59:59",
    )
    workspace_status: Optional[WorkspaceStatus] = Field(
        None,
        description="워크스페이스 상태 (수정 시에만 제공)",
        example=WorkspaceStatus.IN_PROGRESS,
    )
    owner_id: Optional[str] = Field(
        None,
        description="워크스페이스 소유자 ID (수정 시에만 제공)",
        min_length=1,
        example="user_123456",
    )
    team_id: Optional[str] = Field(
        None,
        description="워크스페이스 담당 팀 ID (수정 시에만 제공)",
        min_length=1,
        example="team_789",
    )
    client_id: Optional[str] = Field(
        None,
        description="워크스페이스 클라이언트 ID (수정 시에만 제공)",
        min_length=1,
        example="client_456",
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "수정된 프로젝트명",
                "description": "수정된 프로젝트 설명입니다.",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "workspace_status": "IN_PROGRESS",
                "owner_id": "user_123456",
                "team_id": "team_789",
                "client_id": "client_456",
            }
        }


class WorkspaceDeleteSchema(BaseModel):
    workspace_id: str = Field(
        ...,
        description="삭제할 워크스페이스의 고유 ID",
        min_length=1,
        example="ws_123456",
    )

    class Config:
        schema_extra = {"example": {"workspace_id": "ws_123456"}}


class WorkspaceGetSchema(BaseModel):
    workspace_id: str = Field(
        ...,
        description="조회할 워크스페이스의 고유 ID",
        min_length=1,
        example="ws_123456",
    )

    class Config:
        schema_extra = {"example": {"workspace_id": "ws_123456"}}


class WorkspaceListSchema(BaseModel):
    page: int = Field(
        default=1, ge=1, description="페이지 번호 (1부터 시작)", example=1
    )
    limit: int = Field(
        default=10, ge=1, le=100, description="페이지 크기 (최대 100개)", example=10
    )
    search: Optional[str] = Field(
        None,
        description="검색어 (워크스페이스 이름 또는 설명에서 검색)",
        min_length=1,
        example="프로젝트",
    )
    status: Optional[WorkspaceStatus] = Field(
        None, description="상태별 필터링", example=WorkspaceStatus.ACTIVE
    )
    owner_id: Optional[str] = Field(
        None, description="소유자 ID로 필터링", min_length=1, example="user_123456"
    )
    team_id: Optional[str] = Field(
        None, description="팀 ID로 필터링", min_length=1, example="team_789"
    )
    client_id: Optional[str] = Field(
        None, description="클라이언트 ID로 필터링", min_length=1, example="client_456"
    )

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 10,
                "search": "프로젝트",
                "status": "ACTIVE",
                "owner_id": "user_123456",
                "team_id": "team_789",
                "client_id": "client_456",
            }
        }


class WorkspaceStatusChangeSchema(BaseModel):
    workspace_id: str = Field(
        ...,
        description="상태를 변경할 워크스페이스의 고유 ID",
        min_length=1,
        example="ws_123456",
    )
    new_status: WorkspaceStatus = Field(
        ..., description="새로운 워크스페이스 상태", example=WorkspaceStatus.IN_PROGRESS
    )

    class Config:
        schema_extra = {
            "example": {"workspace_id": "ws_123456", "new_status": "IN_PROGRESS"}
        }


class WorkspaceResponseSchema(BaseModel):
    id: str = Field(..., description="워크스페이스 고유 ID", example="ws_123456")
    name: str = Field(..., description="워크스페이스 이름", example="새로운 프로젝트")
    description: Optional[str] = Field(
        None, description="워크스페이스 설명", example="프로젝트 설명"
    )
    start_date: datetime = Field(
        ..., description="시작 날짜", example="2024-01-01T00:00:00"
    )
    end_date: datetime = Field(
        ..., description="종료 날짜", example="2024-12-31T23:59:59"
    )
    workspace_status: WorkspaceStatus = Field(
        ..., description="워크스페이스 상태", example=WorkspaceStatus.ACTIVE
    )
    owner_id: str = Field(..., description="소유자 ID", example="user_123456")
    team_id: str = Field(..., description="팀 ID", example="team_789")
    client_id: str = Field(..., description="클라이언트 ID", example="client_456")
    created_at: datetime = Field(
        ..., description="생성 날짜", example="2024-01-01T00:00:00"
    )
    updated_at: datetime = Field(
        ..., description="수정 날짜", example="2024-01-01T00:00:00"
    )

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "ws_123456",
                "name": "새로운 프로젝트",
                "description": "프로젝트 설명",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "workspace_status": "ACTIVE",
                "owner_id": "user_123456",
                "team_id": "team_789",
                "client_id": "client_456",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }


class WorkspaceListResponseSchema(BaseModel):
    workspaces: list[WorkspaceResponseSchema] = Field(
        ..., description="워크스페이스 목록"
    )
    total: int = Field(..., description="전체 워크스페이스 개수", example=100)
    page: int = Field(..., description="현재 페이지 번호", example=1)
    limit: int = Field(..., description="페이지 크기", example=10)
    has_next: bool = Field(..., description="다음 페이지 존재 여부", example=False)
    has_prev: bool = Field(..., description="이전 페이지 존재 여부", example=False)

    class Config:
        schema_extra = {
            "example": {
                "workspaces": [
                    {
                        "id": "ws_123456",
                        "name": "새로운 프로젝트",
                        "description": "프로젝트 설명",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "workspace_status": "ACTIVE",
                        "owner_id": "user_123456",
                        "team_id": "team_789",
                        "client_id": "client_456",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00",
                    }
                ],
                "total": 100,
                "page": 1,
                "limit": 10,
                "has_next": False,
                "has_prev": False,
            }
        }


class WorkspaceStatisticsResponseSchema(BaseModel):
    total: int = Field(..., description="전체 워크스페이스 수", example=100)
    active: int = Field(..., description="활성 워크스페이스 수", example=30)
    inactive: int = Field(..., description="비활성 워크스페이스 수", example=10)
    completed: int = Field(..., description="완료된 워크스페이스 수", example=40)
    cancelled: int = Field(..., description="취소된 워크스페이스 수", example=5)
    on_hold: int = Field(..., description="보류 중인 워크스페이스 수", example=8)
    in_progress: int = Field(..., description="진행 중인 워크스페이스 수", example=5)
    pending: int = Field(..., description="대기 중인 워크스페이스 수", example=2)

    class Config:
        schema_extra = {
            "example": {
                "total": 100,
                "active": 30,
                "inactive": 10,
                "completed": 40,
                "cancelled": 5,
                "on_hold": 8,
                "in_progress": 5,
                "pending": 2,
            }
        }
