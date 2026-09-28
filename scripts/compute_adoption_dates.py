import os
import sys

from agent_trend_radar import adoption_dates, config
from agent_trend_radar.github_client import GitHubClient

OUTPUT_PATH = "data/latest/adoption_dates.md"


def run(client: GitHubClient, targets: list[dict], cache: dict) -> dict:
    """全対象リポジトリ分のキャッシュを更新して返す(差分キャッシュ、#40)。"""
    total = len(targets)
    for i, target in enumerate(targets, start=1):
        repo = target["repo"]
        print(f"[{i}/{total}] {repo} ...")
        adoption_dates.update_cache_for_repo(client, repo, cache)
        print(f"[{i}/{total}] {repo}: done")
    return cache


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    targets = config.load_targets()
    client = GitHubClient()

    cache = adoption_dates.load_cache()
    cache = run(client, targets, cache)
    adoption_dates.save_cache(cache)

    report = adoption_dates.build_report(targets, cache)
    dirname = os.path.dirname(OUTPUT_PATH)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"{OUTPUT_PATH} に出力しました({len(targets)}リポジトリ分)。")


if __name__ == "__main__":
    main()
