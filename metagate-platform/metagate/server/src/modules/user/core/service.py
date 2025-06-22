import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

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
    FindUserByEmailVerificationTokenCommand,
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
    UpdateLastLoginCommand,
    UpdateUserCommand,
    VerifyEmailCommand,
)
from src.modules.user.core.entity import User
from src.modules.user.core.query import (
    EmailVerificationResponse,
    EmailVerificationSentResponse,
    OAuthLoginResponse,
    PasswordChangeResponse,
    PasswordResetConfirmResponse,
    PasswordResetResponse,
    UserActivationResponse,
    UserAuthResponse,
    UserDeactivationResponse,
    UserDeleteResponse,
    UserDemotionResponse,
    UserExistsResponse,
    UserListResponse,
    UserLoginResponse,
    UserLogoutResponse,
    UserPromotionResponse,
    UserRegistrationResponse,
    UserResponse,
    UserStatisticsResponse,
    UserSuspensionResponse,
    UserUpdateResponse,
)
from src.modules.user.core.repository import UserRepository
from src.modules.user.core.value import AuthProvider, UserRole, UserStatus


class UserService:
    """사용자 서비스"""

    def __init__(
        self,
        user_repository: UserRepository,
        jwt_secret_key: str,
        jwt_algorithm: str = "HS256",
        jwt_access_token_expire_minutes: int = 30,
        jwt_refresh_token_expire_days: int = 7,
        password_salt: str = "",
        bcrypt_rounds: int = 12,
    ):
        self.user_repository = user_repository
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = jwt_algorithm
        self.jwt_access_token_expire_minutes = jwt_access_token_expire_minutes
        self.jwt_refresh_token_expire_days = jwt_refresh_token_expire_days
        self.password_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=bcrypt_rounds, bcrypt__salt=password_salt.encode() if password_salt else None
        )

    def _hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        return self.password_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return self.password_context.verify(plain_password, hashed_password)

    def _create_access_token(self, data: dict) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def _create_refresh_token(self, data: dict) -> str:
        """리프레시 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.jwt_refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def _create_email_verification_token(self) -> str:
        """이메일 인증 토큰 생성"""
        return str(uuid.uuid4())

    def _create_password_reset_token(self) -> str:
        """비밀번호 재설정 토큰 생성"""
        return str(uuid.uuid4())

    def _to_user_response(self, user: User) -> UserResponse:
        """User 엔티티를 UserResponse로 변환"""
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            nickname=user.nickname,
            phone=user.phone,
            avatar_url=user.avatar_url,
            bio=user.bio,
            auth_provider=user.auth_provider,
            auth_provider_id=user.auth_provider_id,
            email_verified=user.email_verified,
            user_role=user.user_role,
            user_status=user.user_status,
            is_active=user.is_active,
            last_login_at=user.last_login_at,
            last_login_ip=user.last_login_ip,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def create_user(self, command: CreateUserCommand) -> UserRegistrationResponse:
        """사용자 생성"""
        # 이메일 중복 확인
        if self.user_repository.exists_by_email(command.email):
            raise ValueError("이미 존재하는 이메일입니다.")

        # 사용자명 중복 확인
        if self.user_repository.exists_by_username(command.username):
            raise ValueError("이미 존재하는 사용자명입니다.")

        # 비밀번호 해싱
        password_hash = None
        if command.password:
            password_hash = self._hash_password(command.password)

        # 이메일 인증 토큰 생성
        email_verification_token = None
        email_verification_expires = None
        if command.auth_provider == AuthProvider.EMAIL:
            email_verification_token = self._create_email_verification_token()
            email_verification_expires = datetime.utcnow() + timedelta(hours=24)

        # 사용자 생성
        user = User.create(
            id=str(uuid.uuid4()),
            email=command.email,
            username=command.username,
            password_hash=password_hash,
            first_name=command.first_name,
            last_name=command.last_name,
            nickname=command.nickname,
            phone=command.phone,
            avatar_url=command.avatar_url,
            bio=command.bio,
            auth_provider=command.auth_provider,
            auth_provider_id=command.auth_provider_id,
            user_role=command.user_role,
            user_status=command.user_status,
        )

        if email_verification_token:
            user.set_email_verification_token(email_verification_token, email_verification_expires)

        saved_user = self.user_repository.save(user)

        return UserRegistrationResponse(
            user_id=saved_user.id,
            email=saved_user.email,
            username=saved_user.username,
        )

    def update_user(self, command: UpdateUserCommand) -> UserUpdateResponse:
        """사용자 정보 업데이트"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        # 이메일 중복 확인 (다른 사용자가 사용 중인지)
        if command.email and command.email != user.email:
            if self.user_repository.exists_by_email(command.email):
                raise ValueError("이미 존재하는 이메일입니다.")

        # 사용자명 중복 확인 (다른 사용자가 사용 중인지)
        if command.username and command.username != user.username:
            if self.user_repository.exists_by_username(command.username):
                raise ValueError("이미 존재하는 사용자명입니다.")

        user.update(
            email=command.email,
            username=command.username,
            first_name=command.first_name,
            last_name=command.last_name,
            nickname=command.nickname,
            phone=command.phone,
            avatar_url=command.avatar_url,
            bio=command.bio,
            user_role=command.user_role,
            user_status=command.user_status,
            is_active=command.is_active,
        )

        updated_user = self.user_repository.save(user)
        return UserUpdateResponse(user=self._to_user_response(updated_user))

    def change_password(self, command: ChangePasswordCommand) -> PasswordChangeResponse:
        """비밀번호 변경"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        if not user.password_hash:
            raise ValueError("OAuth 사용자는 비밀번호를 변경할 수 없습니다.")

        if not self._verify_password(command.current_password, user.password_hash):
            raise ValueError("현재 비밀번호가 올바르지 않습니다.")

        new_password_hash = self._hash_password(command.new_password)
        user.update_password(new_password_hash)
        self.user_repository.save(user)

        return PasswordChangeResponse(success=True, message="비밀번호가 변경되었습니다.")

    def reset_password(self, command: ResetPasswordCommand) -> PasswordResetResponse:
        """비밀번호 재설정 요청"""
        user = self.user_repository.find_by_email(command.email)
        if not user:
            # 보안상 사용자가 존재하지 않아도 성공 응답
            return PasswordResetResponse(email=command.email)

        if user.auth_provider != AuthProvider.EMAIL:
            raise ValueError("OAuth 사용자는 비밀번호 재설정을 사용할 수 없습니다.")

        # 비밀번호 재설정 토큰 생성 및 저장
        reset_token = self._create_password_reset_token()
        # TODO: 토큰을 데이터베이스에 저장하고 만료 시간 설정
        # TODO: 이메일 발송 로직 구현

        return PasswordResetResponse(email=command.email)

    def confirm_password_reset(self, command: ConfirmPasswordResetCommand) -> PasswordResetConfirmResponse:
        """비밀번호 재설정 확인"""
        # TODO: 토큰 검증 및 비밀번호 업데이트 로직 구현
        return PasswordResetConfirmResponse(success=True, message="비밀번호가 재설정되었습니다.")

    def verify_email(self, command: VerifyEmailCommand) -> EmailVerificationResponse:
        """이메일 인증"""
        user = self.user_repository.find_by_email_verification_token(command.token)
        if not user:
            return EmailVerificationResponse(verified=False, message="유효하지 않은 토큰입니다.")

        if user.email_verification_expires and user.email_verification_expires < datetime.utcnow():
            return EmailVerificationResponse(verified=False, message="만료된 토큰입니다.")

        user.verify_email()
        self.user_repository.save(user)

        return EmailVerificationResponse(verified=True, message="이메일 인증이 완료되었습니다.")

    def send_email_verification(self, command: SendEmailVerificationCommand) -> EmailVerificationSentResponse:
        """이메일 인증 메일 발송"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        if user.email_verified:
            raise ValueError("이미 인증된 이메일입니다.")

        # 새로운 인증 토큰 생성
        token = self._create_email_verification_token()
        expires = datetime.utcnow() + timedelta(hours=24)
        user.set_email_verification_token(token, expires)
        self.user_repository.save(user)

        # TODO: 이메일 발송 로직 구현

        return EmailVerificationSentResponse(user_id=user.id)

    def login(self, command: LoginCommand) -> UserLoginResponse:
        """이메일 로그인"""
        user = self.user_repository.find_by_email(command.email)
        if not user:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        if not user.password_hash:
            raise ValueError("OAuth 계정입니다. 소셜 로그인을 사용해주세요.")

        if not self._verify_password(command.password, user.password_hash):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        if not user.is_active:
            raise ValueError("비활성화된 계정입니다.")

        # 마지막 로그인 정보 업데이트
        user.update_last_login(command.ip_address)
        self.user_repository.save(user)

        # JWT 토큰 생성
        access_token = self._create_access_token({"sub": user.id})
        refresh_token = self._create_refresh_token({"sub": user.id})

        auth_response = UserAuthResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            user_role=user.user_role,
            user_status=user.user_status,
            is_active=user.is_active,
            email_verified=user.email_verified,
            auth_provider=user.auth_provider,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return UserLoginResponse(user=auth_response)

    def oauth_login(self, command: OAuthLoginCommand) -> OAuthLoginResponse:
        """OAuth 로그인"""
        # 기존 사용자 확인
        user = self.user_repository.find_by_auth_provider_id(command.provider, command.provider_id)
        is_new_user = False

        if not user:
            # 새 사용자 생성
            is_new_user = True
            user = User.create(
                id=str(uuid.uuid4()),
                email=command.email,
                username=command.username,
                first_name=command.first_name,
                last_name=command.last_name,
                avatar_url=command.avatar_url,
                auth_provider=command.provider,
                auth_provider_id=command.provider_id,
                user_role=UserRole.USER,
                user_status=UserStatus.ACTIVE,
                email_verified=True,  # OAuth는 이미 인증된 것으로 간주
            )

        # 마지막 로그인 정보 업데이트
        user.update_last_login(command.ip_address)
        saved_user = self.user_repository.save(user)

        # JWT 토큰 생성
        access_token = self._create_access_token({"sub": saved_user.id})
        refresh_token = self._create_refresh_token({"sub": saved_user.id})

        auth_response = UserAuthResponse(
            id=saved_user.id,
            email=saved_user.email,
            username=saved_user.username,
            user_role=saved_user.user_role,
            user_status=saved_user.user_status,
            is_active=saved_user.is_active,
            email_verified=saved_user.email_verified,
            auth_provider=saved_user.auth_provider,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        message = "새 계정이 생성되었습니다." if is_new_user else "로그인 성공"
        return OAuthLoginResponse(user=auth_response, is_new_user=is_new_user, message=message)

    def logout(self, command: LogoutCommand) -> UserLogoutResponse:
        """로그아웃"""
        # TODO: 토큰 블랙리스트 처리 로직 구현
        return UserLogoutResponse()

    def activate_user(self, command: ActivateUserCommand) -> UserActivationResponse:
        """사용자 활성화"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user.activate()
        self.user_repository.save(user)

        return UserActivationResponse(user_id=user.id)

    def deactivate_user(self, command: DeactivateUserCommand) -> UserDeactivationResponse:
        """사용자 비활성화"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user.deactivate()
        self.user_repository.save(user)

        return UserDeactivationResponse(user_id=user.id)

    def suspend_user(self, command: SuspendUserCommand) -> UserSuspensionResponse:
        """사용자 정지"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user.suspend()
        self.user_repository.save(user)

        return UserSuspensionResponse(user_id=user.id, reason=command.reason)

    def delete_user(self, command: DeleteUserCommand) -> UserDeleteResponse:
        """사용자 삭제"""
        if command.hard_delete:
            # 하드 삭제
            success = self.user_repository.delete(command.user_id)
            if not success:
                raise ValueError("사용자를 찾을 수 없습니다.")
        else:
            # 소프트 삭제
            user = self.user_repository.find_by_id(command.user_id)
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다.")
            user.delete()
            self.user_repository.save(user)

        return UserDeleteResponse(user_id=command.user_id)

    def promote_to_admin(self, command: PromoteToAdminCommand) -> UserPromotionResponse:
        """관리자로 승격"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user.promote_to_admin()
        self.user_repository.save(user)

        return UserPromotionResponse(user_id=user.id, new_role=user.user_role)

    def demote_to_user(self, command: DemoteToUserCommand) -> UserDemotionResponse:
        """일반 사용자로 강등"""
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user.demote_to_user()
        self.user_repository.save(user)

        return UserDemotionResponse(user_id=user.id, new_role=user.user_role)

    def check_email_exists(self, command: CheckEmailExistsCommand) -> UserExistsResponse:
        """이메일 존재 여부 확인"""
        exists = self.user_repository.exists_by_email(command.email)
        return UserExistsResponse(exists=exists)

    def check_username_exists(self, command: CheckUsernameExistsCommand) -> UserExistsResponse:
        """사용자명 존재 여부 확인"""
        exists = self.user_repository.exists_by_username(command.username)
        return UserExistsResponse(exists=exists)

    def find_user_by_id(self, command: FindUserByIdCommand) -> Optional[UserResponse]:
        """ID로 사용자 조회"""
        user = self.user_repository.find_by_id(command.user_id)
        return self._to_user_response(user) if user else None

    def find_user_by_email(self, command: FindUserByEmailCommand) -> Optional[UserResponse]:
        """이메일로 사용자 조회"""
        user = self.user_repository.find_by_email(command.email)
        return self._to_user_response(user) if user else None

    def find_user_by_username(self, command: FindUserByUsernameCommand) -> Optional[UserResponse]:
        """사용자명으로 사용자 조회"""
        user = self.user_repository.find_by_username(command.username)
        return self._to_user_response(user) if user else None

    def find_user_by_oauth(self, command: FindUserByOAuthCommand) -> Optional[UserResponse]:
        """OAuth 제공자 ID로 사용자 조회"""
        user = self.user_repository.find_by_auth_provider_id(command.provider, command.provider_id)
        return self._to_user_response(user) if user else None

    def list_users(self, command: ListUsersCommand) -> UserListResponse:
        """사용자 목록 조회"""
        users = self.user_repository.search_users(
            search_term=command.search_term,
            role=command.role,
            status=command.status,
            auth_provider=command.auth_provider,
            email_verified=command.email_verified,
            is_active=command.is_active,
            skip=command.skip,
            limit=command.limit,
        )

        user_responses = [self._to_user_response(user) for user in users]
        # TODO: 전체 개수 조회 로직 구현
        total_count = len(user_responses)  # 임시

        return UserListResponse(
            users=user_responses,
            total_count=total_count,
            skip=command.skip,
            limit=command.limit,
        )

    def list_admins(self, command: ListAdminsCommand) -> UserListResponse:
        """관리자 목록 조회"""
        users = self.user_repository.find_admins()
        user_responses = [self._to_user_response(user) for user in users]

        return UserListResponse(
            users=user_responses,
            total_count=len(user_responses),
            skip=command.skip,
            limit=command.limit,
        )

    def list_active_users(self, command: ListActiveUsersCommand) -> UserListResponse:
        """활성 사용자 목록 조회"""
        users = self.user_repository.find_active_users()
        user_responses = [self._to_user_response(user) for user in users]

        return UserListResponse(
            users=user_responses,
            total_count=len(user_responses),
            skip=command.skip,
            limit=command.limit,
        )

    def list_verified_users(self, command: ListVerifiedUsersCommand) -> UserListResponse:
        """이메일 인증 완료된 사용자 목록 조회"""
        users = self.user_repository.find_verified_users()
        user_responses = [self._to_user_response(user) for user in users]

        return UserListResponse(
            users=user_responses,
            total_count=len(user_responses),
            skip=command.skip,
            limit=command.limit,
        )

    def get_user_statistics(self, command: GetUserStatisticsCommand) -> UserStatisticsResponse:
        """사용자 통계 조회"""
        total_users = self.user_repository.find_all()
        active_users = self.user_repository.find_by_status(UserStatus.ACTIVE)
        pending_users = self.user_repository.find_by_status(UserStatus.PENDING)
        suspended_users = self.user_repository.find_by_status(UserStatus.SUSPENDED)
        deleted_users = self.user_repository.find_by_status(UserStatus.DELETED)
        admin_users = self.user_repository.find_by_role(UserRole.ADMIN)

        verified_users = [user for user in total_users if user.email_verified]
        unverified_users = [user for user in total_users if not user.email_verified]

        return UserStatisticsResponse(
            total_users=len(total_users),
            active_users=len(active_users),
            pending_users=len(pending_users),
            suspended_users=len(suspended_users),
            deleted_users=len(deleted_users),
            admin_users=len(admin_users),
            verified_users=len(verified_users),
            unverified_users=len(unverified_users),
        )

    # 관리자 전용 메서드들
    async def create_user_by_admin(
        self,
        email: str,
        username: str,
        password: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        user_role: UserRole = UserRole.USER,
        user_status: UserStatus = UserStatus.ACTIVE,
        email_verified: bool = True,
    ) -> User:
        """관리자가 사용자 생성 (이메일 인증 없이)"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)

            # 이메일 중복 확인
            if repo.exists_by_email(email):
                raise ValueError("이미 존재하는 이메일입니다.")

            # 사용자명 중복 확인
            if repo.exists_by_username(username):
                raise ValueError("이미 존재하는 사용자명입니다.")

            # 비밀번호 해싱
            password_hash = None
            if password:
                password_hash = self._hash_password(password)

            # 사용자 생성 (관리자는 이메일 인증 없이도 생성 가능)
            user = User.create(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                nickname=nickname,
                phone=phone,
                auth_provider=AuthProvider.EMAIL,
                user_role=user_role,
                user_status=user_status,
            )

            # 이메일 인증 상태 설정
            if email_verified:
                user.verify_email()

            return repo.save(user)

    async def update_user_by_admin(
        self,
        user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        user_role: Optional[UserRole] = None,
        user_status: Optional[UserStatus] = None,
        email_verified: Optional[bool] = None,
    ) -> Optional[User]:
        """관리자가 사용자 정보 수정"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)

            user = repo.find_by_id(user_id)
            if not user:
                return None

            # 이메일 중복 확인 (다른 사용자가 사용 중인지)
            if email and email != user.email and repo.exists_by_email(email):
                raise ValueError("이미 존재하는 이메일입니다.")

            # 사용자명 중복 확인 (다른 사용자가 사용 중인지)
            if username and username != user.username and repo.exists_by_username(username):
                raise ValueError("이미 존재하는 사용자명입니다.")

            # 정보 업데이트
            user.update(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                nickname=nickname,
                phone=phone,
                user_role=user_role,
                user_status=user_status,
            )

            # 이메일 인증 상태 설정
            if email_verified is not None:
                if email_verified and not user.email_verified:
                    user.verify_email()
                elif not email_verified and user.email_verified:
                    user.email_verified = False

            return repo.save(user)

    async def delete_user_by_admin(self, user_id: str) -> bool:
        """관리자가 사용자 삭제"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)

            user = repo.find_by_id(user_id)
            if not user:
                return False

            user.delete()
            repo.save(user)
            return True

    async def activate_user_by_admin(self, user_id: str) -> Optional[User]:
        """관리자가 사용자 활성화"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)

            user = repo.find_by_id(user_id)
            if not user:
                return None

            user.activate()
            return repo.save(user)

    async def suspend_user_by_admin(self, user_id: str) -> Optional[User]:
        """관리자가 사용자 정지"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)

            user = repo.find_by_id(user_id)
            if not user:
                return None

            user.suspend()
            return repo.save(user)

    async def promote_to_admin(self, user_id: str) -> Optional[User]:
        """관리자가 사용자를 관리자로 승격"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)

            user = repo.find_by_id(user_id)
            if not user:
                return None

            user.promote_to_admin()
            return repo.save(user)

    async def demote_to_user(self, user_id: str) -> Optional[User]:
        """관리자가 관리자를 일반 사용자로 강등"""
        from src.infrastructure.database import get_db_session
        from src.modules.user.infrastructure.repository.repository import SQLAlchemyUserRepository

        with get_db_session() as session:
            repo = SQLAlchemyUserRepository(session)

            user = repo.find_by_id(user_id)
            if not user:
                return None

            user.demote_to_user()
            return repo.save(user)
