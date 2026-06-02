import uuid


class TenantContext:
    def __init__(self, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id


async def get_tenant(tenant_id: uuid.UUID) -> TenantContext:
    """Provee el tenant activo. En C-02 recibe tenant_id inyectado explícitamente.
    En C-03+ se resolverá desde el JWT autenticado.
    """
    return TenantContext(tenant_id=tenant_id)
