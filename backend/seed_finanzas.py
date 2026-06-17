"""Seed sample data for liquidaciones, facturas, and salarios_base."""
import asyncio
import uuid
from datetime import datetime, date
import asyncpg

TENANT_ID = "a232c35d-2dad-5510-8948-5ce14f18b85d"


async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@127.0.0.1:5432/trace")
    NS = uuid.NAMESPACE_DNS

    # Get existing users and cohortes
    users = await conn.fetch("SELECT id, email FROM users LIMIT 10")
    cohortes = await conn.fetch("SELECT id, nombre FROM cohortes LIMIT 5")

    if not users or not cohortes:
        print("No users or cohortes found - run main seed first")
        await conn.close()
        return

    roles = ["PROFESOR", "TUTOR", "NEXO", "COORDINADOR"]
    periodos = ["2025-03", "2025-04", "2025-05"]

    # === SALARIOS BASE ===
    existing_salarios = await conn.fetchval("SELECT COUNT(*) FROM salarios_base")
    if existing_salarios == 0:
        for rol in roles:
            montos = {"PROFESOR": 150000, "TUTOR": 100000, "NEXO": 120000, "COORDINADOR": 180000}
            sid = uuid.uuid5(NS, f"seed-salario-{rol}")
            await conn.execute(
                """INSERT INTO salarios_base (id, tenant_id, rol, monto, desde)
                   VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING""",
                sid, uuid.UUID(TENANT_ID), rol, montos[rol], date(2025, 3, 1),
            )
        print(f"✅ Created {len(roles)} salary base entries")
    else:
        print(f"⏭️  Salarios base already has {existing_salarios} entries")

    # === LIQUIDACIONES ===
    existing_liquidaciones = await conn.fetchval("SELECT COUNT(*) FROM liquidaciones")
    if existing_liquidaciones == 0:
        count = 0
        for cohorte in cohortes:
            for periodo in periodos:
                for user in users[:4]:
                    r = roles[count % len(roles)]
                    base = {"PROFESOR": 150000, "TUTOR": 100000, "NEXO": 120000, "COORDINADOR": 180000}[r]
                    plus = (hash(f"plus-{user['id']}-{periodo}") % 30000)
                    total = base + plus
                    lid = uuid.uuid5(NS, f"seed-liq-{user['id']}-{cohorte['id']}-{periodo}")
                    es_nexo = r == "NEXO"
                    estados_liq = ["Abierta", "Calculada", "Cerrada"]
                    await conn.execute(
                        """INSERT INTO liquidaciones (id, tenant_id, usuario_id, cohorte_id, periodo, rol, monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado)
                           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12) ON CONFLICT DO NOTHING""",
                        lid, uuid.UUID(TENANT_ID), user["id"], cohorte["id"],
                        periodo, r, base, plus, total, es_nexo, False, estados_liq[count % 3],
                    )
                    count += 1
        print(f"✅ Created {count} liquidacion entries")
    else:
        print(f"⏭️  Liquidaciones already has {existing_liquidaciones} entries")

    # === FACTURAS ===
    existing_facturas = await conn.fetchval("SELECT COUNT(*) FROM facturas")
    if existing_facturas == 0:
        count = 0
        for periodo in periodos:
            for user in users[:3]:
                fid = uuid.uuid5(NS, f"seed-fac-{user['id']}-{periodo}")
                await conn.execute(
                    """INSERT INTO facturas (id, tenant_id, usuario_id, periodo, detalle, estado, cargada_at)
                       VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT DO NOTHING""",
                    fid, uuid.UUID(TENANT_ID), user["id"], periodo,
                    f"Honorarios - {periodo}",
                    ["Pendiente", "Pendiente", "Abonada"][count % 3],
                    datetime(2025, 3, 15 + count),
                )
                count += 1
        print(f"✅ Created {count} factura entries")
    else:
        print(f"⏭️  Facturas already has {existing_facturas} entries")

    await conn.close()
    print("\n🎉 Seed finanzas completo!")


asyncio.run(main())
