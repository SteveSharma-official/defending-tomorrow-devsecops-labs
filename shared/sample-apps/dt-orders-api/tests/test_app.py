import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ORDERS_DB", str(tmp_path / "test.db"))
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_orders_for_customer(client):
    data = client.get("/orders?customer=alice").get_json()
    assert len(data) == 1 and data[0]["item"] == "widget"


def test_sql_injection_payload_returns_nothing(client):
    """Security regression test: a classic tautology payload must not dump every row."""
    data = client.get("/orders", query_string={"customer": "x' OR '1'='1"}).get_json()
    assert data == []


def test_security_headers(client):
    headers = client.get("/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
