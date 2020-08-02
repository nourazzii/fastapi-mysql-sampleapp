import sys
from fastapi.testclient import TestClient

sys.path.append(".")

from src.main import app

client = TestClient(app)


def test_process_missing_field():
    response = client.post(
        "/api/v1/process",
        json={
            "tagID": 2,
            "userID": "aaaaaaaa-bbbb-cccc-1111-222222222222",
            "remoteIP": "123.234.56.78",
            "timestamp": 1500000000,
        },
    )
    assert response.status_code == 422


def test_process_customer_not_found():
    response = client.post(
        "/api/v1/process",
        json={
            "customerID": 5000000, #TODO: if my API gets more than 5000000M users I will be surprised
            "tagID": 0,
            "userID": "string",
            "remoteIP": "32.0.0.1",
            "timestamp": 10000000,
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}


def test_process_blacklisted_ip():
    response = client.post(
        "/api/v1/process",
        json={
            "customerID": 2,
            "tagID": 0,
            "userID": "string",
            "remoteIP": "0",
            "timestamp": 10000000,
        },
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Remote IP is blocked"}


def test_process_valid_request():
    response = client.post(
        "/api/v1/process",
        json={
            "customerID": 2,
            "tagID": 0,
            "userID": "string",
            "remoteIP": "32.0.0.1",
            "timestamp": 10000000,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Request was processed",
        "data": {},
    }


def test_statistics():
    payload = {"customer_id": 5000000, "date": "01/08/1980"}
    response = client.get("/api/v1/stats", params=payload)
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Returning User Stats",
        "data": {
            "customer": {
                "id": 5000000,
                "valid_requests_count": 0,
                "invalid_requests_count": 0,
            },
            "daily_total_all_customers": 0,
        },
    }
