from fastapi import APIRouter

from src.modules.project.interface.adapter.project_schema import (
    ProjectCreateSchema,
    ProjectDeleteSchema,
    ProjectGetSchema,
    ProjectListSchema,
    ProjectUpdateSchema,
)

projects = APIRouter()


@projects.get("/")
async def get_projects(adapter: ProjectListSchema):
    return {"message": "List of projects"}


@projects.get("/{project_id}")
async def get_project(adapter: ProjectGetSchema):
    return {"message": f"Project {adapter.project_id}"}


@projects.post("/")
async def create_project(adapter: ProjectCreateSchema):
    return {"message": "Project created"}


@projects.delete("/{project_id}")
async def delete_project(project_delete_schema: ProjectDeleteSchema):
    return {"message": f"Project {project_delete_schema.project_id} deleted"}


@projects.put("/{project_id}")
async def edit_project(adapter: ProjectUpdateSchema):
    return {"message": f"Project {adapter.project_id} edited"}
