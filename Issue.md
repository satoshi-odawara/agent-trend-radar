# Issue.md

MVP完成までのタスクリスト。各項目はGitHub Issue化する単位を想定した粒度で
書いている。詳細方針は @Development_plan.md、仕様は @SPEC.md を参照。
起票時の書式ルールは下記「起票ルール」を参照。

---

## 起票ルール

Issueは「実装型」「調査・検討型」いずれかのテンプレートで書く。

**実装型**(変更対象ファイル・作業内容が着手前から明確なもの)

```
## #N タイトル

**概要**: 何をするかを1〜3文で。

**変更対象ファイル**
- path(新規/修正)

**タスク**
- [ ] 具体的な作業項目

**完了条件**: 検証可能な達成基準。

**依存**: #M または なし
```

**調査・検討型**(発見事項の整理・方針検討で、着手時にファイルが確定
しないもの)

```
## #N タイトル

**概要**: 何が問題/検討事項かを1〜3文で。

**タスク**
- [ ] 検討・調査項目(未確定なら「着手時に定義する」のみでもよい)

**完了条件**: 着手時に別途定義する、または具体的な基準。

**依存**: #M または なし
```

**共通ルール**
- 見出しは`## #N タイトル`。番号は必ず独立した見出しを持ち、他Issueの
  箇条書きの中に内容をネストしない。
- 作業項目の見出し名は常に「タスク」に統一する(「スコープ」「検討の
  方向性」「発見した注意点」等の別名は使わない)。発見事項の整理など
  タスクと性質が異なる補足セクションを追加すること自体は妨げない。
- ファイル内は`#N`の昇順に並べる。
- 完了・中止・廃止したIssueは、元のセクションを書き換えず末尾に追記
  する形でクローズ記録を残す。
  - 完了/対応済み: `**対応内容(YYYY-MM-DD)**: 何をした/しなかったか、
    結論。`
  - 中止: `**中止理由(YYYY-MM-DD)**: なぜ中止したか。` +
    `**後続対応**: 中止に伴う新規Issueや成果物の再利用方針(該当する
    場合)。`
- 「MVP後」の一覧は状態と一行ポインタのみのインデックスとし、詳細は
  各Issueの個別セクションに書く。

---

## #1 プロジェクト初期セットアップ

**概要**: `uv` ベースのPythonプロジェクトとして初期化する。

**変更対象ファイル**
- `pyproject.toml`(新規)
- `uv.lock`(新規)
- `.gitignore`(新規)
- `src/agent_trend_radar/__init__.py`(新規)

**タスク**
- [x] `uv init` でプロジェクト作成(Python 3.12+指定)
- [x] ディレクトリ構成を決める(例: `src/agent_trend_radar/`, `scripts/`)
- [x] `.gitignore` 追加(`*.db`, `.env`, `__pycache__/` 等)
- [x] `pyproject.toml` に必要最低限の依存を追加(HTTPクライアント等)
- [x] `uv.lock` をコミット

**完了条件**: `uv run python -c "print('ok')"` が通る状態でコミットされて
いる。

**依存**: なし

---

## #2 対象リポジトリリストの確定

**概要**: SPEC.mdの対象リポジトリ表(TBD)を埋め、10〜20個を確定する。

**変更対象ファイル**
- `SPEC.md`(対象リポジトリ表を更新)
- `config/targets.yaml`(新規)

**タスク**
- [x] SPEC.mdの選定基準(スター数/開始日/収益化モデル)に沿って候補を洗い出す
- [x] 収益化モデル(commercial_saas/big_corp_internal/nonprofit_foundation/
      individual_community)の構成バランスを確認
- [x] SPEC.mdの表を更新(owner/repo, segment, 収益化モデル, 備考)
- [x] 対象リポジトリを設定ファイル化(例: `config/targets.yaml` or `.json`)

**完了条件**: SPEC.mdの表が埋まっており、同じリストがスクリプトから読み込
める形式でリポジトリ内に存在する。

**依存**: なし(ユーザーの手動判断が必要)

---

## #3 GitHub APIクライアント実装

**概要**: 認証付きでGitHub REST APIを叩き、指定パスの存在有無を返す
最小限のクライアントを実装する。

**変更対象ファイル**
- `src/agent_trend_radar/github_client.py`(新規)
- `tests/test_github_client.py`(新規)

**タスク**
- [x] PATを環境変数(例: `GITHUB_TOKEN`)から読み込む
- [x] 「owner/repo内の指定パスが存在するか」を返す関数を実装
      (Contents API `GET /repos/{owner}/{repo}/contents/{path}` の
      200/404で判定)
- [x] ファイル内容を取得する関数(依存チェック用に必要)
- [x] レート制限エラー時の最低限のハンドリング(リトライ or 明確なエラー
      メッセージ)

**完了条件**: 実在パスと存在しないパスの両方で正しく真偽値が返る単体
テストが通る。

**依存**: #1

---

## #4 チェック項目ロジック実装

**概要**: SPEC.md記載の6項目を判定するロジックを実装する。

**変更対象ファイル**
- `src/agent_trend_radar/checks.py`(新規)
- `tests/test_checks.py`(新規)

**タスク**
- [x] `has_agent_instructions`: `CLAUDE.md` / `AGENTS.md` / `.cursorrules`
      いずれかの存在確認
- [x] `has_tests`: `tests/` の存在確認
- [x] `has_eval`: `evals/` / `eval/` の存在確認
- [x] `has_ci`: `.github/workflows/` の存在確認
- [x] `has_security_policy`: `SECURITY.md` の存在確認
- [x] `has_observability_dep`: マニフェストファイル
      (`pyproject.toml`/`package.json`/`requirements.txt`)を読み込み、
      既知の観測可能性関連パッケージ名(SPEC.md記載の6件)との文字列一致で判定

**完了条件**: 各関数が既知の実在リポジトリに対して期待通りの真偽値を
返すことを手動確認済み。

**依存**: #3

---

## #5 CLAUDE.md/AGENTS.md内容分析ロジック実装

