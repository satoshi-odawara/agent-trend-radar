import base64
import logging

import pytest
import requests

from agent_trend_radar import github_client as github_client_module
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
    """URLごとに応答(または例外)を返すフェイク。

    値は単一の`FakeResponse`/`Exception`、またはそのリスト(呼び出しの
    たびに先頭から消費し、1件になったら以降は同じものを返し続ける)を
    受け付ける。リトライ挙動のテスト(#11)で、1回目は失敗・2回目は成功
    といったシーケンスを表現するために使う。
    """

    def __init__(self, responses):
        self._responses = {
            url: (list(value) if isinstance(value, list) else [value])
            for url, value in responses.items()
        }
        self.last_headers = None
        self.last_timeout = None
        self._call_counts: dict[str, int] = {}

    def get(self, url, headers=None, timeout=None):
        self.last_headers = headers
        self.last_timeout = timeout
        self._call_counts[url] = self._call_counts.get(url, 0) + 1
        queue = self._responses[url]
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        return item

    def call_count(self, url):
        return self._call_counts.get(url, 0)


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
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

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


def test_request_passes_timeout():
    session = FakeSession({CONTENTS_URL: FakeResponse(200, json_data={"type": "file"})})
    client = GitHubClient(token="dummy", session=session)

    client.path_exists("owner/repo", "CLAUDE.md")

    assert session.last_timeout == github_client_module.DEFAULT_TIMEOUT_SECONDS


def test_request_retries_on_network_error_then_succeeds():
    session = FakeSession(
        {CONTENTS_URL: [requests.exceptions.ConnectionError("boom"), FakeResponse(200, json_data={"type": "file"})]}
    )
    sleeps = []
    client = GitHubClient(token="dummy", session=session, sleep=sleeps.append)

    assert client.path_exists("owner/repo", "CLAUDE.md") is True
    assert session.call_count(CONTENTS_URL) == 2
    assert sleeps == [1]


def test_request_raises_after_exhausting_retries_on_network_error():
    session = FakeSession({CONTENTS_URL: [requests.exceptions.ConnectionError("boom")] * 10})
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

    with pytest.raises(GitHubClientError, match="接続"):
        client.path_exists("owner/repo", "CLAUDE.md")


def test_request_retries_on_5xx_then_succeeds():
    session = FakeSession({CONTENTS_URL: [FakeResponse(502), FakeResponse(200, json_data={"type": "file"})]})
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

    assert client.path_exists("owner/repo", "CLAUDE.md") is True


def test_request_does_not_retry_404():
    session = FakeSession({CONTENTS_URL: [FakeResponse(404), FakeResponse(200, json_data={"type": "file"})]})
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

    assert client.path_exists("owner/repo", "CLAUDE.md") is False
    assert session.call_count(CONTENTS_URL) == 1


def test_request_does_not_retry_primary_rate_limit():
    response = FakeResponse(
        403,
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "9999999999"},
    )
    session = FakeSession({CONTENTS_URL: response})
    sleeps = []
    client = GitHubClient(token="dummy", session=session, sleep=sleeps.append)

    with pytest.raises(GitHubClientError, match="レート制限"):
        client.path_exists("owner/repo", "CLAUDE.md")
    assert sleeps == []
    assert session.call_count(CONTENTS_URL) == 1


def test_request_retries_on_secondary_rate_limit_then_succeeds():
    secondary = FakeResponse(403, headers={"Retry-After": "2"})
    session = FakeSession({CONTENTS_URL: [secondary, FakeResponse(200, json_data={"type": "file"})]})
    sleeps = []
    client = GitHubClient(token="dummy", session=session, sleep=sleeps.append)

    assert client.path_exists("owner/repo", "CLAUDE.md") is True
    assert sleeps == [2]


def test_request_raises_after_exhausting_secondary_rate_limit_retries():
    secondary = FakeResponse(429, headers={"Retry-After": "1"})
    session = FakeSession({CONTENTS_URL: [secondary] * 10})
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

    with pytest.raises(GitHubClientError, match="二次レート制限"):
        client.path_exists("owner/repo", "CLAUDE.md")


