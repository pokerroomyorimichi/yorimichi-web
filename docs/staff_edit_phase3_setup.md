# Phase3 セットアップ手順（今すぐ反映ボタン / 場所リスト自動更新）

対象: 太田（1回だけの設置作業） / スクリプト: `tools/gas_sheet_button.gs`

Phase3で追加する2機能:
- **① 今すぐ反映**: シートのボタンでGitHub Actionsを即起動（5分待たず約1分で公開）
- **② 場所リスト更新**: 新規作成した記事の箇所を、修正用プルダウンに自動追加（公開CSVから取得）

いずれも社員用シートに **Apps Script を1回貼るだけ** で有効化できる。

---

## 手順

### 1. スクリプトを貼る（①②共通）
1. 社員用シートを開く →〔拡張機能〕→〔Apps Script〕
2. `tools/gas_sheet_button.gs` の中身を全部貼り付けて保存
3. シートを再読み込み → メニュー「**YORIMICHI HP更新**」が出る

### 2. GitHubトークンを登録（①のみ必要）
「今すぐ反映」はGitHubを起動するためトークンが要る（②は不要）。
1. GitHub → Settings → Developer settings → **Fine-grained personal access tokens** → Generate new token
   - Repository access: **Only select repositories** → `pokerroomyorimichi/yorimichi-web`
   - Permissions: **Contents = Read and write**
2. 発行された `github_pat_...` をコピー
3. Apps Script →〔プロジェクトの設定 ⚙〕→〔スクリプト プロパティ〕→
   - プロパティ名 `GITHUB_TOKEN` / 値 = コピーしたトークン → 保存

### 3. 自動更新をON（②を自動化・任意）
メニュー「YORIMICHI HP更新」→「自動更新をON（1時間ごと）」を1回押す。
→ 1時間ごとに場所リストを最新化（新記事が自動でプルダウンに増える）。
※すぐ反映したい時はメニュー「② 場所リストを更新」を手押しでもOK。

---

## 使い方（社員向け・設置後）
- 文言を直したら → メニュー「**① 今すぐ反映**」で即公開（押さなくても5分ごとに自動反映）
- 新記事を作ったら → 数分後にメニュー「**② 場所リストを更新**」を押すと、その記事の各箇所も修正プルダウンに出る

## 補足
- 自動反映(cron 5分)は常時動いているので、ボタンは「急ぎの時だけ」でよい。
- トークンは太田のGitHub権限に紐づく。流出時はGitHubで即Revoke可能。
