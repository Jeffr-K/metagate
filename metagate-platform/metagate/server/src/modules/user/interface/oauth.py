from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from src.modules.user.core.command import (
    FindUserByOAuthCommand,
    OAuthLoginCommand,
)
from src.modules.user.core.service import UserService
from src.modules.user.core.value import AuthProvider
from src.modules.user.interface.adapter import (
    ErrorResponse,
    UserOAuthLoginRequest,
    UserOAuthLoginResponse,
    UserResponse,
)

router = APIRouter(prefix="/oauth", tags=["OAuth"])


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


# 카카오 OAuth 시작
@router.get(
    "/kakao",
    summary="카카오 OAuth 시작",
    description="카카오 OAuth 인증을 시작합니다.",
    responses={
        302: {"description": "카카오 OAuth 페이지로 리다이렉트"},
    },
)
async def kakao_oauth_start():
    """카카오 OAuth 시작"""
    try:
        import os

        client_id = os.getenv("KAKAO_CLIENT_ID")
        redirect_uri = os.getenv("KAKAO_REDIRECT_URI")

        if not client_id or not redirect_uri:
            raise HTTPException(status_code=500, detail="카카오 OAuth 설정이 누락되었습니다.")

        auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        return RedirectResponse(url=auth_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="카카오 OAuth 시작 중 오류가 발생했습니다.")


# 카카오 OAuth 콜백
@router.get(
    "/kakao/callback",
    summary="카카오 OAuth 콜백",
    description="카카오 OAuth 인증 후 콜백을 처리합니다.",
    responses={
        200: {"description": "카카오 OAuth 로그인 성공"},
        400: {"model": ErrorResponse, "description": "인증 실패"},
    },
)
async def kakao_oauth_callback(
    code: str = Query(..., description="인증 코드"),
    error: Optional[str] = Query(None, description="에러 코드"),
    user_service: UserService = Depends(get_user_service),
) -> UserOAuthLoginResponse:
    """카카오 OAuth 콜백"""
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"카카오 OAuth 인증 실패: {error}")

        # TODO: 카카오 API를 통해 액세스 토큰 및 사용자 정보 획득
        # 실제 구현에서는 카카오 API를 호출하여 사용자 정보를 가져와야 합니다.

        # 임시 사용자 정보 (실제로는 카카오 API에서 가져온 정보)
        kakao_user_info = {
            "id": "temp_kakao_id",
            "email": "user@example.com",
            "username": "kakao_user",
            "first_name": "카카오",
            "last_name": "사용자",
            "avatar_url": "https://example.com/avatar.jpg",
        }

        command = OAuthLoginCommand(
            provider=AuthProvider.KAKAO,
            provider_id=kakao_user_info["id"],
            email=kakao_user_info["email"],
            username=kakao_user_info["username"],
            first_name=kakao_user_info["first_name"],
            last_name=kakao_user_info["last_name"],
            avatar_url=kakao_user_info["avatar_url"],
        )

        return user_service.oauth_login(command)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="카카오 OAuth 콜백 처리 중 오류가 발생했습니다.")


# 구글 OAuth 시작
@router.get(
    "/google",
    summary="구글 OAuth 시작",
    description="구글 OAuth 인증을 시작합니다.",
    responses={
        302: {"description": "구글 OAuth 페이지로 리다이렉트"},
    },
)
async def google_oauth_start():
    """구글 OAuth 시작"""
    try:
        import os

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

        if not client_id or not redirect_uri:
            raise HTTPException(status_code=500, detail="구글 OAuth 설정이 누락되었습니다.")

        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=openid%20email%20profile"
        return RedirectResponse(url=auth_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="구글 OAuth 시작 중 오류가 발생했습니다.")


# 구글 OAuth 콜백
@router.get(
    "/google/callback",
    summary="구글 OAuth 콜백",
    description="구글 OAuth 인증 후 콜백을 처리합니다.",
    responses={
        200: {"description": "구글 OAuth 로그인 성공"},
        400: {"model": ErrorResponse, "description": "인증 실패"},
    },
)
async def google_oauth_callback(
    code: str = Query(..., description="인증 코드"),
    error: Optional[str] = Query(None, description="에러 코드"),
    user_service: UserService = Depends(get_user_service),
) -> UserOAuthLoginResponse:
    """구글 OAuth 콜백"""
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"구글 OAuth 인증 실패: {error}")

        # TODO: 구글 API를 통해 액세스 토큰 및 사용자 정보 획득
        # 실제 구현에서는 구글 API를 호출하여 사용자 정보를 가져와야 합니다.

        # 임시 사용자 정보 (실제로는 구글 API에서 가져온 정보)
        google_user_info = {
            "id": "temp_google_id",
            "email": "user@example.com",
            "username": "google_user",
            "first_name": "구글",
            "last_name": "사용자",
            "avatar_url": "https://example.com/avatar.jpg",
        }

        command = OAuthLoginCommand(
            provider=AuthProvider.GOOGLE,
            provider_id=google_user_info["id"],
            email=google_user_info["email"],
            username=google_user_info["username"],
            first_name=google_user_info["first_name"],
            last_name=google_user_info["last_name"],
            avatar_url=google_user_info["avatar_url"],
        )

        return user_service.oauth_login(command)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="구글 OAuth 콜백 처리 중 오류가 발생했습니다.")


