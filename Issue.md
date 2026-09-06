# Issue.md

MVP完成までのタスクリスト。各項目はGitHub Issue化する単位を想定した粒度で
書いている。詳細方針は @Development_plan.md、仕様は @SPEC.md を参照。

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
- [ ] `uv run scripts/collect.py` のようなエントリポイントを作成
- [ ] #2の対象リポジトリ設定を読み込む
- [ ] #4(ファイル存在6項目)と#5(内容分析8項目)のチェック関数をまとめて
      実行する集約処理を実装する(#4/#5では個々の判定関数のみを実装し、
      集約はこのIssueの責務とした)
- [ ] 各リポジトリに対し上記の集約処理を実行
- [ ] #6の保存処理を呼び出す
- [ ] 実行ログ(進捗・エラー)を標準出力に出す

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
- [ ] SQLiteから最新のチェック結果を読み出す処理
- [ ] リポジトリ×項目のマトリクスをMarkdown表として出力
- [ ] 同内容をCSVでも出力できるようにする(任意)
- [ ] 出力をファイルに保存する簡単なCLI(例:
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
- [ ] `uv run scripts/collect.py` を実行し、全対象リポジトリの結果を
      収集する
- [ ] `uv run scripts/report.py` で表を生成し、目視確認する
- [ ] チェック項目・対象リポジトリの妥当性についてメモを残す
      (SPEC.mdの見直し方針に沿って更新するかどうかの判断材料)
- [ ] README.mdに実行手順を追記する

**完了条件**: 生成された表を見て「次に何を見直すべきか」が言語化できて
いる。

**依存**: #7, #8

---

## MVP後(参考・着手はMVP振り返り後に判断)

- [ ] #10 GitHub Actions週次cron化
- [ ] #11 レート制限・エラーハンドリングの強化
- [ ] #12 LLMによる要約・記事生成
- [ ] #13 対象リポジトリ追加・入れ替えのフロー整備
- [ ] #14 モノレポ/組織継承ファイルの扱い見直し(#4実装中に発見)
      トップレベル直下のみのパス存在チェックでは、モノレポ構成の
      リポジトリ(langchain-ai/langchain, apache/airflow等)で実際には
      サブディレクトリ配下にtests/があっても`has_tests=false`になる。
      また`SECURITY.md`がGitHub組織の`.github`特別リポジトリに置かれ
      継承表示されているケース(apache/airflow, langchain-ai/langchain等)
      も、対象リポジトリ自体には存在しないため`has_security_policy=false`
      になる。MVPでは意図的な割り切り(CLAUDE.mdのスコープ方針)として
      許容しているが、結果を解釈する際にこの制約を明記する必要がある。
      対応するなら「一段階だけ再帰的に探索する」「組織の.github repoも
      チェックする」等の拡張が考えられるが、いずれもスコープ拡大になる
      ため要検討

---

## #15 LLMによるCLAUDE.md/AGENTS.md内容分析(MVP後)

**概要**: #5のルールベース構造分析(キーワード一致)には、
`reports/agent_doc_analysis_validation.md`で検証した通り明確な限界がある
(PR/コミット規約や「してはいけないことの境界線」等、表現のバリエーション
が大きいテーマを取りこぼす)。この限界を踏まえ、MVP完成後にLLMを使った
内容分析を追加する。ユーザー判断により、コストをかけてでも実施する価値が
あると判断された。

**背景・参照**
- `reports/agent_doc_analysis_validation.md`(発見2・発見3のセクション)
- CLAUDE.mdの「LLM利用」欄(要約・記事生成に加えこの用途も追記済み)

**スコープ(たたき台、着手時に確定する)**
- [ ] レポートで指摘した見逃しテーマ(リポジトリ構造説明、してはいけない
      ことの境界線、PRレビュー基準・人間チェックポイント、リリース手順)を
      LLMでカテゴリ分類できるか検証する
- [ ] #5のルールベース8項目を置き換えるのか、併存させるのかを決める
- [ ] 低コストモデルの選定(CLAUDE.mdの「低コスト優先のモデルを使う」
      方針に従う)
- [ ] 20リポジトリ分の分析コストを試算し、運用可能な範囲か確認する
      (CLAUDE.mdの「低コスト運用必須」制約との整合性確認)
- [ ] プロンプト設計とキャッシュ方針(同一内容の再分析を避ける)

**完了条件**: 着手時に別途定義する。

**依存**: #5(完了済み)、MVP(#1〜#9)の完了
