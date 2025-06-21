from fastapi import APIRouter

workspaces = APIRouter()


@workspaces.get()
async def get_workspaces():
    pass


@workspaces.get()
async def get_workspace():
    pass


@workspaces.post()
async def create_workspace():
    pass


@workspaces.delete()
async def delete_workspace():
    pass


@workspaces.put()
async def edit_workspace():
    pass
