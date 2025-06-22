from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.modules.user.core.entity import User
from src.modules.user.core.query import UserQuery
from src.modules.user.core.service import UserService
from src.modules.user.core.value import UserRole, UserStatus
from src.modules.user.interface.adapter import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

# 관리자 전용 라우터
admin = APIRouter(prefix="/admin/users", tags=["Admin - User Management"])


# 관리자 권한 확인을 위한 의존성 (TODO: 실제 JWT 토큰 검증 로직 구현 필요)
async def verify_admin_permission():
    """관리자 권한 확인"""
    # TODO: JWT 토큰에서 사용자 정보를 추출하고 관리자 권한 확인
    # 현재는 임시로 True 반환
    return True


# 관리자 전용 스키마
class AdminUserStatisticsSchema(BaseModel):
    total_users: int = Field(..., description="전체 사용자 수")
    active_users: int = Field(..., description="활성 사용자 수")
    pending_users: int = Field(..., description="대기 중인 사용자 수")
    suspended_users: int = Field(..., description="정지된 사용자 수")
    deleted_users: int = Field(..., description="삭제된 사용자 수")
    admin_users: int = Field(..., description="관리자 수")
    verified_users: int = Field(..., description="이메일 인증 완료 사용자 수")
    unverified_users: int = Field(..., description="이메일 미인증 사용자 수")

    class Config:
        schema_extra = {
            "example": {
                "total_users": 150,
                "active_users": 120,
                "pending_users": 15,
                "suspended_users": 10,
                "deleted_users": 5,
                "admin_users": 3,
                "verified_users": 130,
                "unverified_users": 20,
            }
        }


class AdminUserSearchSchema(BaseModel):
    search_term: Optional[str] = Field(None, description="검색어 (이메일, 사용자명, 이름)")
    user_role: Optional[UserRole] = Field(None, description="사용자 역할")
    user_status: Optional[UserStatus] = Field(None, description="사용자 상태")
    email_verified: Optional[bool] = Field(None, description="이메일 인증 여부")
    is_active: Optional[bool] = Field(None, description="활성 상태")
    created_after: Optional[datetime] = Field(None, description="생성일 시작")
    created_before: Optional[datetime] = Field(None, description="생성일 종료")
    last_login_after: Optional[datetime] = Field(None, description="마지막 로그인 시작")
    last_login_before: Optional[datetime] = Field(None, description="마지막 로그인 종료")

    class Config:
        schema_extra = {
            "example": {
                "search_term": "john",
                "user_role": "USER",
                "user_status": "ACTIVE",
                "email_verified": True,
                "is_active": True,
                "created_after": "2024-01-01T00:00:00",
                "created_before": "2024-12-31T23:59:59",
            }
        }


class AdminUserBulkActionSchema(BaseModel):
    user_ids: List[str] = Field(..., description="대상 사용자 ID 목록", min_items=1)
    action: str = Field(..., description="수행할 액션", example="activate")

    class Config:
        schema_extra = {
            "example": {
                "user_ids": ["user_123", "user_456", "user_789"],
                "action": "activate",
            }
        }


# 관리자 전용 API 엔드포인트들


