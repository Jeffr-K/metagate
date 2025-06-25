from abc import ABC, abstractmethod
from typing import Optional, List

from sqlmodel import select

from src.modules.user.core.entity import User


class SQLModelUserRepository:
    def __init__(self, database_engine=None):
        if database_engine is None:
            from src.infrastructure.database.postgres.config import get_database_engine
            database_engine = get_database_engine()
        self.database_engine = database_engine

    async def save(self, user: User) -> User:
        """사용자 저장"""
        with self.database_engine.get_db_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        with self.database_engine.get_db_session() as session:
            statement = select(User).where(User.id == user_id)
            result = session.exec(statement)
            return result.first()

    def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        with self.database_engine.get_db_session() as session:
            statement = select(User).where(User.email == email)
            result = session.exec(statement)
            return result.first()

    def find_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        with self.database_engine.get_db_session() as session:
            statement = select(User).where(User.username == username)
            result = session.exec(statement)
            return result.first()

    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회 (페이징)"""
        with self.database_engine.get_db_session() as session:
            statement = select(User).offset(skip).limit(limit)
            result = session.exec(statement)
            return result.all()

    async def delete(self, user_id: int) -> bool:
        with self.database_engine.get_db_session() as session:
            user = self.find_by_id(user_id)
            if user:
                session.delete(user)
                session.commit()
                return True
            return False

    async def update(self, user_id: int) -> bool:
        with self.database_engine.get_db_session() as session:
            user = self.find_by_id(user_id)
            if user:
                session.add(user)
                session.commit()
                session.refresh(user)
                return True
            return False

    def exists_by_email(self, email: str) -> bool:
        """이메일로 사용자 존재 여부 확인"""
        with self.database_engine.get_db_session() as session:
            statement = select(User.id).where(User.email == email)
            result = session.exec(statement)
            return result.first() is not None

    def exists_by_username(self, username: str) -> bool:
        """사용자명으로 사용자 존재 여부 확인"""
        with self.database_engine.get_db_session() as session:
            statement = select(User.id).where(User.username == username)
            result = session.exec(statement)
            return result.first() is not None

    def update(self, user: User) -> User:
        """사용자 정보 업데이트"""
        with self.database_engine.get_db_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def count(self) -> int:
        """전체 사용자 수 조회"""
        with self.database_engine.get_db_session() as session:
            statement = select(User)
            result = session.exec(statement)
            return len(result.all())