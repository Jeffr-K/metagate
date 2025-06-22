from datetime import datetime
from typing import List, Optional

from src.infrastructure.database import get_db_session
from src.modules.project.core.entity import Project
from src.modules.project.core.repository import SQLAlchemyProjectRepository
from src.modules.project.core.value import ProjectStatus


class ProjectQuery:
    """프로젝트 조회 Query"""

    def __init__(self):
        pass

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """ID로 프로젝트 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_by_id(project_id)

    async def get_by_name(self, name: str) -> Optional[Project]:
        """이름으로 프로젝트 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_by_name(name)

    async def get_by_owner_id(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """소유자 ID로 프로젝트 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_by_owner_id(owner_id)[skip : skip + limit]

    async def get_by_team_id(self, team_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """팀 ID로 프로젝트 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_by_team_id(team_id)[skip : skip + limit]

    async def get_by_client_id(self, client_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """클라이언트 ID로 프로젝트 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_by_client_id(client_id)[skip : skip + limit]

    async def get_by_workspace_id(self, workspace_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """워크스페이스 ID로 프로젝트 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_by_workspace_id(workspace_id)[skip : skip + limit]

    async def get_by_status(self, status: ProjectStatus, skip: int = 0, limit: int = 100) -> List[Project]:
        """상태로 프로젝트 목록 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_by_status(status)[skip : skip + limit]

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """모든 프로젝트 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.find_all(skip=skip, limit=limit)

    async def search(
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
        """고급 검색"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.search_projects(
                search_term=search_term,
                status=status,
                owner_id=owner_id,
                team_id=team_id,
                client_id=client_id,
                workspace_id=workspace_id,
                priority=priority,
                start_date=start_date,
                end_date=end_date,
                skip=skip,
                limit=limit,
            )

    async def exists_by_id(self, project_id: str) -> bool:
        """프로젝트 존재 여부 확인"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.exists_by_id(project_id)

    async def exists_by_name(self, name: str) -> bool:
        """이름으로 프로젝트 존재 여부 확인"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            return repo.exists_by_name(name)


class ProjectStatisticsQuery:
    """프로젝트 통계 Query"""

    def __init__(self):
        self.query = ProjectQuery()

    async def get_status_count(self) -> dict:
        """상태별 프로젝트 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)

            stats = {}
            for status in ProjectStatus:
                projects = repo.find_by_status(status)
                stats[status.value] = len(projects)

            return stats

    async def get_owner_project_count(self, owner_id: str) -> int:
        """소유자별 프로젝트 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            projects = repo.find_by_owner_id(owner_id)
            return len(projects)

    async def get_team_project_count(self, team_id: str) -> int:
        """팀별 프로젝트 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            projects = repo.find_by_team_id(team_id)
            return len(projects)

    async def get_client_project_count(self, client_id: str) -> int:
        """클라이언트별 프로젝트 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            projects = repo.find_by_client_id(client_id)
            return len(projects)

    async def get_workspace_project_count(self, workspace_id: str) -> int:
        """워크스페이스별 프로젝트 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            projects = repo.find_by_workspace_id(workspace_id)
            return len(projects)

    async def get_total_count(self) -> int:
        """전체 프로젝트 개수 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            projects = repo.find_all(limit=10000)  # 큰 수로 설정하여 전체 조회
            return len(projects)

    async def get_budget_statistics(self) -> dict:
        """예산 통계 조회"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)
            projects = repo.find_all(limit=10000)

            total_budget = sum(p.budget or 0 for p in projects)
            avg_budget = total_budget / len(projects) if projects else 0
            max_budget = max((p.budget or 0 for p in projects), default=0)
            min_budget = min((p.budget or 0 for p in projects), default=0)

            return {
                "total_budget": total_budget,
                "average_budget": avg_budget,
                "max_budget": max_budget,
                "min_budget": min_budget,
                "projects_with_budget": len([p for p in projects if p.budget]),
            }


# 편의를 위한 팩토리 함수들
async def get_project_by_id(project_id: str) -> Optional[Project]:
    """ID로 프로젝트 조회 편의 함수"""
    query = ProjectQuery()
    return await query.get_by_id(project_id)


async def get_projects_by_owner(owner_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
    """소유자별 프로젝트 조회 편의 함수"""
    query = ProjectQuery()
    return await query.get_by_owner_id(owner_id, skip=skip, limit=limit)


async def get_projects_by_status(status: ProjectStatus, skip: int = 0, limit: int = 100) -> List[Project]:
    """상태별 프로젝트 조회 편의 함수"""
    query = ProjectQuery()
    return await query.get_by_status(status, skip=skip, limit=limit)


async def get_projects_by_workspace(workspace_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
    """워크스페이스별 프로젝트 조회 편의 함수"""
    query = ProjectQuery()
    return await query.get_by_workspace_id(workspace_id, skip=skip, limit=limit)


async def search_projects(
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
    """프로젝트 검색 편의 함수"""
    query = ProjectQuery()
    return await query.search(
        search_term=search_term,
        status=status,
        owner_id=owner_id,
        team_id=team_id,
        client_id=client_id,
        workspace_id=workspace_id,
        priority=priority,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


async def get_project_statistics() -> dict:
    """프로젝트 통계 조회 편의 함수"""
    query = ProjectStatisticsQuery()
    return await query.get_status_count()
