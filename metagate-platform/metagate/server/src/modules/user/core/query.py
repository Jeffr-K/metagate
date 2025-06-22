from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from src.modules.user.core.entity import User
from src.modules.user.core.value import AuthProvider, UserRole, UserStatus


@dataclass
class UserResponse:
    """사용자 응답"""

    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    nickname: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    auth_provider: AuthProvider
    auth_provider_id: Optional[str]
    email_verified: bool
    user_role: UserRole
    user_status: UserStatus
    is_active: bool
    last_login_at: Optional[datetime]
    last_login_ip: Optional[str]
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        """전체 이름"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    @property
    def display_name(self) -> str:
        """표시 이름"""
        return self.nickname or self.username

    @property
    def is_admin(self) -> bool:
        """관리자 여부"""
        return self.user_role == UserRole.ADMIN

    @property
    def is_moderator(self) -> bool:
        """모더레이터 여부"""
        return self.user_role == UserRole.MODERATOR


@dataclass
class UserListResponse:
    """사용자 목록 응답"""

    users: List[UserResponse]
    total_count: int
    skip: int
    limit: int


@dataclass
class UserStatisticsResponse:
    """사용자 통계 응답"""

    total_users: int
    active_users: int
    pending_users: int
    suspended_users: int
    deleted_users: int
    verified_users: int
    unverified_users: int
    admin_users: int


@dataclass
class UserExistsResponse:
    """사용자 존재 여부 응답"""

    exists: bool


@dataclass
class UserProfileResponse:
    """사용자 프로필 응답"""

    id: str
    username: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    user_role: UserRole
    is_verified: bool
    created_at: datetime


@dataclass
class UserAuthResponse:
    """사용자 인증 응답"""

    id: str
    email: str
    username: str
    user_role: UserRole
    user_status: UserStatus
    is_active: bool
    email_verified: bool
    auth_provider: AuthProvider
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


@dataclass
class UserLoginResponse:
    """사용자 로그인 응답"""

    user: UserAuthResponse
    message: str = "로그인 성공"


@dataclass
class UserLogoutResponse:
    """사용자 로그아웃 응답"""

    message: str = "로그아웃 성공"


@dataclass
class UserRegistrationResponse:
    """사용자 회원가입 응답"""

    user_id: str
    email: str
    username: str
    message: str = "회원가입이 완료되었습니다. 이메일을 확인해주세요."


@dataclass
class UserUpdateResponse:
    """사용자 업데이트 응답"""

    user: UserResponse
    message: str = "사용자 정보가 업데이트되었습니다."


@dataclass
class UserDeleteResponse:
    """사용자 삭제 응답"""

    user_id: str
    message: str = "사용자가 삭제되었습니다."


@dataclass
class UserActivationResponse:
    """사용자 활성화 응답"""

    user_id: str
    message: str = "사용자가 활성화되었습니다."


@dataclass
class UserDeactivationResponse:
    """사용자 비활성화 응답"""

    user_id: str
    message: str = "사용자가 비활성화되었습니다."


@dataclass
class UserSuspensionResponse:
    """사용자 정지 응답"""

    user_id: str
    reason: Optional[str]
    message: str = "사용자가 정지되었습니다."


@dataclass
class UserPromotionResponse:
    """사용자 승격 응답"""

    user_id: str
    new_role: UserRole
    message: str = "사용자 역할이 변경되었습니다."


@dataclass
class UserDemotionResponse:
    """사용자 강등 응답"""

    user_id: str
    new_role: UserRole
    message: str = "사용자 역할이 변경되었습니다."


@dataclass
class EmailVerificationResponse:
    """이메일 인증 응답"""

    verified: bool
    message: str


@dataclass
class EmailVerificationSentResponse:
    """이메일 인증 메일 발송 응답"""

    user_id: str
    message: str = "인증 메일이 발송되었습니다."


@dataclass
class PasswordResetResponse:
    """비밀번호 재설정 응답"""

    email: str
    message: str = "비밀번호 재설정 메일이 발송되었습니다."


@dataclass
class PasswordResetConfirmResponse:
    """비밀번호 재설정 확인 응답"""

    success: bool
    message: str


@dataclass
class PasswordChangeResponse:
    """비밀번호 변경 응답"""

    success: bool
    message: str


@dataclass
class OAuthLoginResponse:
    """OAuth 로그인 응답"""

    user: UserAuthResponse
    is_new_user: bool
    message: str


@dataclass
class UserSearchResponse:
    """사용자 검색 응답"""

    users: List[UserResponse]
    total_count: int
    search_term: Optional[str]
    filters: dict
    skip: int
    limit: int


@dataclass
class UserDetailResponse:
    """사용자 상세 정보 응답"""

    user: UserResponse
    statistics: Optional[dict] = None


class UserQuery:
    """사용자 조회 Query"""

    def __init__(self):
        pass

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)
            return repo.find_by_id(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)
            return repo.find_by_email(email)

    async def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)
            return repo.find_by_username(username)

    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """역할로 사용자 목록 조회"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)
            return repo.find_by_role(role)[skip : skip + limit]

    async def get_by_status(self, status: UserStatus, skip: int = 0, limit: int = 100) -> List[User]:
        """상태로 사용자 목록 조회"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)
            return repo.find_by_status(status)[skip : skip + limit]

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)
            return repo.find_all(skip=skip, limit=limit)

    async def search_users(
        self,
        search_term: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        email_verified: Optional[bool] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """사용자 검색"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)
            return repo.search_users(
                search_term=search_term,
                role=role,
                status=status,
                email_verified=email_verified,
                is_active=is_active,
                skip=skip,
                limit=limit,
            )
