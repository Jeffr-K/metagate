from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import HTTPBearer

from src.modules.user.core.command import (
    ActivateUserCommand,
    ChangePasswordCommand,
    CheckEmailExistsCommand,
    CheckUsernameExistsCommand,
    ConfirmPasswordResetCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    DeleteUserCommand,
    DemoteToUserCommand,
    FindUserByEmailCommand,
    FindUserByIdCommand,
    FindUserByOAuthCommand,
    FindUserByUsernameCommand,
    GetUserStatisticsCommand,
    ListActiveUsersCommand,
    ListAdminsCommand,
    ListUsersCommand,
    ListVerifiedUsersCommand,
    LoginCommand,
    LogoutCommand,
    OAuthLoginCommand,
    PromoteToAdminCommand,
    ResetPasswordCommand,
    SendEmailVerificationCommand,
    SuspendUserCommand,
    UpdateUserCommand,
    VerifyEmailCommand,
)
from src.modules.user.core.service import UserService
from src.modules.user.core.value import AuthProvider, UserRole, UserStatus
from src.modules.user.interface.adapter import (
    EmailVerificationResponse,
    EmailVerificationSentResponse,
    ErrorResponse,
    PasswordChangeResponse,
    PasswordResetConfirmResponse,
    PasswordResetResponse,
    SuccessResponse,
    UserActivationResponse,
    UserAuthResponse,
    UserChangePasswordRequest,
    UserConfirmPasswordResetRequest,
    UserCreateRequest,
    UserDeactivationResponse,
    UserDeleteResponse,
    UserDemotionResponse,
    UserExistsResponse,
    UserListRequest,
    UserListResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserOAuthLoginRequest,
    UserOAuthLoginResponse,
    UserPromotionResponse,
    UserRegistrationResponse,
    UserResetPasswordRequest,
    UserResponse,
    UserSearchRequest,
    UserSendEmailVerificationRequest,
    UserStatisticsResponse,
    UserSuspendRequest,
    UserSuspensionResponse,
    UserUpdateRequest,
    UserUpdateResponse,
    UserVerifyEmailRequest,
)

# JWT 토큰 검증을 위한 의존성 (실제 구현은 별도로 필요)
security = HTTPBearer()

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service() -> UserService:
    """UserService 의존성 주입"""
    # TODO: 실제 의존성 주입 구현
    from src.infrastructure.database import get_session
    from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

    session = next(get_session())
    repository = SQLAlchemyUserRepository(session)

    # 환경 변수에서 설정 가져오기
    import os

    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    jwt_refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    password_salt = os.getenv("PASSWORD_SALT", "")
    bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))

    return UserService(
        user_repository=repository,
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        jwt_access_token_expire_minutes=jwt_access_token_expire_minutes,
        jwt_refresh_token_expire_days=jwt_refresh_token_expire_days,
        password_salt=password_salt,
        bcrypt_rounds=bcrypt_rounds,
    )


