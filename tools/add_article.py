#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_article.py — YORIMICHI公式HP 社員更新システム Phase2（記事新規作成）
シート「記事追加」タブのCSVを読み、新しい記事ページを生成し、一覧にカードを追加する。
- 種別: NEWS（koJlgd6l2 + news一覧） / トーナメントイベント（g9rZPguu2 + tounament-events一覧）
- 冪等: 既に同slugのページがあればスキップ（重複生成しない）
- 生成ページには data-slot を付与し data/slots.json に追記（以後は修正対象にもなる）
使い方: python3 tools/add_article.py --csv <URL|ファイル> [--dry]
CSV列（部分一致・順不同）: 種別, 日付, タイトル, 本文, 画像URL, slug, 公開
"""
import os, re, csv, json, html, argparse, io, hashlib
from urllib.request import urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

KIND = {
    'NEWS':          {'dir': 'koJlgd6l2', 'list': 'news/index.html',            'label': 'NEWS'},
    'トーナメントイベント': {'dir': 'g9rZPguu2', 'list': 'tounament-events/index.html', 'label': 'トーナメントイベント'},
}
DEFAULT_OG = '../../assets/img/hero_room.webp'

TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>%title% | ポーカールーム YORIMICHI</title>
  <meta name="description" content="%desc%">
  <meta name="robots" content="all">
  <meta property="og:site_name" content="ポーカールーム YORIMICHI">
  <meta property="og:title" content="%title% | ポーカールーム YORIMICHI">
  <meta property="og:description" content="%desc%">
  <meta property="og:type" content="article">
  <meta property="og:image" content="%ogimg%">
  <meta property="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="../../assets/img/favicon.png">
  <link rel="apple-touch-icon" href="../../assets/img/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../assets/css/style.css">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-6GTM7TRD42"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-6GTM7TRD42');</script>
</head>
<body>
  <header class="header" id="header">
    <a href="../../" class="logo"><img src="../../assets/img/logo_home_ink.png" alt="ポーカールーム YORIMICHI"></a>
    <button class="nav-toggle" id="navToggle" aria-label="メニューを開く">
      <span class="bars"><span></span><span></span><span></span></span> MENU
    </button>
  </header>
  <nav class="drawer" id="drawer">
    <button class="close" id="drawerClose" aria-label="閉じる">&times;</button>
    <div class="drawer-inner">
      <a href="../../" style="display:block;text-align:center;margin-bottom:8px;font-weight:700;letter-spacing:.12em">HOME</a>
      <div class="nav-group">
        <div class="gh">はじめての方</div>
        <a href="../../for_beginner">🔰 ポーカーデビュープラン</a>
        <a href="../../for_beginner">はじめての方へ・遊び方</a>
      </div>
      <div class="nav-group">
        <div class="gh">遊ぶ</div>
        <a href="../../cashgame-infomation">リングゲームのご案内</a>
        <a href="../../tournament-infomation">トーナメントのご案内</a>
        <a href="../../housetournament-summary">ハウストーナメント一覧</a>
        <a href="../../houserule">ハウスルール</a>
      </div>
      <div class="nav-group">
        <div class="gh">イベント・お知らせ</div>
        <a href="../../monthlyschedule">マンスリースケジュール</a>
        <a href="../../news">NEWS / お知らせ</a>
        <a href="../../tounament-events">トーナメントイベント</a>
        <a href="../../monthlyranking">月間ランキング</a>
        <a href="../../tablestatus">稼働状況</a>
      </div>
      <div class="nav-group">
        <div class="gh">店舗情報</div>
        <a href="../../#access">アクセス</a>
        <a href="../../contact">お問い合わせ</a>
        <a href="../../recruit">求人情報</a>
        <a href="../../privacy-policy">プライバシーポリシー</a>
      </div>
      <div class="drawer-cta">
        <a href="https://lin.ee/vNUBKse" class="btn btn-line" target="_blank" rel="noopener">💬 LINEで予約・相談</a>
        <a href="../../for_beginner" class="btn btn-primary">🔰 初めての方へ</a>
      </div>
    </div>
  </nav>
  <nav class="breadcrumb"><ol><li><a href="../../">HOME</a></li><li><a href="../../%listtop%">%kind%</a></li><li>%title%</li></ol></nav>
  <section class="page-body">
    <div class="container article">
      <div data-slot="%key%-001" class="meta">%date%　|　%kind%</div>
      <h1 data-slot="%key%-002" class="title">%title%</h1>
%leadimg%%paras%
      <div class="back-link"><a href="../../%listtop%">‹ %kind%一覧へ戻る</a></div>
    </div>
  </section>
  <footer class="footer">
    <div class="container">
      <div class="f-top">
        <div class="f-logo">
          <img src="../../assets/img/logo_lockup_footer.png" alt="YORIMICHI">
          <p>沼津初のカジュアルポーカールーム。JR沼津駅南口より徒歩5分。日本でいちばん気軽に立ち寄れるポーカールームを目指しています。</p>
        </div>
        <nav>
          <a href="../../">HOME</a>
          <a href="../../for_beginner">🔰 ポーカーデビュープラン</a>
          <a href="../../monthlyschedule">マンスリースケジュール</a>
          <a href="../../cashgame-infomation">リングゲームのご案内</a>
          <a href="../../tournament-infomation">トーナメントのご案内</a>
          <a href="../../housetournament-summary">ハウストーナメント一覧</a>
          <a href="../../tablestatus">稼働状況</a>
          <a href="../../monthlyranking">月間ランキング</a>
          <a href="../../recruit">求人情報</a>
          <a href="../../contact">お問い合わせ</a>
          <a href="../../privacy-policy">PRIVACY POLICY</a>
        </nav>
      </div>
      <div class="copy">©️2025 BeeBloom LLC</div>
    </div>
  </footer>
  <div class="floatbar">
    <a class="fb fb-debut" href="../../for_beginner">🔰 初めての方</a>
    <a class="fb fb-line" href="https://lin.ee/vNUBKse" target="_blank" rel="noopener">💬 LINEで予約</a>
    <a class="fb fb-tel" href="tel:05071121879">📞 電話</a>
  </div>
  <script>
    const header=document.getElementById('header');
    const onScroll=()=>header.classList.toggle('scrolled',window.scrollY>40);
    window.addEventListener('scroll',onScroll,{passive:true});onScroll();
    const drawer=document.getElementById('drawer');
    document.getElementById('navToggle').addEventListener('click',()=>drawer.classList.add('open'));
    document.getElementById('drawerClose').addEventListener('click',()=>drawer.classList.remove('open'));
    drawer.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>drawer.classList.remove('open')));
  </script>
</body>
</html>
'''


def norm(k):
    return (k or '').strip().replace('﻿', '')


def esc_attr(s):
    return html.escape(s, quote=True)


def esc_text(s):
    return html.escape(s, quote=False)


def slugify(s):
    s = re.sub(r'[^0-9A-Za-z_-]+', '', s)
    return s.strip('-_')


def load_rows(src):
    if re.match(r'^https?://', src):
        data = urlopen(src, timeout=30).read().decode('utf-8')
    else:
        data = open(src, encoding='utf-8').read()
    rows = list(csv.reader(io.StringIO(data)))
    hidx = 0
    for i, r in enumerate(rows):
        cells = [norm(c) for c in r]
        if any('タイトル' in c for c in cells):
            hidx = i
            break
    hdr = [norm(c) for c in rows[hidx]]
    out = []
    for r in rows[hidx + 1:]:
        out.append({hdr[j]: (r[j] if j < len(r) else '') for j in range(len(hdr))})
    return out


def col(row, *names):
    m = {norm(k): (v or '') for k, v in row.items()}
    for n in names:
        for k, v in m.items():
            if n and n in k:
                return v.strip()
    return ''


def date_digits(s):
    d = re.findall(r'\d+', s)
    if len(d) >= 3:
        return f'{int(d[0]):04d}{int(d[1]):02d}{int(d[2]):02d}'
    return ''.join(d)


def is_publish(v):
    return norm(v) in ('✅', '公開', 'TRUE', 'true', 'はい', '○', 'yes', 'YES', '1')


def add_card(list_path, dir_name, slug, title, date):
    text = open(list_path, encoding='utf-8').read()
    href = f'../{dir_name}/{slug}'
    if href in text:            # 既にカードがある
        return text, False
    card = (f'      <a href="{href}"><span class="t">{esc_text(title)}</span>'
            f'<span class="d">{esc_text(date)}</span></a>\n')
    m = re.search(r'(<div class="list-rows">\s*\n)', text)
    if not m:
        return text, False
    pos = m.end()
    return text[:pos] + card + text[pos:], True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    rows = load_rows(args.csv)
    registry = json.load(open('data/slots.json', encoding='utf-8'))
    existing_labels = {s['label'] for s in registry}
    created, skipped, errors = [], [], []
    list_cache = {}

    for i, row in enumerate(rows, 2):
        title = col(row, 'タイトル', 'title')
        if not title:
            continue
        pub = col(row, '公開', 'publish', 'status')
        if not is_publish(pub):
            skipped.append(f'行{i}: 「{title}」未公開（公開=✅で反映）のためスキップ')
            continue
        kind_in = col(row, '種別', 'kind') or 'NEWS'
        kind = 'トーナメントイベント' if 'トーナ' in kind_in else 'NEWS'
        conf = KIND[kind]
        date = col(row, '日付', 'date')
        body = col(row, '本文', 'body', '内容')
        img = col(row, '画像', 'image', 'img')

        slug = slugify(col(row, 'slug', 'スラッグ'))
        if not slug:
            base = 'post_' + (date_digits(date) or hashlib.md5(title.encode()).hexdigest()[:6])
            slug = base
        # 一意化
        d = conf['dir']
        s2, n = slug, 2
        while os.path.isdir(os.path.join(d, s2)) and f'../{d}/{s2}' not in \
                list_cache.get(conf['list'], open(conf['list'], encoding='utf-8').read()):
            s2 = f'{slug}-{n}'; n += 1
        slug = s2
        page_path = os.path.join(d, slug, 'index.html')
        if os.path.exists(page_path):
            skipped.append(f'行{i}: 「{title}」は生成済み({slug})')
            continue

        key = f'{d}__{slug}'
        # 段落
        paras, new_slots = [], []
        c = 3
        for line in re.split(r'\r?\n', body):
            line = line.strip()
            if not line:
                continue
            sid = f'{key}-{c:03d}'; c += 1
            paras.append(f'        <p data-slot="{sid}">{esc_text(line)}</p>')
            new_slots.append((sid, 'text', line))
        paras_html = ('\n'.join(paras) + '\n') if paras else ''

        # リード画像
        if img:
            sid = f'{key}-002i'
            leadimg = f'      <div class="lead-img"><img data-slot="{sid}" src="{esc_attr(img)}" alt="{esc_attr(title)}"></div>\n'
            new_slots.append((sid, 'image', img))
            ogimg = img
        else:
            leadimg = ''
            ogimg = DEFAULT_OG

        desc = esc_attr(re.sub(r'\s+', ' ', body)[:90])
        repl = {'%title%': esc_text(title), '%desc%': desc, '%ogimg%': esc_attr(ogimg),
                '%listtop%': conf['list'].replace('/index.html', ''),
                '%kind%': conf['label'], '%key%': key, '%date%': esc_text(date),
                '%leadimg%': leadimg, '%paras%': paras_html}
        page = TEMPLATE
        for a, b in repl.items():
            page = page.replace(a, b)

        # 一覧カード
        lp = conf['list']
        if lp not in list_cache:
            list_cache[lp] = open(lp, encoding='utf-8').read()
        newlist, ok = add_card(lp, d, slug, title, date)
        if ok:
            list_cache[lp] = newlist

        if not args.dry:
            os.makedirs(os.path.dirname(page_path), exist_ok=True)
            open(page_path, 'w', encoding='utf-8').write(page)
            open(lp, 'w', encoding='utf-8').write(list_cache[lp])
            # 登録簿へ追記
            def snip(s, n=26):
                s = re.sub(r'\s+', ' ', s).strip()
                return (s[:n] + '…') if len(s) > n else s
            # meta/title
            base_slots = [(f'{key}-001', 'text', f'{date}　|　{kind}'),
                          (f'{key}-002', 'text', title)] + new_slots
            for sid, typ, cur in base_slots:
                num = sid.rsplit('-', 1)[1]
                lbl = f'{title} ▸ {num} {snip(cur)}'
                while lbl in existing_labels:
                    lbl += f' 〔{sid}〕'
                existing_labels.add(lbl)
                registry.append({'slotId': sid, 'type': typ, 'group': title, 'role': 'p',
                                 'current': snip(cur), 'current_full': cur, 'label': lbl,
                                 'pageKey': key, 'pageLabel': title})
        created.append(f'{kind}「{title}」→ {d}/{slug}/（段落{len(paras)}）')

    if not args.dry and created:
        json.dump(registry, open('data/slots.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        # シートのプルダウン(IMPORTDATA)用CSVも更新 → 新記事も修正対象に自動追加
        with open('data/slots.csv', 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            for s in registry:
                w.writerow([s['label'], s['slotId'],
                            '画像' if s['type'] == 'image' else 'テキスト', s['pageLabel']])

    print(f'=== add_article {"(DRY)" if args.dry else ""} ===')
    print(f'新規作成: {len(created)} / スキップ: {len(skipped)} / エラー: {len(errors)}')
    for x in created: print('  ＋', x)
    for x in skipped: print('  －', x)
    for x in errors:  print('  ✖', x)
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        open(gh, 'a').write(f'created={len(created)}\n')


if __name__ == '__main__':
    main()
