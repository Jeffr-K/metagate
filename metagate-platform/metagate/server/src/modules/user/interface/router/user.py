from fastapi import APIRouter

user = APIRouter()


@user.get("/list")
async def users():
    pass


@user.get("/")
async def user():
    pass


@user.post("/register")
async def register():
    pass


@user.delete("/dropdown")
async def dropdown():
    pass


@user.put("/")
async def edit():
    pass
