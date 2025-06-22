from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from modules.workspace.core.entity import Workspace
from modules.workspace.core.repository import WorkspaceRepository
from modules.workspace.core.value import WorkspaceStatus


class SQLAlchemyWorkspaceRepository(WorkspaceRepository):
    """SQLAlchemy 기반 워크스페이스 Repository 구현체"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, workspace: Workspace) -> Workspace:
        """워크스페이스 저장"""
        self.session.add(workspace)
        self.session.commit()
        self.session.refresh(workspace)
        return workspace

    def find_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """ID로 워크스페이스 조회"""
        stmt = select(Workspace).where(Workspace.id == workspace_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_name(self, name: str) -> Optional[Workspace]:
        """이름으로 워크스페이스 조회"""
        stmt = select(Workspace).where(Workspace.name == name)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_owner_id(self, owner_id: str) -> List[Workspace]:
        """소유자 ID로 워크스페이스 목록 조회"""
        stmt = select(Workspace).where(Workspace.owner_id == owner_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_team_id(self, team_id: str) -> List[Workspace]:
        """팀 ID로 워크스페이스 목록 조회"""
        stmt = select(Workspace).where(Workspace.team_id == team_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_client_id(self, client_id: str) -> List[Workspace]:
        """클라이언트 ID로 워크스페이스 목록 조회"""
        stmt = select(Workspace).where(Workspace.client_id == client_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_by_status(self, status: WorkspaceStatus) -> List[Workspace]:
        """상태로 워크스페이스 목록 조회"""
        stmt = select(Workspace).where(Workspace.workspace_status == status)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Workspace]:
        """모든 워크스페이스 조회 (페이징)"""
        stmt = select(Workspace).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def delete(self, workspace_id: str) -> bool:
        """워크스페이스 삭제"""
        workspace = self.find_by_id(workspace_id)
        if workspace:
            self.session.delete(workspace)
            self.session.commit()
            return True
        return False

    def exists_by_id(self, workspace_id: str) -> bool:
        """워크스페이스 존재 여부 확인"""
        stmt = select(Workspace.id).where(Workspace.id == workspace_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def exists_by_name(self, name: str) -> bool:
        """이름으로 워크스페이스 존재 여부 확인"""
        stmt = select(Workspace.id).where(Workspace.name == name)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def search_workspaces(
        self,
        search_term: Optional[str] = None,
        status: Optional[WorkspaceStatus] = None,
        owner_id: Optional[str] = None,
        team_id: Optional[str] = None,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Workspace]:
        """고급 검색 기능"""
        conditions = []

        if search_term:
            conditions.append(
                or_(
                    Workspace.name.ilike(f"%{search_term}%"),
                    Workspace.description.ilike(f"%{search_term}%"),
                )
            )

        if status:
            conditions.append(Workspace.workspace_status == status)

        if owner_id:
            conditions.append(Workspace.owner_id == owner_id)

        if team_id:
            conditions.append(Workspace.team_id == team_id)

        if client_id:
            conditions.append(Workspace.client_id == client_id)

        if start_date:
            conditions.append(Workspace.start_date >= start_date)

        if end_date:
            conditions.append(Workspace.end_date <= end_date)

        stmt = select(Workspace)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())
