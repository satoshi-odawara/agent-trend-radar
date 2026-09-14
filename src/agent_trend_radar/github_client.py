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
        self._tree_cache: dict[str, list[dict]] = {}

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

        モノレポ構成でルート直下に対象ディレクトリがないケースを検知するため
        (#14参照)。
        """
        return {
            entry["path"].rsplit("/", 1)[-1]
            for entry in self._get_tree_entries(repo)
            if entry.get("type") == "tree"
        }

    def get_file_paths(self, repo: str) -> set[str]:
        """リポジトリ全体(任意の深さ)に存在するファイルパス(リポジトリルートからの相対パス)の集合を返す。"""
        return {
            entry["path"]
            for entry in self._get_tree_entries(repo)
            if entry.get("type") == "blob"
        }

    def get_symlink_target(self, repo: str, path: str) -> str | None:
        """pathがシンボリックリンクの場合、そのリンク先(生のtargetテキスト)を返す。

        シンボリックリンクでない場合・存在しない場合はNoneを返す。
        `.claude/skills`自体がシンボリックリンク(共有先ディレクトリへの
        リンク)になっているケース(getsentry/sentry等)を解決するため
        (#21フォローアップ)。
        """
        response = self._get_contents(repo, path)
        if response.status_code != 200:
            return None
        data = response.json()
        if not isinstance(data, dict) or data.get("type") != "symlink":
            return None
        return data.get("target")

    def list_immediate_children(self, repo: str, dir_path: str) -> set[str]:
        """dir_path直下の子要素のbasename集合を返す(ディレクトリ・ファイル・
        シンボリックリンクいずれも対象)。

        Skillの実体が`.claude/skills/<name>/SKILL.md`ではなく、共有先への
        シンボリックリンク`.claude/skills/<name>`として置かれているケース
        (cline/cline等)があるため、ファイル種別を問わず直下の子要素数を
        数える(#21)。
        """
        prefix = f"{dir_path}/"
        children = set()
        for entry in self._get_tree_entries(repo):
            path = entry["path"]
            if path.startswith(prefix):
                children.add(path[len(prefix):].split("/", 1)[0])
        return children

    def _get_tree_entries(self, repo: str) -> list[dict]:
        """Git Trees APIのrecursive=1を1リクエストで取得し、リポジトリ単位でキャッシュする。

        get_directory_names/get_file_pathsが同一repoに対して個別にAPIを
        叩くと収集全体のAPI呼び出し数が増えるため(#21で新設)、キャッシュ
        して1リポジトリ1回に抑える。
        """
        if repo not in self._tree_cache:
            owner, name = repo.split("/", 1)
            url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/git/trees/HEAD?recursive=1"
            response = self._request(url)
            if response.status_code != 200:
                raise GitHubClientError(
                    f"GitHub APIエラー: {repo}のツリー取得 -> {response.status_code}"
                )
            self._tree_cache[repo] = response.json().get("tree", [])
        return self._tree_cache[repo]

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
