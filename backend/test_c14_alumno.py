"""Test C-14 coloquios como ALUMNO."""
import asyncio
import httpx

API = 'http://localhost:8000'


async def test():
    async with httpx.AsyncClient(base_url=API, timeout=10) as c:
        # Login as admin first to get materia
        r = await c.post('/api/v1/auth/login', json={'email': 'admin@test.com', 'password': 'admin123'})
        h = {'Authorization': f'Bearer {r.json()["access_token"]}'}
        r2 = await c.get('/api/v1/admin/materias', headers=h)
        mid = r2.json()['items'][0]['id']
        r3 = await c.get('/api/v1/admin/cohortes', headers=h)
        coid = r3.json()['items'][0]['id']

        # Create coloquio as admin
        r4 = await c.post('/api/v1/coloquios/', headers=h,
                          json={'materia_id': mid, 'cohorte_id': coid,
                                'instancia': 'Test', 'tipo': 'Coloquio',
                                'turnos': [{'fecha': '2026-07-01', 'hora_inicio': '09:00',
                                            'hora_fin': '10:00', 'cupo': 2}]})
        if r4.status_code == 201:
            ev_id = r4.json()['id']
            print(f'1. Coloquio creado: {ev_id[:8]}... ✅')
            turno_id = r4.json()['turnos'][0]['id']
        else:
            print(f'1. Error creando coloquio: {r4.status_code}')
            return

        # Login as alumno
        r5 = await c.post('/api/v1/auth/login', json={'email': 'alumno@test.com', 'password': 'alumno123'})
        if r5.status_code != 200:
            print(f'2. Login alumno fallo: {r5.status_code} {r5.text[:100]}')
            return
        ah = {'Authorization': f'Bearer {r5.json()["access_token"]}'}
        print('2. Login alumno ✅')

        # GET /coloquios/ (listar como alumno)
        r6 = await c.get('/api/v1/coloquios/', headers=ah)
        print(f'3. GET /coloquios/ (alumno): {r6.status_code} {"✅" if r6.status_code == 200 else "❌"}')

        # GET /coloquios/{id} (detalle)
        r7 = await c.get(f'/api/v1/coloquios/{ev_id}', headers=ah)
        print(f'4. GET /coloquios/{ev_id[:8]} (detalle): {r7.status_code} {"✅" if r7.status_code == 200 else "❌"}')

        # POST /coloquios/{id}/reservas (reservar turno)
        r8 = await c.post(f'/api/v1/coloquios/{ev_id}/reservas', headers=ah,
                          json={'turno_id': turno_id})
        print(f'5. POST /coloquios/{ev_id[:8]}/reservas: {r8.status_code} {"✅" if r8.status_code == 201 else "❌"}')
        if r8.status_code == 201:
            res_id = r8.json()['id']
            # DELETE /coloquios/reservas/{id} (cancelar)
            r9 = await c.delete(f'/api/v1/coloquios/reservas/{res_id}', headers=ah)
            print(f'6. DELETE /coloquios/reservas/{res_id[:8]}: {r9.status_code} {"✅" if r9.status_code == 200 else "❌"}')

        # Sin auth
        r10 = await c.get('/api/v1/coloquios/')
        print(f'7. Sin auth: {r10.status_code} {"✅ 401" if r10.status_code == 401 else "❌"}')

        print(f'\n{"=" * 50}')
        print('C-14: ✅ TEST COMPLETO CON ALUMNO')
        print(f'{"=" * 50}')


asyncio.run(test())
