import base64

import pytest

from agent_trend_radar.github_client import GitHubClient, GitHubClientError

CONTENTS_URL = "https://api.github.com/repos/owner/repo/contents/CLAUDE.md"
TREE_URL = "https://api.github.com/repos/owner/repo/git/trees/HEAD?recursive=1"


class FakeResponse:
    def __init__(self, status_code, json_data=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.headers = headers or {}

    def json(self):
        return self._json_data


class FakeSession:
    def __init__(self, responses):
        self._responses = responses
        self.last_headers = None

    def get(self, url, headers=None):
        self.last_headers = headers
        return self._responses[url]


def test_path_exists_true_for_existing_path():
    session = FakeSession({CONTENTS_URL: FakeResponse(200, json_data={"type": "file"})})
    client = GitHubClient(token="dummy", session=session)

    assert client.path_exists("owner/repo", "CLAUDE.md") is True


def test_path_exists_false_for_missing_path():
    session = FakeSession({CONTENTS_URL: FakeResponse(404)})
    client = GitHubClient(token="dummy", session=session)

    assert client.path_exists("owner/repo", "CLAUDE.md") is False


def test_path_exists_raises_on_unexpected_status():
    session = FakeSession({CONTENTS_URL: FakeResponse(500)})
    client = GitHubClient(token="dummy", session=session)

    with pytest.raises(GitHubClientError):
        client.path_exists("owner/repo", "CLAUDE.md")


def test_path_exists_raises_clear_error_on_rate_limit():
    response = FakeResponse(
        403,
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "9999999999"},
    )
    session = FakeSession({CONTENTS_URL: response})
    client = GitHubClient(token="dummy", session=session)

    with pytest.raises(GitHubClientError, match="レート制限"):
        client.path_exists("owner/repo", "CLAUDE.md")


def test_get_file_content_decodes_base64():
    content = "dependencies = []"
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    session = FakeSession(
        {CONTENTS_URL: FakeResponse(200, json_data={"encoding": "base64", "content": encoded})}
    )
    client = GitHubClient(token="dummy", session=session)

    assert client.get_file_content("owner/repo", "CLAUDE.md") == content


def test_get_file_content_returns_none_when_missing():
    session = FakeSession({CONTENTS_URL: FakeResponse(404)})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_file_content("owner/repo", "CLAUDE.md") is None


def test_get_directory_names_returns_basenames_at_any_depth():
    tree = {
        "tree": [
            {"path": "libs", "type": "tree"},
            {"path": "libs/core", "type": "tree"},
            {"path": "libs/core/tests", "type": "tree"},
            {"path": "libs/core/tests/test_foo.py", "type": "blob"},
        ]
    }
    session = FakeSession({TREE_URL: FakeResponse(200, json_data=tree)})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_directory_names("owner/repo") == {"libs", "core", "tests"}


def test_get_directory_names_raises_on_unexpected_status():
    session = FakeSession({TREE_URL: FakeResponse(500)})
    client = GitHubClient(token="dummy", session=session)

    with pytest.raises(GitHubClientError):
        client.get_directory_names("owner/repo")


def test_uses_token_from_env_var(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "env-token")
    session = FakeSession({CONTENTS_URL: FakeResponse(200)})
    client = GitHubClient(session=session)

    client.path_exists("owner/repo", "CLAUDE.md")

    assert session.last_headers["Authorization"] == "Bearer env-token"


def test_no_token_omits_authorization_header(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    session = FakeSession({CONTENTS_URL: FakeResponse(200)})
    client = GitHubClient(session=session)

    client.path_exists("owner/repo", "CLAUDE.md")

    assert "Authorization" not in session.last_headers
