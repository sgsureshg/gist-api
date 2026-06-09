import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class GistAPIError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

    def user_message(self):
        return str(self)


def get_session():
    session = requests.Session()
    session.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    if GITHUB_TOKEN:
        session.headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return session


def fetch_public_gists(username: str):
    session = get_session()
    url = f"{GITHUB_API_BASE}/users/{username}/gists"

    try:
        response = session.get(url, timeout=10)
    except requests.ConnectionError:
        raise GistAPIError("Service unavailable", 503)
    except requests.Timeout:
        raise GistAPIError("Timeout", 504)

    if response.status_code == 404:
        raise GistAPIError("Not found", 404)
    if response.status_code == 403:
        raise GistAPIError("Rate limited", 429)
    if not response.ok:
        raise GistAPIError("GitHub error", 502)

    return [
        {
            "id": g["id"],
            "description": g["description"] or "",
            "url": g["html_url"],
            "files": list(g["files"].keys()),
            "created_at": g["created_at"],
            "updated_at": g["updated_at"],
        }
        for g in response.json()
    ]


@app.route("/<username>")
def user_gists(username):
    try:
        return jsonify(fetch_public_gists(username))
    except GistAPIError as e:
        return jsonify({"error": str(e)}), e.status_code


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)