**概要**: SPEC.md「CLAUDE.md/AGENTS.md内容分析(構造ベース)」記載の8項目を
判定するロジックを実装する。エージェントツールの使われ方の実態(テスト/lint/
セキュリティ/コミット規約/Skill・MCP等の利用法への言及)を、ファイル存在
チェックより一段深く見るために追加した(#4実装後にユーザー要望で追加)。

**変更対象ファイル**
- `src/agent_trend_radar/agent_doc_analysis.py`(新規)
- `tests/test_agent_doc_analysis.py`(新規)

**タスク**
- [x] CLAUDE.md/AGENTS.mdの内容を`GitHubClient.get_file_content`で取得し、
      両方存在する場合は連結する関数を実装する(どちらも存在しない場合は
      空文字列として扱う)。CLAUDE.mdがAGENTS.mdへのシンボリックリンクとして
      運用され両パスが同一内容を返すケース(apache/airflow, colinhacks/zod
      で実在確認)があるため、同一内容は重複カウントしないようにした
- [x] `agent_doc_char_count`: 文字数を返す
- [x] `agent_doc_heading_count`: `#`で始まる行数を返す
- [x] `agent_doc_has_code_block`: \`\`\`の有無を真偽値で返す
- [x] `agent_doc_mentions_test`: test/pytest/jest/vitestのいずれかを含むか
- [x] `agent_doc_mentions_lint`: lint/ruff/eslint/prettierのいずれかを含むか
- [x] `agent_doc_mentions_security`: security/secret/credential/vulnerability
      のいずれかを含むか
- [x] `agent_doc_mentions_commit_convention`: commit message/conventional
      commitのいずれかを含むか
- [x] `agent_doc_mentions_tool_usage`: mcp/skill/subagent/slash command/
      hook/tool use/function callingのいずれかを含むか
- [x] キーワード一致はすべて大小文字無視で行う

**完了条件**: 各関数が既知の実在リポジトリ(CLAUDE.md/AGENTS.mdの内容が
既知のもの)に対して期待通りの値を返すことを手動確認済み。

**依存**: #3

---

## #6 SQLite永続化実装

**概要**: SPEC.mdのデータスキーマに沿って `repo_checks` テーブルを作成し、
チェック結果を保存する。

**変更対象ファイル**
- `src/agent_trend_radar/storage.py`(新規)
- `tests/test_storage.py`(新規)
- `.gitignore`(`data/*.db` 追加、必要なら)

**タスク**
- [x] `repo_checks` テーブルのスキーマ定義(repo, segment, monetization_model,
      checked_at, #4/#5の各チェック項目キー)
- [x] テーブル作成処理(存在しなければ作成)
- [x] 1リポジトリ分の結果をINSERTする関数
- [x] SQLiteファイルの保存先を決定(`.gitignore`対象であることを確認)

**完了条件**: スクリプトを2回実行すると、レコードが2回分(実行日ごと)
蓄積されることを確認できる。

**依存**: #1

---

## #7 収集スクリプトの統合

**概要**: 対象リポジトリ一覧の読み込み→チェック実行→SQLite保存までを
1コマンドで実行できるようにする。

**変更対象ファイル**
- `scripts/collect.py`(新規)
- `src/agent_trend_radar/config.py`(新規、対象リポジトリ設定の読み込み)

**タスク**
- [x] `uv run scripts/collect.py` のようなエントリポイントを作成
- [x] #2の対象リポジトリ設定を読み込む
- [x] #4(ファイル存在6項目)と#5(内容分析8項目)のチェック関数をまとめて
      実行する集約処理を実装する(#4/#5では個々の判定関数のみを実装し、
      集約はこのIssueの責務とした)
- [x] 各リポジトリに対し上記の集約処理を実行
- [x] #6の保存処理を呼び出す
- [x] 実行ログ(進捗・エラー)を標準出力に出す

**完了条件**: 1コマンドで全対象リポジトリのチェックが完走し、SQLiteに
結果が残る。

**依存**: #2, #4, #5, #6

---

## #8 結果ビューア(Markdown表 / CSV出力)

**概要**: SQLiteに溜まった結果を人間が読める形で出力する。使用感を確認
するための最重要ステップ。

**変更対象ファイル**
- `scripts/report.py`(新規)
- `report.md`(実行時生成物、コミット対象外)

**タスク**
- [x] SQLiteから最新のチェック結果を読み出す処理
- [x] リポジトリ×項目のマトリクスをMarkdown表として出力
- [x] 同内容をCSVでも出力できるようにする(任意)
- [x] 出力をファイルに保存する簡単なCLI(例:
      `uv run scripts/report.py > report.md`)

**完了条件**: 生成したMarkdown表を見て、segment(tool/adopter)や
収益化モデル間の違いが一目で読み取れる。

**依存**: #6, #7

---

## #9 実データでの通し実行・振り返り

**概要**: #2で確定した10〜20リポジトリに対して実際に一気通貫で実行し、
結果を確認する。

**変更対象ファイル**
- `README.md`(実行手順を追記)
- `SPEC.md`(必要に応じて見直しメモ・項目更新)

**タスク**
- [x] `uv run scripts/collect.py` を実行し、全対象リポジトリの結果を
      収集する
- [x] `uv run scripts/report.py` で表を生成し、目視確認する
- [x] チェック項目・対象リポジトリの妥当性についてメモを残す
      (SPEC.mdの見直し方針に沿って更新するかどうかの判断材料)
- [x] README.mdに実行手順を追記する

**振り返りメモ(次に見直すべき点)**
- `has_tests`が20リポジトリ中16件でfalseになり、うち大半はモノレポ構成が
  原因と実データで確認できた(既存Issue #14に評拠を追記、SPEC.mdに既知の
  制限として明記済み)。「テストの有無」という指標としての説得力が現状
  弱いため、post-MVPで#14に対応するかどうかが最優先の見直し候補。
- `has_observability_dep`は20リポジトリ全件でfalse。判定対象パッケージが
  LangChainエコシステム寄りの少数リストであることに加え、`has_tests`と
  同じくルート直下のマニフェストしか見ていないため、モノレポでは
  ワークスペース直下に依存が現れないケースがある。指標として機能して
  いるか疑わしく、対象パッケージリストの拡充とあわせて要検討。
- 対象リポジトリの選定(segment/収益化モデルの構成)自体は、20件とも
  問題なく収集・分析が完走し、tool/adopter間で`has_tests`以外の項目
  (has_agent_instructions, has_ci等)では傾向差も観測できたため、
  現時点でのリスト見直しは不要と判断。

**完了条件**: 生成された表を見て「次に何を見直すべきか」が言語化できて
いる。

**依存**: #7, #8

---

## MVP後

参考・着手はMVP振り返り後に判断。詳細は各Issueの個別セクションを参照。

- [x] #10 GitHub Actions週次cron化 — 2026-09-13 #24の中で実装完了
      (詳細は末尾セクション参照)
- [x] #11 レート制限・エラーハンドリングの強化 — 2026-09-27 実装完了。
      タイムアウト・リトライ・二次レート制限対応・エラーログ出力を追加
      (詳細は末尾セクション参照)
- [x] #12 LLMによる要約・記事生成 — 2026-09-08 方針転換により中止
- [ ] #13 対象リポジトリ追加・入れ替えのフロー整備
- [x] #14 モノレポ/組織継承ファイルの扱い見直し — 2026-09-07
      has_tests対応完了・has_security_policyは対応せずクローズ
- [x] #15 LLMによるCLAUDE.md/AGENTS.md内容分析 — 2026-09-08 実装・実データ
      検証(分散確認・スポットチェック)完了(詳細は末尾セクション参照)
- [x] #16 has_observability_depのsegment適用範囲の見直し — 2026-09-07
      項目自体を廃止してクローズ
- [x] #17 分析結果を要約・記事化する際の統計的な注意点整理 —
      2026-09-07対応完了
- [ ] #18 可観測性指標の測り方の再設計(#16で発見)
- [ ] #19 データをClaude Projectから参照しやすい公開形式の検討 —
      2026-09-08 実装・実データ生成完了、Claude Project側の接続確認待ち
      (#12中止に伴い新設、詳細は末尾セクション参照)
- [ ] #20 has_ci / agent_doc_has_code_blockの天井・床効果の見直し
      (MVP品質評価で発見、詳細は末尾セクション参照)
- [x] #21 高度なエージェント運用ツール導入の有無チェック項目の追加
      (#15議論中に発見) — 2026-09-13 実装・実データでの反映確認完了
      (詳細は末尾セクション参照)
- [x] #22 #19の公開データにCLAUDE.md/AGENTS.mdの本文を含める —
      2026-09-08 #19に統合して実装完了(詳細は末尾セクション参照)
- [ ] #23 PR品質・レビュー通過率・インシデント率等のアウトカム指標の
      収集検討(#15議論中に発見、未解決の方法論的課題あり)
- [x] #24 agent-trend-dataへの連携機能を実装する — 2026-09-13
      PAT発行に時間がかかるためローカルスクリプト(`sync_to_hub.ps1`)
      連携に方針転換、実装・実行確認完了(CI版はPAT発行後に別途確認、
      詳細は末尾セクション参照)
- [x] #25 分析担当(playbook)からのデータ収集issue案3件への対応 —
      2026-09-14 SCHEMA.md未反映・snapshots上書き・skills_countの
      シンボリックリンク未解決バグ、3件とも対応完了(LLM分類の非決定性は
      既知の制限として記録のみ、詳細は末尾セクション参照)
- [x] #26 agent-trend-data SCHEMA.mdの反映漏れを再発防止する仕組みの構築
      — 2026-09-14 実装完了(#25の#1で発生した事象を受けて起票、詳細は
      末尾セクション参照)
- [x] #27 分析担当(playbook)からのデータ収集issue案3件への対応(2回目)
      — 2026-09-14 完了。#1は案Cで確定・注意書き追記、#2→#28、
      #3→#29へ切り出し(詳細は末尾セクション参照)
- [x] #28 skills検出ロジックを.agents/skills対応に拡張する — 2026-09-14
      実装完了、実データで6リポジトリの想定通りの変化を確認(#27の#2から
      分離、詳細は末尾セクション参照)
- [x] #29 モノレポでの指示文書網羅性とモノレポ傾向の指標化 — 2026-09-14
      実装完了。continuedev/continueのhas_agent_instructions誤りを修正、
      agent_doc_count新設(#27の#3から分離、詳細は末尾セクション参照)
- [x] #30 LLM分類のキャッシュ導入と実行環境の隔離
      (agent-trend-playbook調査案R1+R2) — 2026-09-26 実装完了。R1は当初想定の
      「スキップ」方式からB案(非決定性検出用のキー公開)に変更、R2は実データで
      cwd隔離の効果を確認(詳細は末尾セクション参照)
- [x] #31 スナップショット差分レポートの追加(agent-trend-playbook調査案R3)
      — 2026-09-26 実装完了。出力先は`data/latest/changes.md`に限定
      (ハブへの公開配線は別Issue化、詳細は末尾セクション参照)
- [x] #32 未知のエージェント関連規約パスの検出(agent-trend-playbook調査案R4)
      — 2026-09-27 実装完了。実データで9候補パスと既存チェック対象パスの
      非重複を確認、`.github/copilot-instructions.md`等の実データ発見あり
      (詳細は末尾セクション参照)
- [ ] #33 規約ファイル初出コミット日による採用ラグの計測方法の検討
      (agent-trend-playbook調査案R5)
- [ ] #34 フィードフォワード/フィードバックの集計ビューの追加
      (agent-trend-playbook調査案R6)
- [ ] #35 LLM分類で実際に使用されたモデル名の記録(#30から見送り分)
- [ ] #36 スナップショット差分レポートのハブへの公開(#31から見送り分)
- [ ] #37 収集失敗の可視化・追跡(#11から見送り分)

---

## #10 GitHub Actions週次cron化

**概要**: `scripts/collect.py`をGitHub Actionsで週次実行し、収集作業を
自動化する。

**#15実装中に判明した追加論点(2026-09-08)**: #15でCLAUDE.md/AGENTS.mdの
LLM分類にClaude Code CLIのヘッドレス実行(`claude -p`)を採用したため、
本Issueのシークレット管理方針にはGITHUB_TOKENに加えてこの認証方式の
決定が必要になった。調査済みの選択肢:
- `CLAUDE_CODE_OAUTH_TOKEN`(`claude setup-token`で発行、サブスクリプション
  認証): 追加のAPI課金なしだが、`--bare`モード(CI再現性重視の推奨設定)
  では使えない(bareモードはOAuth認証を読まずANTHROPIC_API_KEYを要求する)
- `ANTHROPIC_API_KEY`: `--bare`モードでの再現性は高いが、Anthropic APIの
  従量課金が発生する
- 公式の`anthropics/claude-code-action`がGitHub Actions用に存在する

**タスク**
- [ ] 着手時に詳細(ワークフロー定義、シークレット管理方針等)を定義する。
      上記の認証方式(サブスクリプション認証 vs API課金、CI再現性との
      トレードオフ)をどちらにするかを含めて決める

**完了条件**: 着手時に別途定義する。

**依存**: #7(完了済み)、#15(完了済み)

**対応内容(2026-09-13)**: #24(agent-trend-dataへの連携機能実装)の
中で、ハブへのpush検証に必要な前提として本Issueのワークフロー本体を
実装した。認証方式はサブスクリプション認証(`CLAUDE_CODE_OAUTH_TOKEN`)
を採用。詳細は#24を参照。

---

## #11 レート制限・エラーハンドリングの強化

**概要**: GitHub API呼び出しにおけるレート制限対応・エラーハンドリングを、
#3実装時点の最低限の実装から強化する。

**タスク**
- [x] 着手時に詳細を定義する — 対応内容参照。タイムアウト未設定・リトライ
      皆無・二次レート制限未対応の3点を`github_client.py`のHTTPロバスト
      ネス強化として定義した(「部分失敗時のデータ欠損蓄積」への対応は
      別Issue候補として切り出し、対応内容参照)

**完了条件**: 着手時に定義した以下がテスト・実データで確認できること。
(1) リクエストにタイムアウトが設定されている。(2) ネットワークエラー・
5xxエラーは指数バックオフで最大3回リトライする。(3) 一次レート制限は
即座にエラーとする(リトライしない)。(4) 二次レート制限
(`Retry-After`ヘッダー付きの403/429)は待ってリトライする。(5) 404等の
リトライ不可能なエラーは即座にエラーとする。(6) エラー・リトライの発生が
ログファイルに残る。

**依存**: #3(完了済み)

**対応内容(2026-09-27)**: 着手前の設計確認で、ユーザーと以下の方針を
確認した。

- スコープは`github_client.py`のHTTPロバストネス強化(タイムアウト・
  リトライ・二次レート制限対応)に限定。`reports/api_cost_evaluation.md`
  が指摘していた「部分失敗時のデータ欠損蓄積」(週次自動実行でリポジトリの
  収集が失敗した場合、そのリポジトリのデータが古いまま気づかれずに
  残り続ける)への対応(可視化・アラート等)は、`collect.py`の設計変更を
  伴い本Issueの範囲を超えると判断し、別Issue候補として報告する(下記
  「新Issue案」参照)
- ユーザー追加要望: エラー発生をログファイルに残す(標準出力はCIログ
  以外に残らないため)

**実施内容**:
- `src/agent_trend_radar/github_client.py`: `_request`をリトライループに
  書き換えた。
  - タイムアウト30秒(`DEFAULT_TIMEOUT_SECONDS`)を全リクエストに設定
  - ネットワークエラー(`requests.exceptions.RequestException`)・5xx
    エラーは指数バックオフ(1, 2, 4秒)で最大3回(`DEFAULT_MAX_RETRIES`)
    リトライ
  - 二次レート制限(403/429で`Retry-After`ヘッダー付き、一次レート制限
    とは別ルート)を新規検知し、`Retry-After`秒(上限60秒、
    `MAX_SECONDARY_RATE_LIMIT_WAIT_SECONDS`)待ってリトライ
  - 一次レート制限(`X-RateLimit-Remaining: 0`)・404等のリトライ不可能な
    エラーは従来通り即座にエラー(リトライで無駄なコールを消費しない)
  - `sleep`関数をコンストラクタ引数として注入可能にし(既定`time.sleep`)、
    テストで実際に待たずに検証できるようにした
  - リトライ発生時に`logging`モジュールでWARNINGを出力(#11のログ要望)
- `scripts/collect.py`: `configure_logging()`を新設し、`data/collect.log`
  (gitignore対象)にWARNING以上を書き出すよう設定。リポジトリ単位の収集
  失敗時も`logger.error`で同じログファイルに記録するようにした(標準出力
  への`print`は従来通り維持)
- `.gitignore`に`/data/collect.log`を追加
- `tests/test_github_client.py`: `FakeSession`を、URLごとに複数回の応答
  (例外含む)を順番に返せるよう拡張(後方互換は維持)。新規11件のテストで
  タイムアウト付与・各種リトライ・非リトライ・ログ出力を確認。既存2件
  (500エラー系)は、新しいリトライで実際にスリープしてしまわないよう
  `sleep=lambda seconds: None`を注入する形に修正した

**確認結果**:
- テスト: 新規11件・既存修正2件を含め、全154件パス(`uv run pytest -q`)
- 実データ確認(GITHUB_TOKEN利用可能な環境で実施): `uv run scripts/collect.py`
  を実行し、20リポジトリ全件が正常完了することを確認。**実行中に実際の
  ネットワーク切断(`RemoteDisconnected`)が`apache/airflow`のCLAUDE.md
  取得で発生し、自動リトライで成功、`data/collect.log`にWARNINGとして
  記録されることを実データで確認できた**(意図的な障害注入ではなく、
  実行中に偶発的に発生した実例)。また、存在しないリポジトリ名を使って
  意図的に404エラーを発生させ、`logger.error`経由で`data/collect.log`に
  記録されることも確認した

**未完のタスク**: なし。「部分失敗時のデータ欠損蓄積」への対応は下記
新Issue案として切り出した。

---

## #12 LLMによる要約・記事生成(中止)

**概要**: 収集したデータをLLMで要約し、記事化する機能をこのリポジトリに
実装する計画だった(MVP後の項目、CLAUDE.mdの「LLM利用」欄参照)。

**中止理由(2026-09-08)**: データからの考察(要約・記事化を含む)は、
Claude Projectの専用チャットスペースで行う方針に変更した。考察のみを
行うチャットスペースを別に設けることで、このリポジトリの実装作業
(Claude Code側のコンテキスト)が考察に混入するのを避けるのが狙い。
この方針変更により、リポジトリ内にLLM要約・記事生成機能を実装する
必要がなくなったため、#12自体を中止する。

**後続対応**: 考察をClaude Project側で行うには、このリポジトリの
ファイルシステムに直接アクセスできないClaude Projectから、収集済み
データを参照できるようにする必要がある。この検討をIssue #19として
新設した。また、#17(分析結果を要約・記事化する際の統計的な注意点整理)
で作成した`reports/analysis_interpretation_caveats.md`は、リポジトリ内
実装への組み込みを前提とせず、Claude Project側での考察時に参照する
資料として引き続き活用する。

**依存**: なし

---

## #13 対象リポジトリ追加・入れ替えのフロー整備

**概要**: SPEC.mdの「対象の見直し」方針に沿って、対象リポジトリの追加・
入れ替えを行う際のフロー(手順・確認観点)を整備する。

**タスク**
- [ ] 着手時に詳細を定義する

**完了条件**: 着手時に別途定義する。

**依存**: #2(完了済み)

---

## #14 モノレポ/組織継承ファイルの扱い見直し

**概要**: #4実装中に発見。トップレベル直下のみのパス存在チェックでは、
モノレポ構成のリポジトリ(langchain-ai/langchain, apache/airflow等)で
実際にはサブディレクトリ配下に`tests/`があっても`has_tests=false`に
なる。また`SECURITY.md`がGitHub組織の`.github`特別リポジトリに置かれ
継承表示されているケース(apache/airflow, langchain-ai/langchain等)も、
対象リポジトリ自体には存在しないため`has_security_policy=false`になる。

**発見の裏付け(#9実データ通し実行、2026-09-06)**: 20リポジトリ中16件で
`has_tests=false`となり、うち少なくともastral-sh/ruff、
langchain-ai/langchain、apache/airflow、supabase/supabase、
crewAIInc/crewAI、continuedev/continue、microsoft/autogenの7件は
GitHub API上で実際にモノレポ構造(crates/、libs/、providers/、
packages/等)であることを確認済み(テスト自体が存在しないと確認できた
のはyoheinakajima/babyagiのみ)。さらにvercel/next.jsはルート直下に
`tests`ではなく`test`(単数形)のディレクトリを持つため、モノレポ云々
ではなく命名バリエーションのみでfalseになるケースも確認した。
`has_security_policy`についてもapache/airflow、langchain-ai/langchainの
2件で予想通りfalseになることを確認した。

**変更対象ファイル**
- `src/agent_trend_radar/github_client.py`(`get_directory_names`追加)
- `src/agent_trend_radar/checks.py`(`has_tests`の判定方式変更)

**タスク**
- [x] `has_tests`をGit Trees API
      (`GET /repos/{owner}/{repo}/git/trees/HEAD?recursive=1`)で
      リポジトリ全体のディレクトリ名を1リクエストで取得し、任意の深さで
      `tests`または`test`という名前のディレクトリが存在するかを判定する
      方式に変更する
- [x] 対象20リポジトリがGitHub側のtruncated制限(7MB/10万エントリ)に
      該当しないことを事前確認する

**対応内容(2026-09-07)**: 上記の通り`has_tests`をGit Trees API方式に
変更し、実データ再実行の結果20リポジトリ中19件がtrueに改善した(false
は実際にテストが存在しないyoheinakajima/babyagiのみ)。
`has_security_policy`の組織`.github`継承問題は対応せず、SPEC.mdの既知の
制限として文書化のみでクローズすることをユーザーと合意した。

**依存**: #4(完了済み)、#9(完了済み)

---

## #15 LLMによるCLAUDE.md/AGENTS.md内容分析

**概要**: #5のルールベース構造分析(キーワード一致)には、
`reports/agent_doc_analysis_validation.md`で検証した通り明確な限界がある
(PR/コミット規約や「してはいけないことの境界線」等、表現のバリエーション
が大きいテーマを取りこぼす)。この限界を踏まえ、MVP完成後にLLMを使った
内容分析を追加する。ユーザー判断により、コストをかけてでも実施する価値が
あると判断された。

**背景・参照**
- `reports/agent_doc_analysis_validation.md`(発見2・発見3のセクション)
- CLAUDE.mdの「LLM利用」欄

**変更対象ファイル**
- `src/agent_trend_radar/llm_content_analysis.py`(新規)
- `src/agent_trend_radar/storage.py`(CHECK_COLUMNSに4項目追加)
- `scripts/collect.py`(新規4項目の呼び出しを追加)
- `scripts/report.py`(真偽値項目のsegment×monetization_model別集計を
  `--format stats`に追加。有効性評価方法を兼ねる)
- `tests/test_llm_content_analysis.py`(新規)、`tests/test_report.py`
  (新規)、`tests/conftest.py`(新規、scripts/のimport用)、
  `tests/test_storage.py`(SAMPLE_CHECKSに4項目追加)
- `SPEC.md`、`CLAUDE.md`、`README.md`(方針・セットアップ手順の反映)

**タスク**
- [x] レポートで指摘した見逃しテーマ(リポジトリ構造説明、してはいけない
      ことの境界線、PRレビュー基準・人間チェックポイント、リリース手順)を
      LLMでカテゴリ分類する4項目(`agent_doc_mentions_repo_structure`/
      `_boundaries`/`_pr_review`/`_release_process`)として実装した
- [x] #5のルールベース8項目とは**置き換えず併存**させる方針に決定
      (validation reportの結論通り、単語自体が本文に出現するテーマでは
      ルールベースが機能しているため)
- [x] モデル選定はユーザー判断により方針転換。Anthropic API(Claude
      Haiku 4.5等)の従量課金ではなく、**Claude Code CLIのヘッドレス実行**
      (`claude -p --output-format json --json-schema ...`)を
      サブスクリプション認証のまま使う設計にした(詳細は「対応内容」参照)
- [x] 20リポジトリ分のコスト: サブスクリプション認証のため追加のAPI
      課金は発生しない設計にした。ただし実行時間・サブスクリプション
      利用枠の消費量は未実測(下記「未検証の項目」参照)
- [ ] プロンプト設計とキャッシュ方針(同一内容の再分析を避ける): 1リポ
      ジトリ1回呼び出しの設計に留め、キャッシュは未実装(低コスト化の
      主眼はAPI課金回避で達成済みのため優先度を下げた)

**対応内容(2026-09-08)**: 当初はAnthropic API(Claude Haiku 4.5)を
`anthropic` SDK経由で呼ぶ設計を提案したが、ユーザーから「Claude Codeの
skillとして登録できないか」という提案があり、対話型Skillとヘッドレス
CLI(`claude -p`+`claude-code-action`)の両方の実現性を調査した上で、
ヘッドレスCLI方式を採用した。

- `claude -p <分類プロンプト> --output-format json --json-schema
  <4項目のJSON Schema> --permission-prompts none`をサブプロセスとして
  呼び出し、標準入力でCLAUDE.md/AGENTS.mdの内容を渡す設計
  (`src/agent_trend_radar/llm_content_analysis.py`)
- 出力は`structured_output`キー配下に4つの真偽値が入る(公式ドキュメント
  調査で確認)
- `--bare`は使わない(bareモードはOAuth認証を読まずANTHROPIC_API_KEYが
  必要になるため、サブスクリプション認証を維持する目的と相反する)
- 有効性評価方法として、`scripts/report.py`の`--format stats`に真偽値
  項目のsegment×monetization_model別count/true率集計を追加した
  (`render_boolean_stats`)。#15の完了確認(新規4項目が天井/床効果に
  陥っていないか)と、プロジェクト全体の品質担保(#20等の既存項目にも
  同じ評価方法を適用可能)を兼ねる

**実データ検証(2026-09-08、GITHUB_TOKEN・claude CLI(v2.1.263)が利用
できる環境で実施)**: 古いスキーマの`data/repo_checks.db`(#16以前、
`has_observability_dep`が残存)を退避し、`uv run scripts/collect.py`を
20リポジトリ全件に対して実行。エラーなく完走し(所要時間は
`data/latest/`生成分も合わせて実測)、新規4項目を含む全21列でDBが
再構築されたことを確認した。

- **分散確認**(`uv run scripts/report.py --format stats`): 新規4項目は
  いずれもsegment×monetization_model別に0%〜100%の幅のあるtrue率を
  示し、`has_ci`(全グループ100%近辺、天井効果)とは対照的に比較材料
  として機能していることを確認した(例:
  `agent_doc_mentions_release_process`はadopter×commercial_saas 20%、
  tool×big_corp_internal 0%など)
- **既知の見逃し事例のスポットチェック**: `reports/
  agent_doc_analysis_validation.md`が指摘していた2件
  (astral-sh/ruffの"PR conventions"見出し、oven-sh/bunの"Landing PRs:
  What Bun Reviewers Catch"見出し)は、旧`agent_doc_mentions_
  commit_convention`(キーワード一致)では両者ともfalseのままだが、
  新規`agent_doc_mentions_pr_review`はどちらも正しくtrueと判定した
- 全20リポジトリのうちCLAUDE.md/AGENTS.mdを実際に保有していたのは16件
  (`data/latest/agent_docs/`に16ファイル生成、4件
  (microsoft/autogen, Aider-AI/aider, continuedev/continue,
  yoheinakajima/babyagi)はスキップ)。これは
  agent_doc_analysis_validation.mdの表(✓16件)と一致する
  (同レポート本文中の「14件(70%)」という記述は数値が古い/誤りの
  可能性があり、本Issueでは実測の16件を正とする)

**副次的に見つけた修正**: `collect.py`/`publish.py`の`print()`出力が
Windows環境でリダイレクト時に文字化けしていたため、`report.py`と同様に
`sys.stdout.reconfigure(encoding="utf-8")`を追加した。

**完了条件**:
1. 実装・ユニットテスト(モック)が完了している(達成済み)
2. 実データで新規4項目を実行し、天井/床効果(has_ci等と同じ問題)に
   陥っていないことを`report.py --format stats`で確認する(達成済み)
3. 既知の見逃し事例のスポットチェックで、新規項目が意図通り機能して
   いることを確認する(達成済み)

**依存**: #5(完了済み)、MVP(#1〜#9)の完了

---

## #16 has_observability_depのsegment適用範囲の見直し(MVP品質評価で発見)

**概要**: `reports/mvp_data_insights_evaluation.md`のMVP品質評価で発見。
`has_observability_dep`はLangSmith/Langfuse等、LLMアプリ自体の
可観測性SDKへの依存有無を見る項目だが、実データでは20リポジトリ中
1件(crewAIInc/crewAI、toolセグメント)しかtrueにならず、分散が
実質ゼロで比較材料として機能していない。

原因は検知漏れではなく設計上のミスマッチと考えられる。adopterセグメント
(Next.js, Zod, Bun等)はAI開発エージェント(Claude Code/Cursor等)を
"使って"開発しているだけで、自分たちがLLMアプリを"作っている"わけでは
ない。LangSmith/LangfuseのようなLチェック対象パッケージは、LLMアプリを
開発しているtoolセグメント向けの指標であり、adopter側に同じ基準を
適用すること自体が指標設計として噛み合っていない。

**対応内容(2026-09-07)**: 検討の結果、adopterセグメントへの不整合だけ
でなく、本来の対象であるtoolセグメントでも「フレームワークはLangSmith等
との連携機能を"提供"するだけで、自身が"依存"するとは限らない」という
測定方法自体の構造的な限界があると判明した(tool 10件中1件のみtrue)。
「実行時の観測性」という測りたい実態と「依存マニフェストの文字列一致」
という測り方が原理的に噛み合っていないと判断し、対応案(a)/(b)/(c)を
採らずに**`has_observability_dep`を廃止**した(`checks.py`、
`storage.py`のCHECK_COLUMNS、`scripts/collect.py`から削除。
`report.py`はCHECK_COLUMNSを動的参照するため無変更で追従)。
詳細はSPEC.md「廃止した項目とその理由」を参照。測り方の再設計は
Issue #18で検討する。

**依存**: #5(完了済み)、MVP(#1〜#9)の完了

---

## #17 分析結果を要約・記事化する際の統計的な注意点整理(MVP品質評価で発見)

**概要**: `reports/mvp_data_insights_evaluation.md`のMVP品質評価で、
集計結果の解釈を誤りかけた事例が複数見つかった。#12(LLMによる要約・
記事生成、現在は中止)着手時に踏まえるべき前提条件としてまとめる。

**発見した注意点**
1. **平均値は外れ値の影響を強く受ける**: `agent_doc_char_count`の
   commercial_saas平均(23,275字)はOpenHands/OpenHands(120,034字、
   2位browser-useの倍以上)という外れ値に強く引っ張られていた。
   中央値(12,202字)の方が実態に近い。要約時は平均だけでなく中央値・
   分布(min/max)も併記すること。
2. **segment間比較には選定バイアスの影響を受ける項目がある**:
   `has_agent_instructions`はSPEC.mdの選定基準上、adopterが
   「CLAUDE.md/AGENTS.md等の採用が公知の事例」という条件で選ばれて
   いるため、segment間(tool vs adopter)の比較はそのままでは無効。
   選定基準に組み込まれていない軸(例: monetization_model軸で
   tool segmentのみに限定)を選ぶ必要がある。
3. **天井/床効果のある項目は比較材料にならない**: `has_ci`
   (90〜100%)や`agent_doc_has_code_block`(セグメント間67% vs 70%と
   僅差)のようにほぼ全件同じ値になる項目は、差を語る根拠として
   使えないことを明記する。

**対応内容(2026-09-07)**: #12(LLMによる要約・記事生成)自体が未着手で、
組み込み先のプロンプト/チェックリストという実体がまだ存在しないため、
`reports/analysis_interpretation_caveats.md`として独立した参照
ドキュメントを作成した。あわせて`scripts/report.py`に
`--format stats`を追加し、`agent_doc_char_count`/
`agent_doc_heading_count`についてsegment×monetization_modelで
グループ化したn/min/中央値/平均/maxを出力できるようにした。実データで
実行し、tool×commercial_saasの中央値5,263字・平均28,583字という
大きな乖離(外れ値の影響)が数値として再現されることを確認した。

**追記(2026-09-08)**: #12は方針転換により中止した(詳細は#12セクション
参照)。本ドキュメントはリポジトリ内実装への組み込みではなく、Claude
Project側で考察を行う際の参照資料として活用する。

**依存**: #9(完了済み)。#12は中止(詳細は#12セクション参照)

---

## #18 可観測性指標の測り方の再設計(#16で発見)

**概要**: #16で`has_observability_dep`(依存にLangSmith/Langfuse等が
あるか)を廃止した際に判明した課題。「LLM/エージェントの実行時挙動を
追跡できているか」というテーマ自体は、このプロジェクトが掲げる
「品質・セキュリティ・運用の実践知」の「運用」軸として今も妥当だが、
「自リポジトリの依存マニフェストへの文字列一致」という測り方では、
以下の理由から実態を捉えられなかった。

- adopterセグメントには概念的に適用対象外(AI開発エージェントを使って
  開発しているだけで、自らLLMアプリを作っているわけではないため)
- 本来の対象であるtoolセグメントでも、フレームワークはLangSmith等との
  連携機能を"提供"するだけで自身が"依存"するとは限らず、実質機能
  しなかった(10件中1件のみtrue)

**タスク**(たたき台、着手時に確定する)
- [ ] そもそも「運用の実践知」の別の側面(has_ci等)で既にある程度代替
      できているため、無理に復活させる必要があるか自体を再検討する
- [ ] 復活させる場合、依存マニフェストではなく`docs/`・`examples/`での
      言及や、実際の統合方法(webhook/callback設定等)を見るアプローチが
      考えられるが、CLAUDE.mdのシンプルさ優先方針(複雑な依存パーサは
      作らない)との整合を要検討
- [ ] toolセグメントとadopterセグメントで別々の指標を持つべきか
      (adopter向けにはAPM/エラートラッキング等、別カテゴリの運用指標を
      検討する余地がある)

**完了条件**: 着手時に別途定義する。

**依存**: #16(完了済み)

---

## #19 データをClaude Projectから参照しやすい公開形式の検討(#12中止に伴い新設)

**概要**: #12(LLMによる要約・記事生成)を中止し、データからの考察は
Claude Projectの専用チャットスペースで行う方針に変更したことに伴い
新設。Claude Projectはこのリポジトリのファイルシステムに直接アクセス
できないため、収集済みデータ(`repo_checks`テーブル)を、実装コンテキ
スト(src/, tests/等)を含まない形でClaude Projectから参照できるように
する「公開の形」を検討する。

**背景**
- `scripts/report.py`はmarkdown/csv/statsをstdoutに出力するのみで、
  リポジトリにコミットされる安定したスナップショットが現状存在しない
  (Issue #8で生成物はコミット対象外とする方針にしたため)。
- GitHub Actions週次cron化(#10)も未着手のため、定期的に自動更新される
  公開データという仕組み自体がまだ存在しない。
- リポジトリはCLAUDE.mdの通りOSS公開を最終目標としているが、現時点では
  非公開(GitHub上で未認証アクセス時に404を確認)。

**検討候補(たたき台、着手時に絞り込む)**
1. `scripts/report.py`の出力を`data/latest/`のような固定パスにコミット
   する運用にし、生成物をClaude Projectの「プロジェクトの知識」に
   ファイルとして手動アップロードする
2. リポジトリ自体を公開(public)化し、Claude ProjectのGitHub連携機能を
   使って接続先リポジトリを直接参照する。ただしsrc/やtests/等の実装
   コードまで見えてしまうため、「考察用チャットへの実装コンテキスト
   混入を避ける」という#12中止の理由と整合するかは要検討
3. 実装コードとデータ公開先を物理的に分離する(例: レポート生成物のみを
   別の公開readonlyリポジトリやGitHub Pagesにpushする)
4. SQLite DBファイル自体を配布し、Claude Project側でクエリを書いて
   もらう。生データへのアクセス性は高いが、Claude Project側でのDB
   ファイル解析の実用性を要検証

**判断基準**
- 実装コンテキスト(src/, tests/等)が考察用チャットスペースに混入
  しないこと(#12中止の理由と直結する最優先条件)
- 低コスト運用必須(CLAUDE.md制約)。有料SaaS・高額API課金は避ける
- 更新の手間(手動アップロード vs 自動公開)とデータの鮮度のバランス

**採用した形式(2026-09-08)**: 候補1をベースに、当初の想定より発展した
形で確定した。実装過程でClaude GitHub連携(Claude Help Center公式記事
で確認)が(a)非公開リポジトリに対応しており、(b)「Configure files」
機能で同期対象を特定フォルダに絞り込め、(c)コミット履歴・PR等の
メタデータは同期されないと判明したため、候補2の「実装コード混入」
という当初の懸念は解消できることが分かった。最終形:

- `scripts/publish.py`で`data/latest/`配下に公開データを生成
  (`report.md`: マトリクス表、`stats.md`: segment×monetization_model別
  統計、`agent_docs/<owner>__<repo>.md`: CLAUDE.md/AGENTS.mdの生テキスト
  (#22を統合、要約・解釈はしない))
- `data/latest/`はコミット対象(`.gitignore`を`/report.md`/`/report.csv`
  に絞り、`data/latest/report.md`等を誤って除外していた不具合も修正)
- リポジトリは非公開のまま、Claude Project側でこのリポジトリを
  GitHub連携し、「Configure files」で`data/latest/`のみを同期対象に
  設定する運用とする(候補2を、非公開のまま・フォルダ限定で採用した形)
- 候補3(別リポジトリへの分離)・候補4(SQLite配布)は不採用

**タスク**
- [x] 採用する公開形式を決定した(候補1+候補2のハイブリッド、上記参照)
- [x] `scripts/publish.py`を実装し、report.py出力とagent doc生テキストを
      `data/latest/`に生成する処理を作成した
- [x] 実データ(GITHUB_TOKEN・claude CLI利用可能な環境)で実行し、
      `data/latest/report.md`・`stats.md`・`agent_docs/`16件が正しく
      生成されることを確認した
- [x] `data/latest/ANALYSIS_INSTRUCTIONS.md`を追加し、Claude Project側で
      データの有効性・妥当性を検証してもらうための指示書とした
      (`reports/analysis_interpretation_caveats.md`(#17)の注意点を
      要約転記。`publish.py`はこのファイルを上書きしない静的ファイル)
- [ ] 実際にClaude Projectにこのリポジトリを接続し、「Configure files」
      で`data/latest/`に絞り込んだ上で考察が行えることを確認する
      (Claude Project側の操作のためユーザーが実施)
- [x] README.mdに運用手順(`uv run scripts/publish.py`の実行方法、
      Claude Project側のGitHub連携設定)を追記した

**完了条件**:
1. `scripts/publish.py`が実データで正しく`data/latest/`を生成する
   (達成済み)
2. Claude Project側で`data/latest/`のみを同期対象に接続し、実際に
   考察が行えることを確認する(ユーザー側での確認待ち)

**依存**: #8(完了済み)、#17(完了済み。考察時の解釈上の注意点として
Claude Project側で参照)、#22(本Issueに統合)

---

## #20 has_ci / agent_doc_has_code_blockの天井・床効果の見直し(MVP品質評価で発見)

**概要**: `reports/mvp_data_insights_evaluation.md`のMVP品質評価で発見。
`has_ci`はadopter 100%・tool 90%とほぼ全件trueに張り付いており、
`agent_doc_has_code_block`もtool 67%(4/6)・adopter 70%(7/10)と
segment間の差がほとんどない。両項目とも判定ロジック自体に誤りはないが、
天井/床効果により比較材料としての情報量が乏しいと評価されている。

**タスク**(たたき台、着手時に確定する)
- [ ] 項目として維持する価値があるか再検討する(「分散がない」こと自体が
      無価値とは限らない。例えばhas_ciがほぼ全件trueという結果は「CI
      導入はもはや前提条件」という示唆を持つ)
- [ ] 廃止する場合、代替の切り口(例: has_ciはワークフロー数・実行内容の
      複雑さ、agent_doc_has_code_blockはコードブロック数・言語種別等)を
      検討する
- [ ] 廃止・維持いずれの場合もSPEC.mdの「既知の制限」または「廃止した
      項目とその理由」に反映する

**完了条件**: 着手時に別途定義する。

**依存**: #5(完了済み)、#9(完了済み)

---

## #21 高度なエージェント運用ツール導入の有無チェック項目の追加(#15議論中に発見)

**概要**: 現行17項目(#1〜#9のファイル存在5項目、#5のルールベース8項目、
#15のLLM分類4項目)はいずれも「有無」のシグナルだが、既存項目はagent
instructions/tests/CI等の基礎的な運用整備に留まる。ユーザーとの議論
(2026-09-08、#15の完了報告時)で「ベストプラクティスを考察するには
情報が薄い」という指摘があり、カスタムスラッシュコマンド・Skill・
サブエージェント・MCP連携など、より高度なエージェント運用への投資
度合いを示すシグナルを追加する案が挙がった。既存の「ファイル/
ディレクトリ存在確認」という決定的な方法論のまま拡張できる。

**変更対象ファイル**
- `src/agent_trend_radar/github_client.py`(`get_file_paths`・Tree API
  レスポンスのキャッシュを追加)
- `src/agent_trend_radar/checks.py`(6項目のチェック関数を追加)
- `src/agent_trend_radar/storage.py`(`CHECK_COLUMNS`に6項目追加)
- `scripts/collect.py`(新チェックの呼び出しを追加)
- `scripts/report.py`(`NUMERIC_COLUMNS`に3項目追加)
- `SPEC.md`(チェック項目表・既知の制限に追記)
- `tests/test_github_client.py`・`tests/test_checks.py`・
  `tests/test_storage.py`・`tests/test_export_hub_snapshot.py`

**具体化の経緯(2026-09-13)**: `agent-trend-data/data-requests/pending/
2026-09-13-agent-tooling-metrics.md`として、記事作成システム側
(`agent-trend-playbook`)から「ルール化とツール化の境界線」というテーマ
検証のため、具体的なフィールド名を伴う要望が届いた。ユーザー確認の上、
本Issueのたたき台をこの要望で具体化し、そのまま着手した。

**確定した6項目**(候補にあった`.claude/agents/`・`.cursor/rules/`は
今回のスコープ外、SPEC.md「既知の制限」に将来の拡張候補として記載):
- `has_skills_dir` / `skills_count`: `.claude/skills/*/SKILL.md`の有無・数
- `has_custom_commands` / `custom_commands_count`:
  `.claude/commands/`配下の`.md`ファイルの有無・数(サブディレクトリ含む)
- `has_hooks_config`: `.claude/settings.json`の`hooks`キーが空でないか
- `mcp_servers_count`: `.mcp.json`の`mcpServers`の数

**タスク**
- [x] 候補パスを確定した(上記4フィールド6項目、`.claude/agents/`・
      `.cursor/rules/`は対象外)
- [x] Git Trees APIを使う方針とした。既存`get_directory_names`に加えて
      `get_file_paths`(blobパス一覧)を追加し、両者が同一repoに対して
      重複してAPIを叩かないよう`GitHubClient`内でTreeレスポンスを
      リポジトリ単位にキャッシュした(API呼び出し数を増やさない対応)
- [x] `has_hooks_config`/`mcp_servers_count`はファイル存在だけでは
      判定できないため、JSON内容を読んでキー有無・件数を見る方式とした
      (CLAUDE.md/AGENTS.md内容分析で既に認めている「決定的な構造分析」の
      延長として整理、SPEC.md参照)
- [x] SPEC.mdのチェック項目表・既知の制限に追記した
- [x] 各関数のユニットテストを追加し、全76件パス確認済み
- [x] 実データ(`cline/cline`, `astral-sh/ruff`, `langchain-ai/langchain`)
      で動作確認する過程で、`skills_count`の初期実装(`SKILL.md`
      ファイル名一致)がバグを含むことを発見・修正した。cline/cline は
      Skill実体を別の場所に置き`.claude/skills/<name>`をシンボリック
      リンクとして公開する形式(mode 120000)を使っており、SKILL.md
      ファイル名一致では0件になっていた(実際は6件)。`GitHubClient`に
      `list_immediate_children`を追加し、ファイル種別を問わず
      `.claude/skills/`直下の子要素数を数える方式に修正。テスト追加の上
      全79件パス確認済み

**完了条件**: 対象20リポジトリ分の収集で新規6項目が正しく収集され、
`agent-trend-data`のmetrics.jsonに反映される(達成済み、2026-09-13
`sync_to_hub.ps1`実行・コミット`720b4ad`で確認。cline/cline:
skills_count=6/custom_commands_count=2/has_hooks_config=1、
astral-sh/ruff: has_hooks_config=1、langchain-ai/langchain:
mcp_servers_count=2など、事前の個別確認と一致)。

**依存**: #4(完了済み)、#14(完了済み)、#24(完了済み、収集結果は
`sync_to_hub.ps1`経由でagent-trend-dataへ連携)

---

## #22 #19の公開データにCLAUDE.md/AGENTS.mdの本文を含める(#19に統合済み)

**概要**: #19(データをClaude Projectから参照しやすい公開形式の検討)
で公開するデータが、真偽値・数値に変換した派生指標のみだと、Claude
Project側での定性的な考察の材料が乏しい。ユーザーとの議論(2026-09-08、
#15の完了報告時)で、CLAUDE.md/AGENTS.mdの本文そのもの(一次情報)も
公開データに含めるべきという方向性が挙がった。このリポジトリ側で
本文を要約・解釈することはせず(#12中止の理由と同じ)、生のテキストを
渡すことで要約・解釈自体はClaude Project側に委ねる。

**対応内容(2026-09-08)**: 独立したタスクにはせず、#19の実装に統合した。
`scripts/publish.py`が各リポジトリのCLAUDE.md/AGENTS.mdの生テキストを
`data/latest/agent_docs/<owner>__<repo>.md`として出力する
(抜粋・要約はせず全文をそのまま出力。出典(owner/repo)をファイル名と
見出しに明記した抜粋転載として扱う)。実データで16リポジトリ分
(最大約120KB/件)の生成を確認済み。詳細はIssue #19参照。

**依存**: #19(完了、詳細は#19セクション参照)、#5(完了済み)

---

## #23 PR品質・レビュー通過率・インシデント率等のアウトカム指標の収集検討(#15議論中に発見)

**概要**: 現行の全項目は「エージェント運用ルールが文書化・整備されて
いるか」という**整備状況**のシグナルであり、それが実際に機能している
かという**アウトカム**(PR品質、レビュー通過率、インシデント率等)は
一切測っていない。ユーザーから、これらのアウトカム指標も収集したいと
いう要望があった(2026-09-08、#15の完了報告時)。

**未解決の方法論的課題(着手前に必ず検討が必要)**
- **AIエージェント関与の特定問題**: GitHub API単体では「このPRがAI
  エージェントによって(補助)作成されたか」を確実に判定する手段が
  ない(明示的なラベル付け運用をしているリポジトリは稀、botアカウント
  経由のコミットも一部のみ検知可能)。この特定ができないと、「AI
  エージェント運用の実態」ではなく「リポジトリ全体のPR健全性」を測る
  だけになり、本プロジェクトの目的(AIエージェント活用の実態サーベイ)
  からずれるリスクがある
- **「インシデント率」の定義・計測手段が任意のOSSリポジトリに対して
  標準化されていない**(postmortem/incidentラベルの運用はリポジトリ
  依存で、一貫した基準が取れない可能性が高い)
- **APIコスト**: PR/レビュー/Issue一覧の取得は既存のファイル存在
  チェックよりAPI呼び出し数が大きく増える可能性があり、
  `reports/api_cost_evaluation.md`の再評価が必要になる

**タスク**(たたき台、着手時に確定する)
- [ ] AIエージェント関与を判定する現実的な方法があるか調査する
      (bot commit署名、PR本文の定型文言、Co-Authored-By等の可能性を
      個別リポジトリで確認)。判定できない場合、この指標群自体を
      見送るかどうかも含めて再検討する
- [ ] 「PR品質」「レビュー通過率」「インシデント率」それぞれの操作的
      定義を決める
- [ ] GitHub API呼び出しコストを試算し、api_cost_evaluation.mdと
      同水準の実測評価を行う
- [ ] 決定的に収集可能な指標のみに絞り込む(本プロジェクトの「収集は
      決定的に行う」方針との整合)

**完了条件**: 着手時に別途定義する。

**依存**: #9(完了済み)

---

## #24 agent-trend-dataへの連携機能を実装する

**概要**: データ収集システム(agent-trend-radar)と記事作成システムは
意図的にコンテキストを分離しており、記事作成システムが収集結果を
参照できるよう、ハブリポジトリ`agent-trend-data`へ収集結果を自動反映
する仕組みを実装する。

**変更対象ファイル**
- `.github/workflows/collect-and-publish.yml`(新規、現時点では未使用。
  下記「方針転換」参照)
- `scripts/export_hub_snapshot.py`(新規)
- `scripts/update_hub_manifest.py`(新規)
- `tests/test_export_hub_snapshot.py`(新規)
- `tests/test_update_hub_manifest.py`(新規)
- `sync_to_hub.ps1`(新規、方針転換により追加)
- `.gitignore`(`/hub_export/`追加)
- `README.md`(運用手順・必要Secrets追記)

**着手前に判明した前提のずれ**: 本Issueのタスクは「既存の収集ワーク
フローの末尾にpushステップを追加する」ことを想定していたが、
着手時点で本リポジトリにGitHub Actionsワークフローが1つも存在せず
(#10が未着手のまま)、この前提が成立しなかった。ユーザーに確認の上、
本Issueの中で新規ワークフローを作成する形で対応した(#10も実質的に
解決)。

**方針転換(2026-09-13)**: Fine-grained PATの発行に時間がかかるとの
判断から、GitHub Actions経由のCI自動化(PAT前提)を一旦保留し、
ローカル実行のPowerShellスクリプト(`sync_to_hub.ps1`)による連携に
切り替えた。`agent-trend-data`が`agent-trend-radar`と同階層の兄弟
ディレクトリにcloneされている前提で、collect.py実行からハブへの
commit・pushまでを1スクリプトで完結させる(ユーザー判断により
commit・pushまで完全自動化)。`.github/workflows/collect-and-publish.yml`
は削除せず、PAT発行後に有効化する想定でそのまま残した(現状は
Secrets未設定のため実行しても失敗する)。

**タスク**
- [x] デフォルト`GITHUB_TOKEN`での書き込みテストは実施せず、PATを直接
      採用した。理由: デフォルト`GITHUB_TOKEN`が実行元リポジトリにしか
      アクセス権を持たないことはGitHub Actionsの既知の制約であり、
      `agent-trend-data`のCLAUDE.md自体が「専用のFine-grained PATを
      使ってpushしてくる」ことを設計前提として明記していたため、実際に
      失敗するテストワークフローを1回分実行する価値がないと判断した
- [x] Fine-grained PAT(`agent-trend-data`のみ、`Contents: Read and
      write`のみ)を発行し、`HUB_REPO_PAT`としてリポジトリSecretsに
      登録する運用とした(発行・登録はユーザー側の手動作業。README.md
      に手順を明記)
- [x] `.github/workflows/collect-and-publish.yml`を新規作成(手動実行
      `workflow_dispatch`+週次cron)。`collect.py`実行→
      `export_hub_snapshot.py`でJSONスナップショット生成→
      `agent-trend-data`をcheckout→`snapshots/<実行日>/metrics.json`・
      `latest/metrics.json`更新→`update_hub_manifest.py`で
      `manifest.json`に実行日追記→コミット・push
      (`data: <実行日> snapshot`)
- [x] `claude` CLIのCI認証は`CLAUDE_CODE_OAUTH_TOKEN`(サブスクリプション
      認証)を採用し、CLAUDE.mdの低コスト運用方針に合わせた
      (#10の未解決論点をあわせて解消)
- [x] `agent-trend-data/schema/SCHEMA.md`はTBD(未確定)のため、
      現状の収集結果フォーマット(`report.py`の`ALL_COLUMNS`)を
      そのまま暫定採用し、ワークフロー内にコメントで明記した
- [x] `manifest.json`の日付重複追加を防ぐロジック(`update_hub_manifest
      .add_date`、setで重複排除)を実装・テストした
- [x] 収集失敗時はジョブが途中で失敗し、後続のハブへのpushが行われない
      (GitHub Actionsのステップ失敗時のデフォルト挙動)ことを確認した
- [x] 方針転換に伴い`sync_to_hub.ps1`を新規作成。collect.py実行→
      `export_hub_snapshot.py`でJSON生成→`..\agent-trend-data`配下の
      `snapshots\<実行日>\metrics.json`・`latest\metrics.json`を更新→
      `update_hub_manifest.py`で`manifest.json`更新→`agent-trend-data`
      側でcommit・pushまでを1スクリプトで実行する
- [x] `sync_to_hub.ps1`を実際に実行し、`agent-trend-data`に当日分の
      `snapshots/`・`latest/`・`manifest.json`が正しく反映され、
      pushされることを確認した(2026-09-13、20リポジトリ全件収集
      成功、コミット`5a805a2`「data: 2026-09-13 snapshot」でpush済み。
      GitHub側の`manifest.json`・`snapshots/2026-09-13/`の実在も確認)
- [ ] (将来)Fine-grained PAT発行後、`workflow_dispatch`でCI版
      ワークフローも実行確認する

**完了条件**:
1. `sync_to_hub.ps1`実行後、`agent-trend-data`に当日分のスナップショット
   と`latest/`が反映され、pushされる(達成済み、2026-09-13確認)
2. `manifest.json`が正しく更新される(達成済み、同上)
3. 収集が失敗した場合、ハブ側に不完全なデータが書き込まれない(達成済み、
   `sync_to_hub.ps1`はcollect.py失敗時に後続処理を実行しない設計、
   GitHub Actions版もステップ失敗時のデフォルト挙動により保証)

**依存**: #7(完了済み)、#15(完了済み)、#19(完了済み)

---

## #25 分析担当(playbook)からのデータ収集issue案3件への対応

**概要**: 記事作成システム側(`agent-trend-playbook`)から、収集データの
品質に関する3件のissue案がユーザー経由で届いた。実データで裏取りした上で
対応方針をユーザーと協議し、3件とも事実と判断して対応した。

**変更対象ファイル**
- `agent-trend-data/schema/SCHEMA.md`(v1.1、6フィールド追記+LLM非決定性の補足)
- `sync_to_hub.ps1`・`.github/workflows/collect-and-publish.yml`
  (snapshots上書き防止)
- `src/agent_trend_radar/github_client.py`(`get_symlink_target`新設)
- `src/agent_trend_radar/checks.py`(`_resolve_dir_path`でシンボリック
  リンク解決を追加)
- `tests/test_github_client.py`・`tests/test_checks.py`
- `README.md`

**受領した3件と対応**:

1. **SCHEMA.md未反映**: Issue #21で追加した6フィールドが
   `agent-trend-data/schema/SCHEMA.md`に未反映だった(単純な記載漏れ、
   事実確認)。→ SCHEMA.mdをv1.1に更新して対応(達成済み)。

2. **同日スナップショット上書き**: `snapshots/2026-09-13/`が同日中に
   2回(07:11→09:32)上書きされ、`agent-trend-data`のCLAUDE.md運用ルール
   (snapshots配下は追記のみ)に違反していた(事実確認)。検証の過程で、
   上書きされた差分が`agent_doc_mentions_boundaries`・
   `agent_doc_mentions_pr_review`という**LLM分類(#15)由来のフィールド
   のみ**であり、ルールベースのフィールドは一切変化していないことが
   判明。これは2つの別問題:
   - a. `sync_to_hub.ps1`/CI版ワークフローの設計バグ →
     ユーザーと協議の上、「`latest/`は常に最新内容で上書き、
     `snapshots/<日付>/`は既に存在する場合は上書きせずスキップ
     (警告のみ)」という挙動に修正した(達成済み)
   - b. LLM分類(`claude -p`)自体が同一入力に対して非決定的である
     という、より大きな方法論的論点。今回はSCHEMA.mdに既知の制限として
     記録するに留め、対応方針(temperature固定・seed指定の可否等)は
     別途協議することとした(未着手)

3. **has_skills_dir=1 かつ skills_count=0の不整合**: `getsentry/sentry`・
   `supabase/supabase`・`vercel/next.js`の3件で発生していた(事実確認、
   原因特定)。原因は`.claude/skills`という**ディレクトリ自体が
   シンボリックリンク**(3件とも`../.agents/skills`を指す)になっており、
   既存のシンボリックリンク対応(cline/cline用、ディレクトリ内の個別
   エントリがシンボリックリンクのケース)ではこの「ディレクトリそのもの
   がシンボリックリンク」というケースを解決できていなかったため。
   → `GitHubClient.get_symlink_target`と`checks._resolve_dir_path`を
   新設し、`.claude/skills`/`.claude/commands`自体がシンボリックリンク
   の場合はリンク先を解決してから数える方式に修正(達成済み、実データで
   getsentry/sentry: 0→28、supabase/supabase: 0→22、
   vercel/next.js: 0→21に修正されたことを確認)。

**タスク**
- [x] 3件とも実データで事実確認・原因特定した
- [x] #1: SCHEMA.mdをv1.1に更新(コミット`a55e383`)
- [x] #2a: `sync_to_hub.ps1`・CI版ワークフローの上書き防止ロジックを実装
- [x] #2b: LLM非決定性をSCHEMA.mdに既知の制限として記録(対応方針の
      決定は別途協議、本Issueではここまで)
- [x] #3: シンボリックリンク解決ロジックを拡張、テスト追加、全84件パス
- [ ] `sync_to_hub.ps1`を再実行し、修正後の`skills_count`が
      `agent-trend-data`に正しく反映されることを確認する(ユーザー側で実施)

**完了条件**: #1・#2a・#3が実装され、実データで妥当性を確認している
(#2bは既知の制限としての記録のみで完了とする)。

**依存**: #21(完了済み)、#24(完了済み)

---

## #26 agent-trend-data SCHEMA.mdの反映漏れを再発防止する仕組みの構築

**概要**: #25の#1で、Issue #21で追加した6フィールドが
`agent-trend-data/schema/SCHEMA.md`に反映されないまま`sync_to_hub.ps1`
で実データ連携まで進んでしまう事象が発生した。`agent-trend-data`
CLAUDE.md自身の運用ルール(「フィールドを追加・変更する際は、この
ファイルの更新をセットで行う」)があるにもかかわらず、それを機械的に
強制する仕組みがなく、人手のチェックだけに依存していたことが原因。
同種の反映漏れが再発しないよう、収集システム側のフィールド定義
(`storage.CHECK_COLUMNS`)と`agent-trend-data/schema/SCHEMA.md`の記載を
機械的に突き合わせる仕組みを構築する。

**変更対象ファイル**
- `scripts/check_hub_schema_sync.py`(新規): `storage.CHECK_COLUMNS`と
  `agent-trend-data/schema/SCHEMA.md`の「`repos` の各要素」テーブルを
  パースし、片方にしか存在しないフィールドがあれば非ゼロ終了する
- `sync_to_hub.ps1`・`.github/workflows/collect-and-publish.yml`:
  ハブへのファイル更新前にこのチェックを実行し、不一致があれば中断する
- `tests/test_check_hub_schema_sync.py`(新規)

**着手前の確認事項への回答(2026-09-14、ユーザー確認済み)**:
「SCHEMA.mdにあってCHECK_COLUMNSにない(廃止済みフィールドの記載残り)」
はエラーとして中断する方針で確定(双方向の厳密一致)。

**タスク**
- [x] SCHEMA.mdの「`repos` の各要素」テーブルの1列目
      (バッククォート内フィールド名)からフィールド名を抽出するパース
      を実装した。トップレベルの`metrics.json`テーブル
      (`generated_at`/`repos`)や`manifest.json`テーブル(`dates`)を
      誤って拾わないよう、セクション見出しでスコープを絞っている
- [x] `storage.CHECK_COLUMNS`(collect.py側の正)との差分検出ロジックを
      実装した。CHECK_COLUMNSにあってSCHEMA.mdにない→エラー、
      SCHEMA.mdにあってCHECK_COLUMNSにない(`report.META_COLUMNS`を除く)
      →エラー、の双方向とも中断する
- [x] `sync_to_hub.ps1`・CI版ワークフロー双方で、ハブのファイル更新
      (latest/snapshots上書き)前のタイミングに組み込んだ
- [x] チェックにパスしないと後続処理まで進まないことを確認した。
      実際のSCHEMA.mdから`mcp_servers_count`の記載を意図的に削除した
      コピーに対して実行し、exit code 1で中断することを確認(実ファイル
      は変更していない)
- [x] ユニットテスト5件を追加、全89件パス確認済み

**完了条件**: `storage.CHECK_COLUMNS`にフィールドを追加してSCHEMA.mdを
更新しないまま`sync_to_hub.ps1`を実行すると、ハブへのファイル更新前に
検知して中断する(達成済み、上記の意図的な不一致テストで確認)。

**依存**: #21(完了済み)、#24(完了済み)、#25(完了済み、本Issueの
発端)

---

## #27 分析担当(playbook)からのデータ収集issue案3件への対応(2回目)

**概要**: 記事作成システム側(`agent-trend-playbook`)から、収集データの
品質・指標設計に関する3件のissue案が届いた(2026-09-14、ユーザー経由)。
根拠ログ(`agent-trend-playbook/verifications/2026-09-14-rule-vs-tool-boundary/log.md`)
と実データで裏取りした上で対応方針を協議した。

**受領した3件と対応**:

1. **指示文書の"統制の強さ"を測る指標を検討する**: nuxt/nuxt(948字、
   AI自律コントリビューション禁止)がAutoGPT(3,822字、通常のコード
   スタイル規約)より明らかに強い統制なのに既存指標では差が見えない、
   という事実は確認した。提案の3案(A: キーワード一致、B: LLM分類、
   C: 新指標を追加せず記事作成側の手動読解に委ねる)のうち、以下の理由で
   **案C(新指標は追加しない)を推奨**する:
   - 案Aは「統制の強さ」という多段階・文脈依存の概念をキーワード一致
     だけでは捉えられず、既存の`agent_doc_mentions_boundaries`と実質
     同じ精度の二値フラグにしかならない
   - 案Bは#25で判明したばかりのLLM分類の非決定性(#25の#2b、未解決)を
     抱えたまま、さらにLLM依存フィールドを増やすことになる
   - 検証ログ自体が「データだけでは分からず実際に読まないと分からない
     ことがあると実感した」と結論しており、これはCLAUDE.mdの「収集は
     決定的に行い、解釈は記事作成側に委ねる」という設計方針と整合する
   - 代替として、既存の量的指標(`agent_doc_char_count`等)を統制の強さ
     の代理指標として使わないよう、SCHEMA.mdまたは
     `ANALYSIS_INSTRUCTIONS.md`に注意書きを追記することを提案する
   **対応内容(2026-09-14)**: 案Cで進めることをユーザーに確認済み。
   `agent-trend-data/schema/SCHEMA.md`(コミット`954c556`)と
   `agent-trend-radar/data/latest/ANALYSIS_INSTRUCTIONS.md`の両方に
   「文書量を統制の強さの代理指標にしない」注意書きを追記した。

2. **OpenHandsのskills検出漏れの原因を調査する**: 原因を特定した。
   OpenHandsは`.claude/skills`が存在せず`.agents/skills/`を直接使用
   しており、現行ロジックは`.claude/skills`起点でしか探索しないため
   検知できなかった。さらに調査したところ、OpenHands固有の問題では
   なく、`.agents/skills/`はAgentSkills.io等が推進する実在のクロスツール
   標準(Codex/Gemini CLI/Cursor/VS Code Copilot/Zed等が対応、Web検索で
   裏取り済み)であり、20リポジトリ中6件で`.claude/skills`とのカウント
   不一致(remix-run/remix: 0→19等)を確認した。修正範囲がOpenHands限定
   という当初想定より大きいため、**修正自体は新規Issue #28として
   切り出した**。

3. **指示文書の適用範囲(スコープ)を測る指標を検討する**: AutoGPTの
   AGENTS.mdが`autogpt_platform/`限定という主張は、実際に文書を読んで
   確認した(「This guide provides context for coding agents when
   updating the autogpt_platform folder」と明記)。ただし調査の過程で、
   AutoGPTはリポジトリ全体で21個のAGENTS.md/CLAUDE.mdを持つモノレポ
   構成であるにもかかわらず、現行の収集ロジック(`has_agent_instructions`
   /`agent_doc_*`)がルート直下のファイルしか見ていないという、より
   根本的な問題を発見した(`has_tests`が#14で対応済みの「モノレポでの
   検知漏れ」と同型のバグ)。20リポジトリ中10件でルート外に指示文書が
   あり、`continuedev/continue`は`has_agent_instructions`の真偽値自体が
   誤っていた(実際はtrueなのにfalse)。この問題を先に解決する必要が
   あるため、**提案#3は保留し、新規Issue #29(モノレポでの指示文書
   網羅性)として切り出した**。ユーザーから「モノレポ構成である傾向
   自体も指標として捉えたい」という追加要望があり、#29のスコープに
   含めた。

**タスク**
- [x] #1(統制の強さ)の対応方針(案C採用)についてユーザーの最終確認を
      得て、SCHEMA.md・ANALYSIS_INSTRUCTIONS.mdに注意書きを追記した
- [x] #2(OpenHandsのskills検出漏れ)の原因調査完了、修正はIssue #28へ
- [x] #3(指示文書のスコープ)の調査完了、より根本的な問題(モノレポ
      網羅性)を発見しIssue #29へ

**完了条件**: 3件とも対応方針が確定している(達成済み。#1は注意書き
追記で対応完了、#2・#3は後続Issueへの引き継ぎ完了)。

**依存**: #21(完了済み)、#25(完了済み)

---

## #28 skills検出ロジックを.agents/skills対応に拡張する(#27の#2から分離)

**概要**: #27の#2の調査で判明した、`.claude/skills`起点の検出だけでは
実データの多くのパターンを取りこぼす問題を修正する。`.agents/skills/`は
AgentSkills.io等が推進する実在のクロスツール標準で、`.claude/skills`は
その Claude Code向け互換レイヤ(ディレクトリ単位または個別スキル単位の
シンボリックリンク)として運用されているケースが多い。

**実データで確認したパターン(20リポジトリ中)**:
- `.agents/skills`が実体、`.claude/skills`がそこへのシンボリックリンク
  (ディレクトリ単位): getsentry/sentry, supabase/supabase, vercel/next.js
- `.agents/skills`が実体、`.claude/skills`が個別スキルごとのシンボリック
  リンク(かつ不完全な場合あり): cline/cline, apache/airflow
- `.claude/skills`が実体、`.agents/skills`がそこへのシンボリックリンク
  (逆方向): Significant-Gravitas/AutoGPT
- `.claude/skills`が存在せず`.agents/skills`のみ: OpenHands/OpenHands,
  sveltejs/svelte, astral-sh/ruff, remix-run/remix

**変更対象ファイル**
- `src/agent_trend_radar/checks.py`(`has_skills_dir`/`skills_count`の
  ロジックを`.claude/skills`・`.agents/skills`両方を見る方式に変更)
- `tests/test_checks.py`
- `SPEC.md`(既知の制限を更新)

**タスク**
- [x] `.claude/skills`・`.agents/skills`それぞれを(自身がシンボリック
      リンクの場合は解決した上で)直下要素の集合として取得し、和集合を
      取る方式に変更した(`SKILLS_DIRS`リスト化、`skills_count`は
      各候補パスの`list_immediate_children`結果を`set`で合成)
- [x] `has_skills_dir`も同様に両パスの存在を見るように修正した
      (`_any_path_exists`にリストを渡す形に変更)
- [x] `.claude/commands`側は`.agents/commands`という対応する標準が
      存在しないことをWeb調査で確認済みのため対象外とした(変更なし、
      SPEC.mdに調査結果を記載)
- [x] 実データで検証した。想定通りの値になった: remix-run/remix 0→19、
      astral-sh/ruff 0→4、OpenHands/OpenHands 0→3、apache/airflow 4→6、
      cline/cline 6→7、sveltejs/svelte 0→1。既存の正しいケース
      (sentry=28/supabase=22/next.js=21/AutoGPT=10/continue=1/zod=2/
      bun=9)は変化なしを確認
- [x] SPEC.mdの既知の制限を更新した(実データで確認した4パターンを記載)
- [x] ユニットテスト4件を追加(和集合・`.agents/skills`単独・
      `.claude/commands`非対象の確認は既存踏襲)、全92件パス確認済み

**完了条件**: 上記6リポジトリの`skills_count`が想定通りの値になり、
既存の正しいケース(sentry/supabase/next.js/AutoGPT/continue/zod)が
変化しないことをテストで保証する(達成済み、実データ・ユニットテスト
両方で確認)。

**依存**: #21(完了済み)、#25(完了済み)、#27(完了済み、本Issueの発端)

---

## #29 モノレポでの指示文書(AGENTS.md/CLAUDE.md)網羅性とモノレポ傾向の指標化(#27の#3から分離)

**概要**: #27の#3の調査で、`has_agent_instructions`/`agent_doc_*`系の
全フィールドがリポジトリルート直下のファイルしか見ておらず、サブ
ディレクトリに配置された指示文書を一切検知していないことが判明した。
`has_tests`がモノレポでの検知漏れに対応済み(#14、Git Trees APIによる
全深度探索)なのと同型のバグ。20リポジトリ中10件でルート外に指示文書が
存在し、`continuedev/continue`は`has_agent_instructions`の真偽値自体が
誤っていた(実際はtrue、現状false)。

ユーザーから、この調査を通じて「対象リポジトリにモノレポ構成が一定数
存在する」という傾向自体も指標として捉えたいという要望があった
(2026-09-14)。

**実データ(全20リポジトリ、root=ルート直下、nested=サブディレクトリの
AGENTS.md/CLAUDE.md/.cursorrules数)**:

| repo | root | nested |
|---|---|---|
| Significant-Gravitas/AutoGPT | 2 | 19 |
| apache/airflow | 2 | 14 |
| oven-sh/bun | 2 | 13 |
| getsentry/sentry | 2 | 7 |
| vercel/next.js | 2 | 6 |
| supabase/supabase | 2 | 6 |
| remix-run/remix | 2 | 3 |
| cline/cline | 1 | 2 |
| crewAIInc/crewAI | 1 | 2 |
| continuedev/continue | 0 | 1 |
| (残り10リポジトリ) | — | 0 |

**確定した設計方針(2026-09-14、ユーザー確認済み)**
- 内容分析フィールドは案B'(ルート優先、無ければ最も浅いディレクトリを
  代表として分析。複数文書の合算はしない)を採用
- `agent_doc_count`を新設。ただし当初案(ファイル数)には実データによる
  反例(`colinhacks/zod`はCLAUDE.md・AGENTS.md・`.cursorrules`をルートに
  揃えているだけでモノレポではないが、ファイル数で数えると2以上になり
  誤検知する)が見つかったため、**ディレクトリ数(重複排除)**に修正して
  確定した。対象はCLAUDE.md/AGENTS.mdのみ(`.cursorrules`は含めない)
- モノレポ傾向の指標化は案B(`agent_doc_count > 1`を代理指標として使う、
  新規API呼び出しなし)を採用。より正確な判定(ワークスペース設定検知)
  は将来の拡張候補として見送り

**変更対象ファイル**
- `src/agent_trend_radar/agent_doc_analysis.py`(`find_agent_doc_paths`・
  `agent_doc_count`新設、`fetch_agent_doc_content`の代表文書選定ロジック
  拡張)
- `src/agent_trend_radar/checks.py`(`has_agent_instructions`を全深度探索に)
- `src/agent_trend_radar/storage.py`(`CHECK_COLUMNS`に`agent_doc_count`追加)
- `scripts/collect.py`(新フィールドの呼び出し追加)
- `scripts/report.py`(`NUMERIC_COLUMNS`に追加)
- `SPEC.md`(チェック項目表・既知の制限に追記)
- `tests/test_agent_doc_analysis.py`・`tests/test_checks.py`・
  `tests/test_storage.py`・`tests/test_export_hub_snapshot.py`

**タスク**
- [x] `has_agent_instructions`を全深度探索に修正した(`get_file_paths`で
      全深度のベースネームを見る方式、`has_tests`と同型)
- [x] 内容分析フィールドの代表文書選定ロジックを実装した(ルート優先、
      無ければ最も浅い[同深度ならパス辞書順で先頭の]ディレクトリ)
- [x] `agent_doc_count`(ディレクトリ数)を新設した
- [x] SPEC.mdに反映した(全深度探索・代表文書選定ルール・
      `agent_doc_count`の定義とモノレポ代理指標としての注意点)
- [x] ユニットテスト13件を追加、全100件パス確認済み
- [x] 実データで検証した。`continuedev/continue`の`has_agent_instructions`
      がfalse→trueに改善(`extensions/cli/AGENTS.md`の内容
      [char_count=4302]も正しく取得されるようになった)。
      `colinhacks/zod`は`agent_doc_count=1`(誤検知なし)、
      Significant-Gravitas/AutoGPTは`agent_doc_count=13`・
      `char_count=3822`(ルート文書優先、既存値から変化なし)を確認。
      root文書がある既存リポジトリの`char_count`はいずれも変化なし

**完了条件**: `continuedev/continue`のような「ルートに指示文書が無い
モノレポ」で`has_agent_instructions`が正しくtrueになり、既存の
root文書を持つリポジトリの内容分析結果(`agent_doc_char_count`等)が
変化しないことを実データで確認する(達成済み)。

**依存**: #14(完了済み、同型バグの先例)、#25(完了済み)、#27(完了済み、
本Issueの発端)

---

## #30 LLM分類のキャッシュ導入と実行環境の隔離(agent-trend-playbook調査案R1+R2)

**概要**: LLM分類(#15)には2つの積み残しがある。(1) #15で未実装のままだった
キャッシュ方針: 代表文書が前回と変わっていなければLLM分類をやり直さない
仕組みがなく、#25の2bで判明したLLMの非決定性により、文書が変化していないのに
分類結果だけが変わる偽の時系列変化が起きうる。(2)
`llm_content_analysis._run_claude_cli`がサブプロセス起動時に`cwd`を指定せず
ツールも制限していないため、収集対象リポジトリとは無関係なradar自身の
CLAUDE.md/SPEC.mdが毎回の分類コンテキストに混入している可能性がある。
どちらも同じ`claude -p`呼び出しの信頼性に関わるため1つのIssueにまとめる
(agent-trend-playbookの調査ページ R1・R2、2026-09-26付)。

**変更対象ファイル**
- `src/agent_trend_radar/github_client.py`(修正: キャッシュ済みTreeエントリ
  からblob SHAを取り出すアクセサを追加。新規API呼び出しは発生させない)
- `src/agent_trend_radar/agent_doc_analysis.py`(修正: 代表文書のパス集合
  からキャッシュキー用のパス+SHA一覧を組み立てるヘルパーを追加)
- `src/agent_trend_radar/llm_content_analysis.py`(修正: 入力ハッシュ
  [パス+SHA]による前回結果の再利用、`_run_claude_cli`への`cwd`指定・
  ツール制限フラグの追加、claude CLIバージョン/モデル名/プロンプトハッシュ
  の記録)
- `src/agent_trend_radar/storage.py`(修正: トレーサビリティ用の列を追加
  する場合はここに追加。列を新設し公開するかは着手時に決める)
- `scripts/collect.py`(修正: キャッシュ判定ロジックの呼び出し)
- `tests/test_github_client.py`・`tests/test_agent_doc_analysis.py`・
  `tests/test_llm_content_analysis.py`・`tests/test_storage.py`(修正/新規)
- `agent-trend-data/schema/SCHEMA.md`(※新規に公開列を追加する場合のみ。
  #26のスキーマ整合チェックの対象)
- `SPEC.md`(修正: キャッシュ方針・既知の制限への追記)

**タスク**
- [x] (R1) `GitHubClient`のTreeキャッシュから指定パスのblob SHAを取得できる
      アクセサを追加する(新規APIコールなし)
- [x] (R1) 代表文書(1〜2ファイル、`fetch_agent_doc_content`が連結する対象)
      のパス+SHAの組からキャッシュキーを作る
- [ ] (R1) 前回のキャッシュキーが一致する場合はLLM分類を実行せず前回の
      4項目の値を再利用する — **不採用(対応内容参照、B案を採用)**
- [x] (R1) claude CLIのバージョン・分類プロンプトのハッシュを記録する
      (モデル名は見送り、対応内容参照)
- [x] (R2) 使用しているclaude CLIのバージョンで`claude --help`を確認し、
      ツール使用を無効化できるフラグの有無・名称を確定する
- [x] (R2) `_run_claude_cli`に空の一時ディレクトリを`cwd`として渡し、
      確認できたツール制限フラグを追加する
- [x] (R2) 同一の代表文書に対して「リポジトリ直下から実行」と「空
      ディレクトリ+ツール制限で実行」を数回ずつ比較し、分類結果に差が
      出るか確認する(#25の2bの非決定性の一部がこれで説明できるか含む)
- [x] 新規に公開列(キャッシュキー・CLIバージョン等)を追加する場合、
      `agent-trend-data/schema/SCHEMA.md`を同一PRで更新する(#26の対象)

**完了条件**: (1) 代表文書のSHAが前回と同じリポジトリでLLM分類が再実行
されず前回値が再利用されることをテスト・実データで確認する。(2)
`_run_claude_cli`が空の`cwd`とツール制限付きで実行されることを確認する。
(3) R2の比較実験の結果(差の有無)を本Issueに記録する。

**依存**: #15(完了済み、未実装だったキャッシュタスクの後続)、#25(完了済み、
2bのLLM非決定性は未解決のまま関連)

**対応内容(2026-09-26)**: 着手前の設計確認で、Issue原文が想定していた
「前回値を再利用してLLM分類をスキップする」方式(以下A案)は、
`repo_checks`がCI実行のたびに作り直される(run間で状態を持たない)ため、
実際に機能させるには「収集(`collect.py`)がハブ(`agent-trend-data`)の
前回スナップショットを読みに行く新しい依存」と「CIワークフローの
ハブcheckout順序の変更」が必要になることが分かった。ユーザーと協議の上、
以下のB案+(ii)を採用した(完了条件(1)は当初の「スキップされることを
確認する」から、実質的に以下の対応に置き換えている)。

- **B案**: LLM分類は毎回実行するが、入力(代表文書)のパス+blob SHAから
  作ったキー(`agent_doc_llm_cache_key`)を新規フィールドとして
  `repo_checks`/`metrics.json`に公開する。今後(#31想定)、キーが前回と
  同じなのに`agent_doc_mentions_*`(LLM分類4項目)の値が変わっていれば、
  それは文書の変更ではなく#25の2bで判明したLLMの非決定性によるものと
  機械的に判別できる。A案(呼び出し自体のスキップ)よりクロスリポジトリ
  依存・CIワークフロー変更が不要な分シンプルだが、`claude -p`の呼び出し
  回数自体は削減されない(ただしサブスク認証のため$コストへの影響はない、
  #15参照)。
- **(ii)**: claude CLIバージョン・分類プロンプトのハッシュは、1回の収集
  実行内で20リポジトリ全件が同一値になる「実行単位の事実」のため、
  `repo_checks`(リポジトリ単位)には含めず、`collect.py`が
  `data/llm_run_metadata.json`(gitignore対象、ローカルの受け渡し用)に
  一度だけ書き出し、`export_hub_snapshot.py`がそれを読んで
  `metrics.json`トップレベルの`llm_classification`に1回だけ埋め込む
  設計にした。**モデル名の記録は見送った**。`claude -p`は`--model`を
  指定しておらずCLIバージョンからは分からないため、実際に使われた
  モデル名は分類呼び出し自体のJSON出力(`modelUsage`キー)からしか
  取得できない(実行時に実測: `claude-sonnet-5`)。これを記録するには
  `classify_agent_doc_themes`の戻り値や`collect.py`との受け渡し構造を
  変える必要があり、スコープが広がるため今回は見送った(必要になれば
  別Issueで検討)。

**実施内容**:
- `github_client.py`: `get_file_sha`を追加(Treeキャッシュから取り出す
  だけで新規API呼び出しなし)
- `agent_doc_analysis.py`: `representative_doc_cache_key`を追加
  (`fetch_agent_doc_content`と同じ代表文書選定ロジックを再利用し、
  パス+SHAを`|`区切りで連結)
- `llm_content_analysis.py`: `_run_claude_cli`に空の一時ディレクトリ
  (`tempfile.TemporaryDirectory`)を`cwd`として渡し、`--tools ""`を追加。
  `classification_prompt_hash`・`get_claude_cli_version`・
  `collect_run_metadata`・`write_run_metadata`・`read_run_metadata`を追加
- `storage.py`: `CHECK_COLUMNS`に`agent_doc_llm_cache_key`(TEXT)を追加。
  `ensure_schema`が列ごとに型(TEXT/INTEGER)を出し分けるよう修正
- `scripts/collect.py`: 新フィールドの算出呼び出しと、収集完了後の
  `write_run_metadata`呼び出しを追加
- `scripts/report.py`: `format_cell`・`render_boolean_stats`に
  `storage.TEXT_COLUMNS`の分岐を追加(新フィールドが○/×判定や
  真偽値集計に誤って混ざらないようにする対応。当初のIssue案には
  無かったが、実装中に見つけた必要な追随修正)
- `scripts/export_hub_snapshot.py`: `build_snapshot`が
  `llm_run_metadata`引数を受け取り、指定時のみ`metrics.json`トップレベル
  の`llm_classification`に含めるよう修正
- `SPEC.md`・`README.md`・`agent-trend-data/schema/SCHEMA.md`(v1.3)を
  更新。`.gitignore`に`/data/llm_run_metadata.json`を追加

**確認結果**:
- テスト: 新規31件を追加し、全120件パス(`uv run pytest -q`)
- `uv run scripts/check_hub_schema_sync.py ../agent-trend-data/schema/SCHEMA.md`
  が一致を確認
- **R2比較実験(実データ、claude CLI v2.1.283で実施)**: 「あなたのシステム
  プロンプト/プロジェクトメモリに'agent-radar'や'SPEC.md'が含まれるか」を
  直接尋ねる診断プロンプトで検証した(4テーマ分類は無関係な内容の入力
  では条件間で差が出ず[3回ずつ、いずれもFalse]、診断に不向きだったため
  切り替えた)。
  - 条件A(cwd=repo root、ツール制限なし=旧挙動): 「含まれています。
    CLAUDE.mdの1行目: ...」→ **radar自身のCLAUDE.mdが実際に分類コンテキスト
    に混入することを確認**
  - 条件B(cwd=空の一時ディレクトリ、`--tools ""`=新挙動): 「該当なし」
    → 混入なしを確認
  - 条件C(cwd=repo root、`--tools ""`のみ追加): 「含まれています...」
    → **`--tools ""`単独ではCLAUDE.mdの混入は防げず、cwdの変更が本質的な
    対策であることを確認**(`--tools ""`はプロンプト注入によるツール
    実行への防御として別途有効)
- 実データで全20リポジトリの収集を実行(`data/repo_checks.db`は#29以前の
  スキーマだったため退避・再作成)。`agent_doc_llm_cache_key`が
  `has_agent_instructions=0`の3件(Aider-AI/aider,
  microsoft/autogen, yoheinakajima/babyagi)で空文字列、それ以外で
  `パス:sha`形式の値になることを確認。`export_hub_snapshot.py`実行で
  `metrics.json`トップレベルに`llm_classification`
  (`{"claude_cli_version": "2.1.283 (Claude Code)", "classification_prompt_hash": "536e..."}`)
  が含まれることを確認

**未完のタスク**: なし(A案のスキップ実装はB案採用により対象外)

---

## #31 スナップショット差分レポートの追加(agent-trend-playbook調査案R3)

**概要**: hubの`snapshots/`は2026-09-13から日次のスナップショットが蓄積
している。決定的に取得している項目(LLM分類4項目を除く)について、直近
2回のスナップショットを比較し、値が変化したリポジトリ×項目の一覧を出力
する。playbookが記事の候補を探す際の入力にする(agent-trend-playbookの
調査ページ R3、2026-09-26付)。

**変更対象ファイル**
- `scripts/diff_snapshots.py`(新規): `../agent-trend-data/snapshots/`配下の
  直近2回分の`metrics.json`を読み、決定的な項目(#30のキャッシュ導入前は
  LLM分類4項目を除外)の差分を`repo`×`項目`単位で抽出する
- `tests/test_diff_snapshots.py`(新規)
- `README.md`(実行手順の追記)

**タスク**
- [x] `../agent-trend-data/snapshots/`配下の日付ディレクトリを新しい順に
      2つ選ぶロジックを実装する(1つしかない場合は差分なしとして終了)
- [x] 決定的な項目のみを比較対象にする(#30でLLM分類4項目のキャッシュが
      導入されるまでは`agent_doc_mentions_repo_structure`等4項目を除外する)
      — 対応内容参照。#30がB案で完了したため、単純除外ではなく
      `agent_doc_llm_cache_key`を使った判別ロジックに変更した
- [x] 変化があった`repo`×`項目`×旧値→新値を人間が読めるMarkdown
      (`changes.md`)として出力する
- [x] スナップショットが1つしかない/差分がない場合の挙動を決める —
      対応内容参照

**完了条件**: 直近2回のスナップショットで値が変化した項目がある場合に
`changes.md`へ正しく出力され、変化がない項目・LLM分類4項目(#30導入前)が
含まれないことをテストで確認する。

**依存**: #24(完了済み、hubへのスナップショット連携)、#30(LLM分類4項目を
対象から除外する期間の終了条件として関連)

**対応内容(2026-09-26)**: 着手前の設計確認で、Issue原文と食い違う2点を
ユーザーと協議し、以下の方針(案A+案2)で進めた。

1. **出力先(案A)**: playbookは`agent-trend-radar`に一切関与しない設計
   (`agent-trend-playbook/CLAUDE.md`)のため、`changes.md`をこのリポジトリ
   だけに置いても実際にはplaybookから読めない。ハブ(`agent-trend-data`)
   への公開配線(`sync_to_hub.ps1`/CIワークフローの拡張)は本Issueの
   スコープ外とし、まず`data/latest/changes.md`(#19/#22と同じ、Claude
   Project公開用の慣習)に出力するに留めた。ハブへの反映は別途判断が
   必要(下記「新Issue案」参照)。
2. **LLM4項目の扱い(案2)**: Issue原文は「#30のキャッシュ導入までは
   除外」としていたが、#30は「スキップ」ではなくB案(非決定性の検出を
   可能にする`agent_doc_llm_cache_key`の公開)で完了したため、単純な
   期限付き除外ではなく、`agent_doc_llm_cache_key`が両スナップショットに
   存在し値が同じ場合はLLM4項目の変化を非決定性の疑いとして除外、
   キーが変わっていれば通常の変化として含める、キーがどちらかに
   存在しない場合(#30より前のスナップショット同士)は無条件で除外する
   ロジックにした(`diff_snapshots.diff_snapshots`)。
3. **0/1件・差分なしの場合の挙動**: 比較可能なスナップショットが2件
   未満の場合はファイルを生成せずメッセージ表示のみで終了する(既存の
   `changes.md`を誤って上書き・削除しない)。2件あって差分が無い場合は
   「変化した項目はありませんでした。」という内容の`changes.md`を出力する
   (空ファイルにはしない)。

**実施内容**: `scripts/diff_snapshots.py`(新規)を実装。`list_snapshot_dates`
/`select_latest_two_dates`/`load_snapshot`/`diff_snapshots`/
`format_changes_markdown`/`build_report`の純粋関数群+CLI(`main`)構成。
LLM分類4項目の判定は`llm_content_analysis.CLASSIFICATION_FIELDS`を再利用
し、独自の重複リストは作らなかった。README.mdに実行手順を追記した。

**確認結果**:
- テスト: `tests/test_diff_snapshots.py`を新規15件追加、全135件パス
  (`uv run pytest -q`)
- 実データ確認: `uv run scripts/diff_snapshots.py`を実行し、実在する
  `agent-trend-data/snapshots/2026-09-13`→`2026-09-14`(#30より前、
  cache keyフィールドなし)を比較。20件の変化を検出し、すべて#25・#28・
  #29で実際に変更されたと記録済みの値と一致することを確認した(例:
  `continuedev/continue`の`has_agent_instructions 0→1`[#29]、
  `getsentry/sentry`の`skills_count 0→28`[#25の#3]、`OpenHands/OpenHands`
  等の`has_skills_dir 0→1`[#28])。LLM分類4項目の変化は0件で、意図通り
  除外されていることを確認した。`agent_doc_llm_cache_key`自体が単独の
  変化行として出力されないことも確認済み(現時点ではこの2スナップショット
  にはそもそもこのフィールドが存在しないため、フォールバック経路の実証)

**未完のタスク**: なし。ただしハブへの公開配線(下記「新Issue案」)は
このIssueのスコープ外として見送った。

---

## #32 未知のエージェント関連規約パスの検出(agent-trend-playbook調査案R4)

**概要**: `.agents/skills`はplaybookが手動で気づいて発覚した(#27・#28)。
既存のキャッシュ済みTreeから、既知のチェック対象パス一覧にない、エージェント
関連と思われるパスをリポジトリごとに件数付きで一覧化し、同種の見落としを
決定的に拾えるようにする。チェック項目に昇格させるかは人間が判断する
(agent-trend-playbookの調査ページ R4、2026-09-26付)。

**変更対象ファイル**
- `src/agent_trend_radar/unknown_paths.py`(新規): 候補パスのリストと、
  `GitHubClient.get_file_paths`/`get_directory_names`から件数を集計する関数
- `scripts/detect_unknown_paths.py`(新規): 20リポジトリ分を集計し
  `reports/unknown_agent_paths.md`に出力する
- `tests/test_unknown_paths.py`(新規)

**タスク**
- [x] 候補パスの初期リストを確定する(ページ提案の`.cursor/`、
      `.github/copilot-instructions.md`、`.github/instructions/`、
      `.clinerules/`、`.windsurfrules`、`GEMINI.md`、`.openhands/`、
      `.claude/agents/`に加え、#21の「将来の拡張候補」記載分と重複整理する)
      — 対応内容参照。最終的に9件に確定
- [x] 各候補パスをディレクトリ/ファイルいずれかとして件数付きで判定する
      ロジックを実装する(新規API呼び出しなし、既存Treeキャッシュを再利用)
- [x] 20リポジトリ分を集計し、リポジトリ×候補パス×件数の表を
      `reports/unknown_agent_paths.md`に出力する
- [x] 候補にないが実データで見つかった意外なパスがあれば本Issueに記録する
      — 対応内容参照(候補リスト自体には無かったが、`.clinerules`/
      `.github/copilot-instructions.md`の実際の広がりが分かった)

**完了条件**: 20リポジトリ分の集計結果が`reports/unknown_agent_paths.md`に
出力され、既存のチェック対象パス(SPEC.md記載分)が候補から除外されている
ことを確認する。

**依存**: #21(完了済み、「将来の拡張候補」として`.claude/agents/`・
`.cursor/rules/`が既出)、#28(完了済み、`.agents/skills`発見の先例)

**対応内容(2026-09-27)**: 着手前の設計確認で以下の点をユーザーと協議し、
確定した。

1. **候補パスリスト(9件)**: ページ提案の`.cursor/`(ディレクトリ全体)は
   採用せず、#21の表記に合わせて`.cursor/rules`(AIルール専用のサブパス)
   のみを候補とした。Windsurfは`.windsurfrules`(単一ファイル)から
   `.windsurf/rules`(ディレクトリ)への移行が進んでいるため両方を候補に
   含めた。最終候補: `.cursor/rules`、`.github/copilot-instructions.md`、
   `.github/instructions`、`.clinerules`、`.windsurfrules`、
   `.windsurf/rules`、`GEMINI.md`、`.openhands`、`.claude/agents`。
2. **件数の定義**: ディレクトリ型は配下の全ファイル数を再帰的にカウント
   (`skills_count`の「直下の子要素数」とは異なる。探索的な検出のため、
   各ツールのサブディレクトリ規約を個別に調べ込む価値は薄いと判断し、
   シンプルな再帰カウントに統一した)。ファイル型は存在すれば1、無ければ0。
3. **API呼び出し**: `collect.py`とは別プロセスのため、実行するとリポジトリ
   ごとに1回Tree APIを叩く(20リポジトリで20コール)。候補パス数を増やしても
   1リポジトリあたりの追加コールは発生しない、という意味での「新規API
   呼び出しなし」であることを確認した。今回は試験的な調査のため許容し、
   正式なチェック項目に昇格する場合にコール数の節約を検討することとした。
4. **実行形態**: `collect.py`の週次パイプラインには組み込まない、手動実行
   の一回限りの調査スクリプト(`reports/api_cost_evaluation.md`等と同じ
   位置づけ)とした。

**実施内容**: `src/agent_trend_radar/unknown_paths.py`(新規、候補パス
リスト+`count_candidate`/`detect_unknown_paths`)、
`scripts/detect_unknown_paths.py`(新規、20リポジトリ分を集計し
`reports/unknown_agent_paths.md`に出力)を実装。

**確認結果**:
- テスト: `tests/test_unknown_paths.py`・`tests/test_detect_unknown_paths.py`
  を新規16件追加、全144件パス(`uv run pytest -q`)
- 実データ確認(`uv run scripts/detect_unknown_paths.py`、GITHUB_TOKEN
  利用可能な環境で実施): `reports/unknown_agent_paths.md`を生成。9候補パス
  はいずれもSPEC.md記載の既存チェック対象パスと重複していないことを確認
  (完了条件達成)。実データでの発見:
  - `cline/cline`の`.clinerules`配下に16ファイル(自社ツールを自ら
    多用している例)
  - `.github/copilot-instructions.md`が4リポジトリ
    (Significant-Gravitas/AutoGPT, microsoft/autogen, cline/cline,
    supabase/supabase)に存在
  - `apache/airflow`の`.github/instructions`に1ファイル、
    `OpenHands/OpenHands`の`.openhands`に1ファイル
  - `.cursor/rules`・`.windsurfrules`・`.windsurf/rules`・`GEMINI.md`・
    `.claude/agents`は20リポジトリ中いずれも0件
  - 候補リストの外で目視上「意外」と感じるパスは見つからなかった
    (Q4での確認どおり、自動検出の対象は固定候補リストに限定しているため、
    候補外の発見は本質的にできない設計であることに留意)

**未完のタスク**: なし。`.github/copilot-instructions.md`(4/20)・
`.clinerules`(1/20だが16ファイル)をチェック項目に昇格させるかどうかは
今回判断せず、人間の判断に委ねる。

**追記(2026-09-27)**: 上記の結果を踏まえ、ユーザーが「現時点では正式な
チェック項目にする必要はない」と判断した。理由は出現率が低い(候補9件中
2件のみ、うち`.github/copilot-instructions.md`も4/20)ためと考えられる。
再検討する場合は、対象リポジトリの追加・入れ替え(#13)後に本Issueの
`reports/unknown_agent_paths.md`を再実行して傾向を見直すとよい。

---

## #33 規約ファイル初出コミット日による採用ラグの計測方法の検討(agent-trend-playbook調査案R5)

**概要**: Commits APIにパスを指定すると、`AGENTS.md`・`.agents/skills`・
`.claude/settings.json`等の既知パスをリポジトリが最初にコミットした日付が
取得できる。「機能がリリースされてから実プロジェクトで採用されるまでの
時間差」を示せる、radar独自の切り口になりうる(agent-trend-playbookの
調査ページ R5、2026-09-26付)。ただし、この値は取得対象パスが存在する限り
不変の事実であり、週次で値が変わりうる既存の`repo_checks`とは性質が
異なるため、保存・公開方法を実装前に決める必要がある。

**タスク**
- [ ] 対象パス集合を確定する(#32の結果次第で見直す可能性あり)
- [ ] Commits APIでの初出コミット日取得方法を確定する。一覧APIは新しい順
      にしか返さないため、`per_page=1`で1ページ目を取得しLinkヘッダーから
      総ページ数(=コミット数)を得た上で最終ページを取得する、1パスあたり
      2回のAPIコール設計とする(ファイル名変更は追えない制約は許容する)
- [ ] API呼び出し数の見積もりを更新する。上記2回/パス設計で20リポジトリ×
      パス数を計算し、`reports/api_cost_evaluation.md`(2026-09-07時点、
      Tree API導入[#14/#21]前の呼び出し構成が前提で現状と前提が異なる
      点に注意)と#11(レート制限・エラーハンドリング強化、未着手)を
      踏まえて確認する
- [ ] 「値が変わらない事実」の保存・公開方式を設計する(候補:
      `repo_checks`とは別の一回限りのテーブル/エクスポート、週次収集の
      たびに再取得しない仕組みなど)。低コスト・シンプルさ優先の方針
      (CLAUDE.md)に沿い、毎週同じ事実を再取得しないキャッシュ方針を含める
- [ ] 設計が決まった時点で実装型Issueとして切り出すか、本Issueで継続する
      かを判断する

**完了条件**: 対象パス・API呼び出し設計・保存方式の3点が決まり、実装に
着手できる状態になっている。

**依存**: #11(未着手、レート制限・エラーハンドリング強化と関連)、
#13(未着手、対象リポジトリ追加時の前提と関連)、#32(未知パス検出の結果
次第で対象パスを見直す可能性)

---

## #34 フィードフォワード/フィードバックの集計ビューの追加(agent-trend-playbook調査案R6)

**概要**: 既存のチェック項目を「フィードフォワード(事前に指示するもの:
指示文書・skills・commands・MCP)」と「フィードバック(事後に検証する
もの: tests・CI・hooks・eval)」に分け直した集計を`scripts/report.py
--format stats`に追加する。新規のデータ収集・スキーマ変更は伴わない、
既存項目の表示上の分類追加(agent-trend-playbookの調査ページ R6、
2026-09-26付)。

**変更対象ファイル**
- `scripts/report.py`(修正: 既存項目をフィードフォワード/フィードバック
  の2群に分類する定数を追加し、`--format stats`にsegment×
  monetization_model別の群別集計を追加する)
- `tests/test_report.py`(修正)

**タスク**
- [ ] 既存項目をフィードフォワード群(`has_agent_instructions`、
      `has_skills_dir`/`skills_count`、`has_custom_commands`/
      `custom_commands_count`、`mcp_servers_count`等)とフィードバック群
      (`has_tests`、`has_eval`、`has_ci`、`has_hooks_config`等)に分類する
      対応表を定義する(#20で天井/床効果が指摘されている`has_ci`を
      どちらに含めるか、既存議論と矛盾しないか確認する)
- [ ] `--format stats`に群別の集計(例: 群別true率平均、segment×
      monetization_model別)を追加する
- [ ] 既存の`--format stats`出力(項目別集計)を壊さないことを確認する

**完了条件**: `--format stats`で既存の項目別集計に加え、フィードフォワード
/フィードバック群別の集計が出力され、既存テストに加えて群分類のテストが
通ることを確認する。

**依存**: #20(未着手、`has_ci`等の解釈と関連)、#21(完了済み、群分類の
対象項目の多くがここで追加されたもの)

---

## #35 LLM分類で実際に使用されたモデル名の記録(#30から見送り分)

**概要**: #30でLLM分類(`claude -p`)呼び出しのトレーサビリティ用メタデータ
(`llm_classification`、claude CLIバージョン・分類プロンプトのハッシュ)を
`metrics.json`トップレベルに追加した際、モデル名の記録は見送った。
`_run_claude_cli`は`--model`を指定していないため、使用モデルはCLI
バージョンからは分からず、分類呼び出し自体のJSON出力
(`modelUsage`キー、#30の実行時確認で`claude-sonnet-5`を確認)からしか
取得できない。これを記録できるようにする。

優先度は低い(トレーサビリティの補強であり、既存項目の分析には影響しない)。

**変更対象ファイル**
- `src/agent_trend_radar/llm_content_analysis.py`(修正: `_run_claude_cli`
  の生JSON出力から`modelUsage`のキー[モデル名]を取り出すヘルパーを追加し、
  `classify_agent_doc_themes`が4項目の分類結果と合わせてモデル名も返す
  よう戻り値構造を変更する)
- `scripts/collect.py`(修正: 各リポジトリの分類呼び出しで得たモデル名を
  集約し、`collect_run_metadata`/`write_run_metadata`に渡す)
- `tests/test_llm_content_analysis.py`(修正/新規)
- `SPEC.md`・`agent-trend-data/schema/SCHEMA.md`(`llm_classification`に
  `model_name`等を追記)

**タスク**
- [ ] `_run_claude_cli`のJSON出力(`modelUsage`)からモデル名を取り出す
      ヘルパーを追加する
- [ ] `classify_agent_doc_themes`の戻り値構造を、4項目の分類結果と
      モデル名を両方返せるように変更する(呼び出し側`collect.py`への
      影響を確認する)
- [ ] 1回の収集実行内で20リポジトリ全件のモデル名が一致する前提で
      よいか、異なる場合にどう扱うか(複数値を記録する/警告する等)を
      着手時に決める
- [ ] `collect.py`が収集完了後、実際に使われたモデル名を
      `llm_classification`に含めて記録するようにする
- [ ] `SPEC.md`・`agent-trend-data/schema/SCHEMA.md`を更新する

**完了条件**: 実データで収集を実行し、`metrics.json`の`llm_classification`
に実際に使用されたモデル名(例: `claude-sonnet-5`)が記録されることを
確認する。

**依存**: #30(完了済み、モデル名記録を見送った経緯)

---

## #36 スナップショット差分レポートのハブへの公開(#31から見送り分)

**概要**: #31で`scripts/diff_snapshots.py`を実装したが、出力先は
`agent-trend-radar/data/latest/changes.md`に留めた。`agent-trend-playbook`
は`agent-trend-radar`に一切関与しない設計(`agent-trend-playbook/CLAUDE.md`
「このリポジトリはagent-trend-radarには一切関与しない」)のため、このまま
では`changes.md`をplaybookが実際に読めない。ハブ(`agent-trend-data`)へ
公開する配線を追加し、#31が本来意図していた「playbookが記事の候補を
探す際の入力にする」を実現する。

**変更対象ファイル**
- `sync_to_hub.ps1`(修正: `scripts/diff_snapshots.py`を実行し、
  `data/latest/changes.md`を`..\agent-trend-data\latest\changes.md`へ
  コピーするステップを追加)
- `.github/workflows/collect-and-publish.yml`(修正: 同様のステップをCI版にも追加)
- `agent-trend-data/CLAUDE.md`(修正: `latest/`の説明に`changes.md`が
  含まれることを追記。ディレクトリツリーの変更は伴わない想定)
- `README.md`(修正: hubへの連携手順の説明に追記)

**タスク**
- [ ] `changes.md`の公開先を`agent-trend-data/latest/changes.md`とする
      (`snapshots/<date>/`配下への保存は行わない。理由: `changes.md`は
      「直近2回の差分」という導出データであり、過去のペアごとの差分を
      履歴として保存する需要は今のところ無いため。`snapshots/`自体は
      引き続き完全な生データを保持しているので、過去の任意の2時点間の
      差分はそこから再計算できる)
- [ ] `sync_to_hub.ps1`に`diff_snapshots.py`実行とコピーのステップを追加する
      (`latest/metrics.json`の上書きと同様、`changes.md`も毎回上書きでよい
      と判断した理由も含め記録する)
- [ ] `.github/workflows/collect-and-publish.yml`に同様のステップを追加する
- [ ] `agent-trend-data/CLAUDE.md`に`changes.md`の説明を追記する
- [ ] 実データで`sync_to_hub.ps1`を実行し、`agent-trend-data/latest/changes.md`
      が生成されることを確認する

**完了条件**: `sync_to_hub.ps1`(またはCIワークフロー)を実行すると、
`agent-trend-data/latest/changes.md`が最新の差分内容で生成・更新される
ことを実データで確認する。

**依存**: #31(完了済み、`diff_snapshots.py`本体)、#24(完了済み、hub連携の基盤)

---

## #37 収集失敗の可視化・追跡(#11から見送り分)

**概要**: `reports/api_cost_evaluation.md`が指摘していた「週次自動実行
(#10)でリポジトリの収集が失敗した場合、そのリポジトリのデータが古い
まま気づかれずに残り続ける」問題。`collect.py`は失敗したリポジトリを
スキップして次に進む設計で(#11で維持、合理的な設計として変更せず)、
新しい行が挿入されないだけなので、`report.py`の「最新の`checked_at`」
クエリは黙って古い行を返し続ける。#11でエラー自体はログファイル
(`data/collect.log`、実行間で追記され続ける。ローテーション等は未実装)
に残るようになったが、「どのリポジトリのデータが実際にはどれだけ古いか」
を人間が能動的に確認できる形にはなっていない。

**タスク**
- [ ] 着手時に詳細を定義する。候補(いずれか、または組み合わせ):
  - `report.py`の出力に各リポジトリの`checked_at`(最終更新日)を含め、
    一定期間(例: 2週間)以上更新されていないリポジトリを目視で分かる
    形にする
  - `collect.py`が収集完了後、その回に失敗したリポジトリの一覧を
    `data/latest/`配下に出力する(Claude Project公開データに含める)
  - 上記いずれも実装せず、`data/collect.log`を人間が定期的に確認する
    運用でよいと判断し、本Issueを中止する
- [ ] 低コスト・シンプルさ優先の方針(CLAUDE.md)に照らし、新しい仕組みを
      追加する価値があるかを判断する(現状、収集失敗は実測で稀
      [#11の実データ確認で1件のネットワーク断が発生したが自動リトライで
      解消済み]なため、過剰な仕組みにならないよう注意する)

**完了条件**: 着手時に別途定義する。

**依存**: #11(完了済み、エラーログ出力の基盤)
