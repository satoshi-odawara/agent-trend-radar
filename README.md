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

segment×monetization_model別の統計(中央値・true率等)を見たい場合:

```
uv run scripts/report.py --format stats
```

## Claude Projectへのデータ公開(Issue #19, #22)

データからの考察はClaude Projectの専用チャットスペースで行う方針のため
(実装コンテキストの混入を避ける狙い、Issue.md #12参照)、考察に必要な
データを`data/latest/`に固定パスで生成する。

```
uv run scripts/publish.py
```

生成されるファイル:
- `data/latest/report.md`: リポジトリ×項目のマトリクス
- `data/latest/stats.md`: segment×monetization_model別の統計
- `data/latest/agent_docs/<owner>__<repo>.md`: 各リポジトリのCLAUDE.md/
  AGENTS.mdの生テキスト(要約・解釈はせず原文のまま。出典明記の抜粋転載
  として扱う)
- `data/latest/ANALYSIS_INSTRUCTIONS.md`: Claude Project側でこのデータ
  の有効性・妥当性を検証してもらうための指示書(手書きの静的ファイルで
  `publish.py`の再実行では上書きされない)。Claude Projectのカスタム
  指示または最初のメッセージとして使う想定

`data/latest/`はコミット対象(`.gitignore`対象外)。リポジトリは非公開の
ままでよい。Claude Project側でこのリポジトリをGitHub連携し、
「Configure files」機能で同期対象を`data/latest/`だけに絞り込むことで、
`src/`/`tests/`等の実装コードをProjectに混入させずにデータだけを参照
できる(コミット履歴・PR等のメタデータは連携でも同期されない)。

## agent-trend-dataへの連携(Issue #24)

記事作成システムがデータを参照できるよう、収集結果を別リポジトリ
`agent-trend-data`(ハブ)へ反映する。Fine-grained PATの発行に時間が
かかるため、当面はローカル実行のPowerShellスクリプトで連携し、
GitHub Actions経由の自動化はPAT発行後に切り替える(下記参照)。

### 現在の運用: ローカルスクリプトによる連携

`agent-trend-data`が`agent-trend-radar`と同階層の兄弟ディレクトリ
(`..\agent-trend-data`)にcloneされていることが前提。

```
.\sync_to_hub.ps1
```

このスクリプトが以下を一気通貫で行う:

1. `scripts/collect.py`で収集
2. `scripts/export_hub_snapshot.py`で収集結果をJSONスナップショットに変換
   (`agent-trend-data/schema/SCHEMA.md`は2026-09-13時点でTBDのため、
   スキーマ確定までの暫定措置として現状の収集結果フォーマットをそのまま
   採用している)
3. `..\agent-trend-data\snapshots\<実行日>\metrics.json`と
   `latest\metrics.json`を更新、`scripts/update_hub_manifest.py`で
   `manifest.json`に実行日を追記(重複追加なし)
4. 変更があれば`agent-trend-data`側でコミット・push
   (`data: <実行日> snapshot`)

収集(`collect.py`)が失敗した場合、スクリプトはそこで停止し、後続の
ハブへのコピー・push は行われない。ハブへのpushがコンフリクト等で
失敗した場合はエラーで停止する(自動リトライはしない)。

### 将来の運用: GitHub Actionsによる自動化(未使用、PAT発行後に有効化)

`.github/workflows/collect-and-publish.yml`に、週次(毎週月曜
00:00 UTC)/手動実行(`workflow_dispatch`)でCI上から直接
`agent-trend-data`へpushする定義を用意済みだが、Fine-grained PAT
未発行のため現時点では実行しても失敗する(Secrets未設定)。有効化する
場合、以下のリポジトリSecretsが必要:

- `CLAUDE_CODE_OAUTH_TOKEN`: `claude setup-token`で発行するサブスク
  リプション認証トークン(`scripts/collect.py`内のLLMテーマ分類が
  `claude` CLIを使うため。追加のAPI課金は発生しない)
- `HUB_REPO_PAT`: `agent-trend-data`リポジトリのみに限定した
  Fine-grained PAT(権限は`Contents: Read and write`のみ)。デフォルトの
  `GITHUB_TOKEN`は実行元リポジトリにしかアクセス権を持たず、別リポジトリ
  への書き込みができないため必要(`agent-trend-data`のCLAUDE.mdもこの
  前提で設計されている)
