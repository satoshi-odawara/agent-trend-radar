# agent-trend-radar
”ソフトウェア開発におけるAIエージェント活用ノウハウ"として、AIエージェントツールが実際のソフトウェア開発で「どう使われているか」を、公開リポジトリの実態から定量的にサーベイし、OSSとして公開するプロジェクト。
単なる人気度(stars等)ではなく、品質・セキュリティ・運用の実践知がどう現れているかをエビデンスとして示すことを狙う。

## セットアップ

```
uv sync
```

GitHub APIのレート制限緩和のため、`GITHUB_TOKEN`環境変数にpersonal access
tokenを設定することを推奨する(未設定でも動作するが、未認証のレート制限
にすぐ達する)。

CLAUDE.md/AGENTS.mdのLLMによるテーマ分類(Issue #15)には、Claude Code CLI
(`claude`コマンド、v2.1.259+)がインストール済みでログイン済みであること
が必要。Anthropic APIキー(`ANTHROPIC_API_KEY`)は不要で、Claude Code CLIの
サブスクリプション認証をそのまま利用する(追加のAPI課金は発生しない)。

## 実行方法

対象リポジトリ(`config/targets.yaml`、SPEC.md参照)に対しチェックを実行し、
SQLite(`data/repo_checks.db`)に結果を保存する。

```
uv run scripts/collect.py
```

保存された最新のチェック結果をMarkdown表として出力する。

```
uv run scripts/report.py > report.md
```

CSVで出力したい場合:

```
uv run scripts/report.py --format csv > report.csv
```
