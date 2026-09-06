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

## #5 SQLite永続化実装

**概要**: SPEC.mdのデータスキーマに沿って `repo_checks` テーブルを作成し、
チェック結果を保存する。

**変更対象ファイル**
- `src/agent_trend_radar/storage.py`(新規)
- `tests/test_storage.py`(新規)
- `.gitignore`(`data/*.db` 追加、必要なら)

**タスク**
- [ ] `repo_checks` テーブルのスキーマ定義(repo, category, checked_at,
      各チェック項目キー)
- [ ] テーブル作成処理(存在しなければ作成)
- [ ] 1リポジトリ分の結果をINSERTする関数
- [ ] SQLiteファイルの保存先を決定(`.gitignore`対象であることを確認)

**完了条件**: スクリプトを2回実行すると、レコードが2回分(実行日ごと)
蓄積されることを確認できる。

**依存**: #1

---

## #6 収集スクリプトの統合

**概要**: 対象リポジトリ一覧の読み込み→チェック実行→SQLite保存までを
1コマンドで実行できるようにする。

**変更対象ファイル**
- `scripts/collect.py`(新規)
- `src/agent_trend_radar/config.py`(新規、対象リポジトリ設定の読み込み)

**タスク**
- [ ] `uv run scripts/collect.py` のようなエントリポイントを作成
- [ ] #2の対象リポジトリ設定を読み込む
- [ ] #4で実装した6項目のチェック関数をまとめて実行する集約処理を実装する
      (#4では個々の判定関数のみを実装し、集約は#6の責務とした)
- [ ] 各リポジトリに対し上記の集約処理を実行
- [ ] #5の保存処理を呼び出す
- [ ] 実行ログ(進捗・エラー)を標準出力に出す

**完了条件**: 1コマンドで全対象リポジトリのチェックが完走し、SQLiteに
結果が残る。

**依存**: #2, #4, #5

---

## #7 結果ビューア(Markdown表 / CSV出力)

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

**完了条件**: 生成したMarkdown表を見て、企業/個人プロジェクト間の違いが
一目で読み取れる。

**依存**: #5, #6

---

## #8 実データでの通し実行・振り返り

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

**依存**: #6, #7

---

## MVP後(参考・着手はMVP振り返り後に判断)

- [ ] #9 GitHub Actions週次cron化
- [ ] #10 レート制限・エラーハンドリングの強化
- [ ] #11 LLMによる要約・記事生成
- [ ] #12 対象リポジトリ追加・入れ替えのフロー整備
- [ ] #13 モノレポ/組織継承ファイルの扱い見直し(#4実装中に発見)
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
