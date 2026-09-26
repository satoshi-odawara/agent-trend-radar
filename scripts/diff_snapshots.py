import argparse
import json
import os
import sys

from agent_trend_radar.llm_content_analysis import CLASSIFICATION_FIELDS

CACHE_KEY_FIELD = "agent_doc_llm_cache_key"
DEFAULT_SNAPSHOTS_DIR = "../agent-trend-data/snapshots"
DEFAULT_OUTPUT_PATH = "data/latest/changes.md"


def list_snapshot_dates(snapshots_dir: str) -> list[str]:
    """snapshots_dir直下の日付ディレクトリ名を昇順で返す(存在しなければ空リスト)。"""
    if not os.path.isdir(snapshots_dir):
        return []
    return sorted(
        name
        for name in os.listdir(snapshots_dir)
        if os.path.isdir(os.path.join(snapshots_dir, name))
    )


def select_latest_two_dates(dates: list[str]) -> tuple[str, str] | None:
    """日付を新しい順に2つ選び(古い方, 新しい方)で返す。2件未満ならNone。"""
    if len(dates) < 2:
        return None
    ordered = sorted(dates)
    return ordered[-2], ordered[-1]


def load_snapshot(snapshots_dir: str, date: str) -> dict:
    path = os.path.join(snapshots_dir, date, "metrics.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def diff_snapshots(old: dict, new: dict) -> list[dict]:
    """2つのスナップショット(metrics.json相当の辞書)を比較し、値が変化した
    `repo`×`項目`の一覧を`repo`昇順・`field`昇順で返す。

    LLM分類4項目(#15)は、`agent_doc_llm_cache_key`(#30)が両スナップ
    ショットに存在し値が同じ場合、実際の文書変更ではなく#25の2bで判明した
    LLMの非決定性による変化とみなし除外する。cache keyがどちらかに
    存在しない場合(#30より前のスナップショット同士の比較等)は、判別する
    手段が無いためLLM4項目を無条件で除外する(フォールバック)。
    """
    old_repos = {row["repo"]: row for row in old.get("repos", [])}
    new_repos = {row["repo"]: row for row in new.get("repos", [])}

    changes = []
    for repo in sorted(set(old_repos) & set(new_repos)):
        old_row = old_repos[repo]
        new_row = new_repos[repo]
        cache_key_available = CACHE_KEY_FIELD in old_row and CACHE_KEY_FIELD in new_row
        cache_key_unchanged = (
            cache_key_available and old_row[CACHE_KEY_FIELD] == new_row[CACHE_KEY_FIELD]
        )

        for field in sorted(set(old_row) & set(new_row)):
            if field in ("repo", CACHE_KEY_FIELD):
                continue
            if old_row[field] == new_row[field]:
                continue
            if field in CLASSIFICATION_FIELDS:
                if not cache_key_available or cache_key_unchanged:
                    continue
            changes.append(
                {
                    "repo": repo,
                    "field": field,
                    "old_value": old_row[field],
                    "new_value": new_row[field],
                }
            )
    return changes


def format_changes_markdown(old_date: str, new_date: str, changes: list[dict]) -> str:
    lines = [f"# スナップショット差分レポート({old_date} → {new_date})", ""]
    if not changes:
        lines.append("変化した項目はありませんでした。")
        return "\n".join(lines) + "\n"

    lines += ["| repo | 項目 | 旧値 | 新値 |", "| --- | --- | --- | --- |"]
    for change in changes:
        lines.append(
            f"| {change['repo']} | {change['field']} | {change['old_value']} | {change['new_value']} |"
        )
    return "\n".join(lines) + "\n"


def build_report(snapshots_dir: str) -> tuple[str, str, list[dict], str] | None:
    """直近2回のスナップショットから(旧日付, 新日付, 変化一覧, Markdown本文)を
    組み立てる。比較可能なスナップショットが2件未満ならNone。"""
    dates = list_snapshot_dates(snapshots_dir)
    selected = select_latest_two_dates(dates)
    if selected is None:
        return None

    old_date, new_date = selected
    old = load_snapshot(snapshots_dir, old_date)
    new = load_snapshot(snapshots_dir, new_date)
    changes = diff_snapshots(old, new)
    markdown = format_changes_markdown(old_date, new_date, changes)
    return old_date, new_date, changes, markdown


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="hubのスナップショット直近2回を比較し、変化した項目をMarkdownで出力する"
    )
    parser.add_argument("snapshots_dir", nargs="?", default=DEFAULT_SNAPSHOTS_DIR)
    parser.add_argument("output_path", nargs="?", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    result = build_report(args.snapshots_dir)
    if result is None:
        dates = list_snapshot_dates(args.snapshots_dir)
        print(
            f"比較可能なスナップショットが2件未満です({len(dates)}件)。"
            "差分レポートは生成しません。"
        )
        return

    old_date, new_date, changes, markdown = result
    dirname = os.path.dirname(args.output_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"{args.output_path} に出力しました({len(changes)}件の変化、{old_date} → {new_date})。")


if __name__ == "__main__":
    main()
