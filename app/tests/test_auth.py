def test_user_registration(
    client
):

    response = client.post(
        "/api/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "Password@123",
            "role": "Admin"
        }
    )

    print("REGISTER STATUS:", response.status_code)
    print("REGISTER RESPONSE:", response.json())

    assert response.status_code in [200, 201]

    data = response.json()

    assert "id" in data
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["role"] == "Admin"


def test_duplicate_registration(
    client
):

    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "Password@123",
        "role": "Admin"
    }

    first_response = client.post(
        "/api/auth/register",
        json=payload
    )

    assert first_response.status_code in [200, 201]

    second_response = client.post(
        "/api/auth/register",
        json=payload
    )

    print("DUPLICATE STATUS:", second_response.status_code)
    print("DUPLICATE RESPONSE:", second_response.json())

    assert second_response.status_code in [400, 409]


def test_login_success(
    client
):

    client.post(
        "/api/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "Password@123",
            "role": "Admin"
        }
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "john@example.com",
            "password": "Password@123"
        }
    )

    print("LOGIN STATUS:", response.status_code)
    print("LOGIN RESPONSE:", response.json())

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_credentials(
    client
):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "WrongPassword"
        }
    )

    print("INVALID LOGIN STATUS:", response.status_code)
    print("INVALID LOGIN RESPONSE:", response.json())

    assert response.status_code in [401, 403]


def test_protected_endpoint_without_token(
    client
):

    response = client.get(
        "/api/auth/me"
    )

    print("UNAUTHORIZED STATUS:", response.status_code)
    print("UNAUTHORIZED RESPONSE:", response.json())

    assert response.status_code == 401
