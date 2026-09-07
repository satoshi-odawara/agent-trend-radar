import base64
import os
import time

import requests

GITHUB_API_BASE = "https://api.github.com"


class GitHubClientError(Exception):
    pass


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._token = token if token is not None else os.environ.get("GITHUB_TOKEN")
        self._session = session or requests.Session()

    def path_exists(self, repo: str, path: str) -> bool:
        response = self._get_contents(repo, path)
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        raise GitHubClientError(
            f"GitHub APIエラー: {repo}/{path} -> {response.status_code}"
        )

    def get_file_content(self, repo: str, path: str) -> str | None:
        response = self._get_contents(repo, path)
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise GitHubClientError(
                f"GitHub APIエラー: {repo}/{path} -> {response.status_code}"
            )
        data = response.json()
        if data.get("encoding") != "base64":
            raise GitHubClientError(
                f"想定外のencoding: {data.get('encoding')} ({repo}/{path})"
            )
        return base64.b64decode(data["content"]).decode("utf-8")

    def get_directory_names(self, repo: str) -> set[str]:
        """リポジトリ全体(任意の深さ)に存在するディレクトリ名(basename)の集合を返す。

        Git Trees APIのrecursive=1を使い1リクエストで全深度を取得する。
        モノレポ構成でルート直下に対象ディレクトリがないケースを検知するため
        (#14参照)。
        """
        owner, name = repo.split("/", 1)
        url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/git/trees/HEAD?recursive=1"
        response = self._request(url)
        if response.status_code != 200:
            raise GitHubClientError(
                f"GitHub APIエラー: {repo}のツリー取得 -> {response.status_code}"
            )
        data = response.json()
        return {
            entry["path"].rsplit("/", 1)[-1]
            for entry in data.get("tree", [])
            if entry.get("type") == "tree"
        }

    def _get_contents(self, repo: str, path: str) -> requests.Response:
        owner, name = repo.split("/", 1)
        url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/contents/{path}"
        return self._request(url)

    def _request(self, url: str) -> requests.Response:
        response = self._session.get(url, headers=self._headers())
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset_at = int(response.headers.get("X-RateLimit-Reset", "0"))
            wait_seconds = max(int(reset_at - time.time()), 0)
            raise GitHubClientError(
                f"GitHub APIのレート制限に達しました。約{wait_seconds}秒後にリセットされます。"
            )
        return response

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers
