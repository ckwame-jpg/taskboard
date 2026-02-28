def test_create_board(client, auth_headers):
    response = client.post("/boards/", json={"title": "My Board"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Board"
    assert "id" in data


def test_list_boards(client, auth_headers):
    client.post("/boards/", json={"title": "Board 1"}, headers=auth_headers)
    client.post("/boards/", json={"title": "Board 2"}, headers=auth_headers)
    response = client.get("/boards/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_board_detail(client, auth_headers):
    create_resp = client.post("/boards/", json={"title": "Detail Board"}, headers=auth_headers)
    board_id = create_resp.json()["id"]

    response = client.get(f"/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Detail Board"
    assert "columns" in data
    assert "members" in data
    assert len(data["members"]) == 1
    assert data["members"][0]["role"] == "owner"


def test_update_board(client, auth_headers):
    create_resp = client.post("/boards/", json={"title": "Old Title"}, headers=auth_headers)
    board_id = create_resp.json()["id"]

    response = client.put(f"/boards/{board_id}", json={"title": "New Title"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_delete_board(client, auth_headers):
    create_resp = client.post("/boards/", json={"title": "To Delete"}, headers=auth_headers)
    board_id = create_resp.json()["id"]

    response = client.delete(f"/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get("/boards/", headers=auth_headers)
    assert len(response.json()) == 0


def test_invite_member(client, auth_headers, second_auth_headers):
    create_resp = client.post("/boards/", json={"title": "Team Board"}, headers=auth_headers)
    board_id = create_resp.json()["id"]

    response = client.post(f"/boards/{board_id}/invite", json={
        "email": "user2@example.com",
        "role": "editor",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "editor"

    # Second user can now see the board
    response = client.get("/boards/", headers=second_auth_headers)
    assert len(response.json()) == 1


def test_non_member_cannot_access(client, auth_headers, second_auth_headers):
    create_resp = client.post("/boards/", json={"title": "Private Board"}, headers=auth_headers)
    board_id = create_resp.json()["id"]

    response = client.get(f"/boards/{board_id}", headers=second_auth_headers)
    assert response.status_code == 403
