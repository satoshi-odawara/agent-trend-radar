import json
import os
import sys


def load_manifest(path: str) -> dict:
    if not os.path.exists(path):
        return {"dates": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def add_date(manifest: dict, date: str) -> dict:
    """manifestにdateを追記する。既存日付との重複は追加しない(冪等性、Issue.md #24)。"""
    dates = set(manifest.get("dates", []))
    dates.add(date)
    manifest["dates"] = sorted(dates)
    return manifest


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 3:
        print(
            "usage: uv run scripts/update_hub_manifest.py <manifest_path> <YYYY-MM-DD>",
            file=sys.stderr,
        )
        raise SystemExit(1)
    manifest_path, date = sys.argv[1], sys.argv[2]

    manifest = add_date(load_manifest(manifest_path), date)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"{manifest_path} を更新しました(dates: {len(manifest['dates'])}件)。")


if __name__ == "__main__":
    main()
