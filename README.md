# YORIMICHI 公式サイト

ポーカールーム「YORIMICHI」（静岡県沼津市・BeeBloom合同会社）の公式サイト。
STUDIO（ノーコード）製の旧サイトを、GitHub管理のクリーンな静的サイトとして再構築したもの。

## 構成
```
yorimichi-web/
├── index.html          トップページ
├── assets/
│   ├── css/style.css   スタイル
│   └── img/            画像（webp / png）
├── CNAME               独自ドメイン設定（yorimichi.beebloom.fun）
└── README.md
```

## ローカル確認
```bash
cd yorimichi-web
python3 -m http.server 8000
# → http://localhost:8000 をブラウザで開く
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

## 未接続（要・実URL差し込み）
以下のリンクは現状 `#`（プレースホルダ）。旧サイトの遷移先URLを後日接続する：
- ポーカー体験会の予約
- NEWS / トーナメント各記事
- LINE問い合わせ
- 稼働状況 / 月間ランキング / ポーカー用語集 / 求人情報 / プライバシーポリシー

---
©️2025 BeeBloom LLC
