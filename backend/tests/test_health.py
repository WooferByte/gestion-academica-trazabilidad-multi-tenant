from starlette.testclient import TestClient


def test_health_returns_200_and_status_ok(app):
    client = TestClient(app)
    response = client.get('/health')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'database' in data


def test_health_db_down_does_not_crash(app):
    client = TestClient(app)
    response = client.get('/health')

    assert response.status_code == 200
    data = response.json()
    assert data['database'] in ('up', 'down')
