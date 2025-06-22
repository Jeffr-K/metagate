from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.modules.user.core.command import (
    ChangePasswordCommand,
    ConfirmPasswordResetCommand,
    LoginCommand,
    LogoutCommand,
    ResetPasswordCommand,
    SendEmailVerificationCommand,
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
    UserChangePasswordRequest,
    UserConfirmPasswordResetRequest,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserResetPasswordRequest,
    UserSendEmailVerificationRequest,
    UserVerifyEmailRequest,
)

# JWT 토큰 검증을 위한 의존성
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])


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


# 이메일 로그인
@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="이메일 로그인",
    description="이메일과 비밀번호로 로그인합니다.",
    responses={
        200: {"description": "로그인 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        401: {"model": ErrorResponse, "description": "인증 실패"},
    },
)
async def login(request: UserLoginRequest, user_service: UserService = Depends(get_user_service)) -> UserLoginResponse:
    """이메일 로그인"""
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


# 로그아웃
@router.post(
    "/logout",
    response_model=UserLogoutResponse,
    summary="로그아웃",
    description="사용자를 로그아웃합니다.",
    responses={
        200: {"description": "로그아웃 성공"},
    },
)
async def logout(user_service: UserService = Depends(get_user_service), token: str = Depends(security)) -> UserLogoutResponse:
    """로그아웃"""
    try:
        # TODO: 토큰에서 사용자 ID 추출
        user_id = "temp_user_id"  # 실제로는 JWT 토큰에서 추출
        command = LogoutCommand(user_id=user_id, token=token.credentials)
        return user_service.logout(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그아웃 중 오류가 발생했습니다.")


# 비밀번호 변경
@router.post(
    "/change-password",
    response_model=PasswordChangeResponse,
    summary="비밀번호 변경",
    description="현재 비밀번호를 확인하고 새 비밀번호로 변경합니다.",
    responses={
        200: {"description": "비밀번호 변경 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        401: {"model": ErrorResponse, "description": "현재 비밀번호 불일치"},
    },
)
async def change_password(
    request: UserChangePasswordRequest, user_service: UserService = Depends(get_user_service), token: str = Depends(security)
) -> PasswordChangeResponse:
    """비밀번호 변경"""
    try:
        # TODO: 토큰에서 사용자 ID 추출
        user_id = "temp_user_id"  # 실제로는 JWT 토큰에서 추출
        command = ChangePasswordCommand(
            user_id=user_id,
            current_password=request.current_password,
            new_password=request.new_password,
        )
        return user_service.change_password(command)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="비밀번호 변경 중 오류가 발생했습니다.")


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
    "/send-verification",
    response_model=EmailVerificationSentResponse,
    summary="이메일 인증 메일 발송",
    description="사용자에게 이메일 인증 메일을 발송합니다.",
    responses={
        200: {"description": "인증 메일 발송 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def send_email_verification(
    request: UserSendEmailVerificationRequest, user_service: UserService = Depends(get_user_service)
) -> EmailVerificationSentResponse:
    """이메일 인증 메일 발송"""
    try:
        command = SendEmailVerificationCommand(user_id=request.user_id)
        return user_service.send_email_verification(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="인증 메일 발송 중 오류가 발생했습니다.")


# 토큰 갱신 (리프레시 토큰 사용)
@router.post(
    "/refresh",
    response_model=UserLoginResponse,
    summary="토큰 갱신",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
    responses={
        200: {"description": "토큰 갱신 성공"},
        401: {"model": ErrorResponse, "description": "유효하지 않은 토큰"},
    },
)
async def refresh_token(user_service: UserService = Depends(get_user_service), token: str = Depends(security)) -> UserLoginResponse:
    """토큰 갱신"""
    try:
        # TODO: 리프레시 토큰 검증 및 새로운 액세스 토큰 발급 로직 구현
        raise HTTPException(status_code=501, detail="토큰 갱신 기능은 아직 구현되지 않았습니다.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="토큰 갱신 중 오류가 발생했습니다.")


# 현재 사용자 정보 조회
@router.get(
    "/me",
    response_model=UserLoginResponse,
    summary="현재 사용자 정보 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        401: {"model": ErrorResponse, "description": "인증되지 않은 사용자"},
    },
)
async def get_current_user(user_service: UserService = Depends(get_user_service), token: str = Depends(security)) -> UserLoginResponse:
    """현재 사용자 정보 조회"""
    try:
        # TODO: JWT 토큰에서 사용자 정보 추출 및 반환 로직 구현
        raise HTTPException(status_code=501, detail="현재 사용자 정보 조회 기능은 아직 구현되지 않았습니다.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 정보 조회 중 오류가 발생했습니다.")


# 계정 잠금 해제
@router.post(
    "/unlock-account",
    response_model=EmailVerificationResponse,
    summary="계정 잠금 해제",
    description="계정이 잠긴 경우 잠금을 해제합니다.",
    responses={
        200: {"description": "계정 잠금 해제 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
    },
)
async def unlock_account(request: UserVerifyEmailRequest, user_service: UserService = Depends(get_user_service)) -> EmailVerificationResponse:
    """계정 잠금 해제"""
    try:
        # TODO: 계정 잠금 해제 로직 구현
        raise HTTPException(status_code=501, detail="계정 잠금 해제 기능은 아직 구현되지 않았습니다.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="계정 잠금 해제 중 오류가 발생했습니다.")


# 로그인 시도 횟수 확인
@router.get(
    "/login-attempts",
    summary="로그인 시도 횟수 확인",
    description="현재 IP에서의 로그인 시도 횟수를 확인합니다.",
    responses={
        200: {"description": "로그인 시도 횟수 조회 성공"},
    },
)
async def get_login_attempts(user_service: UserService = Depends(get_user_service)) -> dict:
    """로그인 시도 횟수 확인"""
    try:
        # TODO: 로그인 시도 횟수 조회 로직 구현
        return {"attempts": 0, "max_attempts": 5, "locked_until": None, "message": "로그인 시도 횟수 확인 기능은 아직 구현되지 않았습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그인 시도 횟수 확인 중 오류가 발생했습니다.")


# 세션 관리
@router.get(
    "/sessions",
    summary="활성 세션 목록 조회",
    description="현재 사용자의 활성 세션 목록을 조회합니다.",
    responses={
        200: {"description": "세션 목록 조회 성공"},
        401: {"model": ErrorResponse, "description": "인증되지 않은 사용자"},
    },
)
async def get_active_sessions(user_service: UserService = Depends(get_user_service), token: str = Depends(security)) -> dict:
    """활성 세션 목록 조회"""
    try:
        # TODO: 활성 세션 목록 조회 로직 구현
        return {"sessions": [], "message": "세션 관리 기능은 아직 구현되지 않았습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="세션 목록 조회 중 오류가 발생했습니다.")


# 특정 세션 종료
@router.delete(
    "/sessions/{session_id}",
    summary="특정 세션 종료",
    description="특정 세션을 종료합니다.",
    responses={
        200: {"description": "세션 종료 성공"},
        401: {"model": ErrorResponse, "description": "인증되지 않은 사용자"},
        404: {"model": ErrorResponse, "description": "세션을 찾을 수 없음"},
    },
)
async def terminate_session(session_id: str, user_service: UserService = Depends(get_user_service), token: str = Depends(security)) -> dict:
    """특정 세션 종료"""
    try:
        # TODO: 특정 세션 종료 로직 구현
        return {"message": f"세션 {session_id} 종료 기능은 아직 구현되지 않았습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="세션 종료 중 오류가 발생했습니다.")


# 모든 세션 종료 (현재 세션 제외)
@router.delete(
    "/sessions",
    summary="모든 세션 종료",
    description="현재 세션을 제외한 모든 세션을 종료합니다.",
    responses={
        200: {"description": "모든 세션 종료 성공"},
        401: {"model": ErrorResponse, "description": "인증되지 않은 사용자"},
    },
)
async def terminate_all_sessions(user_service: UserService = Depends(get_user_service), token: str = Depends(security)) -> dict:
    """모든 세션 종료"""
    try:
        # TODO: 모든 세션 종료 로직 구현
        return {"message": "모든 세션 종료 기능은 아직 구현되지 않았습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="세션 종료 중 오류가 발생했습니다.")
