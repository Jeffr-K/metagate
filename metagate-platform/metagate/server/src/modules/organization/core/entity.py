from sqlalchemy import Integer, String
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import registry

mapper_registry = registry()

@mapper_registry.mapped
class Organization:
    __tablename__ = "organization"

    id = ColumnProperty(Integer, primary_key=True, index=True)
    name = ColumnProperty(String(255), unique=True, nullable=False, index=True)