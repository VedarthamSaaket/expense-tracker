import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


@pytest.fixture
def make_expense(client):
    def make(**overrides):
        body = {"title": "Lunch", "amount": 250, "category": "food", "spent_on": "2026-10-10"}
        body.update(overrides)
        res = client.post("/expenses", json=body)
        assert res.status_code == 201
        return res.get_json()

    return make
