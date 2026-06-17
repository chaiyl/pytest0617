import pytest


@pytest.mark.api
@pytest.mark.smoke
def test_get_user(api_client, test_data):
    response = api_client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["id"] == test_data["valid_user"]["id"]
