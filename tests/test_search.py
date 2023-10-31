from time import sleep

from starlette.testclient import TestClient

from main import app


def test_limiter():
    with TestClient(app) as client:
        response = client.get("/search?query=John&status=active")
        assert response.status_code == 200

        response = client.get("/search?query=John&status=active")
        assert response.status_code == 200

        response = client.get("/search?query=John&status=active")
        assert response.status_code == 429

        response = client.get("/search?query=John&status=active")
        assert response.status_code == 429
        sleep(5)

        response = client.get("/search?query=John&status=active")
        assert response.status_code == 200

        response = client.get("/search?query=John&status=active")
        assert response.status_code == 200
