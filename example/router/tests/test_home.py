from httpx import Client


def test_home(client: Client) -> None:
    response = client.get("/home/")

    assert response.status_code == 200
    assert response.text == "Home"
