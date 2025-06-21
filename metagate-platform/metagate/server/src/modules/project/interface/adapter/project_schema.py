from datetime import datetime

from pydantic import BaseModel


class ProjectCreateSchema(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: str
    owner_id: str
    team_id: str
    client_id: str


class ProjectUpdateSchema(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: str
    owner_id: str
    team_id: str
    client_id: str


class ProjectDeleteSchema(BaseModel):
    project_id: str


class ProjectGetSchema(BaseModel):
    project_id: str


class ProjectListSchema(BaseModel):
    page: int
    limit: int
    search: str
