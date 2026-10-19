def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_categories(client):
    res = client.get("/categories")
    assert "food" in res.get_json()


def test_create_expense(client):
    res = client.post(
        "/expenses",
        json={"title": " Metro card ", "amount": 99.999, "category": "transport",
              "spent_on": "2026-10-01"},
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] == 1
    assert data["title"] == "Metro card"
    assert data["amount"] == 100.0
    assert data["category"] == "transport"


def test_create_defaults_category_and_date(client):
    res = client.post("/expenses", json={"title": "Snack", "amount": 20})
    data = res.get_json()
    assert data["category"] == "other"
    assert len(data["spent_on"]) == 10


def test_create_rejects_bad_input(client):
    res = client.post("/expenses", json={"amount": -5, "category": "rent", "spent_on": "nope"})
    assert res.status_code == 400
    errors = res.get_json()["errors"]
    assert "title is required" in errors
    assert "amount must be greater than 0" in errors
    assert any(e.startswith("category must be one of") for e in errors)
    assert any(e.startswith("spent_on must be a date") for e in errors)


def test_create_rejects_non_json(client):
    res = client.post("/expenses", data="hello")
    assert res.status_code == 400


def test_create_rejects_bool_amount(client):
    res = client.post("/expenses", json={"title": "x", "amount": True})
    assert res.status_code == 400


def test_get_expense(client, make_expense):
    created = make_expense()
    res = client.get(f"/expenses/{created['id']}")
    assert res.status_code == 200
    assert res.get_json() == created


def test_get_missing_expense(client):
    res = client.get("/expenses/999")
    assert res.status_code == 404


def test_list_and_filter(client, make_expense):
    make_expense(title="Bus", category="transport", spent_on="2026-09-30")
    make_expense(title="Pizza", spent_on="2026-10-05")
    make_expense(title="Coffee", spent_on="2026-10-12")

    all_items = client.get("/expenses").get_json()
    assert [e["title"] for e in all_items] == ["Coffee", "Pizza", "Bus"]

    food = client.get("/expenses?category=food").get_json()
    assert {e["title"] for e in food} == {"Pizza", "Coffee"}

    september = client.get("/expenses?month=2026-09").get_json()
    assert [e["title"] for e in september] == ["Bus"]


def test_update_expense(client, make_expense):
    created = make_expense()
    res = client.put(f"/expenses/{created['id']}", json={"amount": 300, "category": "fun"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["amount"] == 300
    assert data["category"] == "fun"
    assert data["title"] == "Lunch"


def test_update_validation(client, make_expense):
    created = make_expense()
    assert client.put(f"/expenses/{created['id']}", json={}).status_code == 400
    assert client.put(f"/expenses/{created['id']}", json={"amount": 0}).status_code == 400
    assert client.put("/expenses/999", json={"amount": 5}).status_code == 404


def test_delete_expense(client, make_expense):
    created = make_expense()
    assert client.delete(f"/expenses/{created['id']}").status_code == 204
    assert client.get(f"/expenses/{created['id']}").status_code == 404
    assert client.delete(f"/expenses/{created['id']}").status_code == 404


def test_summary(client, make_expense):
    make_expense(amount=100.5)
    make_expense(amount=49.5)
    make_expense(title="Cab", amount=300, category="transport")
    make_expense(title="Old", amount=1000, spent_on="2026-08-01")

    data = client.get("/summary?month=2026-10").get_json()
    assert data["total"] == 450
    assert data["count"] == 3
    assert data["by_category"]["food"] == {"total": 150, "count": 2}
    assert data["by_category"]["transport"] == {"total": 300, "count": 1}

    everything = client.get("/summary").get_json()
    assert everything["total"] == 1450
