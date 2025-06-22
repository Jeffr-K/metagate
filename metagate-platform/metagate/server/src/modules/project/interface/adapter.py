from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.modules.project.core.value import ProjectStatus


class ProjectCreateSchema(BaseModel):
    name: str = Field(..., description="프로젝트 이름", min_length=1, max_length=100, example="새로운 프로젝트")
    description: str = Field(
        ..., description="프로젝트 설명", min_length=1, max_length=500, example="이 프로젝트는 새로운 기능을 개발하는 프로젝트입니다."
    )
    start_date: datetime = Field(..., description="프로젝트 시작 날짜 및 시간", example="2024-01-01T00:00:00")
    end_date: datetime = Field(..., description="프로젝트 종료 날짜 및 시간 (시작 날짜보다 이후여야 함)", example="2024-12-31T23:59:59")
    project_status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, description="프로젝트 상태 (기본값: ACTIVE)", example=ProjectStatus.ACTIVE)
    owner_id: str = Field(..., description="프로젝트 소유자 ID", min_length=1, example="user_123456")
    team_id: str = Field(..., description="프로젝트 담당 팀 ID", min_length=1, example="team_789")
    client_id: str = Field(..., description="프로젝트 클라이언트 ID", min_length=1, example="client_456")
    workspace_id: Optional[str] = Field(None, description="연관된 워크스페이스 ID (선택사항)", example="ws_123456")
    budget: Optional[float] = Field(None, description="프로젝트 예산", ge=0, example=1000000.0)
    priority: Optional[str] = Field(None, description="프로젝트 우선순위 (HIGH, MEDIUM, LOW)", example="HIGH")

    class Config:
        schema_extra = {
            "example": {
                "name": "새로운 프로젝트",
                "description": "이 프로젝트는 새로운 기능을 개발하는 프로젝트입니다.",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "project_status": "ACTIVE",
                "owner_id": "user_123456",
                "team_id": "team_789",
                "client_id": "client_456",
                "workspace_id": "ws_123456",
                "budget": 1000000.0,
                "priority": "HIGH",
            }
        }


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="프로젝트 이름 (수정 시에만 제공)", min_length=1, max_length=100, example="수정된 프로젝트명")
    description: Optional[str] = Field(
        None, description="프로젝트 설명 (수정 시에만 제공)", min_length=1, max_length=500, example="수정된 프로젝트 설명입니다."
    )
    start_date: Optional[datetime] = Field(None, description="프로젝트 시작 날짜 및 시간 (수정 시에만 제공)", example="2024-01-01T00:00:00")
    end_date: Optional[datetime] = Field(
        None, description="프로젝트 종료 날짜 및 시간 (수정 시에만 제공, 시작 날짜보다 이후여야 함)", example="2024-12-31T23:59:59"
    )
    project_status: Optional[ProjectStatus] = Field(None, description="프로젝트 상태 (수정 시에만 제공)", example=ProjectStatus.IN_PROGRESS)
    owner_id: Optional[str] = Field(None, description="프로젝트 소유자 ID (수정 시에만 제공)", min_length=1, example="user_123456")
    team_id: Optional[str] = Field(None, description="프로젝트 담당 팀 ID (수정 시에만 제공)", min_length=1, example="team_789")
    client_id: Optional[str] = Field(None, description="프로젝트 클라이언트 ID (수정 시에만 제공)", min_length=1, example="client_456")
    workspace_id: Optional[str] = Field(None, description="연관된 워크스페이스 ID (수정 시에만 제공)", example="ws_123456")
    budget: Optional[float] = Field(None, description="프로젝트 예산 (수정 시에만 제공)", ge=0, example=1500000.0)
    priority: Optional[str] = Field(None, description="프로젝트 우선순위 (수정 시에만 제공)", example="MEDIUM")

    class Config:
        schema_extra = {
            "example": {
                "name": "수정된 프로젝트명",
                "description": "수정된 프로젝트 설명입니다.",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "project_status": "IN_PROGRESS",
                "owner_id": "user_123456",
                "team_id": "team_789",
                "client_id": "client_456",
                "workspace_id": "ws_123456",
                "budget": 1500000.0,
                "priority": "MEDIUM",
            }
        }


class ProjectDeleteSchema(BaseModel):
    project_id: str = Field(..., description="삭제할 프로젝트의 고유 ID", min_length=1, example="proj_123456")

    class Config:
        schema_extra = {"example": {"project_id": "proj_123456"}}


class ProjectGetSchema(BaseModel):
    project_id: str = Field(..., description="조회할 프로젝트의 고유 ID", min_length=1, example="proj_123456")

    class Config:
        schema_extra = {"example": {"project_id": "proj_123456"}}


