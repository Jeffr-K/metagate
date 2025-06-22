from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.modules.user.core.value import AuthProvider, UserRole, UserStatus


# Request Models
class UserCreateRequest(BaseModel):
    """사용자 생성 요청"""

    email: EmailStr = Field(..., description="사용자 이메일")
    username: str = Field(..., min_length=3, max_length=50, description="사용자명")
    password: Optional[str] = Field(None, min_length=8, description="비밀번호")
    first_name: Optional[str] = Field(None, max_length=100, description="이름")
    last_name: Optional[str] = Field(None, max_length=100, description="성")
    nickname: Optional[str] = Field(None, max_length=100, description="닉네임")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    avatar_url: Optional[str] = Field(None, max_length=500, description="프로필 이미지 URL")
    bio: Optional[str] = Field(None, max_length=1000, description="자기소개")
    auth_provider: AuthProvider = Field(AuthProvider.EMAIL, description="인증 제공자")
    auth_provider_id: Optional[str] = Field(None, description="OAuth 제공자 ID")

    @validator("username")
    def validate_username(cls, v):
        if not v.isalnum() and not all(c in "._-" for c in v if not c.isalnum()):
            raise ValueError("사용자명은 영문, 숫자, 점(.), 언더스코어(_), 하이픈(-)만 사용할 수 있습니다.")
        return v


class UserUpdateRequest(BaseModel):
    """사용자 정보 업데이트 요청"""

    email: Optional[EmailStr] = Field(None, description="사용자 이메일")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="사용자명")
    first_name: Optional[str] = Field(None, max_length=100, description="이름")
    last_name: Optional[str] = Field(None, max_length=100, description="성")
    nickname: Optional[str] = Field(None, max_length=100, description="닉네임")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    avatar_url: Optional[str] = Field(None, max_length=500, description="프로필 이미지 URL")
    bio: Optional[str] = Field(None, max_length=1000, description="자기소개")
    user_role: Optional[UserRole] = Field(None, description="사용자 역할")
    user_status: Optional[UserStatus] = Field(None, description="사용자 상태")
    is_active: Optional[bool] = Field(None, description="활성 상태")

    @validator("username")
    def validate_username(cls, v):
        if v is not None:
            if not v.isalnum() and not all(c in "._-" for c in v if not c.isalnum()):
                raise ValueError("사용자명은 영문, 숫자, 점(.), 언더스코어(_), 하이픈(-)만 사용할 수 있습니다.")
        return v


class UserLoginRequest(BaseModel):
    """사용자 로그인 요청"""

    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., min_length=1, description="비밀번호")


class UserOAuthLoginRequest(BaseModel):
    """OAuth 로그인 요청"""

    provider: AuthProvider = Field(..., description="OAuth 제공자")
    provider_id: str = Field(..., description="OAuth 제공자 ID")
    email: EmailStr = Field(..., description="사용자 이메일")
    username: str = Field(..., min_length=3, max_length=50, description="사용자명")
    first_name: Optional[str] = Field(None, max_length=100, description="이름")
    last_name: Optional[str] = Field(None, max_length=100, description="성")
    avatar_url: Optional[str] = Field(None, max_length=500, description="프로필 이미지 URL")


class UserChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청"""

    current_password: str = Field(..., min_length=1, description="현재 비밀번호")
    new_password: str = Field(..., min_length=8, description="새 비밀번호")

    @validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        return v


class UserResetPasswordRequest(BaseModel):
    """비밀번호 재설정 요청"""

    email: EmailStr = Field(..., description="사용자 이메일")


class UserConfirmPasswordResetRequest(BaseModel):
    """비밀번호 재설정 확인 요청"""

    token: str = Field(..., description="비밀번호 재설정 토큰")
    new_password: str = Field(..., min_length=8, description="새 비밀번호")

    @validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        return v


class UserVerifyEmailRequest(BaseModel):
    """이메일 인증 요청"""

    token: str = Field(..., description="이메일 인증 토큰")


class UserSendEmailVerificationRequest(BaseModel):
    """이메일 인증 메일 발송 요청"""

    user_id: str = Field(..., description="사용자 ID")


class UserSuspendRequest(BaseModel):
    """사용자 정지 요청"""

    reason: Optional[str] = Field(None, max_length=500, description="정지 사유")


class UserSearchRequest(BaseModel):
    """사용자 검색 요청"""

    search_term: Optional[str] = Field(None, description="검색어")
    role: Optional[UserRole] = Field(None, description="사용자 역할")
    status: Optional[UserStatus] = Field(None, description="사용자 상태")
    auth_provider: Optional[AuthProvider] = Field(None, description="인증 제공자")
    email_verified: Optional[bool] = Field(None, description="이메일 인증 여부")
    is_active: Optional[bool] = Field(None, description="활성 상태")
    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")


class UserListRequest(BaseModel):
    """사용자 목록 조회 요청"""

    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")


# Response Models
class UserResponse(BaseModel):
    """사용자 응답"""

    id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자명")
    first_name: Optional[str] = Field(None, description="이름")
    last_name: Optional[str] = Field(None, description="성")
    nickname: Optional[str] = Field(None, description="닉네임")
    phone: Optional[str] = Field(None, description="전화번호")
    avatar_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    bio: Optional[str] = Field(None, description="자기소개")
    auth_provider: AuthProvider = Field(..., description="인증 제공자")
    auth_provider_id: Optional[str] = Field(None, description="OAuth 제공자 ID")
    email_verified: bool = Field(..., description="이메일 인증 여부")
    user_role: UserRole = Field(..., description="사용자 역할")
    user_status: UserStatus = Field(..., description="사용자 상태")
    is_active: bool = Field(..., description="활성 상태")
    last_login_at: Optional[datetime] = Field(None, description="마지막 로그인 시간")
    last_login_ip: Optional[str] = Field(None, description="마지막 로그인 IP")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """사용자 목록 응답"""

    users: List[UserResponse] = Field(..., description="사용자 목록")
    total_count: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회한 개수")


class UserAuthResponse(BaseModel):
    """사용자 인증 응답"""

    id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자명")
    user_role: UserRole = Field(..., description="사용자 역할")
    user_status: UserStatus = Field(..., description="사용자 상태")
    is_active: bool = Field(..., description="활성 상태")
    email_verified: bool = Field(..., description="이메일 인증 여부")
    auth_provider: AuthProvider = Field(..., description="인증 제공자")
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field("bearer", description="토큰 타입")
    expires_in: int = Field(1800, description="토큰 만료 시간(초)")


class UserLoginResponse(BaseModel):
    """사용자 로그인 응답"""

    user: UserAuthResponse = Field(..., description="사용자 인증 정보")
    message: str = Field("로그인 성공", description="응답 메시지")


class UserOAuthLoginResponse(BaseModel):
    """OAuth 로그인 응답"""

    user: UserAuthResponse = Field(..., description="사용자 인증 정보")
    is_new_user: bool = Field(..., description="새 사용자 여부")
    message: str = Field(..., description="응답 메시지")


class UserRegistrationResponse(BaseModel):
    """사용자 회원가입 응답"""

    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자명")
    message: str = Field("회원가입이 완료되었습니다. 이메일을 확인해주세요.", description="응답 메시지")


class UserUpdateResponse(BaseModel):
    """사용자 업데이트 응답"""

    user: UserResponse = Field(..., description="업데이트된 사용자 정보")
    message: str = Field("사용자 정보가 업데이트되었습니다.", description="응답 메시지")


class UserDeleteResponse(BaseModel):
    """사용자 삭제 응답"""

    user_id: str = Field(..., description="사용자 ID")
    message: str = Field("사용자가 삭제되었습니다.", description="응답 메시지")


class UserActivationResponse(BaseModel):
    """사용자 활성화 응답"""

    user_id: str = Field(..., description="사용자 ID")
    message: str = Field("사용자가 활성화되었습니다.", description="응답 메시지")


class UserDeactivationResponse(BaseModel):
    """사용자 비활성화 응답"""

    user_id: str = Field(..., description="사용자 ID")
    message: str = Field("사용자가 비활성화되었습니다.", description="응답 메시지")


class UserSuspensionResponse(BaseModel):
    """사용자 정지 응답"""

    user_id: str = Field(..., description="사용자 ID")
    reason: Optional[str] = Field(None, description="정지 사유")
    message: str = Field("사용자가 정지되었습니다.", description="응답 메시지")


class UserPromotionResponse(BaseModel):
    """사용자 승격 응답"""

    user_id: str = Field(..., description="사용자 ID")
    new_role: UserRole = Field(..., description="새 역할")
    message: str = Field("사용자 역할이 변경되었습니다.", description="응답 메시지")


class UserDemotionResponse(BaseModel):
    """사용자 강등 응답"""

    user_id: str = Field(..., description="사용자 ID")
    new_role: UserRole = Field(..., description="새 역할")
    message: str = Field("사용자 역할이 변경되었습니다.", description="응답 메시지")


class UserExistsResponse(BaseModel):
    """사용자 존재 여부 응답"""

    exists: bool = Field(..., description="존재 여부")


class EmailVerificationResponse(BaseModel):
    """이메일 인증 응답"""

    verified: bool = Field(..., description="인증 성공 여부")
    message: str = Field(..., description="응답 메시지")


class EmailVerificationSentResponse(BaseModel):
    """이메일 인증 메일 발송 응답"""

    user_id: str = Field(..., description="사용자 ID")
    message: str = Field("인증 메일이 발송되었습니다.", description="응답 메시지")


class PasswordResetResponse(BaseModel):
    """비밀번호 재설정 응답"""

    email: str = Field(..., description="사용자 이메일")
    message: str = Field("비밀번호 재설정 메일이 발송되었습니다.", description="응답 메시지")


class PasswordResetConfirmResponse(BaseModel):
    """비밀번호 재설정 확인 응답"""

    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")


class PasswordChangeResponse(BaseModel):
    """비밀번호 변경 응답"""

    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")


class UserLogoutResponse(BaseModel):
    """사용자 로그아웃 응답"""

    message: str = Field("로그아웃 성공", description="응답 메시지")


class UserStatisticsResponse(BaseModel):
    """사용자 통계 응답"""

    total_users: int = Field(..., description="전체 사용자 수")
    active_users: int = Field(..., description="활성 사용자 수")
    inactive_users: int = Field(..., description="비활성 사용자 수")
    suspended_users: int = Field(..., description="정지된 사용자 수")
    pending_users: int = Field(..., description="대기 중인 사용자 수")
    deleted_users: int = Field(..., description="삭제된 사용자 수")
    verified_users: int = Field(..., description="인증된 사용자 수")
    unverified_users: int = Field(..., description="미인증 사용자 수")
    admin_users: int = Field(..., description="관리자 수")
    moderator_users: int = Field(..., description="모더레이터 수")
    regular_users: int = Field(..., description="일반 사용자 수")
    email_auth_users: int = Field(..., description="이메일 인증 사용자 수")
    kakao_auth_users: int = Field(..., description="카카오 인증 사용자 수")
    google_auth_users: int = Field(..., description="구글 인증 사용자 수")
    naver_auth_users: int = Field(..., description="네이버 인증 사용자 수")
    github_auth_users: int = Field(..., description="깃허브 인증 사용자 수")
    users_created_today: int = Field(..., description="오늘 생성된 사용자 수")
    users_created_this_week: int = Field(..., description="이번 주 생성된 사용자 수")
    users_created_this_month: int = Field(..., description="이번 달 생성된 사용자 수")
    users_logged_in_today: int = Field(..., description="오늘 로그인한 사용자 수")


class ErrorResponse(BaseModel):
    """에러 응답"""

    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    code: Optional[str] = Field(None, description="에러 코드")


class SuccessResponse(BaseModel):
    """성공 응답"""

    message: str = Field(..., description="성공 메시지")
    data: Optional[dict] = Field(None, description="응답 데이터")
