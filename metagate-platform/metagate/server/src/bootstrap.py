import os
from typing import Union
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.infrastructure.cache.redis_client import redis_client
from src.infrastructure.logger.logger import logger
from src.infrastructure.nats.client import nats_client
from src.infrastructure.prometheus.metrics import metrics_middleware
from src.infrastructure.sentry.client import init_sentry
from dotenv import load_dotenv

from src.modules.user.interface.user import users


class Bootstrap:
    _instance: Union[FastAPI]
    _cors = ["http://localhost:3000", "*"]

    def __init__(self):
        self.start()

    @classmethod
    def start(cls):
        cls._load_env()
        cls._init_infrastructure()
        cls._instance = FastAPI()
        cls._router()
        cls._middleware()
        cls._database()
        return cls._instance

    @classmethod
    def _load_env(cls):
        if os.path.exists(".env.develop"):
            load_dotenv(".env.develop")
            logger.info("Loaded .env.develop")
        elif os.path.exists(".env.production"):
            load_dotenv(".env.production")
            logger.info("Loaded .env.production")
        elif os.path.exists(".env"):
            load_dotenv(".env")
            logger.info("Loaded .env")

    @classmethod
    def _init_infrastructure(cls):
        try:
            init_sentry()
            logger.info("Sentry initialized")

            if redis_client.ping():
                logger.info("Redis connected")
            else:
                logger.warning("Redis connection failed")

            if nats_client.is_connected():
                logger.info("NATS connected")
            else:
                logger.warning("NATS not connected")

        except Exception as e:
            logger.error(f"Infrastructure initialization failed: {e}")

    @classmethod
    def _router(cls):
        cls._instance.include_router(router=users)
        # cls._instance.include_router(router=auth)
        # cls._instance.include_router(router=oauth)
        # cls._instance.include_router(router=admin)
        # cls._instance.add_route("/metrics", get_metrics)

        logger.info("Routers configured.")

    @classmethod
    def _database(cls):
        try:
            from src.infrastructure.database.postgres.config import database_engine
            database_engine.connect()
            from src.infrastructure.database.redis.config import redis_engine
            redis_engine.connect()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    @classmethod
    def _middleware(cls):
        cls._instance.add_middleware(
            CORSMiddleware,
            allow_origins=cls._cors,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        cls._instance.middleware("http")(metrics_middleware)

        logger.info("Middlewares configured")

    @property
    def instance(self) -> FastAPI:
        return self._instance
