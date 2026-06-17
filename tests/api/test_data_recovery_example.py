import pytest


@pytest.mark.api
@pytest.mark.skip(reason="示例用例：替换为真实新增/删除接口后再启用")
def test_create_resource_with_recovery(api_client, data_recovery):
    create_response = api_client.post("/create-resource", json={
        "name": "pytest_auto_test_resource",
    })
    assert create_response.status_code == 200

    resource_id = create_response.json()["data"]["id"]
    data_recovery.delete_created(
        path="/delete-resource",
        payload={"id": resource_id},
        name=f"delete resource {resource_id}",
    )

    query_response = api_client.post("/query-resource", json={"id": resource_id})
    assert query_response.status_code == 200


@pytest.mark.api
@pytest.mark.skip(reason="示例用例：替换为真实查询/更新接口后再启用")
def test_update_resource_with_recovery(api_client, data_recovery):
    resource_id = "replace-with-real-id"

    before_response = api_client.post("/query-resource", json={"id": resource_id})
    assert before_response.status_code == 200
    old_name = before_response.json()["data"]["name"]

    update_response = api_client.post("/update-resource", json={
        "id": resource_id,
        "name": "pytest_updated_name",
    })
    assert update_response.status_code == 200

    data_recovery.restore_updated(
        path="/update-resource",
        payload={
            "id": resource_id,
            "name": old_name,
        },
        name=f"restore resource {resource_id}",
    )

    query_response = api_client.post("/query-resource", json={"id": resource_id})
    assert query_response.json()["data"]["name"] == "pytest_updated_name"
