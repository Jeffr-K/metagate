from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from src.modules.project.core.command import (
    change_project_status,
    create_project,
    delete_project,
    update_project,
)
from src.modules.project.core.query import (
    get_project_by_id,
    get_project_statistics,
    get_projects_by_owner,
    get_projects_by_status,
    get_projects_by_workspace,
    search_projects,
)
from src.modules.project.interface.adapter import (
    ProjectCreateSchema,
    ProjectDeleteSchema,
    ProjectGetSchema,
    ProjectListResponseSchema,
    ProjectListSchema,
    ProjectResponseSchema,
    ProjectStatisticsResponseSchema,
    ProjectStatusChangeSchema,
    ProjectUpdateSchema,
)

projects = APIRouter(
    prefix="/projects", tags=["projects"], responses={404: {"description": "프로젝트를 찾을 수 없습니다"}, 500: {"description": "서버 내부 오류"}}
)


@projects.get(
    "/",
    response_model=ProjectListResponseSchema,
    summary="프로젝트 목록 조회",
    description="""
    프로젝트 목록을 페이지네이션과 필터링을 통해 조회합니다.
    
    **기능:**
    - 페이지네이션 지원 (page, limit)
    - 검색어로 프로젝트 이름/설명 검색
    - 상태별 필터링
    - 소유자, 팀, 클라이언트, 워크스페이스별 필터링
    - 우선순위별 필터링
    
    **응답:**
    - 프로젝트 목록
    - 전체 개수 및 페이지네이션 정보
    """,
    responses={
        200: {
            "description": "프로젝트 목록 조회 성공",
            "content": {
                "application/json": {
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
                        "total": 1,
                        "page": 1,
                        "limit": 10,
                        "has_next": False,
                        "has_prev": False,
                    }
                }
            },
        },
        400: {
            "description": "잘못된 요청",
            "content": {"application/json": {"example": {"detail": "유효하지 않은 상태입니다: INVALID_STATUS"}}},
        },
    },
)
async def get_projects(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    limit: int = Query(10, ge=1, le=100, description="페이지 크기 (최대 100)"),
    search: str = Query(None, description="검색어 (프로젝트 이름 또는 설명에서 검색)"),
    status: str = Query(None, description="상태 필터 (ACTIVE, INACTIVE, COMPLETED, CANCELLED, ON_HOLD, IN_PROGRESS, PENDING, PLANNING, REVIEW)"),
    owner_id: str = Query(None, description="소유자 ID로 필터링"),
    team_id: str = Query(None, description="팀 ID로 필터링"),
    client_id: str = Query(None, description="클라이언트 ID로 필터링"),
    workspace_id: str = Query(None, description="워크스페이스 ID로 필터링"),
    priority: str = Query(None, description="우선순위로 필터링 (HIGH, MEDIUM, LOW)"),
):
    """프로젝트 목록 조회"""
    try:
        from src.modules.project.core.value import ProjectStatus

        # 상태 문자열을 enum으로 변환
        status_enum = None
        if status:
            try:
                status_enum = ProjectStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"유효하지 않은 상태입니다: {status}")

        # 검색 실행
        projects_list = await search_projects(
            search_term=search,
            status=status_enum,
            owner_id=owner_id,
            team_id=team_id,
            client_id=client_id,
            workspace_id=workspace_id,
            priority=priority,
            skip=(page - 1) * limit,
            limit=limit,
        )

        # 전체 개수 조회 (간단한 구현)
        total = len(projects_list)  # 실제로는 별도 쿼리 필요

        # 응답 구성
        project_responses = [ProjectResponseSchema.from_orm(project) for project in projects_list]

        return ProjectListResponseSchema(
            projects=project_responses,
            total=total,
            page=page,
            limit=limit,
            has_next=total > page * limit,
            has_prev=page > 1,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 목록 조회 실패: {str(e)}")


@projects.get(
    "/{project_id}",
    response_model=ProjectResponseSchema,
    summary="프로젝트 상세 조회",
    description="""
    특정 프로젝트의 상세 정보를 조회합니다.
    
    **파라미터:**
    - project_id: 조회할 프로젝트의 고유 ID
    
    **응답:**
    - 프로젝트의 모든 상세 정보
    """,
    responses={
        200: {
            "description": "프로젝트 조회 성공",
            "content": {
                "application/json": {
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
            },
        },
        404: {
            "description": "프로젝트를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "프로젝트를 찾을 수 없습니다."}}},
        },
    },
)
async def get_project(project_id: str):
    """프로젝트 상세 조회"""
    try:
        project = await get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

        return ProjectResponseSchema.from_orm(project)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 조회 실패: {str(e)}")


@projects.post(
    "/",
    response_model=ProjectResponseSchema,
    status_code=201,
    summary="프로젝트 생성",
    description="""
    새로운 프로젝트를 생성합니다.
    
    **필수 필드:**
    - name: 프로젝트 이름
    - description: 프로젝트 설명
    - start_date: 시작 날짜
    - end_date: 종료 날짜
    - owner_id: 소유자 ID
    - team_id: 팀 ID
    - client_id: 클라이언트 ID
    
    **선택 필드:**
    - project_status: 프로젝트 상태 (기본값: ACTIVE)
    - workspace_id: 연관된 워크스페이스 ID
    - budget: 프로젝트 예산
    - priority: 프로젝트 우선순위
    """,
    responses={
        201: {
            "description": "프로젝트 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "proj_123456",
                        "name": "새로운 프로젝트",
                        "description": "새로 생성된 프로젝트입니다",
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
            },
        },
        400: {
            "description": "잘못된 요청 데이터",
            "content": {"application/json": {"example": {"detail": "종료 날짜는 시작 날짜보다 이후여야 합니다."}}},
        },
    },
)
async def create_project_endpoint(project_data: ProjectCreateSchema):
    """프로젝트 생성"""
    try:
        project = await create_project(
            name=project_data.name,
            description=project_data.description,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            project_status=project_data.project_status,
            owner_id=project_data.owner_id,
            team_id=project_data.team_id,
            client_id=project_data.client_id,
            workspace_id=project_data.workspace_id,
            budget=project_data.budget,
            priority=project_data.priority,
        )

        return ProjectResponseSchema.from_orm(project)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 생성 실패: {str(e)}")


@projects.put(
    "/{project_id}",
    response_model=ProjectResponseSchema,
    summary="프로젝트 수정",
    description="""
    기존 프로젝트의 정보를 수정합니다.
    
    **파라미터:**
    - project_id: 수정할 프로젝트의 고유 ID
    
    **수정 가능한 필드:**
    - name: 프로젝트 이름
    - description: 프로젝트 설명
    - start_date: 시작 날짜
    - end_date: 종료 날짜
    - project_status: 프로젝트 상태
    - owner_id: 소유자 ID
    - team_id: 팀 ID
    - client_id: 클라이언트 ID
    - workspace_id: 워크스페이스 ID
    - budget: 프로젝트 예산
    - priority: 프로젝트 우선순위
    
    **참고:** 모든 필드는 선택사항이며, 제공된 필드만 업데이트됩니다.
    """,
    responses={
        200: {
            "description": "프로젝트 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "proj_123456",
                        "name": "수정된 프로젝트",
                        "description": "수정된 프로젝트 설명",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "project_status": "IN_PROGRESS",
                        "owner_id": "user_123456",
                        "team_id": "team_789",
                        "client_id": "client_456",
                        "workspace_id": "ws_123456",
                        "budget": 1500000.0,
                        "priority": "MEDIUM",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-02T00:00:00",
                    }
                }
            },
        },
        400: {
            "description": "잘못된 요청 데이터",
            "content": {"application/json": {"example": {"detail": "종료 날짜는 시작 날짜보다 이후여야 합니다."}}},
        },
        404: {
            "description": "프로젝트를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "프로젝트를 찾을 수 없습니다."}}},
        },
    },
)
async def update_project_endpoint(project_id: str, project_data: ProjectUpdateSchema):
    """프로젝트 수정"""
    try:
        project = await update_project(
            project_id=project_id,
            name=project_data.name,
            description=project_data.description,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            project_status=project_data.project_status,
            owner_id=project_data.owner_id,
            team_id=project_data.team_id,
            client_id=project_data.client_id,
            workspace_id=project_data.workspace_id,
            budget=project_data.budget,
            priority=project_data.priority,
        )

        if not project:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

        return ProjectResponseSchema.from_orm(project)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 수정 실패: {str(e)}")


