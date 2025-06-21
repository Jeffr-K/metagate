from fastapi import APIRouter

auth = APIRouter()


@auth.route("/login", methods=["POST"])
async def login():
    pass


@auth.delete("/logout")
async def logout():
    pass
