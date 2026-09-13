import json
import os
import sys
from datetime import datetime, timezone

import report

from agent_trend_radar import storage


def build_snapshot(conn) -> dict:
    """agent-trend-data(ハブ)向けのJSONスナップショットを組み立てる。

    agent-trend-data/schema/SCHEMA.mdは2026-09-13時点でTBD(未確定)のため、
    正式スキーマが決まるまでの暫定措置として、report.pyの出力フォーマット
    (ALL_COLUMNS = repo/segment/monetization_model + CHECK_COLUMNS)を
    そのまま採用する(Issue.md #24参照)。
    """
    rows = report.fetch_latest_checks(conn)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repos": [dict(zip(report.ALL_COLUMNS, row)) for row in rows],
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print("usage: uv run scripts/export_hub_snapshot.py <output_path>", file=sys.stderr)
        raise SystemExit(1)
    output_path = sys.argv[1]

    conn = storage.connect()
    storage.ensure_schema(conn)
    snapshot = build_snapshot(conn)
    conn.close()

    dirname = os.path.dirname(output_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"{output_path} に書き出しました。")


if __name__ == "__main__":
    main()
