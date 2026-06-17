import pytest

from utils.config_loader import load_yaml


LOGIN_CASES = load_yaml("data/login_cases.yaml")["scenarios"]


@pytest.mark.api
@pytest.mark.login
@pytest.mark.parametrize("case", LOGIN_CASES, ids=[case["name"] for case in LOGIN_CASES])
def test_login_scenarios(login_client, case):
    response = login_client.post("/login", json=case["payload"])
    body = response.json()

    assert response.status_code == case["expected_status"]
    assert body["code"] == case["expected_code"]

    if response.status_code == 200:
        assert body["data"]["username"] == case["payload"]["username"]
        assert body["data"]["token"].startswith("demo-token-")
    else:
        assert body["data"] is None


@pytest.mark.api
@pytest.mark.login
@pytest.mark.parametrize(
    "payload",
    [
        {"username": "alice", "password": "Alice@123"},
        {"username": "alice", "password": "Wrong@123"},
        None,
    ],
    ids=["success_response", "auth_error_response", "bad_request_response"],
)
def test_login_response_contract(login_client, payload):
    response = login_client.post("/login", json=payload)
    body = response.json()

    assert isinstance(response.status_code, int)
    assert set(body.keys()) == {"code", "message", "data"}
    assert isinstance(body["code"], str)
    assert isinstance(body["message"], str)

    if response.status_code == 200:
        assert set(body["data"].keys()) == {"token", "user_id", "username"}
        assert isinstance(body["data"]["token"], str)
        assert isinstance(body["data"]["user_id"], int)
        assert isinstance(body["data"]["username"], str)
    else:
        assert body["data"] is None
