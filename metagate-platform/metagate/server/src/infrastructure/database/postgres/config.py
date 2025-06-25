from typing import Annotated, Generator
from contextlib import contextmanager

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = ""
    database: str = "metagate_dev"

    class Config:
        env_prefix = "DB_"
        env_file = ".env.develop"
        extra = "ignore"

    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class DatabaseEngine:
    _instance = None
    _engine = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseEngine, cls).__new__(cls)
        return cls._instance

    def connect(self, config: DatabaseConfig = None):
        if self._engine is None:
            if config is None:
                config = DatabaseConfig()

            self._engine = create_engine(
                config.url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            SQLModel.metadata.create_all(self._engine)

        return self._engine

    def get_session(self) -> Generator[Session, None, None]:
        if self._engine is None:
            self.connect()

        with Session(self._engine) as session:
            yield session

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        if self._engine is None:
            self.connect()

        with Session(self._engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    @property
    def engine(self):
        if self._engine is None:
            self.connect()
        return self._engine


database_engine = DatabaseEngine()


def get_database_engine() -> DatabaseEngine:
    return database_engine


def get_session() -> Generator[Session, None, None]:
    yield from database_engine.get_session()


SessionDep = Annotated[Session, Depends(get_session)]