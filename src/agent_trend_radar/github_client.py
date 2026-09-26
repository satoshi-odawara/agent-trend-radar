import base64
import logging
import os
import time
from typing import Callable

import requests

GITHUB_API_BASE = "https://api.github.com"

# #11: タイムアウト・リトライ関連の設定値。リトライ対象はネットワーク
# エラー・5xx・二次レート制限(乱用防止)のみで、404等のリトライ不可能な
# エラーや一次レート制限(reset待ちがhttp相当で長い)は対象外。
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3
MAX_SECONDARY_RATE_LIMIT_WAIT_SECONDS = 60

logger = logging.getLogger(__name__)


class GitHubClientError(Exception):
    pass


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._token = token if token is not None else os.environ.get("GITHUB_TOKEN")
        self._session = session or requests.Session()
        self._tree_cache: dict[str, list[dict]] = {}
        self._sleep = sleep

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

    def get_file_sha(self, repo: str, path: str) -> str | None:
        """キャッシュ済みTreeエントリから指定パスのblob SHAを返す。存在しなければNone。

        Git Trees APIのレスポンスには元々各エントリのblob SHAが含まれており、
        `_get_tree_entries`で既にキャッシュ済みのため、新規API呼び出しは
        発生しない(#30、LLM分類の入力キャッシュキー算出に使う)。
        """
        for entry in self._get_tree_entries(repo):
            if entry.get("type") == "blob" and entry.get("path") == path:
                return entry.get("sha")
        return None

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
        attempt = 0
        while True:
            try:
                response = self._session.get(
                    url, headers=self._headers(), timeout=DEFAULT_TIMEOUT_SECONDS
                )
            except requests.exceptions.RequestException as exc:
                if attempt >= DEFAULT_MAX_RETRIES:
                    raise GitHubClientError(f"GitHub APIへの接続に失敗しました: {exc}") from exc
                logger.warning(
                    "GitHub APIへの接続エラー(リトライ%d/%d): %s: %s",
                    attempt + 1,
                    DEFAULT_MAX_RETRIES,
                    url,
                    exc,
                )
                self._sleep(2**attempt)
                attempt += 1
                continue

            if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
                reset_at = int(response.headers.get("X-RateLimit-Reset", "0"))
                wait_seconds = max(int(reset_at - time.time()), 0)
                raise GitHubClientError(
                    f"GitHub APIのレート制限に達しました。約{wait_seconds}秒後にリセットされます。"
                )

            if self._is_secondary_rate_limited(response):
                if attempt >= DEFAULT_MAX_RETRIES:
                    raise GitHubClientError(
                        "GitHub APIの二次レート制限(乱用防止)に達しました。リトライしても解消しませんでした。"
                    )
                retry_after = min(
                    int(response.headers.get("Retry-After", "1")),
                    MAX_SECONDARY_RATE_LIMIT_WAIT_SECONDS,
                )
                logger.warning(
                    "GitHub APIの二次レート制限を検知(リトライ%d/%d、%d秒待機): %s",
                    attempt + 1,
                    DEFAULT_MAX_RETRIES,
                    retry_after,
                    url,
                )
                self._sleep(retry_after)
                attempt += 1
                continue

            if response.status_code >= 500:
                if attempt >= DEFAULT_MAX_RETRIES:
                    return response
                logger.warning(
                    "GitHub APIサーバーエラー(リトライ%d/%d): %s -> %d",
                    attempt + 1,
                    DEFAULT_MAX_RETRIES,
                    url,
                    response.status_code,
                )
                self._sleep(2**attempt)
                attempt += 1
                continue

            return response

    @staticmethod
    def _is_secondary_rate_limited(response: requests.Response) -> bool:
        """GitHubの二次レート制限(乱用防止)を検知する。

        一次レート制限(`X-RateLimit-Remaining: 0`)とは別に、短時間の
        バースト等で403/429が返り`Retry-After`ヘッダーが付くケース
        (公式ドキュメントで案内されている挙動)。
        """
        return response.status_code in (403, 429) and "Retry-After" in response.headers

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers
