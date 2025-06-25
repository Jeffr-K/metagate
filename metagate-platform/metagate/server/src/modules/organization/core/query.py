from src.modules.organization.interface.adapter import OrganizationPaginationQuery, OrganizationQuery


class OrganizationsQueryUseCase:
    def __init__(self):
        pass

    async def execute(self, query: OrganizationPaginationQuery):
        pass


class OrganizationQueryUseCase:
    def __init__(self):
        pass

    async def execute(self, query: OrganizationQuery):
        pass