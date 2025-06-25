from src.modules.organization.interface.adapter import OrganizationCreateAdapter, OrganizationUpdateAdapter


class OrganizationCreateUseCase:
    def __init__(self):
        pass

    async def execute(self, adapter: OrganizationCreateAdapter):
        pass


class OrganizationDeleteUseCase:
    def __init__(self):
        pass

    async def execute(self, organization_id: int):
        pass


class OrganizationUpdateUseCase:
    def __init__(self):
        pass

    async def execute(self, organization_id: int, adapter: OrganizationUpdateAdapter):
        pass