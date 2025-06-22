import uuid
from datetime import datetime
from typing import Optional

from src.infrastructure.database import get_db_session
from src.modules.workspace.core.entity import Workspace
from src.modules.workspace.core.repository import SQLAlchemyWorkspaceRepository
from src.modules.workspace.core.value import WorkspaceStatus


class WorkspaceCreateCommand:
    """워크스페이스 생성 Command"""

    def __init__(
        self,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        workspace_status: WorkspaceStatus,
        owner_id: str,
        team_id: str,
        client_id: str,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.workspace_status = workspace_status
        self.owner_id = owner_id
        self.team_id = team_id
        self.client_id = client_id

    async def execute(self) -> Workspace:
        """워크스페이스 생성 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)

            # 중복 이름 체크
            if repo.exists_by_name(self.name):
                raise ValueError(f"워크스페이스 이름 '{self.name}'이 이미 존재합니다.")

            # 워크스페이스 생성
            workspace = Workspace.create(
                id=self.id,
                name=self.name,
                description=self.description,
                start_date=self.start_date,
                end_date=self.end_date,
                workspace_status=self.workspace_status,
                owner_id=self.owner_id,
                team_id=self.team_id,
                client_id=self.client_id,
            )

            # 저장
            return repo.save(workspace)


class WorkspaceUpdateCommand:
    """워크스페이스 수정 Command"""

    def __init__(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        workspace_status: Optional[WorkspaceStatus] = None,
        owner_id: Optional[str] = None,
        team_id: Optional[str] = None,
        client_id: Optional[str] = None,
    ):
        self.workspace_id = workspace_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.workspace_status = workspace_status
        self.owner_id = owner_id
        self.team_id = team_id
        self.client_id = client_id

    async def execute(self) -> Optional[Workspace]:
        """워크스페이스 수정 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)

            # 워크스페이스 조회
            workspace = repo.find_by_id(self.workspace_id)
            if not workspace:
                raise ValueError(
                    f"워크스페이스 ID '{self.workspace_id}'를 찾을 수 없습니다."
                )

            # 이름 변경 시 중복 체크
            if self.name and self.name != workspace.name:
                if repo.exists_by_name(self.name):
                    raise ValueError(
                        f"워크스페이스 이름 '{self.name}'이 이미 존재합니다."
                    )

            # 업데이트
            workspace.update(
                name=self.name,
                description=self.description,
                start_date=self.start_date,
                end_date=self.end_date,
                workspace_status=self.workspace_status,
                owner_id=self.owner_id,
                team_id=self.team_id,
                client_id=self.client_id,
            )

            # 저장
            return repo.save(workspace)


class WorkspaceDeleteCommand:
    """워크스페이스 삭제 Command"""

    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id

    async def execute(self) -> bool:
        """워크스페이스 삭제 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)

            # 워크스페이스 존재 확인
            if not repo.exists_by_id(self.workspace_id):
                raise ValueError(
                    f"워크스페이스 ID '{self.workspace_id}'를 찾을 수 없습니다."
                )

            # 삭제
            return repo.delete(self.workspace_id)


class WorkspaceStatusChangeCommand:
    """워크스페이스 상태 변경 Command"""

    def __init__(self, workspace_id: str, new_status: WorkspaceStatus):
        self.workspace_id = workspace_id
        self.new_status = new_status

    async def execute(self) -> Optional[Workspace]:
        """워크스페이스 상태 변경 실행"""
        with get_db_session() as session:
            repo = SQLAlchemyWorkspaceRepository(session)

            # 워크스페이스 조회
            workspace = repo.find_by_id(self.workspace_id)
            if not workspace:
                raise ValueError(
                    f"워크스페이스 ID '{self.workspace_id}'를 찾을 수 없습니다."
                )

            # 상태 변경
            if self.new_status == WorkspaceStatus.ACTIVE:
                workspace.activate()
            elif self.new_status == WorkspaceStatus.INACTIVE:
                workspace.deactivate()
            elif self.new_status == WorkspaceStatus.COMPLETED:
                workspace.complete()
            elif self.new_status == WorkspaceStatus.CANCELLED:
                workspace.cancel()
            elif self.new_status == WorkspaceStatus.ON_HOLD:
                workspace.put_on_hold()
            elif self.new_status == WorkspaceStatus.IN_PROGRESS:
                workspace.start_progress()
            else:
                raise ValueError(f"지원하지 않는 상태입니다: {self.new_status}")

            # 저장
            return repo.save(workspace)


# 편의를 위한 팩토리 함수들
async def create_workspace(
    name: str,
    description: str,
    start_date: datetime,
    end_date: datetime,
    workspace_status: WorkspaceStatus = WorkspaceStatus.ACTIVE,
    owner_id: str = "",
    team_id: str = "",
    client_id: str = "",
) -> Workspace:
    """워크스페이스 생성 편의 함수"""
    command = WorkspaceCreateCommand(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        workspace_status=workspace_status,
        owner_id=owner_id,
        team_id=team_id,
        client_id=client_id,
    )
    return await command.execute()


async def update_workspace(
    workspace_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    workspace_status: Optional[WorkspaceStatus] = None,
    owner_id: Optional[str] = None,
    team_id: Optional[str] = None,
    client_id: Optional[str] = None,
) -> Optional[Workspace]:
    """워크스페이스 수정 편의 함수"""
    command = WorkspaceUpdateCommand(
        workspace_id=workspace_id,
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        workspace_status=workspace_status,
        owner_id=owner_id,
        team_id=team_id,
        client_id=client_id,
    )
    return await command.execute()


async def delete_workspace(workspace_id: str) -> bool:
    """워크스페이스 삭제 편의 함수"""
    command = WorkspaceDeleteCommand(workspace_id=workspace_id)
    return await command.execute()


async def change_workspace_status(
    workspace_id: str, new_status: WorkspaceStatus
) -> Optional[Workspace]:
    """워크스페이스 상태 변경 편의 함수"""
    command = WorkspaceStatusChangeCommand(
        workspace_id=workspace_id, new_status=new_status
    )
    return await command.execute()