# 네이버 OAuth 시작
@router.get(
    "/naver",
    summary="네이버 OAuth 시작",
    description="네이버 OAuth 인증을 시작합니다.",
    responses={
        302: {"description": "네이버 OAuth 페이지로 리다이렉트"},
    },
)
async def naver_oauth_start():
    """네이버 OAuth 시작"""
    try:
        import os

        client_id = os.getenv("NAVER_CLIENT_ID")
        redirect_uri = os.getenv("NAVER_REDIRECT_URI")

        if not client_id or not redirect_uri:
            raise HTTPException(status_code=500, detail="네이버 OAuth 설정이 누락되었습니다.")

        auth_url = f"https://nid.naver.com/oauth2.0/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        return RedirectResponse(url=auth_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="네이버 OAuth 시작 중 오류가 발생했습니다.")


# 네이버 OAuth 콜백
@router.get(
    "/naver/callback",
    summary="네이버 OAuth 콜백",
    description="네이버 OAuth 인증 후 콜백을 처리합니다.",
    responses={
        200: {"description": "네이버 OAuth 로그인 성공"},
        400: {"model": ErrorResponse, "description": "인증 실패"},
    },
)
async def naver_oauth_callback(
    code: str = Query(..., description="인증 코드"),
    error: Optional[str] = Query(None, description="에러 코드"),
    user_service: UserService = Depends(get_user_service),
) -> UserOAuthLoginResponse:
    """네이버 OAuth 콜백"""
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"네이버 OAuth 인증 실패: {error}")

        # TODO: 네이버 API를 통해 액세스 토큰 및 사용자 정보 획득
        # 실제 구현에서는 네이버 API를 호출하여 사용자 정보를 가져와야 합니다.

        # 임시 사용자 정보 (실제로는 네이버 API에서 가져온 정보)
        naver_user_info = {
            "id": "temp_naver_id",
            "email": "user@example.com",
            "username": "naver_user",
            "first_name": "네이버",
            "last_name": "사용자",
            "avatar_url": "https://example.com/avatar.jpg",
        }

        command = OAuthLoginCommand(
            provider=AuthProvider.NAVER,
            provider_id=naver_user_info["id"],
            email=naver_user_info["email"],
            username=naver_user_info["username"],
            first_name=naver_user_info["first_name"],
            last_name=naver_user_info["last_name"],
            avatar_url=naver_user_info["avatar_url"],
        )

        return user_service.oauth_login(command)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="네이버 OAuth 콜백 처리 중 오류가 발생했습니다.")


# 깃허브 OAuth 시작
@router.get(
    "/github",
    summary="깃허브 OAuth 시작",
    description="깃허브 OAuth 인증을 시작합니다.",
    responses={
        302: {"description": "깃허브 OAuth 페이지로 리다이렉트"},
    },
)
async def github_oauth_start():
    """깃허브 OAuth 시작"""
    try:
        import os

        client_id = os.getenv("GITHUB_CLIENT_ID")
        redirect_uri = os.getenv("GITHUB_REDIRECT_URI")

        if not client_id or not redirect_uri:
            raise HTTPException(status_code=500, detail="깃허브 OAuth 설정이 누락되었습니다.")

        auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user:email"
        return RedirectResponse(url=auth_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="깃허브 OAuth 시작 중 오류가 발생했습니다.")


# 깃허브 OAuth 콜백
@router.get(
    "/github/callback",
    summary="깃허브 OAuth 콜백",
    description="깃허브 OAuth 인증 후 콜백을 처리합니다.",
    responses={
        200: {"description": "깃허브 OAuth 로그인 성공"},
        400: {"model": ErrorResponse, "description": "인증 실패"},
    },
)
async def github_oauth_callback(
    code: str = Query(..., description="인증 코드"),
    error: Optional[str] = Query(None, description="에러 코드"),
    user_service: UserService = Depends(get_user_service),
) -> UserOAuthLoginResponse:
    """깃허브 OAuth 콜백"""
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"깃허브 OAuth 인증 실패: {error}")

        # TODO: 깃허브 API를 통해 액세스 토큰 및 사용자 정보 획득
        # 실제 구현에서는 깃허브 API를 호출하여 사용자 정보를 가져와야 합니다.

        # 임시 사용자 정보 (실제로는 깃허브 API에서 가져온 정보)
        github_user_info = {
            "id": "temp_github_id",
            "email": "user@example.com",
            "username": "github_user",
            "first_name": "깃허브",
            "last_name": "사용자",
            "avatar_url": "https://example.com/avatar.jpg",
        }

        command = OAuthLoginCommand(
            provider=AuthProvider.GITHUB,
            provider_id=github_user_info["id"],
            email=github_user_info["email"],
            username=github_user_info["username"],
            first_name=github_user_info["first_name"],
            last_name=github_user_info["last_name"],
            avatar_url=github_user_info["avatar_url"],
        )

        return user_service.oauth_login(command)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="깃허브 OAuth 콜백 처리 중 오류가 발생했습니다.")