def test_secondary_rate_limit_wait_is_capped():
    secondary = FakeResponse(429, headers={"Retry-After": "99999"})
    session = FakeSession({CONTENTS_URL: [secondary, FakeResponse(200, json_data={"type": "file"})]})
    sleeps = []
    client = GitHubClient(token="dummy", session=session, sleep=sleeps.append)

    client.path_exists("owner/repo", "CLAUDE.md")

    assert sleeps == [github_client_module.MAX_SECONDARY_RATE_LIMIT_WAIT_SECONDS]


def test_get_first_commit_date_single_call_when_no_link_header():
    """コミット数が1件のみ(Linkヘッダーが無い)場合は1コールで完了する(#40)。"""
    url = (
        "https://api.github.com/repos/owner/repo/commits?path=.mcp.json&per_page=1"
    )
    session = FakeSession(
        {
            url: FakeResponse(
                200,
                json_data=[{"commit": {"author": {"date": "2026-05-14T20:06:37Z"}}}],
            )
        }
    )
    client = GitHubClient(token="dummy", session=session)

    date = client.get_first_commit_date("owner/repo", ".mcp.json")

    assert date == "2026-05-14T20:06:37Z"
    assert session.call_count(url) == 1


def test_get_first_commit_date_none_when_path_never_committed():
    url = (
        "https://api.github.com/repos/owner/repo/commits?path=.mcp.json&per_page=1"
    )
    session = FakeSession({url: FakeResponse(200, json_data=[])})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_first_commit_date("owner/repo", ".mcp.json") is None
    assert session.call_count(url) == 1


def test_get_first_commit_date_fetches_last_page_when_multiple_commits():
    """複数コミットがある場合は、Linkヘッダーのrel="last"から最終ページを
    取得し、そこに含まれる最古のコミットの日付を返す(#40、#33で検証済みの設計)。"""
    first_url = (
        "https://api.github.com/repos/owner/repo/commits?path=.claude%2Fskills&per_page=1"
    )
    last_url = (
        "https://api.github.com/repos/owner/repo/commits"
        "?path=.claude%2Fskills&per_page=1&page=6"
    )
    session = FakeSession(
        {
            first_url: FakeResponse(
                200,
                json_data=[{"commit": {"author": {"date": "2026-09-25T20:21:38Z"}}}],
                headers={
                    "Link": (
                        '<https://api.github.com/repositories/1/commits?path=.claude%2Fskills'
                        '&per_page=1&page=2>; rel="next", '
                        '<https://api.github.com/repositories/1/commits?path=.claude%2Fskills'
                        '&per_page=1&page=6>; rel="last"'
                    )
                },
            ),
            last_url: FakeResponse(
                200,
                json_data=[{"commit": {"author": {"date": "2026-05-14T20:06:37Z"}}}],
            ),
        }
    )
    client = GitHubClient(token="dummy", session=session)

    date = client.get_first_commit_date("owner/repo", ".claude/skills")

    assert date == "2026-05-14T20:06:37Z"
    assert session.call_count(first_url) == 1
    assert session.call_count(last_url) == 1


def test_get_first_commit_date_raises_on_unexpected_status():
    url = "https://api.github.com/repos/owner/repo/commits?path=.mcp.json&per_page=1"
    session = FakeSession({url: FakeResponse(500)})
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

    with pytest.raises(GitHubClientError):
        client.get_first_commit_date("owner/repo", ".mcp.json")


def test_request_logs_warning_on_each_retry(caplog):
    session = FakeSession(
        {CONTENTS_URL: [requests.exceptions.ConnectionError("boom"), FakeResponse(200, json_data={"type": "file"})]}
    )
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

    with caplog.at_level(logging.WARNING):
        client.path_exists("owner/repo", "CLAUDE.md")

    assert "boom" in caplog.text


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
    client = GitHubClient(token="dummy", session=session, sleep=lambda seconds: None)

    with pytest.raises(GitHubClientError):
        client.get_directory_names("owner/repo")


