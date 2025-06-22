from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.modules.user.core.value import AuthProvider, UserRole, UserStatus


@dataclass
class UserCreatedEvent:
    """사용자 생성 이벤트"""

    user_id: str
    email: str
    username: str
    auth_provider: AuthProvider
    created_at: datetime


@dataclass
class UserUpdatedEvent:
    """사용자 정보 업데이트 이벤트"""

    user_id: str
    updated_fields: dict
    updated_at: datetime


@dataclass
class UserDeletedEvent:
    """사용자 삭제 이벤트"""

    user_id: str
    hard_delete: bool
    deleted_at: datetime


@dataclass
class UserActivatedEvent:
    """사용자 활성화 이벤트"""

    user_id: str
    activated_at: datetime


@dataclass
class UserDeactivatedEvent:
    """사용자 비활성화 이벤트"""

    user_id: str
    deactivated_at: datetime


@dataclass
class UserSuspendedEvent:
    """사용자 정지 이벤트"""

    user_id: str
    reason: Optional[str]
    suspended_at: datetime


@dataclass
class UserPromotedEvent:
    """사용자 승격 이벤트"""

    user_id: str
    old_role: UserRole
    new_role: UserRole
    promoted_at: datetime


@dataclass
class UserDemotedEvent:
    """사용자 강등 이벤트"""

    user_id: str
    old_role: UserRole
    new_role: UserRole
    demoted_at: datetime


@dataclass
class UserLoggedInEvent:
    """사용자 로그인 이벤트"""

    user_id: str
    auth_provider: AuthProvider
    ip_address: Optional[str]
    login_at: datetime


@dataclass
class UserLoggedOutEvent:
    """사용자 로그아웃 이벤트"""

    user_id: str
    logout_at: datetime


@dataclass
class UserEmailVerifiedEvent:
    """사용자 이메일 인증 완료 이벤트"""

    user_id: str
    email: str
    verified_at: datetime


@dataclass
class UserPasswordChangedEvent:
    """사용자 비밀번호 변경 이벤트"""

    user_id: str
    changed_at: datetime


@dataclass
class UserPasswordResetRequestedEvent:
    """사용자 비밀번호 재설정 요청 이벤트"""

    user_id: str
    email: str
    reset_token: str
    expires_at: datetime
    requested_at: datetime


@dataclass
class UserPasswordResetCompletedEvent:
    """사용자 비밀번호 재설정 완료 이벤트"""

    user_id: str
    reset_at: datetime


@dataclass
class UserOAuthLinkedEvent:
    """사용자 OAuth 계정 연결 이벤트"""

    user_id: str
    provider: AuthProvider
    provider_id: str
    linked_at: datetime


@dataclass
class UserProfileUpdatedEvent:
    """사용자 프로필 업데이트 이벤트"""

    user_id: str
    updated_fields: dict
    updated_at: datetime


@dataclass
class UserLastLoginUpdatedEvent:
    """사용자 마지막 로그인 업데이트 이벤트"""

    user_id: str
    login_at: datetime
    ip_address: Optional[str]


@dataclass
class UserAccountLockedEvent:
    """사용자 계정 잠금 이벤트"""

    user_id: str
    reason: str
    locked_at: datetime


@dataclass
class UserAccountUnlockedEvent:
    """사용자 계정 잠금 해제 이벤트"""

    user_id: str
    unlocked_at: datetime


@dataclass
class UserFailedLoginAttemptEvent:
    """사용자 로그인 실패 이벤트"""

    user_id: Optional[str]
    email: str
    ip_address: Optional[str]
    attempt_at: datetime


@dataclass
class UserEmailVerificationSentEvent:
    """사용자 이메일 인증 메일 발송 이벤트"""

    user_id: str
    email: str
    verification_token: str
    expires_at: datetime
    sent_at: datetime


@dataclass
class UserWelcomeEmailSentEvent:
    """사용자 환영 이메일 발송 이벤트"""

    user_id: str
    email: str
    sent_at: datetime


@dataclass
class UserAccountRecoveryRequestedEvent:
    """사용자 계정 복구 요청 이벤트"""

    user_id: str
    email: str
    recovery_token: str
    expires_at: datetime
    requested_at: datetime


@dataclass
class UserAccountRecoveryCompletedEvent:
    """사용자 계정 복구 완료 이벤트"""

    user_id: str
    recovered_at: datetime


@dataclass
class UserDataExportRequestedEvent:
    """사용자 데이터 내보내기 요청 이벤트"""

    user_id: str
    requested_at: datetime


@dataclass
class UserDataExportCompletedEvent:
    """사용자 데이터 내보내기 완료 이벤트"""

    user_id: str
    export_url: str
    completed_at: datetime


@dataclass
class UserPrivacySettingsUpdatedEvent:
    """사용자 개인정보 설정 업데이트 이벤트"""

    user_id: str
    updated_settings: dict
    updated_at: datetime


@dataclass
class UserNotificationPreferencesUpdatedEvent:
    """사용자 알림 설정 업데이트 이벤트"""

    user_id: str
    updated_preferences: dict
    updated_at: datetime


@dataclass
class UserSessionExpiredEvent:
    """사용자 세션 만료 이벤트"""

    user_id: str
    session_id: str
    expired_at: datetime


@dataclass
class UserSessionRevokedEvent:
    """사용자 세션 취소 이벤트"""

    user_id: str
    session_id: str
    revoked_at: datetime
    reason: str
