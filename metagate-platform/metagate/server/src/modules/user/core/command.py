from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.modules.user.core.value import AuthProvider, UserRole, UserStatus


@dataclass
class CreateUserCommand:
    """사용자 생성 명령"""

    email: str
    username: str
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    auth_provider: AuthProvider = AuthProvider.EMAIL
    auth_provider_id: Optional[str] = None
    user_role: UserRole = UserRole.USER
    user_status: UserStatus = UserStatus.PENDING


@dataclass
class UpdateUserCommand:
    """사용자 정보 업데이트 명령"""

    user_id: str
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    user_role: Optional[UserRole] = None
    user_status: Optional[UserStatus] = None
    is_active: Optional[bool] = None


@dataclass
class ChangePasswordCommand:
    """비밀번호 변경 명령"""

    user_id: str
    current_password: str
    new_password: str


@dataclass
class ResetPasswordCommand:
    """비밀번호 재설정 명령"""

    email: str


@dataclass
class ConfirmPasswordResetCommand:
    """비밀번호 재설정 확인 명령"""

    token: str
    new_password: str


@dataclass
class VerifyEmailCommand:
    """이메일 인증 명령"""

    token: str


@dataclass
class SendEmailVerificationCommand:
    """이메일 인증 메일 발송 명령"""

    user_id: str


@dataclass
class LoginCommand:
    """로그인 명령"""

    email: str
    password: str
    ip_address: Optional[str] = None


@dataclass
class OAuthLoginCommand:
    """OAuth 로그인 명령"""

    provider: AuthProvider
    provider_id: str
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    ip_address: Optional[str] = None


@dataclass
class LogoutCommand:
    """로그아웃 명령"""

    user_id: str
    token: str


@dataclass
class ActivateUserCommand:
    """사용자 활성화 명령"""

    user_id: str


@dataclass
class DeactivateUserCommand:
    """사용자 비활성화 명령"""

    user_id: str


@dataclass
class SuspendUserCommand:
    """사용자 정지 명령"""

    user_id: str
    reason: Optional[str] = None


@dataclass
class DeleteUserCommand:
    """사용자 삭제 명령"""

    user_id: str
    hard_delete: bool = False


@dataclass
class PromoteToAdminCommand:
    """관리자 승격 명령"""

    user_id: str


@dataclass
class DemoteToUserCommand:
    """일반 사용자 강등 명령"""

    user_id: str


@dataclass
class UpdateLastLoginCommand:
    """마지막 로그인 업데이트 명령"""

    user_id: str
    ip_address: Optional[str] = None


@dataclass
class CheckEmailExistsCommand:
    """이메일 존재 여부 확인 명령"""

    email: str


@dataclass
class CheckUsernameExistsCommand:
    """사용자명 존재 여부 확인 명령"""

    username: str


@dataclass
class FindUserByIdCommand:
    """ID로 사용자 조회 명령"""

    user_id: str


@dataclass
class FindUserByEmailCommand:
    """이메일로 사용자 조회 명령"""

    email: str


@dataclass
class FindUserByUsernameCommand:
    """사용자명으로 사용자 조회 명령"""

    username: str


@dataclass
class FindUserByOAuthCommand:
    """OAuth 제공자 ID로 사용자 조회 명령"""

    provider: AuthProvider
    provider_id: str


@dataclass
class FindUserByEmailVerificationTokenCommand:
    """이메일 인증 토큰으로 사용자 조회 명령"""

    token: str


@dataclass
class ListUsersCommand:
    """사용자 목록 조회 명령"""

    skip: int = 0
    limit: int = 100
    search_term: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    auth_provider: Optional[AuthProvider] = None
    email_verified: Optional[bool] = None
    is_active: Optional[bool] = None


@dataclass
class ListAdminsCommand:
    """관리자 목록 조회 명령"""

    skip: int = 0
    limit: int = 100


@dataclass
class ListActiveUsersCommand:
    """활성 사용자 목록 조회 명령"""

    skip: int = 0
    limit: int = 100


@dataclass
class ListVerifiedUsersCommand:
    """이메일 인증 완료된 사용자 목록 조회 명령"""

    skip: int = 0
    limit: int = 100


@dataclass
class GetUserStatisticsCommand:
    """사용자 통계 조회 명령"""

    pass
