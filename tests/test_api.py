import pytest

from backend.app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data == {
        "status": "ok",
        "service": "ImpactGraph AI",
    }


def test_predict_requires_json(client):
    response = client.post(
        "/api/predict",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Request body must be JSON."


def test_predict_requires_repository(client):
    response = client.post(
        "/api/predict",
        json={
            "commit": "d8eaaba8",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Missing 'repository'."


def test_predict_requires_commit(client):
    response = client.post(
        "/api/predict",
        json={
            "repository": "data/real_repos/flask",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Missing 'commit'."


def test_predict_rejects_missing_repository(client):
    response = client.post(
        "/api/predict",
        json={
            "repository": "data/real_repos/does_not_exist",
            "commit": "d8eaaba8",
        },
    )

    assert response.status_code == 404

    data = response.get_json()

    assert "Repository not found" in data["error"]


def test_predict_endpoint(client):
    response = client.post(
        "/api/predict",
        json={
            "repository": "data/real_repos/flask",
            "commit": "d8eaaba8",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["commit"] == "d8eaaba8"
    assert len(data["old_commit"]) == 40

    assert data["changed_files"]
    assert data["predictions"]

    assert data["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert 0 <= data["risk_probability"] <= 1

    assert data["feature_importance"]