# OAuth 계정 연결
@router.post(
    "/link",
    summary="OAuth 계정 연결",
    description="기존 계정에 OAuth 계정을 연결합니다.",
    responses={
        200: {"description": "OAuth 계정 연결 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        409: {"model": ErrorResponse, "description": "이미 연결된 계정"},
    },
)
async def link_oauth_account(request: UserOAuthLoginRequest, user_service: UserService = Depends(get_user_service)) -> UserOAuthLoginResponse:
    """OAuth 계정 연결"""
    try:
        # TODO: 기존 계정 확인 및 OAuth 계정 연결 로직 구현
        raise HTTPException(status_code=501, detail="OAuth 계정 연결 기능은 아직 구현되지 않았습니다.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="OAuth 계정 연결 중 오류가 발생했습니다.")


# OAuth 계정 연결 해제
@router.delete(
    "/unlink/{provider}",
    summary="OAuth 계정 연결 해제",
    description="연결된 OAuth 계정을 해제합니다.",
    responses={
        200: {"description": "OAuth 계정 연결 해제 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        404: {"model": ErrorResponse, "description": "연결된 계정을 찾을 수 없음"},
    },
)
async def unlink_oauth_account(provider: AuthProvider, user_service: UserService = Depends(get_user_service)) -> dict:
    """OAuth 계정 연결 해제"""
    try:
        # TODO: OAuth 계정 연결 해제 로직 구현
        return {"message": f"{provider.value} 계정 연결 해제 기능은 아직 구현되지 않았습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="OAuth 계정 연결 해제 중 오류가 발생했습니다.")


# 연결된 OAuth 계정 목록 조회
@router.get(
    "/linked-accounts",
    summary="연결된 OAuth 계정 목록 조회",
    description="현재 사용자에게 연결된 OAuth 계정 목록을 조회합니다.",
    responses={
        200: {"description": "연결된 OAuth 계정 목록 조회 성공"},
        401: {"model": ErrorResponse, "description": "인증되지 않은 사용자"},
    },
)
async def get_linked_oauth_accounts(user_service: UserService = Depends(get_user_service)) -> dict:
    """연결된 OAuth 계정 목록 조회"""
    try:
        # TODO: 연결된 OAuth 계정 목록 조회 로직 구현
        return {"linked_accounts": [], "message": "연결된 OAuth 계정 목록 조회 기능은 아직 구현되지 않았습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="연결된 OAuth 계정 목록 조회 중 오류가 발생했습니다.")


# OAuth 제공자별 사용자 정보 조회
@router.get(
    "/{provider}/user/{provider_id}",
    response_model=UserResponse,
    summary="OAuth 제공자별 사용자 정보 조회",
    description="특정 OAuth 제공자의 사용자 ID로 사용자 정보를 조회합니다.",
    responses={
        200: {"description": "사용자 정보 조회 성공"},
        404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없음"},
    },
)
async def get_user_by_oauth(provider: AuthProvider, provider_id: str, user_service: UserService = Depends(get_user_service)) -> UserResponse:
    """OAuth 제공자별 사용자 정보 조회"""
    try:
        command = FindUserByOAuthCommand(provider=provider, provider_id=provider_id)
        user = user_service.find_user_by_oauth(command)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 정보 조회 중 오류가 발생했습니다.")


# OAuth 상태 확인
@router.get(
    "/status",
    summary="OAuth 상태 확인",
    description="현재 OAuth 설정 상태를 확인합니다.",
    responses={
        200: {"description": "OAuth 상태 확인 성공"},
    },
)
async def get_oauth_status() -> dict:
    """OAuth 상태 확인"""
    try:
        import os

        oauth_status = {
            "kakao": {
                "enabled": bool(os.getenv("KAKAO_CLIENT_ID")),
                "client_id": os.getenv("KAKAO_CLIENT_ID"),
                "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
            },
            "google": {
                "enabled": bool(os.getenv("GOOGLE_CLIENT_ID")),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            },
            "naver": {
                "enabled": bool(os.getenv("NAVER_CLIENT_ID")),
                "client_id": os.getenv("NAVER_CLIENT_ID"),
                "redirect_uri": os.getenv("NAVER_REDIRECT_URI"),
            },
            "github": {
                "enabled": bool(os.getenv("GITHUB_CLIENT_ID")),
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "redirect_uri": os.getenv("GITHUB_REDIRECT_URI"),
            },
        }

        return oauth_status
    except Exception as e:
        raise HTTPException(status_code=500, detail="OAuth 상태 확인 중 오류가 발생했습니다.")
