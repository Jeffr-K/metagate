from typing import List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from src.modules.user.core.entity import User
from src.modules.user.core.repository import UserRepository
from src.modules.user.core.value import AuthProvider, UserRole, UserStatus


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy 기반 사용자 Repository 구현체"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> User:
        """사용자 저장"""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        stmt = select(User).where(User.id == user_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        stmt = select(User).where(User.username == username)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_auth_provider_id(self, provider: AuthProvider, provider_id: str) -> Optional[User]:
        """OAuth 제공자 ID로 사용자 조회"""
        stmt = select(User).where(and_(User.auth_provider == provider, User.auth_provider_id == provider_id))
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_email_verification_token(self, token: str) -> Optional[User]:
        """이메일 인증 토큰으로 사용자 조회"""
        stmt = select(User).where(User.email_verification_token == token)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_role(self, role: UserRole) -> List[User]:
        """역할로 사용자 목록 조회"""
        stmt = select(User).where(User.user_role == role)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_status(self, status: UserStatus) -> List[User]:
        """상태로 사용자 목록 조회"""
        stmt = select(User).where(User.user_status == status)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회 (페이징)"""
        stmt = select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def delete(self, user_id: str) -> bool:
        """사용자 삭제 (소프트 삭제)"""
        user = self.find_by_id(user_id)
        if user:
            user.delete()
            self.session.commit()
            return True
        return False

    def exists_by_id(self, user_id: str) -> bool:
        """사용자 존재 여부 확인"""
        stmt = select(User.id).where(User.id == user_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def exists_by_email(self, email: str) -> bool:
        """이메일로 사용자 존재 여부 확인"""
        stmt = select(User.id).where(User.email == email)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def exists_by_username(self, username: str) -> bool:
        """사용자명으로 사용자 존재 여부 확인"""
        stmt = select(User.id).where(User.username == username)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def search_users(
        self,
        search_term: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        auth_provider: Optional[AuthProvider] = None,
        email_verified: Optional[bool] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """고급 검색 기능"""
        conditions = [User.deleted_at.is_(None)]

        if search_term:
            conditions.append(
                or_(
                    User.email.ilike(f"%{search_term}%"),
                    User.username.ilike(f"%{search_term}%"),
                    User.first_name.ilike(f"%{search_term}%"),
                    User.last_name.ilike(f"%{search_term}%"),
                    User.nickname.ilike(f"%{search_term}%"),
                )
            )

        if role:
            conditions.append(User.user_role == role)

        if status:
            conditions.append(User.user_status == status)

        if auth_provider:
            conditions.append(User.auth_provider == auth_provider)

        if email_verified is not None:
            conditions.append(User.email_verified == email_verified)

        if is_active is not None:
            conditions.append(User.is_active == is_active)

        stmt = select(User)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_admins(self) -> List[User]:
        """관리자 목록 조회"""
        return self.find_by_role(UserRole.ADMIN)

    def find_active_users(self) -> List[User]:
        """활성 사용자 목록 조회"""
        stmt = select(User).where(and_(User.is_active == True, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_verified_users(self) -> List[User]:
        """이메일 인증 완료된 사용자 목록 조회"""
        stmt = select(User).where(and_(User.email_verified == True, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def count_users(self) -> int:
        """전체 사용자 수 조회"""
        stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        result = self.session.execute(stmt)
        return result.scalar()

    def count_users_by_role(self, role: UserRole) -> int:
        """역할별 사용자 수 조회"""
        stmt = select(func.count(User.id)).where(and_(User.user_role == role, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return result.scalar()

    def count_users_by_status(self, status: UserStatus) -> int:
        """상태별 사용자 수 조회"""
        stmt = select(func.count(User.id)).where(and_(User.user_status == status, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return result.scalar()

    def count_users_by_auth_provider(self, provider: AuthProvider) -> int:
        """인증 제공자별 사용자 수 조회"""
        stmt = select(func.count(User.id)).where(and_(User.auth_provider == provider, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return result.scalar()

    def count_verified_users(self) -> int:
        """이메일 인증 완료된 사용자 수 조회"""
        stmt = select(func.count(User.id)).where(and_(User.email_verified == True, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return result.scalar()

    def count_active_users(self) -> int:
        """활성 사용자 수 조회"""
        stmt = select(func.count(User.id)).where(and_(User.is_active == True, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return result.scalar()

    def find_users_created_today(self) -> List[User]:
        """오늘 생성된 사용자 목록 조회"""
        from datetime import date, datetime

        today = date.today()
        stmt = select(User).where(and_(func.date(User.created_at) == today, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_users_created_this_week(self) -> List[User]:
        """이번 주 생성된 사용자 목록 조회"""
        from datetime import date, datetime, timedelta

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        stmt = select(User).where(and_(func.date(User.created_at) >= start_of_week, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_users_created_this_month(self) -> List[User]:
        """이번 달 생성된 사용자 목록 조회"""
        from datetime import date, datetime

        today = date.today()
        start_of_month = today.replace(day=1)
        stmt = select(User).where(and_(func.date(User.created_at) >= start_of_month, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_users_logged_in_today(self) -> List[User]:
        """오늘 로그인한 사용자 목록 조회"""
        from datetime import date, datetime

        today = date.today()
        stmt = select(User).where(and_(func.date(User.last_login_at) == today, User.deleted_at.is_(None)))
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_user_statistics(self) -> dict:
        """사용자 통계 조회"""
        total_users = self.count_users()
        active_users = self.count_active_users()
        verified_users = self.count_verified_users()
        admin_users = self.count_users_by_role(UserRole.ADMIN)
        moderator_users = self.count_users_by_role(UserRole.MODERATOR)
        regular_users = self.count_users_by_role(UserRole.USER)

        email_auth_users = self.count_users_by_auth_provider(AuthProvider.EMAIL)
        kakao_auth_users = self.count_users_by_auth_provider(AuthProvider.KAKAO)
        google_auth_users = self.count_users_by_auth_provider(AuthProvider.GOOGLE)
        naver_auth_users = self.count_users_by_auth_provider(AuthProvider.NAVER)
        github_auth_users = self.count_users_by_auth_provider(AuthProvider.GITHUB)

        users_created_today = len(self.find_users_created_today())
        users_created_this_week = len(self.find_users_created_this_week())
        users_created_this_month = len(self.find_users_created_this_month())
        users_logged_in_today = len(self.find_users_logged_in_today())

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "admin_users": admin_users,
            "moderator_users": moderator_users,
            "regular_users": regular_users,
            "email_auth_users": email_auth_users,
            "kakao_auth_users": kakao_auth_users,
            "google_auth_users": google_auth_users,
            "naver_auth_users": naver_auth_users,
            "github_auth_users": github_auth_users,
            "users_created_today": users_created_today,
            "users_created_this_week": users_created_this_week,
            "users_created_this_month": users_created_this_month,
            "users_logged_in_today": users_logged_in_today,
        }