@projects.delete(
    "/{project_id}",
    summary="프로젝트 삭제",
    description="""
    프로젝트를 삭제합니다.
    
    **파라미터:**
    - project_id: 삭제할 프로젝트의 고유 ID
    
    **주의:** 삭제된 프로젝트는 복구할 수 없습니다.
    """,
    responses={
        200: {
            "description": "프로젝트 삭제 성공",
            "content": {"application/json": {"example": {"message": "프로젝트 proj_123456가 삭제되었습니다."}}},
        },
        400: {
            "description": "잘못된 요청",
            "content": {"application/json": {"example": {"detail": "진행 중인 프로젝트는 삭제할 수 없습니다."}}},
        },
        404: {
            "description": "프로젝트를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "프로젝트를 찾을 수 없습니다."}}},
        },
    },
)
async def delete_project_endpoint(project_id: str):
    """프로젝트 삭제"""
    try:
        deleted = await delete_project(project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

        return {"message": f"프로젝트 {project_id}가 삭제되었습니다."}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 삭제 실패: {str(e)}")


@projects.patch(
    "/{project_id}/status",
    response_model=ProjectResponseSchema,
    summary="프로젝트 상태 변경",
    description="""
    프로젝트의 상태를 변경합니다.
    
    **파라미터:**
    - project_id: 상태를 변경할 프로젝트의 고유 ID
    
    **요청 본문:**
    - new_status: 새로운 상태 (ACTIVE, INACTIVE, COMPLETED, CANCELLED, ON_HOLD, IN_PROGRESS, PENDING, PLANNING, REVIEW)
    
    **상태 설명:**
    - ACTIVE: 활성 상태
    - INACTIVE: 비활성 상태
    - COMPLETED: 완료됨
    - CANCELLED: 취소됨
    - ON_HOLD: 보류 중
    - IN_PROGRESS: 진행 중
    - PENDING: 대기 중
    - PLANNING: 계획 중
    - REVIEW: 검토 중
    """,
    responses={
        200: {
            "description": "상태 변경 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "proj_123456",
                        "name": "새로운 프로젝트",
                        "description": "프로젝트 설명",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "project_status": "IN_PROGRESS",
                        "owner_id": "user_123456",
                        "team_id": "team_789",
                        "client_id": "client_456",
                        "workspace_id": "ws_123456",
                        "budget": 1000000.0,
                        "priority": "HIGH",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-02T00:00:00",
                    }
                }
            },
        },
        400: {
            "description": "잘못된 상태 값",
            "content": {"application/json": {"example": {"detail": "유효하지 않은 상태입니다: INVALID_STATUS"}}},
        },
        404: {
            "description": "프로젝트를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "프로젝트를 찾을 수 없습니다."}}},
        },
    },
)
async def change_project_status_endpoint(project_id: str, status_data: ProjectStatusChangeSchema):
    """프로젝트 상태 변경"""
    try:
        project = await change_project_status(project_id=project_id, new_status=status_data.new_status)

        if not project:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

        return ProjectResponseSchema.from_orm(project)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 상태 변경 실패: {str(e)}")


