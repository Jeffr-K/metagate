from enum import Enum


class UserRole(Enum):
    """사용자 역할"""

    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(Enum):
    """사용자 상태"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class AuthProvider(Enum):
    """인증 제공자"""

    EMAIL = "email"
    KAKAO = "kakao"
    GOOGLE = "google"
    NAVER = "naver"
    GITHUB = "github"


class EmailVerificationStatus(Enum):
    """이메일 인증 상태"""

    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"


class PasswordResetStatus(Enum):
    """비밀번호 재설정 상태"""

    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"
