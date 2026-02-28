def test_register(client):
    response = client.post("/register", json={
        "email": "new@example.com",
        "password": "password123",
        "display_name": "New User",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["display_name"] == "New User"
    assert "id" in data


def test_register_duplicate_email(client):
    client.post("/register", json={
        "email": "dup@example.com",
        "password": "password123",
        "display_name": "User",
    })
    response = client.post("/register", json={
        "email": "dup@example.com",
        "password": "password456",
        "display_name": "User 2",
    })
    assert response.status_code == 400


def test_login_success(client):
    client.post("/register", json={
        "email": "login@example.com",
        "password": "password123",
        "display_name": "Login User",
    })
    response = client.post("/login", data={
        "username": "login@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/register", json={
        "email": "wrong@example.com",
        "password": "password123",
        "display_name": "User",
    })
    response = client.post("/login", data={
        "username": "wrong@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
