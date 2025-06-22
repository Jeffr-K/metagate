from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from src.modules.workspace.core.command import (
    change_workspace_status,
    create_workspace,
    delete_workspace,
    update_workspace,
)
from src.modules.workspace.core.query import (
    get_workspace_by_id,
    get_workspace_statistics,
    get_workspaces_by_owner,
    get_workspaces_by_status,
    search_workspaces,
)
from src.modules.workspace.interface.adapter import (
    WorkspaceCreateSchema,
    WorkspaceDeleteSchema,
    WorkspaceGetSchema,
    WorkspaceListResponseSchema,
    WorkspaceListSchema,
    WorkspaceResponseSchema,
    WorkspaceStatisticsResponseSchema,
    WorkspaceStatusChangeSchema,
    WorkspaceUpdateSchema,
)

workspaces = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"],
    responses={
        404: {"description": "워크스페이스를 찾을 수 없습니다"},
        500: {"description": "서버 내부 오류"},
    },
)


@workspaces.get(
    "/",
    response_model=WorkspaceListResponseSchema,
    summary="워크스페이스 목록 조회",
    description="""
    워크스페이스 목록을 페이지네이션과 필터링을 통해 조회합니다.
    
    **기능:**
    - 페이지네이션 지원 (page, limit)
    - 검색어로 워크스페이스 이름/설명 검색
    - 상태별 필터링
    - 소유자, 팀, 클라이언트별 필터링
    
    **응답:**
    - 워크스페이스 목록
    - 전체 개수 및 페이지네이션 정보
    """,
    responses={
        200: {
            "description": "워크스페이스 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "workspaces": [
                            {
                                "id": "ws_123456",
                                "name": "프로젝트 A",
                                "description": "새로운 프로젝트",
                                "start_date": "2024-01-01T00:00:00",
                                "end_date": "2024-12-31T23:59:59",
                                "workspace_status": "ACTIVE",
                                "owner_id": "user_123",
                                "team_id": "team_456",
                                "client_id": "client_789",
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
async def get_workspaces(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    limit: int = Query(10, ge=1, le=100, description="페이지 크기 (최대 100)"),
    search: str = Query(None, description="검색어 (워크스페이스 이름 또는 설명에서 검색)"),
    status: str = Query(
        None,
        description="상태 필터 (ACTIVE, INACTIVE, COMPLETED, CANCELLED, ON_HOLD, IN_PROGRESS, PENDING)",
    ),
    owner_id: str = Query(None, description="소유자 ID로 필터링"),
    team_id: str = Query(None, description="팀 ID로 필터링"),
    client_id: str = Query(None, description="클라이언트 ID로 필터링"),
):
    """워크스페이스 목록 조회"""
    try:
        from src.modules.workspace.core.value import WorkspaceStatus

        # 상태 문자열을 enum으로 변환
        status_enum = None
        if status:
            try:
                status_enum = WorkspaceStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"유효하지 않은 상태입니다: {status}")

        # 검색 실행
        workspaces_list = await search_workspaces(
            search_term=search,
            status=status_enum,
            owner_id=owner_id,
            team_id=team_id,
            client_id=client_id,
            skip=(page - 1) * limit,
            limit=limit,
        )

        # 전체 개수 조회 (간단한 구현)
        total = len(workspaces_list)  # 실제로는 별도 쿼리 필요

        # 응답 구성
        workspace_responses = [WorkspaceResponseSchema.from_orm(workspace) for workspace in workspaces_list]

        return WorkspaceListResponseSchema(
            workspaces=workspace_responses,
            total=total,
            page=page,
            limit=limit,
            has_next=total > page * limit,
            has_prev=page > 1,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스 목록 조회 실패: {str(e)}")


@workspaces.get(
    "/{workspace_id}",
    response_model=WorkspaceResponseSchema,
    summary="워크스페이스 상세 조회",
    description="""
    특정 워크스페이스의 상세 정보를 조회합니다.
    
    **파라미터:**
    - workspace_id: 조회할 워크스페이스의 고유 ID
    
    **응답:**
    - 워크스페이스의 모든 상세 정보
    """,
    responses={
        200: {
            "description": "워크스페이스 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ws_123456",
                        "name": "프로젝트 A",
                        "description": "새로운 프로젝트",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "workspace_status": "ACTIVE",
                        "owner_id": "user_123",
                        "team_id": "team_456",
                        "client_id": "client_789",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00",
                    }
                }
            },
        },
        404: {
            "description": "워크스페이스를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "워크스페이스를 찾을 수 없습니다."}}},
        },
    },
)
async def get_workspace(workspace_id: str):
    """워크스페이스 상세 조회"""
    try:
        workspace = await get_workspace_by_id(workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="워크스페이스를 찾을 수 없습니다.")

        return WorkspaceResponseSchema.from_orm(workspace)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스 조회 실패: {str(e)}")


@workspaces.post(
    "/",
    response_model=WorkspaceResponseSchema,
    status_code=201,
    summary="워크스페이스 생성",
    description="""
    새로운 워크스페이스를 생성합니다.
    
    **필수 필드:**
    - name: 워크스페이스 이름
    - description: 워크스페이스 설명
    - start_date: 시작 날짜
    - end_date: 종료 날짜
    - owner_id: 소유자 ID
    - team_id: 팀 ID
    - client_id: 클라이언트 ID
    
    **선택 필드:**
    - workspace_status: 워크스페이스 상태 (기본값: ACTIVE)
    """,
    responses={
        201: {
            "description": "워크스페이스 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ws_123456",
                        "name": "새로운 프로젝트",
                        "description": "새로 생성된 프로젝트입니다",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "workspace_status": "ACTIVE",
                        "owner_id": "user_123",
                        "team_id": "team_456",
                        "client_id": "client_789",
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
async def create_workspace_endpoint(workspace_data: WorkspaceCreateSchema):
    """워크스페이스 생성"""
    try:
        workspace = await create_workspace(
            name=workspace_data.name,
            description=workspace_data.description,
            start_date=workspace_data.start_date,
            end_date=workspace_data.end_date,
            workspace_status=workspace_data.workspace_status,
            owner_id=workspace_data.owner_id,
            team_id=workspace_data.team_id,
            client_id=workspace_data.client_id,
        )

        return WorkspaceResponseSchema.from_orm(workspace)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스 생성 실패: {str(e)}")


@workspaces.put(
    "/{workspace_id}",
    response_model=WorkspaceResponseSchema,
    summary="워크스페이스 수정",
    description="""
    기존 워크스페이스의 정보를 수정합니다.
    
    **파라미터:**
    - workspace_id: 수정할 워크스페이스의 고유 ID
    
    **수정 가능한 필드:**
    - name: 워크스페이스 이름
    - description: 워크스페이스 설명
    - start_date: 시작 날짜
    - end_date: 종료 날짜
    - workspace_status: 워크스페이스 상태
    - owner_id: 소유자 ID
    - team_id: 팀 ID
    - client_id: 클라이언트 ID
    
    **참고:** 모든 필드는 선택사항이며, 제공된 필드만 업데이트됩니다.
    """,
    responses={
        200: {
            "description": "워크스페이스 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ws_123456",
                        "name": "수정된 프로젝트",
                        "description": "수정된 프로젝트 설명",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "workspace_status": "IN_PROGRESS",
                        "owner_id": "user_123",
                        "team_id": "team_456",
                        "client_id": "client_789",
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
            "description": "워크스페이스를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "워크스페이스를 찾을 수 없습니다."}}},
        },
    },
)
async def update_workspace_endpoint(workspace_id: str, workspace_data: WorkspaceUpdateSchema):
    """워크스페이스 수정"""
    try:
        workspace = await update_workspace(
            workspace_id=workspace_id,
            name=workspace_data.name,
            description=workspace_data.description,
            start_date=workspace_data.start_date,
            end_date=workspace_data.end_date,
            workspace_status=workspace_data.workspace_status,
            owner_id=workspace_data.owner_id,
            team_id=workspace_data.team_id,
            client_id=workspace_data.client_id,
        )

        if not workspace:
            raise HTTPException(status_code=404, detail="워크스페이스를 찾을 수 없습니다.")

        return WorkspaceResponseSchema.from_orm(workspace)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스 수정 실패: {str(e)}")


@workspaces.delete(
    "/{workspace_id}",
    summary="워크스페이스 삭제",
    description="""
    워크스페이스를 삭제합니다.
    
    **파라미터:**
    - workspace_id: 삭제할 워크스페이스의 고유 ID
    
    **주의:** 삭제된 워크스페이스는 복구할 수 없습니다.
    """,
    responses={
        200: {
            "description": "워크스페이스 삭제 성공",
            "content": {"application/json": {"example": {"message": "워크스페이스 ws_123456가 삭제되었습니다."}}},
        },
        400: {
            "description": "잘못된 요청",
            "content": {"application/json": {"example": {"detail": "진행 중인 워크스페이스는 삭제할 수 없습니다."}}},
        },
        404: {
            "description": "워크스페이스를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "워크스페이스를 찾을 수 없습니다."}}},
        },
    },
)
async def delete_workspace_endpoint(workspace_id: str):
    """워크스페이스 삭제"""
    try:
        deleted = await delete_workspace(workspace_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="워크스페이스를 찾을 수 없습니다.")

        return {"message": f"워크스페이스 {workspace_id}가 삭제되었습니다."}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스 삭제 실패: {str(e)}")


@workspaces.patch(
    "/{workspace_id}/status",
    response_model=WorkspaceResponseSchema,
    summary="워크스페이스 상태 변경",
    description="""
    워크스페이스의 상태를 변경합니다.
    
    **파라미터:**
    - workspace_id: 상태를 변경할 워크스페이스의 고유 ID
    
    **요청 본문:**
    - new_status: 새로운 상태 (ACTIVE, INACTIVE, COMPLETED, CANCELLED, ON_HOLD, IN_PROGRESS, PENDING)
    
    **상태 설명:**
    - ACTIVE: 활성 상태
    - INACTIVE: 비활성 상태
    - COMPLETED: 완료됨
    - CANCELLED: 취소됨
    - ON_HOLD: 보류 중
    - IN_PROGRESS: 진행 중
    - PENDING: 대기 중
    """,
    responses={
        200: {
            "description": "상태 변경 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ws_123456",
                        "name": "프로젝트 A",
                        "description": "새로운 프로젝트",
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-12-31T23:59:59",
                        "workspace_status": "IN_PROGRESS",
                        "owner_id": "user_123",
                        "team_id": "team_456",
                        "client_id": "client_789",
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
            "description": "워크스페이스를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "워크스페이스를 찾을 수 없습니다."}}},
        },
    },
)
async def change_workspace_status_endpoint(workspace_id: str, status_data: WorkspaceStatusChangeSchema):
    """워크스페이스 상태 변경"""
    try:
        workspace = await change_workspace_status(workspace_id=workspace_id, new_status=status_data.new_status)

        if not workspace:
            raise HTTPException(status_code=404, detail="워크스페이스를 찾을 수 없습니다.")

        return WorkspaceResponseSchema.from_orm(workspace)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스 상태 변경 실패: {str(e)}")


@workspaces.get(
    "/owner/{owner_id}",
    response_model=List[WorkspaceResponseSchema],
    summary="소유자별 워크스페이스 조회",
    description="""
    특정 소유자가 소유한 워크스페이스 목록을 조회합니다.
    
    **파라미터:**
    - owner_id: 소유자 ID
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지 크기 (기본값: 10, 최대: 100)
    
    **응답:**
    - 해당 소유자가 소유한 워크스페이스 목록
    """,
    responses={
        200: {
            "description": "소유자별 워크스페이스 조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "ws_123456",
                            "name": "프로젝트 A",
                            "description": "소유자 A의 프로젝트",
                            "start_date": "2024-01-01T00:00:00",
                            "end_date": "2024-12-31T23:59:59",
                            "workspace_status": "ACTIVE",
                            "owner_id": "user_123",
                            "team_id": "team_456",
                            "client_id": "client_789",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00",
                        }
                    ]
                }
            },
        }
    },
)
async def get_workspaces_by_owner_endpoint(
    owner_id: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지 크기"),
):
    """소유자별 워크스페이스 조회"""
    try:
        workspaces_list = await get_workspaces_by_owner(owner_id=owner_id, skip=(page - 1) * limit, limit=limit)

        return [WorkspaceResponseSchema.from_orm(workspace) for workspace in workspaces_list]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"소유자별 워크스페이스 조회 실패: {str(e)}")


