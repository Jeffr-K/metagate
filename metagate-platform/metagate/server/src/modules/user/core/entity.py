from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.database import Base
from src.modules.user.core.value import AuthProvider, EmailVerificationStatus, UserRole, UserStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 인증 관련
    auth_provider: Mapped[AuthProvider] = mapped_column(SQLEnum(AuthProvider), default=AuthProvider.EMAIL, nullable=False)
    auth_provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_verification_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 상태 및 권한
    user_role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    user_status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 마지막 로그인
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # 메타데이터
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    @classmethod
    def create(
        cls,
        id: str,
        email: str,
        username: str,
        password_hash: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        auth_provider: AuthProvider = AuthProvider.EMAIL,
        auth_provider_id: Optional[str] = None,
        user_role: UserRole = UserRole.USER,
        user_status: UserStatus = UserStatus.PENDING,
    ) -> "User":
        """사용자 생성 팩토리 메서드"""
        return cls(
            id=id,
            email=email,
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            phone=phone,
            avatar_url=avatar_url,
            bio=bio,
            auth_provider=auth_provider,
            auth_provider_id=auth_provider_id,
            user_role=user_role,
            user_status=user_status,
        )

    def update(
        self,
        email: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        user_role: Optional[UserRole] = None,
        user_status: Optional[UserStatus] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        """사용자 정보 업데이트"""
        if email is not None:
            self.email = email
        if username is not None:
            self.username = username
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if nickname is not None:
            self.nickname = nickname
        if phone is not None:
            self.phone = phone
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if bio is not None:
            self.bio = bio
        if user_role is not None:
            self.user_role = user_role
        if user_status is not None:
            self.user_status = user_status
        if is_active is not None:
            self.is_active = is_active

    def update_password(self, password_hash: str) -> None:
        """비밀번호 업데이트"""
        self.password_hash = password_hash

    def verify_email(self) -> None:
        """이메일 인증 완료"""
        self.email_verified = True
        self.email_verification_token = None
        self.email_verification_expires = None
        if self.user_status == UserStatus.PENDING:
            self.user_status = UserStatus.ACTIVE

    def set_email_verification_token(self, token: str, expires: datetime) -> None:
        """이메일 인증 토큰 설정"""
        self.email_verification_token = token
        self.email_verification_expires = expires

    def update_last_login(self, ip_address: Optional[str] = None) -> None:
        """마지막 로그인 정보 업데이트"""
        self.last_login_at = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address

    def activate(self) -> None:
        """사용자 활성화"""
        self.user_status = UserStatus.ACTIVE
        self.is_active = True

    def deactivate(self) -> None:
        """사용자 비활성화"""
        self.user_status = UserStatus.INACTIVE
        self.is_active = False

    def suspend(self) -> None:
        """사용자 정지"""
        self.user_status = UserStatus.SUSPENDED
        self.is_active = False

    def delete(self) -> None:
        """사용자 삭제 (소프트 삭제)"""
        self.user_status = UserStatus.DELETED
        self.is_active = False
        self.deleted_at = datetime.utcnow()

    def promote_to_admin(self) -> None:
        """관리자로 승격"""
        self.user_role = UserRole.ADMIN

    def demote_to_user(self) -> None:
        """일반 사용자로 강등"""
        self.user_role = UserRole.USER

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
        """표시 이름 (닉네임 또는 사용자명)"""
        return self.nickname or self.username

    @property
    def is_admin(self) -> bool:
        """관리자 여부"""
        return self.user_role == UserRole.ADMIN

    @property
    def is_moderator(self) -> bool:
        """모더레이터 여부"""
        return self.user_role == UserRole.MODERATOR

    @property
    def is_verified(self) -> bool:
        """이메일 인증 완료 여부"""
        return self.email_verified

    @property
    def is_deleted(self) -> bool:
        """삭제된 사용자 여부"""
        return self.user_status == UserStatus.DELETED
