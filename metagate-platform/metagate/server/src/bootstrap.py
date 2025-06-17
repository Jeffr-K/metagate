from typing import Union

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


class Bootstrap:
    _instance: Union[FastAPI]
    _cors = ["http://localhost:3000", "*"]

    def __init__(self):
        self.start()

    @classmethod
    def start(cls):
        cls._instance = FastAPI()
        cls._router()
        cls._middleware()
        cls._database()
        return cls._instance

    @classmethod
    def _router(cls):
        # cls._instance.include_router(router=user)
        pass

    @classmethod
    def _database(cls):
        pass
        # @cls._instance.on_event("startup")
        # async def initialize_mongo():
        #     await MongoClientConfig.connect()
        #
        # @cls._instance.on_event("shutdown")
        # async def dropdown_mongo():
        #     await MongoClientConfig.close()

    @classmethod
    def _middleware(cls):
        cls._instance.add_middleware(
            CORSMiddleware,
            allow_origins=cls._cors,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

    @property
    def instance(self) -> FastAPI:
        return self._instance