@workspaces.get(
    "/status/{status}",
    response_model=List[WorkspaceResponseSchema],
    summary="상태별 워크스페이스 조회",
    description="""
    특정 상태의 워크스페이스 목록을 조회합니다.
    
    **파라미터:**
    - status: 조회할 상태 (ACTIVE, INACTIVE, COMPLETED, CANCELLED, ON_HOLD, IN_PROGRESS, PENDING)
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지 크기 (기본값: 10, 최대: 100)
    
    **응답:**
    - 해당 상태의 워크스페이스 목록
    """,
    responses={
        200: {
            "description": "상태별 워크스페이스 조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "ws_123456",
                            "name": "진행 중인 프로젝트",
                            "description": "현재 진행 중인 프로젝트",
                            "start_date": "2024-01-01T00:00:00",
                            "end_date": "2024-12-31T23:59:59",
                            "workspace_status": "IN_PROGRESS",
                            "owner_id": "user_123",
                            "team_id": "team_456",
                            "client_id": "client_789",
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
async def get_workspaces_by_status_endpoint(
    status: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지 크기"),
):
    """상태별 워크스페이스 조회"""
    try:
        from src.modules.workspace.core.value import WorkspaceStatus

        try:
            status_enum = WorkspaceStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"유효하지 않은 상태입니다: {status}")

        workspaces_list = await get_workspaces_by_status(status=status_enum, skip=(page - 1) * limit, limit=limit)

        return [WorkspaceResponseSchema.from_orm(workspace) for workspace in workspaces_list]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태별 워크스페이스 조회 실패: {str(e)}")


@workspaces.get(
    "/statistics/overview",
    response_model=WorkspaceStatisticsResponseSchema,
    summary="워크스페이스 통계 조회",
    description="""
    전체 워크스페이스의 통계 정보를 조회합니다.
    
    **응답 정보:**
    - total: 전체 워크스페이스 수
    - active: 활성 워크스페이스 수
    - inactive: 비활성 워크스페이스 수
    - completed: 완료된 워크스페이스 수
    - cancelled: 취소된 워크스페이스 수
    - on_hold: 보류 중인 워크스페이스 수
    - in_progress: 진행 중인 워크스페이스 수
    - pending: 대기 중인 워크스페이스 수
    """,
    responses={
        200: {
            "description": "워크스페이스 통계 조회 성공",
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
                    }
                }
            },
        }
    },
)
async def get_workspace_statistics_endpoint():
    """워크스페이스 통계 조회"""
    try:
        stats = await get_workspace_statistics()

        return WorkspaceStatisticsResponseSchema(
            total=stats.get("active", 0)
            + stats.get("inactive", 0)
            + stats.get("completed", 0)
            + stats.get("cancelled", 0)
            + stats.get("on_hold", 0)
            + stats.get("in_progress", 0)
            + stats.get("pending", 0),
            active=stats.get("active", 0),
            inactive=stats.get("inactive", 0),
            completed=stats.get("completed", 0),
            cancelled=stats.get("cancelled", 0),
            on_hold=stats.get("on_hold", 0),
            in_progress=stats.get("in_progress", 0),
            pending=stats.get("pending", 0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"워크스페이스 통계 조회 실패: {str(e)}")