@projects.get(
    "/owner/{owner_id}",
    response_model=List[ProjectResponseSchema],
    summary="소유자별 프로젝트 조회",
    description="""
    특정 소유자가 소유한 프로젝트 목록을 조회합니다.
    
    **파라미터:**
    - owner_id: 소유자 ID
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지 크기 (기본값: 10, 최대: 100)
    
    **응답:**
    - 해당 소유자가 소유한 프로젝트 목록
    """,
    responses={
        200: {
            "description": "소유자별 프로젝트 조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "proj_123456",
                            "name": "새로운 프로젝트",
                            "description": "소유자 A의 프로젝트",
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
                    ]
                }
            },
        }
    },
)
async def get_projects_by_owner_endpoint(
    owner_id: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지 크기"),
):
    """소유자별 프로젝트 조회"""
    try:
        projects_list = await get_projects_by_owner(owner_id=owner_id, skip=(page - 1) * limit, limit=limit)

        return [ProjectResponseSchema.from_orm(project) for project in projects_list]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"소유자별 프로젝트 조회 실패: {str(e)}")


@projects.get(
    "/status/{status}",
    response_model=List[ProjectResponseSchema],
    summary="상태별 프로젝트 조회",
    description="""
    특정 상태의 프로젝트 목록을 조회합니다.
    
    **파라미터:**
    - status: 조회할 상태 (ACTIVE, INACTIVE, COMPLETED, CANCELLED, ON_HOLD, IN_PROGRESS, PENDING, PLANNING, REVIEW)
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지 크기 (기본값: 10, 최대: 100)
    
    **응답:**
    - 해당 상태의 프로젝트 목록
    """,
    responses={
        200: {
            "description": "상태별 프로젝트 조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "proj_123456",
                            "name": "진행 중인 프로젝트",
                            "description": "현재 진행 중인 프로젝트",
                            "start_date": "2024-01-01T00:00:00",
                            "end_date": "2024-12-31T23:59:59",
                            "project_status": "IN_PROGRESS",
                            "owner_id": "user_123456",
                            "team_id": "team_789",
                            "client_id": "client_456",
                            "workspace_id": "ws_123456",
                            "budget": 1000000.0,
                            "priority": "HIGH",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00",
                        }
                    ]
                }
            },
        },
        400: {
            "description": "잘못된 상태 값",
            "content": {"application/json": {"example": {"detail": "유효하지 않은 상태입니다: INVALID_STATUS"}}},
        },
    },
)
async def get_projects_by_status_endpoint(
    status: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지 크기"),
):
    """상태별 프로젝트 조회"""
    try:
        from src.modules.project.core.value import ProjectStatus

        try:
            status_enum = ProjectStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"유효하지 않은 상태입니다: {status}")

        projects_list = await get_projects_by_status(status=status_enum, skip=(page - 1) * limit, limit=limit)

        return [ProjectResponseSchema.from_orm(project) for project in projects_list]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태별 프로젝트 조회 실패: {str(e)}")


