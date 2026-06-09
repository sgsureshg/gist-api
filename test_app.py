
import app
from unittest.mock import patch, MagicMock


def client():
    app.app.config["TESTING"] = True
    return app.app.test_client()


def test_health():
    c = client()
    res = c.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_user_route_live():
    c = client()
    res = c.get("/octocat")
    assert res.status_code in [200, 429, 502, 503, 504]


def test_user_returns_list_of_gists():
    mock_gists = [
        {
            "id": "abc123",
            "description": "Test gist",
            "html_url": "https://gist.github.com/octocat/abc123",
            "files": {"hello.py": {}},
            "created_at": "2010-04-14T02:15:15Z",
            "updated_at": "2010-04-14T02:15:15Z",
        }
    ]
    with patch("app.get_session") as m:
        m.return_value.get.return_value = MagicMock(
            status_code=200, ok=True, json=lambda: mock_gists
        )
        res = client().get("/octocat")

    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
    assert res.get_json()[0]["id"] == "abc123"


def test_unknown_user_returns_404():
    with patch("app.get_session") as m:
        m.return_value.get.return_value = MagicMock(status_code=404, ok=False)
        res = client().get("/no_such_user_xyz")
    assert res.status_code == 404