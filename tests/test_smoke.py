from main import app, health_check


def test_app_metadata():
    assert app.title == "Invoice Service"
    assert app.version == "1.0.0"


def test_health_check_function():
    assert health_check() == {"status": "healthy"}


def test_routes_registered():
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/health" in paths
    # Ensure the invoices router was included
    assert any(isinstance(p, str) and p.startswith("/invoices") for p in paths)

