import pytest

def test_register_new_user(client):
    response=client.post("/auth/register",
        json={
            "email": "newuser@example.com",
            "phone_number": "+15551234567",
            "password": "testpass123",
        },

        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_rejected(client):
    payload = {
        "email": "dup@example.com",
        "phone_number": "+15551234567",
        "password": "testpass123",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "bad_email",
    [
        "not-an-email",
        "missing-at-sign.com",
        "@missing-local-part.com",
        "spaces in@email.com",
    ],
)
def test_register_rejects_invalid_email(client, bad_email):
    response = client.post(
        "/auth/register",
        json={
            "email": bad_email,
            "phone_number": "+15551234567",
            "password": "validpass123",
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "bad_phone",
    [
        "abc",  # not digits at all
        "123",  # shorter than the 7-digit minimum
        "1" * 20,  # longer than the 15-digit maximum
        "555-123-4567",  # dashes aren't allowed by the pattern
    ],
)
def test_register_rejects_invalid_phone(client, bad_phone):
    response = client.post(
        "/auth/register",
        json={
            "email": "phonetest@example.com",
            "phone_number": bad_phone,
            "password": "validpass123",
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "valid_phone",
    [
        "+15551234567",  # with country code
        "5551234567",  # without leading +
        "+442071234567",  # different country, different length
    ],
)
def test_register_accepts_valid_phone_formats(client, valid_phone):
    response = client.post(
        "/auth/register",
        json={
            "email": "validphone@example.com",
            "phone_number": valid_phone,
            "password": "validpass123",
        },
    )
    assert response.status_code == 201


def test_register_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "shortpass@example.com",
            "phone_number": "+15551234567",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_register_rejects_missing_fields(client):
    response = client.post("/auth/register", json={"email": "missing@example.com"})
    assert response.status_code == 422


def test_login_with_correct_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "loginuser@example.com",
            "phone_number": "+15551234567",
            "password": "correctpass123",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "loginuser@example.com", "password": "correctpass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_rejected(client):
    client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "phone_number": "+15551234567",
            "password": "correctpass123",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
