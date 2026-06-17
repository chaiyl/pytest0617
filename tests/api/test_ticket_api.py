import pytest

from utils.config_loader import load_yaml


LOGIN_CASES = load_yaml("data/ticket.yaml")["scenarios"]


@pytest.mark.api
@pytest.mark.ticket
@pytest.mark.parametrize("case", LOGIN_CASES, ids=[case["name"] for case in LOGIN_CASES])
def test_ticket_scenarios(api_client, case):
    response = api_client.post("/get-ticket-info", json=case["payload"])
    body = response.json()

    assert response.status_code == case["expected_code"]
    assert body["code"] == case["expected_code"]
    assert body["success"] is case["expected_success"]

    if response.status_code == 200:
        assert body["data"]["ticket"]["ticketId"] == case["payload"]["ticketId"]
        assert body["data"]["ticket"]["storeName"].startswith("TANGKUL")
    else:
        assert body["data"] is None
