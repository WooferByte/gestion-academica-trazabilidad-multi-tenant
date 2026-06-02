from app.main import create_app


def test_app_creates_without_error():
    app = create_app()
    assert app.title == 'activia-trace'
    assert app.version == '0.1.0'
