
class UsersPaginationQueryUseCase:
    def __init__(self):
        pass

    @classmethod
    async def execute(cls):
        return {"message": "Users pagination query executed successfully."}


class UserQueryUseCase:
    def __init__(self):
        pass

    @classmethod
    async def execute(cls, user_id: int):
        return {"message": f"{user_id} User query executed successfully."}