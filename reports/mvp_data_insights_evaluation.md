# MVP収集データからの示唆・信頼度評価レポート

**調査日**: 2026-09-07
**調査範囲**: SPEC.md記載の6ファイル存在チェック項目 + 8つのCLAUDE.md/AGENTS.md
内容分析項目から、実際に「AIエージェントツールがどう使われているか」の
示唆が得られるかどうかの評価
**調査対象**: `config/targets.yaml`記載の全20リポジトリの最新チェック結果
(`data/repo_checks.db`)
**方針**: 各項目の生データを鵜呑みにせず、(1)集計結果に外れ値・選定バイアス
による歪みがないか、(2)セグメント間で分散が十分にあり比較材料として
機能しているか、の2点を個別に検証したうえで、項目ごとに示唆の信頼度を
3段階(十分/条件付き/限定的)で評価する。

## 方法論

- `data/repo_checks.db`から各リポジトリの最新チェック結果を抽出し、
  segment別・monetization_model別・両軸のクロス集計を行った。
- 平均値のみで判断せず、外れ値の影響を疑う項目については中央値・分布
  (min/max)も算出して比較した。
- segment間比較については、SPEC.mdの対象リポジトリ選定基準
  (「adopterはCLAUDE.md/AGENTS.md等の採用が公知の事例のみを選ぶ」)に
  照らして、比較軸そのものが選定バイアスの影響を受けていないかを確認した。

## 評価結果サマリ

| 項目 | 評価 | 理由 |
|---|---|---|
| has_security_policy | 十分 | 40%前後で適度な分散があり、既知の限界(Issue #14)の影響も限定的 |
| has_agent_instructions | 十分(比較軸に注意) | segment間比較は選定バイアスで無効。monetization軸(tool内限定)では有効 |
| agent_doc_char_count / heading_count | 条件付き | 平均は外れ値に強く感応。中央値ベースなら方向性は維持 |
| agent_doc_mentions_test / lint / tool_usage | 条件付き | 傾向把握には十分。個別リポジトリ評価にはキーワード一致の既知の限界が残る |
| has_ci | 限定的 | 90〜100%で天井効果。比較材料としての情報量が乏しい |
| agent_doc_has_code_block | 限定的 | セグメント間の差が小さく(67% vs 70%)弁別力が低い |
| has_tests | 不可(既知の問題) | ルート直下限定チェックの検知漏れ。Issue #14で追跡中 |
| has_observability_dep | 不可(既知の問題) | 全20件中1件のみtrue。Issue #16で追跡 |

## 十分な示唆が得られた項目

### has_security_policy
tool・adopterともに約40%(各10件中4件)で、0%/100%に張り付かない
適度な分散があり比較材料として機能した。Issue #14の「組織`.github`
特別リポジトリへの継承」問題の影響対象はapache/airflow、
langchain-ai/langchainの2件に限られ、全体傾向を歪めるほどではない。

**考察**: エージェントに大きな権限を与える文脈が広がる一方、
`SECURITY.md`のような形式知の整備は半数程度にとどまっている。

### has_agent_instructions(monetization軸・tool限定で検証)
前回の「adopter 100% vs tool 60%」という比較は、SPEC.mdの選定基準上
adopterが最初から100%になるよう選ばれているため無効と判断した。
選定バイアスの影響を受けない軸として、**tool segmentの内部だけ**を
monetization_modelで見直した。

| tool内訳 | has_agent_instructions |
|---|---|
| commercial_saas (n=7) | 6/7 (86%) |
| individual_community (n=2) | 0/2 |
| big_corp_internal (n=1) | 0/1 |

**考察**: 同じtool開発元同士で比べても、商用展開している方が
CLAUDE.md/AGENTS.mdの整備率が明確に高い。この軸であれば選定バイアスの
影響を受けず、「商用圧力とエージェント運用ルールの整備」の相関を
示す根拠として使える(ただしbig_corp_internal/individual_communityは
サンプル数が1〜2件と小さく、比率の絶対値は参考程度)。

## 条件付きで示唆が得られた項目

### agent_doc_char_count / agent_doc_heading_count
当初「commercial_saas平均23,275字」を根拠に「商用の方が文書が厚い」と
述べたが、分布を確認するとOpenHands/OpenHands(120,034字)という
突出した外れ値(2位のbrowser-use 49,587字の倍以上)が平均を強く
押し上げていた。

| 集計 | 値 |
|---|---|
| commercial_saas 平均 | 23,275字 |
| commercial_saas 中央値 | 12,202字 |
| individual_community 平均 | 5,137字 |

中央値ベースでも商用の方が2倍以上厚いという方向性自体は維持されるが、
**「23,275字」という絶対値を根拠にするのは不正確**だった。今後この種の
数値を報告する際は、平均だけでなく中央値・分布も併記する必要がある
(Issue #17参照)。

### agent_doc_mentions_test / lint / tool_usage
文書保有16件中、test言及94%・lint言及75%・tool_usage(MCP/subagent等)
言及81%と高い出現率で、「エージェント向け文書は操作手順書として
使われている」という傾向を裏付けるには十分。ただし`reports/
agent_doc_analysis_validation.md`で既に検証済みの通り、単純な
キーワード一致では表現のバリエーションを取りこぼす既知の限界があり、
個々のリポジトリを「言及していない」と断定する用途には使えない。
全体の傾向把握までは十分、個別評価には使うべきでない。

## 限定的だった項目

### has_ci
adopter 100%、tool 90%とほぼ天井に張り付いており、分散がほとんど
ない。「CI導入はもはや前提条件」という一言は言えるが、それ以上の
切り口を語る材料にはならない。チェック自体の実装に誤りはないが、
分析材料としての情報量は乏しい。

### agent_doc_has_code_block
tool 67%(4/6)、adopter 70%(7/10)とセグメント間でほぼ差がなく、
弁別力が低い。判定ロジック自体は単純でノイズが少ないが、示唆と
呼べるほどの発見はなかった。

## 既知の問題があり示唆に使えなかった項目

### has_tests
Issue #14で追跡中。ルート直下`tests`のみを見る実装がモノレポ構成
(ruff, langchain, crewAI等)を検知できず、20件中16件がfalseになる
実態と乖離した数値になっている。

### has_observability_dep
新たに検出した問題としてIssue #16で追跡する。20件中1件
(crewAIInc/crewAI)のみtrueで、分散が実質ゼロ。加えて、この項目が
見ているLangSmith/Langfuse等はLLMアプリ自体の可観測性SDKであり、
adopterセグメント(Next.js, Zod, Bun等、AI開発エージェントを使って
"開発している"だけでLLMアプリを"作っている"わけではないプロジェクト)
には概念的に適用対象外という設計上のミスマッチも判明した。

## 結論

6+8=14項目のうち、明確に「使える」と言えたのは**has_security_policyと
has_agent_instructions(monetization軸・tool限定)の2項目**。
char_count/heading_countとmentions系4項目は傾向把握には使えるが
数値の厳密さ・個別評価への転用には注意が必要。has_ci・has_code_blockは
天井/床効果で分析材料として薄い。has_tests・has_observability_depの
2項目は指標として機能しておらず、既知の問題として個別Issueで追跡する。

## 関連Issue

- 既存 #14: has_testsのモノレポ検知漏れ
- 新規 #16: has_observability_depのsegment適用範囲の見直し
- 新規 #17: 分析結果を要約・記事化する際の統計的な注意点整理
  (#12着手時の前提条件)
- 既存 #15: mentions系のキーワード一致の限界(LLMによる内容分析で補完)
