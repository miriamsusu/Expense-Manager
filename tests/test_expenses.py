def register_and_login(client, email: str) -> str:
    client.post(
        "/auth/register",
        json={"email": email, "phone_number": "+15551234567", "password": "testpass123"},
    )
    response = client.post(
        "/auth/login", json={"email": email, "password": "testpass123"}
    )
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_expense_is_categorized(client):
    token = register_and_login(client, "expenseuser@example.com")
    response = client.post(
        "/expenses",
        json={"amount": 20, "descr": "Walmart run", "date": "2026-08-20"},
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    assert response.json()["category"] == "groceries"


def test_user_cannot_access_another_users_expense(client):
    alice_token = register_and_login(client, "alice@example.com")
    bob_token = register_and_login(client, "bob@example.com")

    create_response = client.post(
        "/expenses",
        json={"amount": 20, "descr": "Alice's item", "date": "2026-08-20"},
        headers=auth_headers(alice_token),
    )
    expense_id = create_response.json()["id"]

    # Bob tries to fetch Alice's expense by its real id
    response = client.get(f"/expenses/{expense_id}", headers=auth_headers(bob_token))
    assert response.status_code == 404


def test_user_cannot_delete_another_users_expense(client):
    alice_token = register_and_login(client, "alice2@example.com")
    bob_token = register_and_login(client, "bob2@example.com")

    create_response = client.post(
        "/expenses",
        json={"amount": 20, "descr": "Alice's item", "date": "2026-08-20"},
        headers=auth_headers(alice_token),
    )
    expense_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/expenses/{expense_id}", headers=auth_headers(bob_token)
    )
    assert delete_response.status_code == 404

    # confirm it's still there, from Alice's own perspective
    get_response = client.get(
        f"/expenses/{expense_id}", headers=auth_headers(alice_token)
    )
    assert get_response.status_code == 200