# 사용자 생성 (회원가입)
@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 회원가입",
    description="새로운 사용자를 등록합니다. 이메일 인증이 필요한 경우 인증 메일이 발송됩니다.",
    responses={
        201: {"description": "회원가입 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        409: {"model": ErrorResponse, "description": "이미 존재하는 이메일 또는 사용자명"},
    },
)
async def register_user(request: UserCreateRequest, user_service: UserService = Depends(get_user_service)) -> UserRegistrationResponse:
    """사용자 회원가입"""
    try:
        command = CreateUserCommand(
            email=request.email,
            username=request.username,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            nickname=request.nickname,
            phone=request.phone,
            avatar_url=request.avatar_url,
            bio=request.bio,
            auth_provider=request.auth_provider,
            auth_provider_id=request.auth_provider_id,
        )
        return user_service.create_user(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")


# 사용자 로그인
@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="사용자 로그인",
    description="이메일과 비밀번호로 로그인합니다.",
    responses={
        200: {"description": "로그인 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        401: {"model": ErrorResponse, "description": "인증 실패"},
    },
)
async def login_user(request: UserLoginRequest, user_service: UserService = Depends(get_user_service)) -> UserLoginResponse:
    """사용자 로그인"""
    try:
        command = LoginCommand(
            email=request.email,
            password=request.password,
        )
        return user_service.login(command)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")


# OAuth 로그인
@router.post(
    "/oauth/login",
    response_model=UserOAuthLoginResponse,
    summary="OAuth 로그인",
    description="OAuth 제공자를 통해 로그인합니다.",
    responses={
        200: {"description": "OAuth 로그인 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
    },
)
async def oauth_login(request: UserOAuthLoginRequest, user_service: UserService = Depends(get_user_service)) -> UserOAuthLoginResponse:
    """OAuth 로그인"""
    try:
        command = OAuthLoginCommand(
            provider=request.provider,
            provider_id=request.provider_id,
            email=request.email,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            avatar_url=request.avatar_url,
        )
        return user_service.oauth_login(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="OAuth 로그인 중 오류가 발생했습니다.")


# 사용자 로그아웃
@router.post(
    "/logout",
    response_model=UserLogoutResponse,
    summary="사용자 로그아웃",
    description="사용자를 로그아웃합니다.",
    responses={
        200: {"description": "로그아웃 성공"},
    },
)
async def logout_user(user_service: UserService = Depends(get_user_service), token: str = Depends(security)) -> UserLogoutResponse:
    """사용자 로그아웃"""
    try:
        # TODO: 토큰에서 사용자 ID 추출
        user_id = "temp_user_id"  # 실제로는 JWT 토큰에서 추출
        command = LogoutCommand(user_id=user_id, token=token.credentials)
        return user_service.logout(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그아웃 중 오류가 발생했습니다.")


# 사용자 목록 조회
@router.get(
    "/",
    response_model=UserListResponse,
    summary="사용자 목록 조회",
    description="사용자 목록을 조회합니다. 관리자만 접근 가능합니다.",
    responses={
        200: {"description": "사용자 목록 조회 성공"},
        403: {"model": ErrorResponse, "description": "권한 없음"},
    },
)
async def list_users(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    search_term: Optional[str] = Query(None, description="검색어"),
    role: Optional[UserRole] = Query(None, description="사용자 역할"),
    status: Optional[UserStatus] = Query(None, description="사용자 상태"),
    auth_provider: Optional[AuthProvider] = Query(None, description="인증 제공자"),
    email_verified: Optional[bool] = Query(None, description="이메일 인증 여부"),
    is_active: Optional[bool] = Query(None, description="활성 상태"),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """사용자 목록 조회"""
    try:
        command = ListUsersCommand(
            skip=skip,
            limit=limit,
            search_term=search_term,
            role=role,
            status=status,
            auth_provider=auth_provider,
            email_verified=email_verified,
            is_active=is_active,
        )
        return user_service.list_users(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 목록 조회 중 오류가 발생했습니다.")


# 사용자 상세 조회
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 상세 조회",
    description="특정 사용자의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 조회 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def get_user(user_id: str = Path(..., description="사용자 ID"), user_service: UserService = Depends(get_user_service)) -> UserResponse:
    """사용자 상세 조회"""
    try:
        command = FindUserByIdCommand(user_id=user_id)
        user = user_service.find_user_by_id(command)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 조회 중 오류가 발생했습니다.")


# 사용자 정보 업데이트
@router.put(
    "/{user_id}",
    response_model=UserUpdateResponse,
    summary="사용자 정보 업데이트",
    description="사용자 정보를 업데이트합니다.",
    responses={
        200: {"description": "사용자 정보 업데이트 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
    },
)
async def update_user(
    user_id: str = Path(..., description="사용자 ID"), request: UserUpdateRequest = None, user_service: UserService = Depends(get_user_service)
) -> UserUpdateResponse:
    """사용자 정보 업데이트"""
    try:
        command = UpdateUserCommand(
            user_id=user_id,
            email=request.email,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            nickname=request.nickname,
            phone=request.phone,
            avatar_url=request.avatar_url,
            bio=request.bio,
            user_role=request.user_role,
            user_status=request.user_status,
            is_active=request.is_active,
        )
        return user_service.update_user(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 정보 업데이트 중 오류가 발생했습니다.")


# 사용자 삭제
@router.delete(
    "/{user_id}",
    response_model=UserDeleteResponse,
    summary="사용자 삭제",
    description="사용자를 삭제합니다. (소프트 삭제)",
    responses={
        200: {"description": "사용자 삭제 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def delete_user(
    user_id: str = Path(..., description="사용자 ID"),
    hard_delete: bool = Query(False, description="하드 삭제 여부"),
    user_service: UserService = Depends(get_user_service),
) -> UserDeleteResponse:
    """사용자 삭제"""
    try:
        command = DeleteUserCommand(user_id=user_id, hard_delete=hard_delete)
        return user_service.delete_user(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 삭제 중 오류가 발생했습니다.")


# 사용자 활성화
@router.post(
    "/{user_id}/activate",
    response_model=UserActivationResponse,
    summary="사용자 활성화",
    description="사용자를 활성화합니다.",
    responses={
        200: {"description": "사용자 활성화 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def activate_user(
    user_id: str = Path(..., description="사용자 ID"), user_service: UserService = Depends(get_user_service)
) -> UserActivationResponse:
    """사용자 활성화"""
    try:
        command = ActivateUserCommand(user_id=user_id)
        return user_service.activate_user(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 활성화 중 오류가 발생했습니다.")


# 사용자 비활성화
@router.post(
    "/{user_id}/deactivate",
    response_model=UserDeactivationResponse,
    summary="사용자 비활성화",
    description="사용자를 비활성화합니다.",
    responses={
        200: {"description": "사용자 비활성화 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def deactivate_user(
    user_id: str = Path(..., description="사용자 ID"), user_service: UserService = Depends(get_user_service)
) -> UserDeactivationResponse:
    """사용자 비활성화"""
    try:
        command = DeactivateUserCommand(user_id=user_id)
        return user_service.deactivate_user(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 비활성화 중 오류가 발생했습니다.")


# 사용자 정지
@router.post(
    "/{user_id}/suspend",
    response_model=UserSuspensionResponse,
    summary="사용자 정지",
    description="사용자를 정지합니다.",
    responses={
        200: {"description": "사용자 정지 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def suspend_user(
    user_id: str = Path(..., description="사용자 ID"), request: UserSuspendRequest = None, user_service: UserService = Depends(get_user_service)
) -> UserSuspensionResponse:
    """사용자 정지"""
    try:
        command = SuspendUserCommand(user_id=user_id, reason=request.reason if request else None)
        return user_service.suspend_user(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 정지 중 오류가 발생했습니다.")


# 사용자 관리자 승격
@router.post(
    "/{user_id}/promote",
    response_model=UserPromotionResponse,
    summary="사용자 관리자 승격",
    description="사용자를 관리자로 승격합니다.",
    responses={
        200: {"description": "사용자 승격 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def promote_user(
    user_id: str = Path(..., description="사용자 ID"), user_service: UserService = Depends(get_user_service)
) -> UserPromotionResponse:
    """사용자 관리자 승격"""
    try:
        command = PromoteToAdminCommand(user_id=user_id)
        return user_service.promote_to_admin(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 승격 중 오류가 발생했습니다.")


# 사용자 일반 사용자 강등
@router.post(
    "/{user_id}/demote",
    response_model=UserDemotionResponse,
    summary="사용자 일반 사용자 강등",
    description="사용자를 일반 사용자로 강등합니다.",
    responses={
        200: {"description": "사용자 강등 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def demote_user(
    user_id: str = Path(..., description="사용자 ID"), user_service: UserService = Depends(get_user_service)
) -> UserDemotionResponse:
    """사용자 일반 사용자 강등"""
    try:
        command = DemoteToUserCommand(user_id=user_id)
        return user_service.demote_to_user(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 강등 중 오류가 발생했습니다.")


# 이메일 존재 여부 확인
@router.get(
    "/check/email/{email}",
    response_model=UserExistsResponse,
    summary="이메일 존재 여부 확인",
    description="이메일이 이미 등록되어 있는지 확인합니다.",
    responses={
        200: {"description": "이메일 존재 여부 확인 성공"},
    },
)
async def check_email_exists(
    email: str = Path(..., description="확인할 이메일"), user_service: UserService = Depends(get_user_service)
) -> UserExistsResponse:
    """이메일 존재 여부 확인"""
    try:
        command = CheckEmailExistsCommand(email=email)
        return user_service.check_email_exists(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="이메일 확인 중 오류가 발생했습니다.")


# 사용자명 존재 여부 확인
@router.get(
    "/check/username/{username}",
    response_model=UserExistsResponse,
    summary="사용자명 존재 여부 확인",
    description="사용자명이 이미 등록되어 있는지 확인합니다.",
    responses={
        200: {"description": "사용자명 존재 여부 확인 성공"},
    },
)
async def check_username_exists(
    username: str = Path(..., description="확인할 사용자명"), user_service: UserService = Depends(get_user_service)
) -> UserExistsResponse:
    """사용자명 존재 여부 확인"""
    try:
        command = CheckUsernameExistsCommand(username=username)
        return user_service.check_username_exists(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자명 확인 중 오류가 발생했습니다.")


# 이메일 인증
@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    summary="이메일 인증",
    description="이메일 인증 토큰을 확인하여 이메일을 인증합니다.",
    responses={
        200: {"description": "이메일 인증 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 토큰"},
    },
)
async def verify_email(request: UserVerifyEmailRequest, user_service: UserService = Depends(get_user_service)) -> EmailVerificationResponse:
    """이메일 인증"""
    try:
        command = VerifyEmailCommand(token=request.token)
        return user_service.verify_email(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="이메일 인증 중 오류가 발생했습니다.")


# 이메일 인증 메일 발송
@router.post(
    "/{user_id}/send-verification",
    response_model=EmailVerificationSentResponse,
    summary="이메일 인증 메일 발송",
    description="사용자에게 이메일 인증 메일을 발송합니다.",
    responses={
        200: {"description": "인증 메일 발송 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def send_email_verification(
    user_id: str = Path(..., description="사용자 ID"), user_service: UserService = Depends(get_user_service)
) -> EmailVerificationSentResponse:
    """이메일 인증 메일 발송"""
    try:
        command = SendEmailVerificationCommand(user_id=user_id)
        return user_service.send_email_verification(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="인증 메일 발송 중 오류가 발생했습니다.")


# 비밀번호 재설정 요청
@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    summary="비밀번호 재설정 요청",
    description="비밀번호 재설정 메일을 발송합니다.",
    responses={
        200: {"description": "비밀번호 재설정 메일 발송 성공"},
    },
)
async def reset_password(request: UserResetPasswordRequest, user_service: UserService = Depends(get_user_service)) -> PasswordResetResponse:
    """비밀번호 재설정 요청"""
    try:
        command = ResetPasswordCommand(email=request.email)
        return user_service.reset_password(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="비밀번호 재설정 요청 중 오류가 발생했습니다.")


# 비밀번호 재설정 확인
@router.post(
    "/confirm-password-reset",
    response_model=PasswordResetConfirmResponse,
    summary="비밀번호 재설정 확인",
    description="비밀번호 재설정 토큰을 확인하고 새 비밀번호를 설정합니다.",
    responses={
        200: {"description": "비밀번호 재설정 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 토큰"},
    },
)
async def confirm_password_reset(
    request: UserConfirmPasswordResetRequest, user_service: UserService = Depends(get_user_service)
) -> PasswordResetConfirmResponse:
    """비밀번호 재설정 확인"""
    try:
        command = ConfirmPasswordResetCommand(token=request.token, new_password=request.new_password)
        return user_service.confirm_password_reset(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="비밀번호 재설정 중 오류가 발생했습니다.")


# 관리자 목록 조회
@router.get(
    "/admins",
    response_model=UserListResponse,
    summary="관리자 목록 조회",
    description="관리자 목록을 조회합니다.",
    responses={
        200: {"description": "관리자 목록 조회 성공"},
    },
)
async def list_admins(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """관리자 목록 조회"""
    try:
        command = ListAdminsCommand(skip=skip, limit=limit)
        return user_service.list_admins(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="관리자 목록 조회 중 오류가 발생했습니다.")


# 활성 사용자 목록 조회
@router.get(
    "/active",
    response_model=UserListResponse,
    summary="활성 사용자 목록 조회",
    description="활성 사용자 목록을 조회합니다.",
    responses={
        200: {"description": "활성 사용자 목록 조회 성공"},
    },
)
async def list_active_users(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """활성 사용자 목록 조회"""
    try:
        command = ListActiveUsersCommand(skip=skip, limit=limit)
        return user_service.list_active_users(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="활성 사용자 목록 조회 중 오류가 발생했습니다.")


# 인증된 사용자 목록 조회
@router.get(
    "/verified",
    response_model=UserListResponse,
    summary="인증된 사용자 목록 조회",
    description="이메일 인증이 완료된 사용자 목록을 조회합니다.",
    responses={
        200: {"description": "인증된 사용자 목록 조회 성공"},
    },
)
async def list_verified_users(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """인증된 사용자 목록 조회"""
    try:
        command = ListVerifiedUsersCommand(skip=skip, limit=limit)
        return user_service.list_verified_users(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="인증된 사용자 목록 조회 중 오류가 발생했습니다.")


# 사용자 통계 조회
@router.get(
    "/statistics",
    response_model=UserStatisticsResponse,
    summary="사용자 통계 조회",
    description="사용자 관련 통계 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 통계 조회 성공"},
    },
)
async def get_user_statistics(user_service: UserService = Depends(get_user_service)) -> UserStatisticsResponse:
    """사용자 통계 조회"""
    try:
        command = GetUserStatisticsCommand()
        return user_service.get_user_statistics(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 통계 조회 중 오류가 발생했습니다.")