def test_get_file_paths_returns_blob_paths_only():
    tree = {
        "tree": [
            {"path": ".claude", "type": "tree"},
            {"path": ".claude/skills", "type": "tree"},
            {"path": ".claude/skills/foo/SKILL.md", "type": "blob"},
        ]
    }
    session = FakeSession({TREE_URL: FakeResponse(200, json_data=tree)})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_file_paths("owner/repo") == {".claude/skills/foo/SKILL.md"}


def test_get_symlink_target_returns_target_for_symlink():
    url = "https://api.github.com/repos/owner/repo/contents/.claude/skills"
    session = FakeSession(
        {url: FakeResponse(200, json_data={"type": "symlink", "target": "../.agents/skills"})}
    )
    client = GitHubClient(token="dummy", session=session)

    assert client.get_symlink_target("owner/repo", ".claude/skills") == "../.agents/skills"


def test_get_symlink_target_returns_none_for_regular_directory():
    url = "https://api.github.com/repos/owner/repo/contents/.claude/skills"
    session = FakeSession({url: FakeResponse(200, json_data=[{"type": "dir", "name": "foo"}])})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_symlink_target("owner/repo", ".claude/skills") is None


def test_get_symlink_target_returns_none_when_missing():
    url = "https://api.github.com/repos/owner/repo/contents/.claude/skills"
    session = FakeSession({url: FakeResponse(404)})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_symlink_target("owner/repo", ".claude/skills") is None


def test_list_immediate_children_includes_symlinks_and_dirs():
    tree = {
        "tree": [
            {"path": ".claude/skills", "type": "tree"},
            {"path": ".claude/skills/foo", "type": "tree"},
            {"path": ".claude/skills/foo/SKILL.md", "type": "blob"},
            {"path": ".claude/skills/bar", "type": "blob"},  # symlink(mode 120000)
        ]
    }
    session = FakeSession({TREE_URL: FakeResponse(200, json_data=tree)})
    client = GitHubClient(token="dummy", session=session)

    assert client.list_immediate_children("owner/repo", ".claude/skills") == {"foo", "bar"}


def test_list_immediate_children_empty_when_dir_missing():
    session = FakeSession({TREE_URL: FakeResponse(200, json_data={"tree": []})})
    client = GitHubClient(token="dummy", session=session)

    assert client.list_immediate_children("owner/repo", ".claude/skills") == set()


def test_get_file_sha_returns_blob_sha_for_existing_path():
    tree = {
        "tree": [
            {"path": "CLAUDE.md", "type": "blob", "sha": "abc123"},
            {"path": "AGENTS.md", "type": "blob", "sha": "def456"},
        ]
    }
    session = FakeSession({TREE_URL: FakeResponse(200, json_data=tree)})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_file_sha("owner/repo", "CLAUDE.md") == "abc123"


def test_get_file_sha_returns_none_for_missing_path():
    tree = {"tree": [{"path": "CLAUDE.md", "type": "blob", "sha": "abc123"}]}
    session = FakeSession({TREE_URL: FakeResponse(200, json_data=tree)})
    client = GitHubClient(token="dummy", session=session)

    assert client.get_file_sha("owner/repo", "AGENTS.md") is None


def test_get_file_sha_reuses_cached_tree_no_extra_request():
    tree = {"tree": [{"path": "CLAUDE.md", "type": "blob", "sha": "abc123"}]}
    session = FakeSession({TREE_URL: FakeResponse(200, json_data=tree)})
    client = GitHubClient(token="dummy", session=session)

    client.get_file_paths("owner/repo")
    client.get_file_sha("owner/repo", "CLAUDE.md")

    assert session.call_count(TREE_URL) == 1


def test_tree_entries_are_cached_per_repo():
    """get_directory_names/get_file_pathsを同じrepoに対して呼んでも、
    Git Trees APIへのリクエストは1回に抑えられる(#21、API呼び出し数の抑制)。"""
    tree = {"tree": [{"path": "tests", "type": "tree"}]}
    session = FakeSession({TREE_URL: FakeResponse(200, json_data=tree)})
    client = GitHubClient(token="dummy", session=session)

    client.get_directory_names("owner/repo")
    client.get_file_paths("owner/repo")

    assert session.call_count(TREE_URL) == 1


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
