from pydantic import BaseModel


class OrganizationCreateAdapter(BaseModel):
    name: str
    creator: str


class OrganizationUpdateAdapter(BaseModel):
    name: str
    creator: str


class OrganizationPaginationQuery(BaseModel):
    page: int = 1
    limit: int = 100
    sort: int = 100


class OrganizationQuery(BaseModel):
    organization_id: int