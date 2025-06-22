import uuid
from datetime import datetime
from typing import Optional

from src.infrastructure.database import get_db_session
from src.modules.project.core.entity import Project
from src.modules.project.core.repository import SQLAlchemyProjectRepository
from src.modules.project.core.value import ProjectStatus


class ProjectCreateCommand:
    """프로젝트 생성 Command"""

    def __init__(
        self,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        project_status: ProjectStatus,
        owner_id: str,
        team_id: str,
        client_id: str,
        workspace_id: Optional[str] = None,
        budget: Optional[float] = None,
        priority: Optional[str] = None,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.project_status = project_status
        self.owner_id = owner_id
        self.team_id = team_id
        self.client_id = client_id
        self.workspace_id = workspace_id
        self.budget = budget
        self.priority = priority

    async def execute(self) -> Project:
        """프로젝트 생성 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)

            # 중복 이름 체크
            if repo.exists_by_name(self.name):
                raise ValueError(f"프로젝트 이름 '{self.name}'이 이미 존재합니다.")

            # 프로젝트 생성
            project = Project.create(
                id=self.id,
                name=self.name,
                description=self.description,
                start_date=self.start_date,
                end_date=self.end_date,
                project_status=self.project_status,
                owner_id=self.owner_id,
                team_id=self.team_id,
                client_id=self.client_id,
                workspace_id=self.workspace_id,
                budget=self.budget,
                priority=self.priority,
            )

            # 저장
            return repo.save(project)


class ProjectUpdateCommand:
    """프로젝트 수정 Command"""

    def __init__(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        project_status: Optional[ProjectStatus] = None,
        owner_id: Optional[str] = None,
        team_id: Optional[str] = None,
        client_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        budget: Optional[float] = None,
        priority: Optional[str] = None,
    ):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.project_status = project_status
        self.owner_id = owner_id
        self.team_id = team_id
        self.client_id = client_id
        self.workspace_id = workspace_id
        self.budget = budget
        self.priority = priority

    async def execute(self) -> Optional[Project]:
        """프로젝트 수정 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)

            # 프로젝트 조회
            project = repo.find_by_id(self.project_id)
            if not project:
                raise ValueError(f"프로젝트 ID '{self.project_id}'를 찾을 수 없습니다.")

            # 이름 변경 시 중복 체크
            if self.name and self.name != project.name:
                if repo.exists_by_name(self.name):
                    raise ValueError(f"프로젝트 이름 '{self.name}'이 이미 존재합니다.")

            # 업데이트
            project.update(
                name=self.name,
                description=self.description,
                start_date=self.start_date,
                end_date=self.end_date,
                project_status=self.project_status,
                owner_id=self.owner_id,
                team_id=self.team_id,
                client_id=self.client_id,
                workspace_id=self.workspace_id,
                budget=self.budget,
                priority=self.priority,
            )

            # 저장
            return repo.save(project)


class ProjectDeleteCommand:
    """프로젝트 삭제 Command"""

    def __init__(self, project_id: str):
        self.project_id = project_id

    async def execute(self) -> bool:
        """프로젝트 삭제 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)

            # 프로젝트 존재 확인
            if not repo.exists_by_id(self.project_id):
                raise ValueError(f"프로젝트 ID '{self.project_id}'를 찾을 수 없습니다.")

            # 삭제
            return repo.delete(self.project_id)


class ProjectStatusChangeCommand:
    """프로젝트 상태 변경 Command"""

    def __init__(self, project_id: str, new_status: ProjectStatus):
        self.project_id = project_id
        self.new_status = new_status

    async def execute(self) -> Optional[Project]:
        """프로젝트 상태 변경 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyProjectRepository(session)

            # 프로젝트 조회
            project = repo.find_by_id(self.project_id)
            if not project:
                raise ValueError(f"프로젝트 ID '{self.project_id}'를 찾을 수 없습니다.")

            # 상태 변경
            if self.new_status == ProjectStatus.ACTIVE:
                project.activate()
            elif self.new_status == ProjectStatus.INACTIVE:
                project.deactivate()
            elif self.new_status == ProjectStatus.COMPLETED:
                project.complete()
            elif self.new_status == ProjectStatus.CANCELLED:
                project.cancel()
            elif self.new_status == ProjectStatus.ON_HOLD:
                project.put_on_hold()
            elif self.new_status == ProjectStatus.IN_PROGRESS:
                project.start_progress()
            elif self.new_status == ProjectStatus.PLANNING:
                project.start_planning()
            elif self.new_status == ProjectStatus.REVIEW:
                project.start_review()
            else:
                raise ValueError(f"지원하지 않는 상태입니다: {self.new_status}")

            # 저장
            return repo.save(project)


# 편의를 위한 팩토리 함수들
async def create_project(
    name: str,
    description: str,
    start_date: datetime,
    end_date: datetime,
    project_status: ProjectStatus = ProjectStatus.ACTIVE,
    owner_id: str = "",
    team_id: str = "",
    client_id: str = "",
    workspace_id: Optional[str] = None,
    budget: Optional[float] = None,
    priority: Optional[str] = None,
) -> Project:
    """프로젝트 생성 편의 함수"""
    command = ProjectCreateCommand(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        project_status=project_status,
        owner_id=owner_id,
        team_id=team_id,
        client_id=client_id,
        workspace_id=workspace_id,
        budget=budget,
        priority=priority,
    )
    return await command.execute()


async def update_project(
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    project_status: Optional[ProjectStatus] = None,
    owner_id: Optional[str] = None,
    team_id: Optional[str] = None,
    client_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    budget: Optional[float] = None,
    priority: Optional[str] = None,
) -> Optional[Project]:
    """프로젝트 수정 편의 함수"""
    command = ProjectUpdateCommand(
        project_id=project_id,
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        project_status=project_status,
        owner_id=owner_id,
        team_id=team_id,
        client_id=client_id,
        workspace_id=workspace_id,
        budget=budget,
        priority=priority,
    )
    return await command.execute()


async def delete_project(project_id: str) -> bool:
    """프로젝트 삭제 편의 함수"""
    command = ProjectDeleteCommand(project_id=project_id)
    return await command.execute()


async def change_project_status(project_id: str, new_status: ProjectStatus) -> Optional[Project]:
    """프로젝트 상태 변경 편의 함수"""
    command = ProjectStatusChangeCommand(project_id=project_id, new_status=new_status)
    return await command.execute()
