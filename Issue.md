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
- [ ] #11 レート制限・エラーハンドリングの強化
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
- [ ] #21 高度なエージェント運用ツール導入の有無チェック項目の追加
      (#15議論中に発見)
- [x] #22 #19の公開データにCLAUDE.md/AGENTS.mdの本文を含める —
      2026-09-08 #19に統合して実装完了(詳細は末尾セクション参照)
- [ ] #23 PR品質・レビュー通過率・インシデント率等のアウトカム指標の
      収集検討(#15議論中に発見、未解決の方法論的課題あり)
- [x] #24 agent-trend-dataへの連携機能を実装する — 2026-09-13
      PAT発行に時間がかかるためローカルスクリプト(`sync_to_hub.ps1`)
      連携に方針転換、実装・実行確認完了(CI版はPAT発行後に別途確認、
      詳細は末尾セクション参照)

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
- [ ] 着手時に詳細を定義する

**完了条件**: 着手時に別途定義する。

**依存**: #3(完了済み)

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

**タスク**(たたき台、着手時に確定する)
- [ ] 候補パスを確定する(例: `.claude/commands/`, `.claude/skills/`,
      `.claude/agents/`, `.mcp.json`, `.cursor/rules/`等。エージェント
      ツールによってパスの慣習が異なる点に注意)
- [ ] Git Trees API(#14で導入済みの`get_directory_names`)を使うか、
      個別パスのContents API確認で足りるかを判断する
- [ ] SPEC.mdのチェック項目表に追記する

**完了条件**: 着手時に別途定義する。

**依存**: #4(完了済み)、#14(完了済み)

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