class ProjectListSchema(BaseModel):
    page: int = Field(default=1, ge=1, description="페이지 번호 (1부터 시작)", example=1)
    limit: int = Field(default=10, ge=1, le=100, description="페이지 크기 (최대 100개)", example=10)
    search: Optional[str] = Field(None, description="검색어 (프로젝트 이름 또는 설명에서 검색)", min_length=1, example="프로젝트")
    status: Optional[ProjectStatus] = Field(None, description="상태별 필터링", example=ProjectStatus.ACTIVE)
    owner_id: Optional[str] = Field(None, description="소유자 ID로 필터링", min_length=1, example="user_123456")
    team_id: Optional[str] = Field(None, description="팀 ID로 필터링", min_length=1, example="team_789")
    client_id: Optional[str] = Field(None, description="클라이언트 ID로 필터링", min_length=1, example="client_456")
    workspace_id: Optional[str] = Field(None, description="워크스페이스 ID로 필터링", min_length=1, example="ws_123456")
    priority: Optional[str] = Field(None, description="우선순위로 필터링", example="HIGH")

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
                "workspace_id": "ws_123456",
                "priority": "HIGH",
            }
        }


class ProjectStatusChangeSchema(BaseModel):
    project_id: str = Field(..., description="상태를 변경할 프로젝트의 고유 ID", min_length=1, example="proj_123456")
    new_status: ProjectStatus = Field(..., description="새로운 프로젝트 상태", example=ProjectStatus.IN_PROGRESS)

    class Config:
        schema_extra = {"example": {"project_id": "proj_123456", "new_status": "IN_PROGRESS"}}


class ProjectResponseSchema(BaseModel):
    id: str = Field(..., description="프로젝트 고유 ID", example="proj_123456")
    name: str = Field(..., description="프로젝트 이름", example="새로운 프로젝트")
    description: Optional[str] = Field(None, description="프로젝트 설명", example="프로젝트 설명")
    start_date: datetime = Field(..., description="시작 날짜", example="2024-01-01T00:00:00")
    end_date: datetime = Field(..., description="종료 날짜", example="2024-12-31T23:59:59")
    project_status: ProjectStatus = Field(..., description="프로젝트 상태", example=ProjectStatus.ACTIVE)
    owner_id: str = Field(..., description="소유자 ID", example="user_123456")
    team_id: str = Field(..., description="팀 ID", example="team_789")
    client_id: str = Field(..., description="클라이언트 ID", example="client_456")
    workspace_id: Optional[str] = Field(None, description="워크스페이스 ID", example="ws_123456")
    budget: Optional[float] = Field(None, description="예산", example=1000000.0)
    priority: Optional[str] = Field(None, description="우선순위", example="HIGH")
    created_at: datetime = Field(..., description="생성 날짜", example="2024-01-01T00:00:00")
    updated_at: datetime = Field(..., description="수정 날짜", example="2024-01-01T00:00:00")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "proj_123456",
                "name": "새로운 프로젝트",
                "description": "프로젝트 설명",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "project_status": "ACTIVE",
                "owner_id": "user_123456",
                "team_id": "team_789",
                "client_id": "client_456",
                "workspace_id": "ws_123456",
                "budget": 1000000.0,
                "priority": "HIGH",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }


class ProjectListResponseSchema(BaseModel):
    projects: list[ProjectResponseSchema] = Field(..., description="프로젝트 목록")
    total: int = Field(..., description="전체 프로젝트 개수", example=100)
    page: int = Field(..., description="현재 페이지 번호", example=1)
    limit: int = Field(..., description="페이지 크기", example=10)
    has_next: bool = Field(..., description="다음 페이지 존재 여부", example=False)
    has_prev: bool = Field(..., description="이전 페이지 존재 여부", example=False)

    class Config:
        schema_extra = {
            "example": {
                "projects": [
                    {
                        "id": "proj_123456",
                        "name": "새로운 프로젝트",
                        "description": "프로젝트 설명",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "project_status": "ACTIVE",
                        "owner_id": "user_123456",
                        "team_id": "team_789",
                        "client_id": "client_456",
                        "workspace_id": "ws_123456",
                        "budget": 1000000.0,
                        "priority": "HIGH",
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


class ProjectStatisticsResponseSchema(BaseModel):
    total: int = Field(..., description="전체 프로젝트 수", example=100)
    active: int = Field(..., description="활성 프로젝트 수", example=30)
    inactive: int = Field(..., description="비활성 프로젝트 수", example=10)
    completed: int = Field(..., description="완료된 프로젝트 수", example=40)
    cancelled: int = Field(..., description="취소된 프로젝트 수", example=5)
    on_hold: int = Field(..., description="보류 중인 프로젝트 수", example=8)
    in_progress: int = Field(..., description="진행 중인 프로젝트 수", example=5)
    pending: int = Field(..., description="대기 중인 프로젝트 수", example=2)
    planning: int = Field(..., description="계획 중인 프로젝트 수", example=3)
    review: int = Field(..., description="검토 중인 프로젝트 수", example=1)

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
                "planning": 3,
                "review": 1,
            }
        }
