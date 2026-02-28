def test_create_column_and_card(client, auth_headers):
    board = client.post("/boards/", json={"title": "Board"}, headers=auth_headers).json()
    board_id = board["id"]

    col = client.post(f"/boards/{board_id}/columns/", json={"title": "To Do"}, headers=auth_headers).json()
    assert col["title"] == "To Do"

    card = client.post(f"/boards/{board_id}/cards/", json={
        "title": "First Task",
        "description": "Do something",
        "column_id": col["id"],
    }, headers=auth_headers).json()
    assert card["title"] == "First Task"
    assert card["column_id"] == col["id"]


def test_move_card(client, auth_headers):
    board = client.post("/boards/", json={"title": "Board"}, headers=auth_headers).json()
    board_id = board["id"]

    col1 = client.post(f"/boards/{board_id}/columns/", json={"title": "To Do"}, headers=auth_headers).json()
    col2 = client.post(f"/boards/{board_id}/columns/", json={"title": "Done"}, headers=auth_headers).json()

    card = client.post(f"/boards/{board_id}/cards/", json={
        "title": "Task",
        "column_id": col1["id"],
    }, headers=auth_headers).json()

    moved = client.put(f"/boards/{board_id}/cards/{card['id']}/move", json={
        "column_id": col2["id"],
        "position": 0,
    }, headers=auth_headers).json()
    assert moved["column_id"] == col2["id"]


def test_update_card(client, auth_headers):
    board = client.post("/boards/", json={"title": "Board"}, headers=auth_headers).json()
    board_id = board["id"]
    col = client.post(f"/boards/{board_id}/columns/", json={"title": "Col"}, headers=auth_headers).json()

    card = client.post(f"/boards/{board_id}/cards/", json={
        "title": "Original",
        "column_id": col["id"],
    }, headers=auth_headers).json()

    updated = client.put(f"/boards/{board_id}/cards/{card['id']}", json={
        "title": "Updated Title",
    }, headers=auth_headers).json()
    assert updated["title"] == "Updated Title"


def test_delete_card(client, auth_headers):
    board = client.post("/boards/", json={"title": "Board"}, headers=auth_headers).json()
    board_id = board["id"]
    col = client.post(f"/boards/{board_id}/columns/", json={"title": "Col"}, headers=auth_headers).json()

    card = client.post(f"/boards/{board_id}/cards/", json={
        "title": "To Delete",
        "column_id": col["id"],
    }, headers=auth_headers).json()

    response = client.delete(f"/boards/{board_id}/cards/{card['id']}", headers=auth_headers)
    assert response.status_code == 200


def test_viewer_cannot_create_card(client, auth_headers, second_auth_headers):
    board = client.post("/boards/", json={"title": "Board"}, headers=auth_headers).json()
    board_id = board["id"]

    # Invite as viewer
    client.post(f"/boards/{board_id}/invite", json={
        "email": "user2@example.com",
        "role": "viewer",
    }, headers=auth_headers)

    col = client.post(f"/boards/{board_id}/columns/", json={"title": "Col"}, headers=auth_headers).json()

    # Viewer tries to create card
    response = client.post(f"/boards/{board_id}/cards/", json={
        "title": "Nope",
        "column_id": col["id"],
    }, headers=second_auth_headers)
    assert response.status_code == 403
