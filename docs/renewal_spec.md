# YORIMICHI 公式HP 全面リニューアル（Option B）要件定義・仕様書

作成: 2026-07-21 / 担当: システム・IT部 / 承認待ち: 太田

---

## 1. 目的
確定した「cafe版デザイン」を全ページに展開し、最新情報（7月〜）を反映した状態で
公式ドメイン `yorimichi.beebloom.fun` に公開する。現状の3つのズレを解消する。

| ズレ | 現状 | 目標 |
|---|---|---|
| ①ドメイン | 旧STUDIO配信中 | GitHub版へ切替 |
| ②情報鮮度 | 6月で凍結 | 最新（7月〜）を反映 |
| ③デザイン | cafe版はトップ1枚のみ | 全16ページをcafe体系で統一 |

## 2. 対象ユーザー
沼津周辺のポーカー初心者・来店検討者。スマホ閲覧が主。

## 3. 現状アーキテクチャ（調査結果）
- 生成: `build_site.py`（1210行）が `/tmp/build/clean.json`＋`/tmp/pageimg.json` を入力に全ページ生成。
  → **両入力ファイルは消失。ジェネレーターは現状そのままでは動かない。**
- 画像アセット75枚はリポジトリに commit 済み（`assets/img/`）。
- cafe版（`preview/cafe/index.html`・760行）は build_site.py の外の独立HTML。
- 動的データは既にライブ連携済み（手動更新不要）:
  - 月間ランキング → `yorimichi-hub.vercel.app/api/ranking`（OPS連携）
  - 稼働状況 → Googleシート公開HTML
- 静的で6月止まりのコンテンツ（要更新）: NEWS / マンスリースケジュール / トーナメントイベント / トップの営業日ブロック。

## 4. 最新情報の取得元
現在の本番（旧STUDIO）が7月の最新情報を保持している（スタッフ運用）。
→ 旧STUDIOから7月分コンテンツをスクレイプして反映元とする。
（NEWS本文・マンスリー・トーナメントイベント）

## 5. デザイン仕様（cafe体系）
- カラー: paper `#F3EEE5` / ink `#3E3A39` / accent `#E63B10` / line `#d8cfbe`
- フォント: Cormorant（英字見出し）/ Noto Serif JP / Noto Sans JP
- ヘッダー: ドロワーメニュー（cafe版準拠）
- フッター: 公式ロゴ（symbol_logo_type_color系）
- トップ独自セクション: hero / board(today) / assure / menu / steps / gallery / promise / inner-room / faq / access
- 本番反映時に「調整パネル(id=adj)」は削除する。

## 6. 実装方針（提案）
build_site.py を「cafe版を出力するジェネレーター」に作り替える二段構え:

**A. 共通デザイン層の刷新（全16ページに効く）**
- `head()` にcafeのCSS変数・フォント・共通スタイルを移植
- `header()`/`footer()` をcafe版のドロワー・ロゴに差し替え
- ボタン・見出し・カード等の共通コンポーネントをcafe体系化

**B. コンテンツ層の再投入**
- `clean.json` / `pageimg.json` を再構築（旧STUDIOから7月分を再スクレイプ）
- トップページ本文をcafeの bespoke レイアウト（hero/steps/faq等）で生成
- 下層15ページは本文構造を維持しつつcafe体系のスタイルを適用

## 7. 完成の判定基準（受け入れ条件）
- [ ] 全16ページがcafeデザイン体系で表示される
- [ ] NEWS / マンスリー / トーナメントイベントに7月分が反映されている
- [ ] 月間ランキング・稼働状況のライブ連携が維持されている
- [ ] スマホ（375px）で崩れがない
- [ ] 調整パネルが本番から除去されている
- [ ] `build_site.py` が入力ファイル込みで再実行可能（再現性確保）
- [ ] `git diff` で意図した変更のみ

## 8. デプロイ・公開
- GitHub: `pokerroomyorimichi/yorimichi-web`（GitHub Pages）
- ドメイン切替: `CNAME` を `yorimichi.beebloom.fun` に設定＋DNS切替
  → **本番影響あり。太田さんの最終GOで実施。切替タイミングは要指定。**

## 9. 未確定事項（要・太田判断）
1. デザイン統一の粒度: 「トップ=bespoke cafe / 下層=cafe共通スタイル」でよいか、
   下層も個別に作り込むか。
2. ドメイン切替のタイミング（切替すると旧STUDIOは見えなくなる）。
3. 旧STUDIOの解約・保管方針（切替後）。

## 10. 作業時間帯
本番システム/データに触れる作業は 00:00–15:00 の枠で実施（15:00–24:00は稼働中のため回避）。