@projects.get(
    "/workspace/{workspace_id}",
    response_model=List[ProjectResponseSchema],
    summary="워크스페이스별 프로젝트 조회",
    description="""
    특정 워크스페이스에 속한 프로젝트 목록을 조회합니다.
    
    **파라미터:**
    - workspace_id: 워크스페이스 ID
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지 크기 (기본값: 10, 최대: 100)
    
    **응답:**
    - 해당 워크스페이스에 속한 프로젝트 목록
    """,
    responses={
        200: {
            "description": "워크스페이스별 프로젝트 조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "proj_123456",
                            "name": "워크스페이스 프로젝트",
                            "description": "워크스페이스에 속한 프로젝트",
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
                    ]
                }
            },
        }
    },
)
async def get_projects_by_workspace_endpoint(
    workspace_id: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지 크기"),
):
    """워크스페이스별 프로젝트 조회"""
    try:
        projects_list = await get_projects_by_workspace(workspace_id=workspace_id, skip=(page - 1) * limit, limit=limit)

        return [ProjectResponseSchema.from_orm(project) for project in projects_list]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스별 프로젝트 조회 실패: {str(e)}")


@projects.get(
    "/statistics/overview",
    response_model=ProjectStatisticsResponseSchema,
    summary="프로젝트 통계 조회",
    description="""
    전체 프로젝트의 통계 정보를 조회합니다.
    
    **응답 정보:**
    - total: 전체 프로젝트 수
    - active: 활성 프로젝트 수
    - inactive: 비활성 프로젝트 수
    - completed: 완료된 프로젝트 수
    - cancelled: 취소된 프로젝트 수
    - on_hold: 보류 중인 프로젝트 수
    - in_progress: 진행 중인 프로젝트 수
    - pending: 대기 중인 프로젝트 수
    - planning: 계획 중인 프로젝트 수
    - review: 검토 중인 프로젝트 수
    """,
    responses={
        200: {
            "description": "프로젝트 통계 조회 성공",
            "content": {
                "application/json": {
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
            },
        }
    },
)
async def get_project_statistics_endpoint():
    """프로젝트 통계 조회"""
    try:
        stats = await get_project_statistics()

        return ProjectStatisticsResponseSchema(
            total=stats.get("active", 0)
            + stats.get("inactive", 0)
            + stats.get("completed", 0)
            + stats.get("cancelled", 0)
            + stats.get("on_hold", 0)
            + stats.get("in_progress", 0)
            + stats.get("pending", 0)
            + stats.get("planning", 0)
            + stats.get("review", 0),
            active=stats.get("active", 0),
            inactive=stats.get("inactive", 0),
            completed=stats.get("completed", 0),
            cancelled=stats.get("cancelled", 0),
            on_hold=stats.get("on_hold", 0),
            in_progress=stats.get("in_progress", 0),
            pending=stats.get("pending", 0),
            planning=stats.get("planning", 0),
            review=stats.get("review", 0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 통계 조회 실패: {str(e)}")
