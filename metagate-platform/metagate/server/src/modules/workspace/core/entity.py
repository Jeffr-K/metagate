from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.database import Base
from src.modules.workspace.core.value import WorkspaceStatus


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workspace_status: Mapped[WorkspaceStatus] = mapped_column(
        SQLEnum(WorkspaceStatus), default=WorkspaceStatus.ACTIVE, nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name='{self.name}', status={self.workspace_status.value})>"

    @classmethod
    def create(
        cls,
        id: str,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        workspace_status: WorkspaceStatus,
        owner_id: str,
        team_id: str,
        client_id: str,
    ) -> "Workspace":
        """워크스페이스 생성 팩토리 메서드"""
        return cls(
            id=id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            workspace_status=workspace_status,
            owner_id=owner_id,
            team_id=team_id,
            client_id=client_id,
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        workspace_status: Optional[WorkspaceStatus] = None,
        owner_id: Optional[str] = None,
        team_id: Optional[str] = None,
        client_id: Optional[str] = None,
    ) -> None:
        """워크스페이스 정보 업데이트"""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if start_date is not None:
            self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date
        if workspace_status is not None:
            self.workspace_status = workspace_status
        if owner_id is not None:
            self.owner_id = owner_id
        if team_id is not None:
            self.team_id = team_id
        if client_id is not None:
            self.client_id = client_id

    def activate(self) -> None:
        """워크스페이스 활성화"""
        self.workspace_status = WorkspaceStatus.ACTIVE

    def deactivate(self) -> None:
        """워크스페이스 비활성화"""
        self.workspace_status = WorkspaceStatus.INACTIVE

    def complete(self) -> None:
        """워크스페이스 완료"""
        self.workspace_status = WorkspaceStatus.COMPLETED

    def cancel(self) -> None:
        """워크스페이스 취소"""
        self.workspace_status = WorkspaceStatus.CANCELLED

    def put_on_hold(self) -> None:
        """워크스페이스 보류"""
        self.workspace_status = WorkspaceStatus.ON_HOLD

    def start_progress(self) -> None:
        """워크스페이스 진행 시작"""
        self.workspace_status = WorkspaceStatus.IN_PROGRESS

    @property
    def is_active(self) -> bool:
        """활성 상태인지 확인"""
        return self.workspace_status == WorkspaceStatus.ACTIVE

    @property
    def is_completed(self) -> bool:
        """완료 상태인지 확인"""
        return self.workspace_status == WorkspaceStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """취소 상태인지 확인"""
        return self.workspace_status == WorkspaceStatus.CANCELLED
