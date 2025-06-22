from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from src.modules.project.core.entity import Project
from src.modules.project.core.value import ProjectStatus


class ProjectRepository(ABC):
    """프로젝트 Repository 인터페이스"""

    @abstractmethod
    def save(self, project: Project) -> Project:
        """프로젝트 저장"""
        pass

    @abstractmethod
    def find_by_id(self, project_id: str) -> Optional[Project]:
        """ID로 프로젝트 조회"""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Project]:
        """이름으로 프로젝트 조회"""
        pass

    @abstractmethod
    def find_by_owner_id(self, owner_id: str) -> List[Project]:
        """소유자 ID로 프로젝트 목록 조회"""
        pass

    @abstractmethod
    def find_by_team_id(self, team_id: str) -> List[Project]:
        """팀 ID로 프로젝트 목록 조회"""
        pass

    @abstractmethod
    def find_by_client_id(self, client_id: str) -> List[Project]:
        """클라이언트 ID로 프로젝트 목록 조회"""
        pass

    @abstractmethod
    def find_by_workspace_id(self, workspace_id: str) -> List[Project]:
        """워크스페이스 ID로 프로젝트 목록 조회"""
        pass

    @abstractmethod
    def find_by_status(self, status: ProjectStatus) -> List[Project]:
        """상태로 프로젝트 목록 조회"""
        pass

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """모든 프로젝트 조회 (페이징)"""
        pass

    @abstractmethod
    def delete(self, project_id: str) -> bool:
        """프로젝트 삭제"""
        pass

    @abstractmethod
    def exists_by_id(self, project_id: str) -> bool:
        """프로젝트 존재 여부 확인"""
        pass

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """이름으로 프로젝트 존재 여부 확인"""
        pass


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy 기반 프로젝트 Repository 구현체"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, project: Project) -> Project:
        """프로젝트 저장"""
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def find_by_id(self, project_id: str) -> Optional[Project]:
        """ID로 프로젝트 조회"""
        stmt = select(Project).where(Project.id == project_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_name(self, name: str) -> Optional[Project]:
        """이름으로 프로젝트 조회"""
        stmt = select(Project).where(Project.name == name)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_owner_id(self, owner_id: str) -> List[Project]:
        """소유자 ID로 프로젝트 목록 조회"""
        stmt = select(Project).where(Project.owner_id == owner_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_team_id(self, team_id: str) -> List[Project]:
        """팀 ID로 프로젝트 목록 조회"""
        stmt = select(Project).where(Project.team_id == team_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_client_id(self, client_id: str) -> List[Project]:
        """클라이언트 ID로 프로젝트 목록 조회"""
        stmt = select(Project).where(Project.client_id == client_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_workspace_id(self, workspace_id: str) -> List[Project]:
        """워크스페이스 ID로 프로젝트 목록 조회"""
        stmt = select(Project).where(Project.workspace_id == workspace_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_status(self, status: ProjectStatus) -> List[Project]:
        """상태로 프로젝트 목록 조회"""
        stmt = select(Project).where(Project.project_status == status)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """모든 프로젝트 조회 (페이징)"""
        stmt = select(Project).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def delete(self, project_id: str) -> bool:
        """프로젝트 삭제"""
        project = self.find_by_id(project_id)
        if project:
            self.session.delete(project)
            self.session.commit()
            return True
        return False

    def exists_by_id(self, project_id: str) -> bool:
        """프로젝트 존재 여부 확인"""
        stmt = select(Project.id).where(Project.id == project_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def exists_by_name(self, name: str) -> bool:
        """이름으로 프로젝트 존재 여부 확인"""
        stmt = select(Project.id).where(Project.name == name)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def search_projects(
        self,
        search_term: Optional[str] = None,
        status: Optional[ProjectStatus] = None,
        owner_id: Optional[str] = None,
        team_id: Optional[str] = None,
        client_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        priority: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Project]:
        """고급 검색 기능"""
        conditions = []

        if search_term:
            conditions.append(
                or_(
                    Project.name.ilike(f"%{search_term}%"),
                    Project.description.ilike(f"%{search_term}%"),
                )
            )

        if status:
            conditions.append(Project.project_status == status)

        if owner_id:
            conditions.append(Project.owner_id == owner_id)

        if team_id:
            conditions.append(Project.team_id == team_id)

        if client_id:
            conditions.append(Project.client_id == client_id)

        if workspace_id:
            conditions.append(Project.workspace_id == workspace_id)

        if priority:
            conditions.append(Project.priority == priority)

        if start_date:
            conditions.append(Project.start_date >= start_date)

        if end_date:
            conditions.append(Project.end_date <= end_date)

        stmt = select(Project)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())
