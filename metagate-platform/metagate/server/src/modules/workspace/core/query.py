from datetime import datetime
from typing import List, Optional

from src.infrastructure.database import get_db_session
from src.modules.workspace.core.entity import Workspace
from src.modules.workspace.core.repository import SQLAlchemyWorkspaceRepository
from src.modules.workspace.core.value import WorkspaceStatus


class WorkspaceQuery:
    """워크스페이스 조회 Query"""

    def __init__(self):
        pass

    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """ID로 워크스페이스 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.find_by_id(workspace_id)

    async def get_by_name(self, name: str) -> Optional[Workspace]:
        """이름으로 워크스페이스 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.find_by_name(name)

    async def get_by_owner_id(
        self, owner_id: str, skip: int = 0, limit: int = 100
    ) -> List[Workspace]:
        """소유자 ID로 워크스페이스 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.find_by_owner_id(owner_id)[skip : skip + limit]

    async def get_by_team_id(
        self, team_id: str, skip: int = 0, limit: int = 100
    ) -> List[Workspace]:
        """팀 ID로 워크스페이스 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.find_by_team_id(team_id)[skip : skip + limit]

    async def get_by_client_id(
        self, client_id: str, skip: int = 0, limit: int = 100
    ) -> List[Workspace]:
        """클라이언트 ID로 워크스페이스 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.find_by_client_id(client_id)[skip : skip + limit]

    async def get_by_status(
        self, status: WorkspaceStatus, skip: int = 0, limit: int = 100
    ) -> List[Workspace]:
        """상태로 워크스페이스 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.find_by_status(status)[skip : skip + limit]

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Workspace]:
        """모든 워크스페이스 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.find_all(skip=skip, limit=limit)

    async def search(
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
        """고급 검색"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.search_workspaces(
                search_term=search_term,
                status=status,
                owner_id=owner_id,
                team_id=team_id,
                client_id=client_id,
                start_date=start_date,
                end_date=end_date,
                skip=skip,
                limit=limit,
            )

    async def exists_by_id(self, workspace_id: str) -> bool:
        """워크스페이스 존재 여부 확인"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.exists_by_id(workspace_id)

    async def exists_by_name(self, name: str) -> bool:
        """이름으로 워크스페이스 존재 여부 확인"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            return repo.exists_by_name(name)


class WorkspaceStatisticsQuery:
    """워크스페이스 통계 Query"""

    def __init__(self):
        self.query = WorkspaceQuery()

    async def get_status_count(self) -> dict:
        """상태별 워크스페이스 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)

            stats = {}
            for status in WorkspaceStatus:
                workspaces = repo.find_by_status(status)
                stats[status.value] = len(workspaces)

            return stats

    async def get_owner_workspace_count(self, owner_id: str) -> int:
        """소유자별 워크스페이스 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            workspaces = repo.find_by_owner_id(owner_id)
            return len(workspaces)

    async def get_team_workspace_count(self, team_id: str) -> int:
        """팀별 워크스페이스 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            workspaces = repo.find_by_team_id(team_id)
            return len(workspaces)

    async def get_client_workspace_count(self, client_id: str) -> int:
        """클라이언트별 워크스페이스 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            workspaces = repo.find_by_client_id(client_id)
            return len(workspaces)

    async def get_total_count(self) -> int:
        """전체 워크스페이스 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)
            workspaces = repo.find_all(limit=10000)  # 큰 수로 설정하여 전체 조회
            return len(workspaces)


# 편의를 위한 팩토리 함수들
async def get_workspace_by_id(workspace_id: str) -> Optional[Workspace]:
    """ID로 워크스페이스 조회 편의 함수"""
    query = WorkspaceQuery()
    return await query.get_by_id(workspace_id)


async def get_workspaces_by_owner(
    owner_id: str, skip: int = 0, limit: int = 100
) -> List[Workspace]:
    """소유자별 워크스페이스 조회 편의 함수"""
    query = WorkspaceQuery()
    return await query.get_by_owner_id(owner_id, skip=skip, limit=limit)


async def get_workspaces_by_status(
    status: WorkspaceStatus, skip: int = 0, limit: int = 100
) -> List[Workspace]:
    """상태별 워크스페이스 조회 편의 함수"""
    query = WorkspaceQuery()
    return await query.get_by_status(status, skip=skip, limit=limit)


async def search_workspaces(
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
    """워크스페이스 검색 편의 함수"""
    query = WorkspaceQuery()
    return await query.search(
        search_term=search_term,
        status=status,
        owner_id=owner_id,
        team_id=team_id,
        client_id=client_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


async def get_workspace_statistics() -> dict:
    """워크스페이스 통계 조회 편의 함수"""
    stats_query = WorkspaceStatisticsQuery()
    return await stats_query.get_status_count()
