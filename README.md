# YORIMICHI 公式サイト

ポーカールーム「YORIMICHI」（静岡県沼津市・BeeBloom合同会社）の公式サイト。
STUDIO（ノーコード）製の旧サイト（yorimichi.beebloom.fun）を、GitHub管理のクリーンな静的サイトとして全ページ再構築したもの。

## 構成（全57ページ）
```
yorimichi-web/
├── index.html              トップページ
├── for_beginner/           ポーカーデビュープラン
├── monthlyschedule/        マンスリースケジュール
├── cashgame-infomation/    リングゲームのご案内
├── tournament-infomation/  トーナメントのご案内
├── housetournament-summary/ ハウストーナメント一覧
├── tablestatus/            稼働状況
├── monthlyranking/         月間ランキング
├── recruit/ entry/         求人情報・エントリーフォーム
├── houserule/              ハウスルール
├── contact/                お問い合わせ
├── privacy-policy/         プライバシーポリシー
├── news/                   NEWS一覧
├── tounament-events/       トーナメントイベント一覧
├── CAJcRlRs2/<slug>/       ハウストーナメント種別（12種）
├── koJlgd6l2/<slug>/       NEWS記事（15本）
├── g9rZPguu2/<slug>/       トーナメントイベント記事（14本）
├── assets/
│   ├── css/style.css       スタイル
│   └── img/                画像（共通写真 + pages/ に旧サイト画像50枚）
├── build_site.py           静的サイトジェネレータ（全ページを生成）
├── CNAME                   独自ドメイン設定（yorimichi.beebloom.fun）※切替時に追加
└── README.md
```

旧サイトのCMS内部パス（CAJcRlRs2 / koJlgd6l2 / g9rZPguu2）をそのまま温存し、
既存の外部リンク（Instagram等の投稿リンク）が切替後も生きるよう 1:1 ミラー構成にしている。

## ページの作り方・更新方法
全ページは `build_site.py` から生成する。本文・画像データは旧サイトをレンダリング取得して
`/tmp/build/clean.json`・`/tmp/pageimg.json` に格納済み（取得スクリプトは開発メモ参照）。

```bash
cd yorimichi-web
/usr/bin/python3 build_site.py      # 全57ページを再生成
```

## ローカル確認
```bash
cd yorimichi-web
python3 -m http.server 8000
# → http://localhost:8000 をブラウザで開く（拡張子なしURLもディレクトリ型でそのまま動作）
```

## 公開（GitHub Pages）
1. GitHubリポジトリへ push
2. Settings → Pages → Source を `main` ブランチに設定
3. Custom domain に `yorimichi.beebloom.fun` を設定（CNAMEファイルで自動設定）
4. ドメイン側DNSを GitHub Pages へ向ける（旧STUDIOから切替）

## ブランドカラー
- 墨グレー `#3E3A39`
- 朱色 `#E63B10`
- 生成り `#EFEFEF`

## 既知の制約 / 要確認
- **ブラインドストラクチャー詳細**：旧サイトの各トーナメントのブラインド数値は STUDIO の埋め込み
  iframeアプリ内にあり機械取得できなかったため、レベル区分（3〜5E 等）のタブのみ再現。
  各レベルのSB/BB/Ante値は店頭・運営案内に委ねる注記とした。要：正式データの差し込み。
- **エントリーフォーム送信先**：`/entry` のフォームは見た目のみ。実送信先（旧フォーム/Googleフォーム等）
  への接続が未設定。
- **過去イベント記事**：日付ものの記事も含め全件を温存しているため、不要になった過去記事は適宜削除可。

---
©️2025 BeeBloom LLC
</content>
