from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.database import Base
from src.modules.project.core.value import ProjectStatus


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    budget: Mapped[Optional[float]] = mapped_column(String(20), nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status={self.project_status.value})>"

    @classmethod
    def create(
        cls,
        id: str,
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
    ) -> "Project":
        """프로젝트 생성 팩토리 메서드"""
        return cls(
            id=id,
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

    def update(
        self,
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
    ) -> None:
        """프로젝트 정보 업데이트"""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if start_date is not None:
            self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date
        if project_status is not None:
            self.project_status = project_status
        if owner_id is not None:
            self.owner_id = owner_id
        if team_id is not None:
            self.team_id = team_id
        if client_id is not None:
            self.client_id = client_id
        if workspace_id is not None:
            self.workspace_id = workspace_id
        if budget is not None:
            self.budget = budget
        if priority is not None:
            self.priority = priority

    def activate(self) -> None:
        """프로젝트 활성화"""
        self.project_status = ProjectStatus.ACTIVE

    def deactivate(self) -> None:
        """프로젝트 비활성화"""
        self.project_status = ProjectStatus.INACTIVE

    def complete(self) -> None:
        """프로젝트 완료"""
        self.project_status = ProjectStatus.COMPLETED

    def cancel(self) -> None:
        """프로젝트 취소"""
        self.project_status = ProjectStatus.CANCELLED

    def put_on_hold(self) -> None:
        """프로젝트 보류"""
        self.project_status = ProjectStatus.ON_HOLD

    def start_progress(self) -> None:
        """프로젝트 진행 시작"""
        self.project_status = ProjectStatus.IN_PROGRESS

    def start_planning(self) -> None:
        """프로젝트 계획 단계"""
        self.project_status = ProjectStatus.PLANNING

    def start_review(self) -> None:
        """프로젝트 검토 단계"""
        self.project_status = ProjectStatus.REVIEW

    @property
    def is_active(self) -> bool:
        """활성 상태인지 확인"""
        return self.project_status == ProjectStatus.ACTIVE

    @property
    def is_completed(self) -> bool:
        """완료 상태인지 확인"""
        return self.project_status == ProjectStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """취소 상태인지 확인"""
        return self.project_status == ProjectStatus.CANCELLED

    @property
    def is_in_progress(self) -> bool:
        """진행 중인지 확인"""
        return self.project_status == ProjectStatus.IN_PROGRESS