@admin.get(
    "/statistics",
    response_model=AdminUserStatisticsSchema,
    summary="사용자 통계 조회",
    description="""
    전체 사용자 통계를 조회합니다.
    
    **조회 가능한 통계:**
    - 전체 사용자 수
    - 상태별 사용자 수 (활성, 대기, 정지, 삭제)
    - 역할별 사용자 수 (관리자, 일반 사용자)
    - 이메일 인증 상태별 사용자 수
    """,
    responses={
        200: {
            "description": "통계 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "total_users": 150,
                        "active_users": 120,
                        "pending_users": 15,
                        "suspended_users": 10,
                        "deleted_users": 5,
                        "admin_users": 3,
                        "verified_users": 130,
                        "unverified_users": 20,
                    }
                }
            },
        },
        403: {"description": "관리자 권한 없음"},
    },
)
async def get_user_statistics(
    _: bool = Depends(verify_admin_permission),
):
    """사용자 통계 조회"""
    try:
        query = UserQuery()
        service = UserService()

        # 각 상태별 사용자 수 조회
        total_users = await query.get_all(limit=10000)
        active_users = await query.get_by_status(UserStatus.ACTIVE, limit=10000)
        pending_users = await query.get_by_status(UserStatus.PENDING, limit=10000)
        suspended_users = await query.get_by_status(UserStatus.SUSPENDED, limit=10000)
        deleted_users = await query.get_by_status(UserStatus.DELETED, limit=10000)

        # 역할별 사용자 수 조회
        admin_users = await query.get_by_role(UserRole.ADMIN, limit=10000)

        # 이메일 인증 상태별 사용자 수 (실제 구현에서는 별도 쿼리 필요)
        verified_count = 0
        unverified_count = 0
        for user in total_users:
            if user.email_verified:
                verified_count += 1
            else:
                unverified_count += 1

        return AdminUserStatisticsSchema(
            total_users=len(total_users),
            active_users=len(active_users),
            pending_users=len(pending_users),
            suspended_users=len(suspended_users),
            deleted_users=len(deleted_users),
            admin_users=len(admin_users),
            verified_users=verified_count,
            unverified_users=unverified_count,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@admin.get(
    "/search",
    response_model=List[UserResponseSchema],
    summary="사용자 고급 검색",
    description="""
    다양한 조건으로 사용자를 검색합니다.
    
    **검색 조건:**
    - 검색어: 이메일, 사용자명, 이름으로 검색
    - 사용자 역할: ADMIN, USER, MODERATOR
    - 사용자 상태: ACTIVE, PENDING, SUSPENDED, DELETED
    - 이메일 인증 여부
    - 활성 상태
    - 생성일 범위
    - 마지막 로그인 범위
    """,
    responses={
        200: {
            "description": "검색 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "user_123",
                            "email": "john@example.com",
                            "username": "john_doe",
                            "first_name": "John",
                            "last_name": "Doe",
                            "user_role": "USER",
                            "user_status": "ACTIVE",
                            "email_verified": True,
                            "created_at": "2024-01-01T00:00:00",
                        }
                    ]
                }
            },
        },
        403: {"description": "관리자 권한 없음"},
    },
)
async def search_users(
    search_term: Optional[str] = Query(None, description="검색어"),
    user_role: Optional[UserRole] = Query(None, description="사용자 역할"),
    user_status: Optional[UserStatus] = Query(None, description="사용자 상태"),
    email_verified: Optional[bool] = Query(None, description="이메일 인증 여부"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    created_after: Optional[datetime] = Query(None, description="생성일 시작"),
    created_before: Optional[datetime] = Query(None, description="생성일 종료"),
    last_login_after: Optional[datetime] = Query(None, description="마지막 로그인 시작"),
    last_login_before: Optional[datetime] = Query(None, description="마지막 로그인 종료"),
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 레코드 수"),
    _: bool = Depends(verify_admin_permission),
):
    """사용자 고급 검색"""
    try:
        query = UserQuery()

        # TODO: 실제 검색 로직 구현 (현재는 기본 조회만)
        users = await query.get_all(skip=skip, limit=limit)

        # 필터링 로직 (실제로는 데이터베이스 레벨에서 처리해야 함)
        filtered_users = []
        for user in users:
            # 검색어 필터
            if search_term:
                search_lower = search_term.lower()
                if not (
                    search_lower in user.email.lower()
                    or search_lower in user.username.lower()
                    or (user.first_name and search_lower in user.first_name.lower())
                    or (user.last_name and search_lower in user.last_name.lower())
                ):
                    continue

            # 역할 필터
            if user_role and user.user_role != user_role:
                continue

            # 상태 필터
            if user_status and user.user_status != user_status:
                continue

            # 이메일 인증 필터
            if email_verified is not None and user.email_verified != email_verified:
                continue

            # 활성 상태 필터
            if is_active is not None and user.is_active != is_active:
                continue

            # 생성일 필터
            if created_after and user.created_at < created_after:
                continue
            if created_before and user.created_at > created_before:
                continue

            # 마지막 로그인 필터
            if last_login_after and (not user.last_login_at or user.last_login_at < last_login_after):
                continue
            if last_login_before and (not user.last_login_at or user.last_login_at > last_login_before):
                continue

            filtered_users.append(user)

        return [UserResponseSchema.from_orm(user) for user in filtered_users]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 검색 실패: {str(e)}")


@admin.post(
    "/",
    response_model=UserResponseSchema,
    status_code=201,
    summary="관리자가 사용자 생성",
    description="""
    관리자가 새로운 사용자를 생성합니다.
    
    **특권:**
    - 일반 사용자 생성
    - 관리자 생성
    - 이메일 인증 상태 설정
    - 사용자 상태 설정
    """,
    responses={
        201: {
            "description": "사용자 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "user_123",
                        "email": "newuser@example.com",
                        "username": "newuser",
                        "user_role": "USER",
                        "user_status": "ACTIVE",
                        "email_verified": True,
                        "created_at": "2024-01-01T00:00:00",
                    }
                }
            },
        },
        400: {"description": "잘못된 요청 데이터"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def create_user_by_admin(
    user_data: UserCreateSchema,
    _: bool = Depends(verify_admin_permission),
):
    """관리자가 사용자 생성"""
    try:
        service = UserService()

        # 관리자는 이메일 인증 없이도 사용자 생성 가능
        user = await service.create_user_by_admin(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            nickname=user_data.nickname,
            phone=user_data.phone,
            user_role=user_data.user_role,
            user_status=user_data.user_status,
            email_verified=user_data.email_verified,
        )

        return UserResponseSchema.from_orm(user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 생성 실패: {str(e)}")


@admin.put(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="관리자가 사용자 정보 수정",
    description="""
    관리자가 사용자 정보를 수정합니다.
    
    **수정 가능한 항목:**
    - 기본 정보 (이름, 닉네임, 전화번호 등)
    - 사용자 역할 (일반 사용자 ↔ 관리자)
    - 사용자 상태 (활성, 정지, 삭제)
    - 이메일 인증 상태
    """,
    responses={
        200: {
            "description": "사용자 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "user_123",
                        "email": "user@example.com",
                        "username": "user",
                        "user_role": "ADMIN",
                        "user_status": "ACTIVE",
                        "email_verified": True,
                        "updated_at": "2024-01-01T00:00:00",
                    }
                }
            },
        },
        404: {"description": "사용자를 찾을 수 없음"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def update_user_by_admin(
    user_id: str,
    user_data: UserUpdateSchema,
    _: bool = Depends(verify_admin_permission),
):
    """관리자가 사용자 정보 수정"""
    try:
        service = UserService()

        user = await service.update_user_by_admin(
            user_id=user_id,
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            nickname=user_data.nickname,
            phone=user_data.phone,
            user_role=user_data.user_role,
            user_status=user_data.user_status,
            email_verified=user_data.email_verified,
        )

        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        return UserResponseSchema.from_orm(user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 수정 실패: {str(e)}")


@admin.delete(
    "/{user_id}",
    status_code=204,
    summary="관리자가 사용자 삭제",
    description="""
    관리자가 사용자를 삭제합니다.
    
    **주의사항:**
    - 실제 삭제가 아닌 소프트 삭제 (deleted_at 설정)
    - 삭제된 사용자는 로그인 불가
    - 복구 가능
    """,
    responses={
        204: {"description": "사용자 삭제 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def delete_user_by_admin(
    user_id: str,
    _: bool = Depends(verify_admin_permission),
):
    """관리자가 사용자 삭제"""
    try:
        service = UserService()

        success = await service.delete_user_by_admin(user_id=user_id)

        if not success:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 삭제 실패: {str(e)}")


@admin.post(
    "/{user_id}/activate",
    response_model=UserResponseSchema,
    summary="사용자 활성화",
    description="관리자가 사용자를 활성화합니다.",
    responses={
        200: {"description": "사용자 활성화 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def activate_user(
    user_id: str,
    _: bool = Depends(verify_admin_permission),
):
    """사용자 활성화"""
    try:
        service = UserService()

        user = await service.activate_user_by_admin(user_id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        return UserResponseSchema.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 활성화 실패: {str(e)}")


@admin.post(
    "/{user_id}/suspend",
    response_model=UserResponseSchema,
    summary="사용자 정지",
    description="관리자가 사용자를 정지합니다.",
    responses={
        200: {"description": "사용자 정지 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def suspend_user(
    user_id: str,
    _: bool = Depends(verify_admin_permission),
):
    """사용자 정지"""
    try:
        service = UserService()

        user = await service.suspend_user_by_admin(user_id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        return UserResponseSchema.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 정지 실패: {str(e)}")


@admin.post(
    "/{user_id}/promote",
    response_model=UserResponseSchema,
    summary="사용자를 관리자로 승격",
    description="관리자가 일반 사용자를 관리자로 승격합니다.",
    responses={
        200: {"description": "관리자 승격 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def promote_to_admin(
    user_id: str,
    _: bool = Depends(verify_admin_permission),
):
    """사용자를 관리자로 승격"""
    try:
        service = UserService()

        user = await service.promote_to_admin(user_id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        return UserResponseSchema.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관리자 승격 실패: {str(e)}")


@admin.post(
    "/{user_id}/demote",
    response_model=UserResponseSchema,
    summary="관리자를 일반 사용자로 강등",
    description="관리자가 다른 관리자를 일반 사용자로 강등합니다.",
    responses={
        200: {"description": "일반 사용자 강등 성공"},
        404: {"description": "사용자를 찾을 수 없음"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def demote_to_user(
    user_id: str,
    _: bool = Depends(verify_admin_permission),
):
    """관리자를 일반 사용자로 강등"""
    try:
        service = UserService()

        user = await service.demote_to_user(user_id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        return UserResponseSchema.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"일반 사용자 강등 실패: {str(e)}")


@admin.post(
    "/bulk-action",
    summary="사용자 일괄 작업",
    description="""
    여러 사용자에 대해 일괄 작업을 수행합니다.
    
    **지원하는 액션:**
    - activate: 활성화
    - suspend: 정지
    - delete: 삭제
    - promote: 관리자 승격
    - demote: 일반 사용자 강등
    """,
    responses={
        200: {
            "description": "일괄 작업 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success_count": 3,
                        "failed_count": 1,
                        "failed_users": ["user_456"],
                        "message": "3명의 사용자가 성공적으로 활성화되었습니다.",
                    }
                }
            },
        },
        400: {"description": "잘못된 액션"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def bulk_action(
    action_data: AdminUserBulkActionSchema,
    _: bool = Depends(verify_admin_permission),
):
    """사용자 일괄 작업"""
    try:
        service = UserService()

        success_count = 0
        failed_users = []

        for user_id in action_data.user_ids:
            try:
                if action_data.action == "activate":
                    await service.activate_user_by_admin(user_id=user_id)
                elif action_data.action == "suspend":
                    await service.suspend_user_by_admin(user_id=user_id)
                elif action_data.action == "delete":
                    await service.delete_user_by_admin(user_id=user_id)
                elif action_data.action == "promote":
                    await service.promote_to_admin(user_id=user_id)
                elif action_data.action == "demote":
                    await service.demote_to_user(user_id=user_id)
                else:
                    raise HTTPException(status_code=400, detail=f"지원하지 않는 액션: {action_data.action}")
                success_count += 1
            except Exception:
                failed_users.append(user_id)

        failed_count = len(failed_users)

        action_names = {
            "activate": "활성화",
            "suspend": "정지",
            "delete": "삭제",
            "promote": "관리자 승격",
            "demote": "일반 사용자 강등",
        }

        action_name = action_names.get(action_data.action, action_data.action)

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_users": failed_users,
            "message": f"{success_count}명의 사용자가 성공적으로 {action_name}되었습니다.",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"일괄 작업 실패: {str(e)}")


@admin.get(
    "/{user_id}/activity",
    summary="사용자 활동 내역 조회",
    description="""
    특정 사용자의 활동 내역을 조회합니다.
    
    **조회 가능한 정보:**
    - 마지막 로그인 시간
    - 마지막 로그인 IP
    - 생성일
    - 수정일
    - 삭제일 (있는 경우)
    """,
    responses={
        200: {
            "description": "활동 내역 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "user_123",
                        "last_login_at": "2024-01-01T10:30:00",
                        "last_login_ip": "192.168.1.100",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T10:30:00",
                        "deleted_at": None,
                    }
                }
            },
        },
        404: {"description": "사용자를 찾을 수 없음"},
        403: {"description": "관리자 권한 없음"},
    },
)
async def get_user_activity(
    user_id: str,
    _: bool = Depends(verify_admin_permission),
):
    """사용자 활동 내역 조회"""
    try:
        query = UserQuery()

        user = await query.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        return {
            "user_id": user.id,
            "last_login_at": user.last_login_at,
            "last_login_ip": user.last_login_ip,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "deleted_at": user.deleted_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"활동 내역 조회 실패: {str(e)}")
