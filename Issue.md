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

## MVP後(参考・着手はMVP振り返り後に判断)

- [ ] #10 GitHub Actions週次cron化
- [ ] #11 レート制限・エラーハンドリングの強化
- [ ] #12 LLMによる要約・記事生成
- [ ] #13 対象リポジトリ追加・入れ替えのフロー整備
- [x] #16 has_observability_depのsegment適用範囲の見直し
      (MVP品質評価で発見、2026-09-07 項目自体を廃止してクローズ、
      詳細は末尾セクション参照)
- [ ] #17 分析結果を要約・記事化する際の統計的な注意点整理
      (MVP品質評価で発見、#12着手時の前提条件、詳細は末尾セクション参照)
- [ ] #18 可観測性指標の測り方の再設計(#16で発見)
      (詳細は末尾セクション参照)
- [x] #14 モノレポ/組織継承ファイルの扱い見直し(#4実装中に発見、
      2026-09-07 has_tests対応完了・has_security_policyは対応せずクローズ)
      トップレベル直下のみのパス存在チェックでは、モノレポ構成の
      リポジトリ(langchain-ai/langchain, apache/airflow等)で実際には
      サブディレクトリ配下にtests/があっても`has_tests=false`になる。
      また`SECURITY.md`がGitHub組織の`.github`特別リポジトリに置かれ
      継承表示されているケース(apache/airflow, langchain-ai/langchain等)
      も、対象リポジトリ自体には存在しないため`has_security_policy=false`
      になる。

      **#9実データ通し実行(2026-09-06)による裏付け**: 20リポジトリ中
      16件で`has_tests=false`となり、うち少なくとも
      astral-sh/ruff、langchain-ai/langchain、apache/airflow、
      supabase/supabase、crewAIInc/crewAI、continuedev/continue、
      microsoft/autogenの7件はGitHub API上で実際にモノレポ構造
      (crates/、libs/、providers/、packages/等)であることを確認済み
      (テスト自体が存在しないと確認できたのはyoheinakajima/babyagiのみ)。
      さらにvercel/next.jsはルート直下に`tests`ではなく`test`(単数形)の
      ディレクトリを持つため、モノレポ云々ではなく命名バリエーションのみで
      falseになるケースも確認した。`has_security_policy`についても
      apache/airflow、langchain-ai/langchainの2件で予想通りfalseになる
      ことを確認した。

      **対応内容(2026-09-07)**: `has_tests`はGit Trees API
      (`GET /repos/{owner}/{repo}/git/trees/HEAD?recursive=1`)で
      リポジトリ全体のディレクトリ名を1リクエストで取得し、任意の深さで
      `tests`または`test`という名前のディレクトリが存在するかを判定する
      方式に変更(`github_client.py`の`get_directory_names`、
      `checks.py`の`has_tests`)。対象20リポジトリいずれもGitHub側の
      truncated制限(7MB/10万エントリ)には該当しないことを事前確認済み。
      実データ再実行の結果、20リポジトリ中19件がtrueに改善(false は
      実際にテストが存在しないyoheinakajima/babyagiのみ)。
      `has_security_policy`の組織`.github`継承問題は対応せず、SPEC.mdの
      既知の制限として文書化のみでクローズすることをユーザーと合意した。

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
記事生成)着手時に踏まえるべき前提条件としてまとめる。

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

**タスク(たたき台、着手時に確定する)**
- [ ] #12の記事生成プロンプト・レビューチェックリストに上記3点を
      組み込む
- [ ] `scripts/report.py`の出力(またはその後段)で、対象項目については
      中央値・分布も出力できるようにするか検討する

**依存**: #9(完了済み)、#12(未着手)

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

**検討の方向性(たたき台、着手時に確定する)**
- そもそも「運用の実践知」の別の側面(has_ci等)で既にある程度代替
  できているため、無理に復活させる必要があるか自体を再検討する
- 復活させる場合、依存マニフェストではなく`docs/`・`examples/`での
  言及や、実際の統合方法(webhook/callback設定等)を見るアプローチが
  考えられるが、CLAUDE.mdのシンプルさ優先方針(複雑な依存パーサは
  作らない)との整合を要検討
- toolセグメントとadopterセグメントで別々の指標を持つべきか
  (adopter向けにはAPM/エラートラッキング等、別カテゴリの運用指標を
  検討する余地がある)

**完了条件**: 着手時に別途定義する。

**依存**: #16(完了済み)
