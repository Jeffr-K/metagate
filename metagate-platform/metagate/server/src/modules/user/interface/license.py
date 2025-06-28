from fastapi import APIRouter

licenses = APIRouter(prefix="/license", tags=["license"])


@licenses.post("/", response_model=None)
async def create_license():
    pass


@licenses.get("/", response_model=None)
async def delete_license():
    pass


@licenses.post("/activate", response_model=None)
async def activate_license():
    pass