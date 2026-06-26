#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YORIMICHI 公式サイト 静的サイトジェネレータ
旧STUDIOサイト(yorimichi.beebloom.fun)の全57ページを、クリーンな静的HTMLとして再現する。
データ元: /tmp/build/clean.json（各ページ本文）, /tmp/pageimg.json（ページ→画像）
"""
import json, re, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
clean   = json.load(open('/tmp/build/clean.json', encoding='utf-8'))
pageimg = json.load(open('/tmp/pageimg.json',  encoding='utf-8'))

LINE = "https://lin.ee/vNUBKse"
IG   = "https://www.instagram.com/yorimichi_poker"
X    = "https://x.com/yorimichi_poker"
TEL  = "050-7112-1879"
GMAP = "https://www.google.com/maps/search/?api=1&query=静岡県沼津市添地町72+青秀ビル"

def esc(s): return html.escape(str(s))
def IMG(fn): return f"/assets/img/pages/{fn}"

# ---- ナビゲーション（正規パス） -------------------------------------------
NAV = [
    ("HOME", "/"),
    ("🔰 ポーカーデビュープラン", "/for_beginner"),
    ("マンスリースケジュール", "/monthlyschedule"),
    ("リングゲームのご案内", "/cashgame-infomation"),
    ("トーナメントのご案内", "/tournament-infomation"),
    ("ハウストーナメント一覧", "/housetournament-summary"),
    ("稼働状況", "/tablestatus"),
    ("月間ランキング", "/monthlyranking"),
    ("求人情報", "/recruit"),
    ("NEWS", "/news"),
    ("お問い合わせ", "/contact"),
]
FOOTNAV = [
    ("HOME", "/"),
    ("🔰 ポーカーデビュープラン", "/for_beginner"),
    ("マンスリースケジュール", "/monthlyschedule"),
    ("リングゲームのご案内", "/cashgame-infomation"),
    ("トーナメントのご案内", "/tournament-infomation"),
    ("ハウストーナメント一覧", "/housetournament-summary"),
    ("稼働状況", "/tablestatus"),
    ("月間ランキング", "/monthlyranking"),
    ("求人情報", "/recruit"),
    ("お問い合わせ", "/contact"),
    ("PRIVACY POLICY", "/privacy-policy"),
]

GA = """  <script async src="https://www.googletagmanager.com/gtag/js?id=G-6GTM7TRD42"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-6GTM7TRD42');</script>"""

def head(title, desc, og="/assets/img/hero_room.webp"):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="robots" content="all">
  <meta property="og:site_name" content="ポーカールーム YORIMICHI">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{og}">
  <meta property="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="/assets/img/favicon.png">
  <link rel="apple-touch-icon" href="/assets/img/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
{GA}
</head>
<body>
"""

NAV_GROUPS = [
    ("はじめての方", [
        ("🔰 ポーカーデビュープラン", "/for_beginner"),
        ("はじめての方へ・遊び方", "/for_beginner"),
    ]),
    ("遊ぶ", [
        ("リングゲームのご案内", "/cashgame-infomation"),
        ("トーナメントのご案内", "/tournament-infomation"),
        ("ハウストーナメント一覧", "/housetournament-summary"),
        ("ハウスルール", "/houserule"),
    ]),
    ("イベント・お知らせ", [
        ("マンスリースケジュール", "/monthlyschedule"),
        ("NEWS / お知らせ", "/news"),
        ("トーナメントイベント", "/tounament-events"),
        ("月間ランキング", "/monthlyranking"),
        ("稼働状況", "/tablestatus"),
    ]),
    ("店舗情報", [
        ("アクセス", "/#access"),
        ("お問い合わせ", "/contact"),
        ("求人情報", "/recruit"),
        ("プライバシーポリシー", "/privacy-policy"),
    ]),
]

def header():
    groups = ""
    for gname, items in NAV_GROUPS:
        links = "\n".join(f'        <a href="{u}">{esc(t)}</a>' for t, u in items)
        groups += f"""      <div class="nav-group">
        <div class="gh">{esc(gname)}</div>
{links}
      </div>
"""
    return f"""  <header class="header" id="header">
    <a href="/" class="logo"><img src="/assets/img/logo_color.png" alt="ポーカールーム YORIMICHI"></a>
    <button class="nav-toggle" id="navToggle" aria-label="メニューを開く">
      <span class="bars"><span></span><span></span><span></span></span> MENU
    </button>
  </header>
  <nav class="drawer" id="drawer">
    <button class="close" id="drawerClose" aria-label="閉じる">&times;</button>
    <div class="drawer-inner">
      <a href="/" style="display:block;text-align:center;margin-bottom:8px;font-weight:700;letter-spacing:.12em">HOME</a>
{groups}      <div class="drawer-cta">
        <a href="{LINE}" class="btn btn-line" target="_blank" rel="noopener">💬 LINEで予約・相談</a>
        <a href="/for_beginner" class="btn btn-primary">🔰 初めての方へ</a>
      </div>
    </div>
  </nav>
"""

def footer():
    links = "\n".join(f'          <a href="{u}">{esc(t)}</a>' for t, u in FOOTNAV)
    return f"""  <footer class="footer">
    <div class="container">
      <div class="f-top">
        <div class="f-logo">
          <img src="/assets/img/logo_lockup_white.png" alt="YORIMICHI">
          <p>沼津初のカジュアルポーカールーム。JR沼津駅南口より徒歩5分。日本でいちばん気軽に立ち寄れるポーカールームを目指しています。</p>
        </div>
        <nav>
{links}
        </nav>
      </div>
      <div class="copy">©️2025 BeeBloom LLC</div>
    </div>
  </footer>
  <div class="floatbar">
    <a class="fb fb-debut" href="/for_beginner">🔰 初めての方</a>
    <a class="fb fb-line" href="{LINE}" target="_blank" rel="noopener">💬 LINEで予約</a>
    <a class="fb fb-tel" href="tel:{TEL.replace('-','')}">📞 電話</a>
  </div>
  <script>
    const header=document.getElementById('header');
    const onScroll=()=>header.classList.toggle('scrolled',window.scrollY>40);
    window.addEventListener('scroll',onScroll,{{passive:true}});onScroll();
    const drawer=document.getElementById('drawer');
    document.getElementById('navToggle').addEventListener('click',()=>drawer.classList.add('open'));
    document.getElementById('drawerClose').addEventListener('click',()=>drawer.classList.remove('open'));
    drawer.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>drawer.classList.remove('open')));
  </script>
</body>
</html>"""

def page_hero(en, title, lead=""):
    leadhtml = f'<p class="lead">{esc(lead)}</p>' if lead else ""
    return f"""  <section class="page-hero">
    <div class="container">
      <span class="en">{esc(en)}</span>
      <h1>{esc(title)}</h1>
      {leadhtml}
    </div>
  </section>
"""

def crumbs(items):
    lis = "".join(
        (f'<li><a href="{u}">{esc(t)}</a></li>' if u else f'<li>{esc(t)}</li>')
        for t, u in items)
    return f'  <nav class="breadcrumb"><ol>{lis}</ol></nav>\n'

def write(path, content):
    out = "index.html" if path == "/" else path.lstrip("/") + "/index.html"
    full = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(full), exist_ok=True) if os.path.dirname(out) else None
    open(full, "w", encoding="utf-8").write(content)
    return out

def doc(path, title, desc, crumb, body, og="/assets/img/hero_room.webp"):
    html_out = head(title, desc, og) + header() + crumb + body + footer()
    return write(path, html_out)

PAGES = []   # collected (path, title) for sanity

# ===========================================================================
#  記事パース（NEWS / トーナメントイベント）
# ===========================================================================
# slug -> (タイトル, 投稿日)
ART = {
 "/koJlgd6l2/schedule202606": ("6月のイベントスケジュール", "2026/5/31"),
 "/koJlgd6l2/event_2026502": ("【Golden Week Special Package】", "2026/4/23"),
 "/koJlgd6l2/schedule_202605": ("5月のイベントスケジュール", "2026/4/23"),
 "/koJlgd6l2/schedule_202604": ("4月のイベントスケジュール", "2026/4/1"),
 "/koJlgd6l2/schedule_202603": ("3月のイベントスケジュール", "2026/3/5"),
 "/koJlgd6l2/schedule_202602": ("2月のイベントスケジュール", "2026/2/1"),
 "/koJlgd6l2/event_20260103": ("🎍 YORIMICHI 新春おみくじ 2026 🎍", "2026/1/3"),
 "/koJlgd6l2/news_20260103": ("新年のご挨拶", "2026/1/2"),
 "/koJlgd6l2/eventresult_20251228": ("YORIMICHI Last Battleトーナメント結果", "2025/12/28"),
 "/koJlgd6l2/lastbattle2025-day1": ("YORIMICHI Last Battle2025 #01 Main Event Day2 シートドロー結果", "2025/12/28"),
 "/koJlgd6l2/eventresult20251221": ("クリスマススペシャルトーナメント結果", "2025/12/21"),
 "/koJlgd6l2/newtournament20251215": ("新トーナメント「Monsterstack」登場！", "2025/12/15"),
 "/koJlgd6l2/xmasevents2025": ("Xmas Special Tournament開催！", "2025/12/7"),
 "/koJlgd6l2/lastbattle2025": ("YORIMICHI Last Battle 2025予選通過者", "2025/12/7"),
 "/koJlgd6l2/schedule202512a": ("12月のイベント案内", "2025/12/5"),
 "/g9rZPguu2/tourny_20260627": ("【つっきー卒業】Graduation Bounty🥊", "2026/6/5"),
 "/g9rZPguu2/tournamentranking_202606": ("【6月】月間トーナメントランキング", "2026/5/20"),
 "/g9rZPguu2/tournamentranking_202605": ("【5月】月間トーナメントランキング", "2026/4/27"),
 "/g9rZPguu2/tourny_20260523": ("【Moe卒業】Moe Final💜Mystery Bonus-8's-", "2026/5/3"),
 "/g9rZPguu2/tourny_20260411": ("【ルナBirthday】20歳記念飲みポ", "2026/4/4"),
 "/g9rZPguu2/tournamentranking_202604": ("【4月】月間トーナメントランキング", "2026/4/1"),
 "/g9rZPguu2/tournamentranking_rules": ("【4月始動】YORIMICHI 月間トーナメントランキング開催決定！", "2026/4/1"),
 "/g9rZPguu2/tourny_20260214": ("【番長卒業】Lucky 7ポットバトル", "2026/2/13"),
 "/g9rZPguu2/tourny_20260130": ("【龍星Birthday】 Bomb Pot -crazy 8's-", "2026/1/22"),
 "/g9rZPguu2/tourny_20251227": ("YORIMICHI Last Battle 2025 #01 Main Event", "2025/12/24"),
 "/g9rZPguu2/tourny_20251228": ("YORIMICHI Last Battle 2025 #02 Megastack", "2025/12/24"),
 "/g9rZPguu2/tourny_20251220": ("Xmas Special Tournament #02 Tag Team -shot clock-", "2025/12/19"),
 "/g9rZPguu2/tourny_20251219": ("Xmas Special Tournament #01 Mystery Bounty", "2025/12/11"),
 "/g9rZPguu2/tourny_20251016": ("【iroha・Ryooona壮行】英語禁止！真の飲みぽを見せてやるぜトーナメント", "2025/12/7"),
}

def datekey(d):  # "2026/5/31" -> sortable
    y, m, dd = d.split("/")
    return (int(y), int(m), int(dd))

def article_body(path):
    """clean text からタイトル・日付・接頭辞を取り除いて本文を返す"""
    t = clean[path]
    # 接頭辞除去
    for pre in ["NEWS お知らせ", "特別トーナメント情報 トーナメントの開催概要です",
                "デイリートーナメント情報 トーナメントの開催概要です"]:
        if t.startswith(pre):
            t = t[len(pre):].strip(); break
    title, date = ART.get(path, ("", ""))
    # 先頭の日付除去
    if date and t.startswith(date):
        t = t[len(date):].strip()
    # 先頭のタイトル除去（重複している場合のみ）
    if title and t.startswith(title):
        t = t[len(title):].strip()
    # 末尾パンくず除去
    for m in ["keyboard_arrow_left", "HOME keyboard_arrow_right", "もっと読む"]:
        i = t.find(m)
        if i > 0: t = t[:i].strip()
    return t

def paragraphize(t):
    """run-on テキストを読みやすい段落に分割"""
    t = t.replace("&amp;", "&")
    # 箇条書き・区切りマーカーの前で改行
    t = re.sub(r'\s*(◎|⭐️|🆕|※|《|【|・|🎍|🎄|🎂|🎓|✨|💜|🥊|🌸|🐦|💎|🔥|🚶|🔍)', r'\n\1', t)
    # 文末で改行
    t = re.sub(r'(。)\s', r'\1\n', t)
    chunks = [c.strip() for c in t.split("\n") if c.strip()]
    # 短すぎる断片は前と結合
    out, buf = [], ""
    for c in chunks:
        if len(buf) < 18 and buf:
            buf = buf + " " + c
        else:
            if buf: out.append(buf)
            buf = c
    if buf: out.append(buf)
    return out

def render_article(path, section):
    title, date = ART[path]
    sec_name, sec_url = ("NEWS", "/news") if section == "news" else ("トーナメントイベント", "/tounament-events")
    imgs = pageimg.get(path, [])
    content_imgs = [i for i in imgs if "img_05_" not in i] or imgs
    lead = content_imgs[0] if content_imgs else None
    extras = content_imgs[1:] if len(content_imgs) > 1 else []
    body = article_body(path)
    paras = paragraphize(body)
    pid = "".join(re.findall(r'\d+', path.split("/")[-1])) or "0"
    leadimg = f'<div class="lead-img"><img src="{IMG(lead)}" alt="{esc(title)}"></div>' if lead else ""
    ps = "\n".join(f'        <p>{esc(p)}</p>' for p in paras)
    figs = "\n".join(f'        <figure class="figure"><img src="{IMG(e)}" alt=""></figure>' for e in extras)
    body_html = f"""  <section class="page-body">
    <div class="container article">
      <div class="meta">{esc(date)}　|　{esc(sec_name)}</div>
      <h1 class="title">{esc(title)}</h1>
      {leadimg}
{ps}
{figs}
      <div class="back-link"><a href="{sec_url}">‹ {esc(sec_name)}一覧へ戻る</a></div>
    </div>
  </section>
"""
    og = IMG(lead) if lead else "/assets/img/hero_room.webp"
    desc = (body[:90] + "…") if body else title
    doc(path, f"{title} | ポーカールーム YORIMICHI", desc,
        crumbs([("HOME", "/"), (sec_name, sec_url), (title, None)]), body_html, og)
    PAGES.append((path, title))

print("generator loaded")

# ===========================================================================
#  トーナメント種別ページ（ハウストーナメント）
# ===========================================================================
STD8 = ["3〜5E","6〜10E","11〜15E","16〜20E","21〜25E","26〜30E","31E〜40E","41〜50E"]
TOURN = [
 ("hyperturbo","Hyper Turbo","2026/1/15","D",["3〜5E","6〜10E","11〜15E","16〜20E","21E〜"]),
 ("shotclock","shot clock","2025/12/28","C",STD8),
 ("winthebutton","Win The Button","2025/12/24","C",STD8),
 ("kobounty","K.O. Bounty","2025/12/24","C",STD8),
 ("theclassic","The Classic","2025/12/24","C",STD8),
 ("highvoltage","High Voltage","2025/12/24","C",STD8),
 ("superkobounty","Super K.O. Bounty","2026/1/15","C",["3〜5E","6〜10E","11〜15E","16〜20E","21〜25E","26〜30E","31E〜40E","41E〜"]),
 ("deepstack","Friday Deepstack","2025/12/2","C",STD8),
 ("dailytournament","YORIMICHI Daily Tournament","2025/12/2","C",STD8),
 ("monsterstack","Monsterstack","2025/12/15","B",STD8),
 ("superstack","Holiday Superstack","2026/1/15","B",["3〜5E","6〜10E","11〜15E","16〜20E","21〜25E","26〜30E","31〜40E","41E〜"]),
 ("spirits","Saturday Spirits","2025/12/13","B",STD8),
]
TNAME = {s: n for s, n, *_ in TOURN}

# 本番HPから取得できた詳細データ（取得できたものから順次追加）。
# ブラインドはiframeクリップによりLv.1-3まで取得可能。Lv.4以降・全プライズは元データ反映待ち。
def _spec(start, regclose, fee, stack, game="ノーリミット／テキサスホールデム"):
    return [("開始時刻", start), ("レジストレーション締切", regclose), ("ゲーム", game),
            ("参加費", fee), ("スタック", stack)]
TOURN_SPEC = {
 "shotclock":      _spec("18:45","20:40 ごろ","¥2,000","20,000点"),
 "winthebutton":   _spec("18:45","20:40 ごろ","¥2,000","20,000点"),
 "kobounty":       _spec("18:45","20:40 ごろ","¥2,000","20,000点"),
 "theclassic":     _spec("18:45","20:40 ごろ","¥2,000","10,000点"),
 "highvoltage":    _spec("18:45","20:40 ごろ","¥2,000","20,000点"),
 "superkobounty":  _spec("18:45","20:40 ごろ","¥2,000","20,000点"),
 "deepstack":      _spec("19:00","20:55 ごろ","¥3,000","25,000点"),
 "dailytournament":_spec("19:00","20:55 ごろ","¥2,000","20,000点"),
 "hyperturbo":     _spec("17:20","18:30 ごろ","¥1,000","10,000点"),
 "monsterstack":   _spec("15:20","19:00 ごろ","¥6,000","50,000点"),
 "superstack":     _spec("17:20","19:30 ごろ","¥5,000","30,000点"),
 "spirits":        _spec("17:20","19:00 ごろ","¥4,000","25,000点"),
}
# (Lv, BB Ante, Blinds, Duration, Time Table) / 全幅ラベル行は ("##","ラベル")
TOURN_STRUCT = {
 "winthebutton": [
   ("1","200","100 - 200","0:15","18:45 - 19:00"),("2","300","200 - 300","0:15","19:00 - 19:15"),
   ("3","400","200 - 400","0:15","19:15 - 19:30"),("4","500","300 - 500","0:15","19:30 - 19:45"),
   ("5","600","300 - 600","0:15","19:45 - 20:00"),("6","800","400 - 800","0:15","20:00 - 20:15"),
   ("7","1,000","500 - 1,000","0:15","20:15 - 20:30"),
   ("##","Break & Registration Close（0:10 / 20:30 - 20:40）"),
   ("8","1,200","600 - 1,200","0:10","20:40 - 20:50"),("9","1,500","1,000 - 1,500","0:10","20:50 - 21:00"),
   ("10","2,000","1,000 - 2,000","0:10","21:00 - 21:10"),("11","2,500","1,000 - 2,500","0:10","21:10 - 21:20"),
   ("##","100 chips Remove"),
   ("12","3,000","1,500 - 3,000","0:10","21:20 - 21:30"),("13","4,000","2,000 - 4,000","0:10","21:30 - 21:40"),
   ("14","5,000","2,500 - 5,000","0:10","21:40 - 21:50")],
 "kobounty": [
   ("1","-","100 - 200","0:15","18:45 - 19:00"),("2","300","200 - 300","0:15","19:00 - 19:15"),
   ("3","400","200 - 400","0:15","19:15 - 19:30"),("4","500","300 - 500","0:15","19:30 - 19:45"),
   ("5","600","300 - 600","0:15","19:45 - 20:00"),("6","800","400 - 800","0:15","20:00 - 20:15"),
   ("7","1,000","500 - 1,000","0:15","20:15 - 20:30"),
   ("##","Break & Registration Close（0:10 / 20:30 - 20:40）"),
   ("8","1,200","600 - 1,200","0:10","20:40 - 20:50"),("9","1,500","1,000 - 1,500","0:10","20:50 - 21:00"),
   ("10","2,000","1,000 - 2,000","0:10","21:00 - 21:10"),("11","2,500","1,000 - 2,500","0:10","21:10 - 21:20"),
   ("##","100 chips Remove"),
   ("12","3,000","1,500 - 3,000","0:10","21:20 - 21:30"),("13","4,000","2,000 - 4,000","0:10","21:30 - 21:40"),
   ("14","5,000","2,500 - 5,000","0:10","21:40 - 21:50")],
 "shotclock": [("1","200","100 - 200","0:15","18:45 - 19:00"),("2","300","200 - 300","0:15","19:00 - 19:15"),
   ("3","400","200 - 400","0:15","19:15 - 19:30")],
 "superkobounty": [("1","200","100 - 200","0:15","18:45 - 19:00"),("2","300","200 - 300","0:15","19:00 - 19:15"),
   ("3","400","200 - 400","0:15","19:15 - 19:30")],
 "theclassic": [("1","-","50 - 100","0:15","18:45 - 19:00"),("2","-","75 - 150","0:15","19:00 - 19:15"),
   ("3","-","100 - 200","0:15","19:15 - 19:30")],
 "highvoltage": [("1","300","100 - 100","0:15","18:45 - 19:00"),("2","400","200 - 200","0:15","19:00 - 19:15"),
   ("3","500","200 - 200","0:15","19:15 - 19:30")],
 "deepstack": [("1","200","100 - 200","0:15","18:45 - 19:00"),("2","300","200 - 300","0:15","19:00 - 19:15"),
   ("3","400","200 - 400","0:15","19:15 - 19:30")],
 "dailytournament": [("1","200","100 - 200","0:15","18:45 - 19:00"),("2","300","200 - 300","0:15","19:00 - 19:15"),
   ("3","400","200 - 400","0:15","19:15 - 19:30")],
 "hyperturbo": [("1","100","100 - 100","0:10","17:20 - 17:30"),("2","200","100 - 200","0:10","17:30 - 17:40"),
   ("3","300","200 - 300","0:10","17:40 - 17:50")],
 "monsterstack": [("1","200","100 - 200","0:20","15:20 - 15:40"),("2","300","200 - 300","0:20","15:40 - 16:00"),
   ("3","400","200 - 400","0:20","16:00 - 16:20")],
 "superstack": [("1","200","100 - 200","0:15","17:20 - 17:35"),("2","300","200 - 300","0:15","17:35 - 17:50"),
   ("3","400","200 - 400","0:15","17:50 - 18:05")],
 "spirits": [("1","200","100 - 200","0:10","17:20 - 17:30"),("2","300","200 - 300","0:10","17:30 - 17:40"),
   ("3","400","200 - 400","0:10","17:40 - 17:50")],
}
# 元HPのiframeがLv.3までしか表示しない（クリップ）ページ
TOURN_STRUCT_PARTIAL = {"shotclock", "superkobounty", "theclassic", "highvoltage",
                        "deepstack", "dailytournament", "hyperturbo", "monsterstack", "superstack", "spirits"}

def render_tournament(slug, name, date, rank, tiers):
    path = "/CAJcRlRs2/" + slug
    body = clean[path]
    for pre in ["デイリートーナメント情報 トーナメントの開催概要です"]:
        if body.startswith(pre): body = body[len(pre):].strip()
    if body.startswith(date): body = body[len(date):].strip()
    if body.startswith(name): body = body[len(name):].strip()
    intro = body.split(tiers[0], 1)[0].strip()
    after = body.rsplit(tiers[-1], 1)[-1]
    notes = [n.strip() for n in after.split("・") if n.strip() and "keyboard" not in n and "HOME" not in n]
    notes = [re.sub(r'こちら', '<a href="/tournament-infomation">こちら</a>', esc(n)) for n in notes]
    img = (pageimg.get(path) or [None])[0]
    introhtml = "\n".join(f'        <p>{esc(p)}</p>' for p in paragraphize(intro))
    tierhtml = "".join(f"<span>{esc(t)}</span>" for t in tiers)
    noteshtml = "\n".join(f'          <li>{n}</li>' for n in notes)
    imghtml = f'      <div class="figure"><img src="{IMG(img)}" alt="{esc(name)}"></div>\n' if img else ""

    # 詳細表（取得済みのみ）
    spec = TOURN_SPEC.get(slug)
    if spec:
        rows = "\n".join(f'          <tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in spec)
        spec_block = f"""      <div class="block">
        <div class="block-head"><span class="en">SUMMARY</span><h2>トーナメント詳細</h2></div>
        <table class="spec">
{rows}
        </table>
      </div>
"""
    else:
        spec_block = f"""      <div class="block">
        <div class="block-head"><span class="en">SUMMARY</span><h2>トーナメント詳細</h2>
          <p class="sub">開始時刻・参加費・スタック等は当日のスケジュール／店頭にてご案内します。</p></div>
      </div>
"""
    # ブラインドストラクチャー
    struct = TOURN_STRUCT.get(slug)
    if struct:
        sr = []
        for row in struct:
            if len(row) == 2 and row[0] == "##":        # 全幅ラベル行（Break / chips Remove 等）
                sr.append(f'              <tr class="span"><td colspan="5">{esc(row[1])}</td></tr>')
            else:
                lv, ba, bl, du, tt = row
                sr.append(f'              <tr><td class="lv">{esc(lv)}</td><td>{esc(ba)}</td><td>{esc(bl)}</td><td>{esc(du)}</td><td>{esc(tt)}</td></tr>')
        srows = "\n".join(sr)
        partial_note = ('<p class="note" style="margin-top:12px">※ Lv.4 以降のストラクチャーは当日のストラクチャーシート／運営にてご案内します。</p>'
                        if slug in TOURN_STRUCT_PARTIAL else '')
        summary = "ストラクチャー表（Lv.1-3）" if slug in TOURN_STRUCT_PARTIAL else "ストラクチャー表（全レベル）"
        struct_block = f"""      <div class="block">
        <div class="block-head"><span class="en">STRUCTURE</span><h2>ブラインドストラクチャー</h2></div>
        <details class="acc" open><summary>{summary}</summary>
          <div class="acc-body" style="overflow-x:auto">
            <table class="struct">
              <thead><tr><th>Lv.</th><th>BB Ante</th><th>Blinds</th><th>Duration</th><th>Time Table</th></tr></thead>
              <tbody>
{srows}
              </tbody>
            </table>
            {partial_note}
          </div>
        </details>
      </div>
"""
    else:
        struct_block = f"""      <div class="block">
        <div class="block-head"><span class="en">STRUCTURE</span><h2>ブラインドストラクチャー</h2>
          <p class="sub">各レベルのブラインドは当日のストラクチャーシート／運営にてご案内します。</p></div>
      </div>
"""
    body_html = f"""  <section class="page-body">
    <div class="container">
{imghtml}      <div class="block">
        <div class="block-head"><span class="en">HOUSE TOURNAMENT</span><h2>{esc(name)}</h2>
          <p class="sub">【{esc(rank)}ランク】トーナメント</p></div>
{introhtml}
      </div>
{spec_block}{struct_block}      <div class="block">
        <div class="block-head"><span class="en">PRIZE</span><h2>プライズ（エントリー数別）</h2>
          <p class="sub">エントリー数に応じてプライズ額・入賞人数が変動します。</p></div>
        <div class="levels">{tierhtml}</div>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">REGULATION</span><h2>レギュレーション</h2></div>
        <ul class="dots">
{noteshtml}
        </ul>
      </div>
      <div class="back-link"><a href="/housetournament-summary">‹ ハウストーナメント一覧へ戻る</a></div>
    </div>
  </section>
"""
    og = IMG(img) if img else "/assets/img/hero_ingame.webp"
    doc(path, f"{name} | ハウストーナメント | YORIMICHI", f"YORIMICHIのハウストーナメント「{name}」（{rank}ランク）の開催概要です。",
        crumbs([("HOME","/"),("ハウストーナメント一覧","/housetournament-summary"),(name,None)]), body_html, og)
    PAGES.append((path, name))

# ===========================================================================
#  一覧ページ
# ===========================================================================
def render_news_list():
    items = sorted([p for p in ART if p.startswith("/koJlgd6l2")],
                   key=lambda p: datekey(ART[p][1]), reverse=True)
    rows = "\n".join(
        f'      <a href="{p}"><span class="t">{esc(ART[p][0])}</span><span class="d">{esc(ART[p][1])}</span></a>'
        for p in items)
    body = page_hero("NEWS", "お知らせ", "YORIMICHIからのお知らせ一覧です。") + f"""  <section class="page-body">
    <div class="container">
      <div class="list-rows">
{rows}
      </div>
    </div>
  </section>
"""
    doc("/news", "NEWS お知らせ | ポーカールーム YORIMICHI", "ポーカールームYORIMICHIからのお知らせ一覧です。",
        crumbs([("HOME","/"),("NEWS",None)]), body)
    PAGES.append(("/news","NEWS"))

def render_tourny_events_list():
    items = sorted([p for p in ART if p.startswith("/g9rZPguu2")],
                   key=lambda p: datekey(ART[p][1]), reverse=True)
    rows = "\n".join(
        f'      <a href="{p}"><span class="t">{esc(ART[p][0])}</span><span class="d">{esc(ART[p][1])}</span></a>'
        for p in items)
    body = page_hero("TOURNAMENT EVENTS", "トーナメントイベント", "イベントでの特別トーナメント一覧です。") + f"""  <section class="page-body">
    <div class="container">
      <div class="list-rows">
{rows}
      </div>
    </div>
  </section>
"""
    doc("/tounament-events", "トーナメントイベント | ポーカールーム YORIMICHI", "YORIMICHIのイベント特別トーナメント一覧です。",
        crumbs([("HOME","/"),("トーナメントイベント",None)]), body)
    PAGES.append(("/tounament-events","トーナメントイベント"))

def render_house_summary():
    groups = [
        ("Dランクトーナメント", [("Hyper Turbo","hyperturbo")]),
        ("Cランクトーナメント", [("shot clock","shotclock"),("Win The Button","winthebutton"),
            ("K.O. Bounty","kobounty"),("The Classic","theclassic"),("High Voltage","highvoltage"),
            ("Super K.O. Bounty","superkobounty"),("Friday Deepstack","deepstack"),
            ("YORIMICHI Daily Tournament","dailytournament")]),
        ("Bランクトーナメント", [("Monsterstack","monsterstack"),("Holiday Superstack","superstack"),
            ("Saturday Spirits","spirits")]),
        ("Aランクトーナメント", None),
        ("Sランクトーナメント", None),
    ]
    blocks = ""
    for gname, items in groups:
        if items is None:
            chips = '<span class="soon">Coming soon...</span>'
        else:
            chips = "".join(f'<a href="/CAJcRlRs2/{slug}">{esc(n)}</a>' for n, slug in items)
        blocks += f"""      <div class="rank-group">
        <h3>{esc(gname)}</h3>
        <div class="chip-list">{chips}</div>
      </div>
"""
    body = page_hero("HOUSE TOURNAMENT", "ハウストーナメント一覧", "YORIMICHIのハウストーナメントです。") + f"""  <section class="page-body">
    <div class="container">
      <div class="block">
        <p>YORIMICHIのハウストーナメント一覧です。参加費やご自身のレベルに合わせてお好みのものをお選びください。</p>
      </div>
{blocks}    </div>
  </section>
"""
    doc("/housetournament-summary", "ハウストーナメント一覧 | YORIMICHI", "YORIMICHIで定期開催しているハウストーナメントの一覧です。",
        crumbs([("HOME","/"),("ハウストーナメント一覧",None)]), body)
    PAGES.append(("/housetournament-summary","ハウストーナメント一覧"))

print("part2 loaded")

# ===========================================================================
#  静的ページ
# ===========================================================================
def render_for_beginner():
    body = page_hero("FOR BEGINNERS", "ポーカーデビュープランのご案内", "今日からあなたもポーカープレイヤー♪") + """  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><span class="en">WELCOME</span><h2>未経験でも大丈夫！</h2>
          <p class="sub">「初めてチップに触る」未経験者に選ばれるお店です。</p></div>
        <p>YORIMICHIは日本で一番初心者のプレイヤーに愛されるお店を目指しています。ご来場される方の中には、「YouTubeで観てやってみたくて！」「友だちから誘われて…」などなど、ポーカーを全くやったことがない方もたくさんいらっしゃいます。</p>
        <p>そんな方に安心してライブポーカーを楽しんでもらいたいという想いで、初めての方がお得にポーカーデビューできるプランをご用意しています。</p>
        <p class="note">※店内の状況によってはご案内できない場合もございますので、ご予約の上でのご来場をお勧めしております。</p>
      </div>
      <div class="block">
        <div class="fee-list">
          <div class="fee-row"><div class="name">参加費<small>入場料無料・要1Dオーダー</small></div><div class="val">¥3,000</div></div>
          <div class="fee-row"><div class="name">所要時間</div><div class="val">60〜90分</div></div>
        </div>
        <div style="margin-top:22px"><a href="%LINE%" class="btn btn-line" target="_blank" rel="noopener">LINEでお問い合わせ <span class="arrow">›</span></a></div>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">PLAN</span><h2>ポーカーデビュープランの内容</h2>
          <p class="sub">初心者の方が安心してデビューできる工夫が盛り沢山！</p></div>
        <div class="cards">
          <div class="scard"><div class="top"><span class="ttl">ルール・用語説明</span></div>
            <p>ポーカーの役や、ゲームの進行、「レイズ」「コール」などの基本的なアクション・用語のご説明をします。わからないところは何度でも丁寧にご説明しますので、どなたでもゲームを楽しめるようになります。</p></div>
          <div class="scard"><div class="top"><span class="ttl">実践練習</span></div>
            <p>練習用のチップを使って実践練習！無くなっても無料で復活できるので、安心してたくさんプレイできます。ポーカーの醍醐味である「ブラフ（ハッタリ）」や、全額チップをかける「オールイン」なども、たくさんトライしてみてください。</p></div>
        </div>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
""".replace("%LINE%", LINE)
    doc("/for_beginner", "ポーカーデビュープラン | ポーカールーム YORIMICHI",
        "ポーカー未経験でも安心。YORIMICHIのポーカーデビュープラン（参加費¥3,000／60〜90分）のご案内です。",
        crumbs([("HOME","/"),("ポーカーデビュープラン",None)]), body)
    PAGES.append(("/for_beginner","ポーカーデビュープラン"))

def render_cashgame():
    body = page_hero("RING GAME", "リングゲームのご案内", "気軽に遊べる王道のゲームスタイルです") + """  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><h2>リングゲームとは？</h2></div>
        <p>好きな時間に参加・退席できる、カジュアルなゲームスタイルです。ビギナープレイヤー専用のレートもご用意しているので、ポーカーデビューにもピッタリです。</p>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">FEE</span><h2>料金システム</h2>
          <p class="sub">勝ち続ければエントランスフィーの¥1,000とドリンク代だけで遊ぶことができます</p></div>
        <div class="fee-list">
          <div class="fee-row"><div class="name">入場料<small>ご来場者全員にお支払いいただく来店チャージ</small></div><div class="val">¥1,000</div></div>
          <div class="fee-row"><div class="name">ドリンク代<small>ポーカーを遊びながら飲めるお飲み物代</small></div><div class="val">¥500</div></div>
        </div>
        <p class="note" style="margin-top:12px">◎トーナメント等その他ゲームにご参加の際にお支払いいただいた場合は不要です。</p>
        <p style="margin-top:18px">チップ代：ゲーム終了時に残ったチップはお預け処理ができ、チップのお預けがある場合は、次回のご来場時に追加購入なしで遊ぶことができます。お預けやお引出しの際に追加料金等は一切かかりません。</p>
        <p class="note">◎原則、お預けの際に10%のコミッション（Y$による手数料）をいただきます。</p>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">STAKES</span><h2>ステークス一覧</h2>
          <p class="sub">ご自身のレベルやご予算にあわせてお好みのレートをお選びください。</p></div>
        <div class="cards">
          <div class="scard"><div class="top"><span class="ttl">100NL</span><span class="tag">バイイン：Y$ 3,000〜</span></div>
            <p>YORIMICHIでスタンダードなレートとしてご用意しているステークスです。初級から上級者までどなたでもご参加いただけます。デビュープランでポーカーを覚えた方も、ポーカーに慣れてきたらこちらのテーブルに参加してみてください◎</p></div>
          <div class="scard"><div class="top"><span class="ttl">200NL</span><span class="tag">バイイン：Y$ 10,000〜</span></div>
            <p>ワンランク上のポーカーを楽しめるステークスです。プレイに自信のある方や、より深い駆け引きを味わいたい方におすすめです🔥</p><p><span class="hl">★期間限定で日替わりフードサービス付き！</span></p></div>
          <div class="scard"><div class="top"><span class="ttl">500NL</span><span class="tag">バイイン：Y$ 25,000〜</span></div>
            <p>YORIMICHIの上級ステークスです。経験豊富なプレイヤーがさらに一歩上を目指すためのテーブルです💎 刺激的な真剣勝負をお楽しみください。</p><p><span class="hl">★期間限定で日替わりフードサービス付き！</span></p></div>
        </div>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
"""
    doc("/cashgame-infomation", "リングゲームのご案内 | ポーカールーム YORIMICHI",
        "YORIMICHIのリングゲーム（キャッシュゲーム）の料金システム・ステークス一覧のご案内です。",
        crumbs([("HOME","/"),("リングゲームのご案内",None)]), body)
    PAGES.append(("/cashgame-infomation","リングゲームのご案内"))

def render_tournament_info():
    ranks = [
        ("Dランク","Dランクトーナメントは初心者の方でも安心して参加できることを目的としたビギナー向けのトーナメントです。プレイヤーおよびディーラーのスキルアップを目的とした側面もあるため、各種レギュレーションやフロアによる裁定も比較的易しく設定しています。どなたでもお気軽にご参加ください。"),
        ("Cランク","Cランクトーナメントは、カジュアルなレギュレーションを採用しています。初級者の方も参加しやすく、中〜上級者の方にとっても納得感のあるストラクチャーとレベルのバランスを意識しています。幅広いプレイヤーに楽しんでいただけるポピュラーなトーナメントです。"),
        ("Bランク","Bランクトーナメントは、どなたでも参加しやすく、さらにストラクチャーの構成にもこだわったワンランク上のトーナメントです。気軽さと本格さのちょうど中間に位置しており、リーズナブルかつ真剣勝負も楽しめます。"),
        ("Aランク","Aランクトーナメントは、ハイレベルかつ幅広いプレイヤーの挑戦を目的としたトーナメントです。良質なブラインドストラクチャーを基準としつつも、参加しやすい雰囲気を大切にしています。中級者から上級者までのプレイヤーが真剣勝負を楽しめる、フラッグシップトーナメントです。"),
        ("Sランク","Sランクトーナメントは、最高峰のレギュレーションを備えたトーナメントです。全国屈指のブラインドストラクチャー、厳格な運営のもと、長期戦を想定した構造でプレイヤーの技術と忍耐力、戦略が徹底的に試されます。YORIMICHIから世界に通用するプレイヤーを輩出することを目的とした特別なタイトルです。"),
    ]
    rankcards = "\n".join(
        f'          <div class="scard"><div class="top"><span class="ttl">{esc(n)}</span></div><p>{esc(d)}</p></div>'
        for n, d in ranks)
    body = page_hero("TOURNAMENT", "トーナメントのご案内", "勝ち抜き形式のゲームスタイルです") + f"""  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><h2>トーナメントとは？</h2></div>
        <p>優勝者が決まるまで戦う、勝ち残り形式のゲームです。リングゲームとは一味違うエキサイティングなゲームがお楽しみいただけます。見事、上位に入賞された方にはプライズが付与されます。</p>
        <div style="margin-top:16px"><a href="/monthlyschedule" class="btn btn-primary">マンスリースケジュール <span class="arrow">›</span></a></div>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">FEE</span><h2>料金システム</h2>
          <p class="sub">基本料金と別に、トーナメントの参加費をお支払いください。</p></div>
        <div class="fee-list">
          <div class="fee-row"><div class="name">入場料<small>ご来場者全員にお支払いいただく来店チャージ</small></div><div class="val">¥1,000</div></div>
          <div class="fee-row"><div class="name">ドリンク代<small>ポーカーを遊びながら飲めるお飲み物代</small></div><div class="val">¥500</div></div>
          <div class="fee-row"><div class="name">参加費<small>トーナメントごとに定められた参加費（ランクが上がるほどプライズも豪華に）</small></div><div class="val">¥2,000〜</div></div>
        </div>
        <p class="note" style="margin-top:12px">◎リングゲーム等その他ゲームにご参加の際にお支払いいただいた場合は入場料・ドリンク代は不要です。</p>
        <div style="margin-top:18px"><a href="/housetournament-summary" class="btn btn-primary">ハウストーナメント一覧 <span class="arrow">›</span></a></div>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">RANK</span><h2>トーナメントランクについて</h2>
          <p class="sub">レギュレーションに応じて S〜D ランクに分かれています。</p></div>
        <div class="cards">
{rankcards}
        </div>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
"""
    doc("/tournament-infomation", "トーナメントのご案内 | ポーカールーム YORIMICHI",
        "YORIMICHIのトーナメントの料金システムとS〜Dのトーナメントランクについてご案内します。",
        crumbs([("HOME","/"),("トーナメントのご案内",None)]), body)
    PAGES.append(("/tournament-infomation","トーナメントのご案内"))

def render_monthlyschedule():
    imgs = pageimg.get("/monthlyschedule", [])
    cal = next((i for i in imgs if "img_05_" not in i), None)
    calhtml = f'      <div class="figure tall"><img src="{IMG(cal)}" alt="今月のスケジュールカレンダー"></div>\n      <p class="figcap">《タップ・クリックで拡大できます》</p>\n' if cal else ""
    body = page_hero("MONTHLY", "マンスリースケジュール", "リングゲーム・トーナメントの各種イベント情報です") + f"""  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><h2>充実のイベント</h2></div>
        <p>YORIMICHIではリングゲームやトーナメントのイベントをたくさん開催しています。普段とは一味違うポーカーが楽しめたり、他のプレイヤーと交流を深められるイベントもあるので、ぜひチェックしてみてください♪</p>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">CALENDAR</span><h2>今月のスケジュール</h2></div>
{calhtml}      </div>
      <div class="block">
        <div class="block-head"><span class="en">PICK UP</span><h2>【6月のイベント・営業カレンダー】</h2></div>
        <p>今月はつっきー卒業イベントやスタッフBountyトナメなどトナメが面白い内容になっています🌸</p>
        <ul class="dots">
          <li>⭐️ 6/27(土) つっきー卒業イベント開催</li>
          <li>⭐️ 6/6(土)&amp;6/13(土) 19:00〜 ビギナー限定トーナメント開催</li>
          <li>⭐️ 6/1(月)〜6/30(火) 来店スタンプラリー🌸 雨の日は来店スタンプ2倍 ※台紙配布中🔍</li>
          <li>⭐️ 6/8(月)〜6/14(日) アーリーバード開催🐦</li>
        </ul>
      </div>
      <div class="block">
        <div class="block-head"><h2>🆕 スタッフBountyトーナメント</h2></div>
        <p>毎週木曜日はスタッフBounty Y$1,000をGETできるチャンス🥊 YORIMICHIメンバーからランダムにトーナメントに参加します✨</p>
      </div>
      <div class="block">
        <div class="block-head"><h2>🆕 貸し卓プラン登場！</h2></div>
        <ul class="dots">
          <li>営業時間：17:00〜23:00</li>
          <li>卓数：1〜2卓（先着順）</li>
          <li>料金：1卓 15,000円（チップ貸出込み・ディーラーなし）</li>
          <li>飲食の持ち込みOK（店舗からの提供はございません）</li>
          <li>ゴミはお持ち帰りをお願いいたします</li>
          <li>ご予約方法：LINEにてお問い合わせください</li>
        </ul>
        <p class="note" style="margin-top:14px">※営業日は変動する可能性があります。最新情報はストーリー・Xをご確認ください。</p>
        <div style="margin-top:16px"><a href="%LINE%" class="btn btn-line" target="_blank" rel="noopener">LINEでお問い合わせ <span class="arrow">›</span></a></div>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
""".replace("%LINE%", LINE)
    doc("/monthlyschedule", "マンスリースケジュール | ポーカールーム YORIMICHI",
        "YORIMICHIの今月のイベント・営業カレンダー。リングゲーム・トーナメントの各種イベント情報です。",
        crumbs([("HOME","/"),("マンスリースケジュール",None)]), body, IMG(cal) if cal else "/assets/img/hero_room.webp")
    PAGES.append(("/monthlyschedule","マンスリースケジュール"))

print("part3 loaded")

def render_tablestatus():
    body = page_hero("TABLE STATUS", "現在の稼働状況", "現在のテーブルの稼働状況をご覧いただけます。") + """  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><h2>テーブル稼働状況</h2></div>
        <div class="status-box">
          <p class="big">YORIMICHIの現在のテーブルの稼働状況をご覧いただけます。<br>おひとり様でもすぐにご案内可能です。</p>
          <p class="note" style="margin-top:14px">※混雑時は更新が遅れる場合もございます。</p>
        </div>
        <p style="margin-top:24px;text-align:center">皆様のご来場 お待ちしております！<br>少人数時はたくさんハンドをプレイできてオススメです！</p>
        <div style="margin-top:18px;text-align:center"><a href="%LINE%" class="btn btn-line" target="_blank" rel="noopener">LINEで確認・お問い合わせ <span class="arrow">›</span></a></div>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
""".replace("%LINE%", LINE)
    doc("/tablestatus", "現在の稼働状況 | ポーカールーム YORIMICHI",
        "YORIMICHIの現在のテーブル稼働状況。おひとり様でもすぐにご案内可能です。",
        crumbs([("HOME","/"),("稼働状況",None)]), body)
    PAGES.append(("/tablestatus","稼働状況"))

def render_monthlyranking():
    body = page_hero("MONTHLY RANKING", "月間ランキング", "今月のランキングと過去のバックナンバーをご確認いただけます。") + """  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><h2>リングゲームランキング</h2>
          <p class="sub">リングゲームの現在のランキング状況です。※50NLは対象外です。</p></div>
        <div class="block-head" style="margin-top:24px"><h2>プライズ</h2></div>
        <div class="fee-list">
          <div class="fee-row"><div class="name">1位</div><div class="val">Y$ 10,000</div></div>
          <div class="fee-row"><div class="name">2位</div><div class="val">Y$ 5,000</div></div>
          <div class="fee-row"><div class="name">3位</div><div class="val">Y$ 3,000</div></div>
          <div class="fee-row"><div class="name">4位</div><div class="val">Y$ 2,000</div></div>
          <div class="fee-row"><div class="name">5位</div><div class="val">Y$ 1,000</div></div>
        </div>
        <p class="note" style="margin-top:12px">※プライズの付与は月末の営業終了時に行われます。</p>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">TOURNAMENT</span><h2>月間トーナメントランキング</h2></div>
        <div class="list-rows">
          <a href="/g9rZPguu2/tournamentranking_202606"><span class="t">【6月】月間トーナメントランキング</span><span class="d">2026/5/20</span></a>
          <a href="/g9rZPguu2/tournamentranking_202605"><span class="t">【5月】月間トーナメントランキング</span><span class="d">2026/4/27</span></a>
          <a href="/g9rZPguu2/tournamentranking_202604"><span class="t">【4月】月間トーナメントランキング</span><span class="d">2026/4/1</span></a>
          <a href="/g9rZPguu2/tournamentranking_rules"><span class="t">月間トーナメントランキングのルール・概要</span><span class="d">2026/4/1</span></a>
        </div>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
"""
    doc("/monthlyranking", "月間ランキング | ポーカールーム YORIMICHI",
        "YORIMICHIの月間ランキング。リングゲームランキングのプライズと月間トーナメントランキングをご確認いただけます。",
        crumbs([("HOME","/"),("月間ランキング",None)]), body)
    PAGES.append(("/monthlyranking","月間ランキング"))

def render_recruit():
    body = page_hero("RECRUIT", "求人情報", "YORIMICHIで一緒に働きませんか？") + """  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><h2>スタッフ募集</h2></div>
        <p>ポーカールームYORIMICHIでは一緒に働いてくれるメンバーを随時募集しております。皆様のお申し込みをお待ちしております！</p>
        <div style="margin-top:16px"><a href="/entry" class="btn btn-primary">エントリーはこちら <span class="arrow">›</span></a></div>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">REQUIREMENTS</span><h2>募集要項</h2>
          <p class="sub">ポーカー好き・接客好きな方大歓迎！</p></div>
        <p>社内研修にて専門的な知識を身につけていただくので、経験の有無は問いません。私たちと一緒に楽しい空間をつくりましょう！</p>
      </div>
      <div class="block">
        <div class="block-head"><h2>業務内容</h2></div>
        <ul class="dots">
          <li>トランプ・チップを用いたゲームの進行（ディーリング）</li>
          <li>お客様との会話でテーブルを盛り上げること</li>
          <li>各種システムを用いた、店舗やお客様のチップの収支管理</li>
        </ul>
      </div>
      <div class="block">
        <div class="block-head"><h2>勤務形態／給与</h2></div>
        <table class="spec">
          <tr><th>勤務形態</th><td>アルバイト／自由シフト制</td></tr>
          <tr><th>勤務時間</th><td>16:30〜23:30の中で応相談</td></tr>
          <tr><th>勤務日数</th><td>3日/週〜・3時間〜/日</td></tr>
          <tr><th>交通費</th><td>支給あり</td></tr>
          <tr><th>試用期間</th><td>2か月</td></tr>
          <tr><th>勤務地</th><td>ポーカールーム YORIMICHI<br>〒410-0803 静岡県沼津市添地町72 青秀ビル 5F</td></tr>
        </table>
      </div>
      <div class="block" style="text-align:center">
        <h2 style="font-size:20px;margin-bottom:14px">あなたもディーラーデビュー！</h2>
        <a href="/entry" class="btn btn-primary">エントリーはこちらから <span class="arrow">›</span></a>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
"""
    doc("/recruit", "求人情報 | ポーカールーム YORIMICHI",
        "ポーカールームYORIMICHIのスタッフ（ディーラー）募集。経験不問・社内研修あり。沼津駅南口徒歩5分。",
        crumbs([("HOME","/"),("求人情報",None)]), body)
    PAGES.append(("/recruit","求人情報"))

def render_entry():
    body = page_hero("ENTRY", "エントリー", "求人のご応募はこちらから！") + """  <section class="page-body">
    <div class="container">
      <div class="block">
        <div class="block-head"><h2>求人応募フォーム</h2></div>
        <p class="note">ご返信に最大3営業日ほどお時間をいただいております。3営業日を過ぎても返信がない場合は、お手数ですが再度お問い合わせをお願いいたします。</p>
      </div>
      <form class="form" onsubmit="alert('現行サイトの応募フォームへ接続予定です。お急ぎの方はLINEまたはお電話ください。');return false;">
        <div class="row2">
          <div class="fld"><label>姓 <span class="req">必須</span></label><input type="text" required></div>
          <div class="fld"><label>名 <span class="req">必須</span></label><input type="text" required></div>
        </div>
        <div class="row2">
          <div class="fld"><label>姓（かな） <span class="req">必須</span></label><input type="text" required></div>
          <div class="fld"><label>名（かな） <span class="req">必須</span></label><input type="text" required></div>
        </div>
        <div class="fld"><label>生年月日 <span class="req">必須</span></label><input type="date" required></div>
        <div class="fld"><label>ポーカーディーラーのご経験 <span class="req">必須</span></label>
          <div class="radios"><label><input type="radio" name="exp"> あり</label><label><input type="radio" name="exp"> なし</label></div>
          <p class="note" style="margin-top:6px">経験がある方はディーラー歴と所属していた店舗もお書きください。</p></div>
        <div class="row2">
          <div class="fld"><label>ディーラー歴</label><input type="text"></div>
          <div class="fld"><label>所属店舗</label><input type="text"></div>
        </div>
        <div class="fld"><label>電話番号 <span class="req">必須</span></label><input type="tel" required></div>
        <div class="fld"><label>メールアドレス <span class="req">必須</span></label><input type="email" required></div>
        <div class="fld"><label>アピールポイント <span class="req">必須</span></label><textarea required></textarea></div>
        <div class="fld"><label><input type="checkbox" required> <a href="/privacy-policy" style="color:var(--accent)">プライバシーポリシー</a> に同意して送信する</label></div>
        <button type="submit" class="btn btn-primary submit">上記の内容で送信する <span class="arrow">›</span></button>
      </form>
      <div class="back-link"><a href="/recruit">‹ 求人情報へ戻る</a></div>
    </div>
  </section>
"""
    doc("/entry", "エントリーフォーム | ポーカールーム YORIMICHI",
        "ポーカールームYORIMICHIの求人応募（エントリー）フォームです。",
        crumbs([("HOME","/"),("求人情報","/recruit"),("エントリーフォーム",None)]), body)
    PAGES.append(("/entry","エントリーフォーム"))

def render_houserule():
    t = clean["/houserule"]
    for pre in ["ハウスルールについて YORIMICHIのハウスルールについてご案内します。"]:
        if t.startswith(pre): t = t[len(pre):].strip()
    for m in ["HOME keyboard_arrow_right"]:
        i = t.find(m)
        if i > 0: t = t[:i].strip()
    paras = "\n".join(f'        <p>{esc(p)}</p>' for p in paragraphize(t))
    body = page_hero("HOUSE RULE", "ハウスルールについて", "YORIMICHIのハウスルールについてご案内します。") + f"""  <section class="page-body">
    <div class="container">
      <div class="block">
{paras}
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
"""
    doc("/houserule", "ハウスルールについて | ポーカールーム YORIMICHI",
        "YORIMICHIのハウスルール（リングゲーム・トーナメント）についてご案内します。",
        crumbs([("HOME","/"),("ハウスルール",None)]), body)
    PAGES.append(("/houserule","ハウスルール"))

def render_privacy():
    t = clean["/privacy-policy"]
    for pre in ["プライバシーポリシー"]:
        if t.startswith(pre): t = t[len(pre):].strip()
    for m in ["HOME keyboard_arrow_right"]:
        i = t.find(m)
        if i > 0: t = t[:i].strip()
    parts = re.split(r'(第\d+条（[^）]+）)', t)
    html_parts = []
    if parts[0].strip():
        html_parts.append(f'        <p>{esc(parts[0].strip())}</p>')
    for i in range(1, len(parts), 2):
        heading = parts[i]
        content = parts[i+1] if i+1 < len(parts) else ""
        html_parts.append(f'        <h3 style="font-size:16px;font-weight:700;margin:26px 0 10px">{esc(heading)}</h3>')
        for p in paragraphize(content):
            html_parts.append(f'        <p>{esc(p)}</p>')
    body = page_hero("PRIVACY POLICY", "プライバシーポリシー") + f"""  <section class="page-body">
    <div class="container">
      <div class="block">
{chr(10).join(html_parts)}
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
"""
    doc("/privacy-policy", "プライバシーポリシー | ポーカールーム YORIMICHI",
        "BeeBloom合同会社（ポーカールームYORIMICHI）のプライバシーポリシーです。",
        crumbs([("HOME","/"),("プライバシーポリシー",None)]), body)
    PAGES.append(("/privacy-policy","プライバシーポリシー"))

def render_contact():
    body = page_hero("CONTACT", "お問い合わせ", "各種お問い合わせは公式LINEにて承っております。") + f"""  <section class="page-body">
    <div class="container">
      <div class="block">
        <p>ポーカーデビュープランのご予約やその他ご質問など、お気軽にお問い合わせください◎</p>
        <div style="margin:22px 0"><a href="{LINE}" class="btn btn-line" target="_blank" rel="noopener">LINEでお問い合わせ <span class="arrow">›</span></a></div>
        <p>お急ぎのお客様は下記のお電話にてご連絡ください。</p>
        <div class="fee-list" style="margin-top:14px">
          <div class="fee-row"><div class="name">電話番号</div><div class="val"><a href="tel:{TEL.replace('-','')}">{TEL}</a></div></div>
        </div>
      </div>
      <div class="block">
        <div class="block-head"><span class="en">SNS</span><h2>公式SNS</h2></div>
        <div class="chip-list">
          <a href="{IG}" target="_blank" rel="noopener">Instagram</a>
          <a href="{X}" target="_blank" rel="noopener">X (旧Twitter)</a>
        </div>
      </div>
      <div class="back-link"><a href="/">‹ HOMEへ戻る</a></div>
    </div>
  </section>
"""
    doc("/contact", "ポーカールームYORIMICHI【お問い合わせ】",
        "静岡・沼津のポーカールームYORIMICHIへのお問い合わせは公式LINEアカウントまで♪",
        crumbs([("HOME","/"),("お問い合わせ",None)]), body)
    PAGES.append(("/contact","お問い合わせ"))

def render_tourny_static():
    path = "/tourny-20251016"
    spec = [
        ("日程","2025年10月16日(木) 17:20〜"),
        ("レイトレジスト締切","Lv.11開始時まで（20:00ごろ）"),
        ("ゲーム","ノーリミット／テキサスホールデム"),
        ("トーナメントランク","Bランク"),
        ("参加費","¥5,000（リエントリー：¥4,000）"),
        ("スタック","50,000点"),
        ("ブラインド","15 - 10分"),
        ("終了想定","22:00ごろ"),
    ]
    img = (pageimg.get(path) or [None])[0]
    spechtml = "\n".join(f'          <tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in spec)
    leadimg = f'      <div class="lead-img"><img src="{IMG(img)}" alt=""></div>\n' if img else ""
    body = f"""  <section class="page-body">
    <div class="container article">
      <div class="meta">2025/10/16　|　トーナメントイベント</div>
      <h1 class="title">【iroha・Ryooona壮行】英語禁止！真の飲みぽを見せてやるぜトーナメント</h1>
{leadimg}      <div class="block">
        <div class="block-head"><span class="en">SUMMARY</span><h2>トーナメント概要</h2></div>
        <table class="spec">
{spechtml}
        </table>
      </div>
      <div class="block">
        <div class="block-head"><h2>《Pick up！》</h2></div>
        <ul class="dots">
          <li>◎ トナメ【参加者全員】にウェルカムクライナー1本プレゼント！</li>
          <li>◎ 通常¥3,000の飛ぶまで飲み放題が【無料】でつきます！</li>
          <li>◎【早期着席特典】として、17:30までの着席でFlip-outに参加できます♪</li>
          <li>◎ Ryooonaもプレイヤーで参加します！（irohaは無限にみんなのドリンクを作るので、その場の気分次第で参加します）</li>
          <li>Ryooonaを倒せば豪華バウンティ！ただし、Ryooonaに飛ばされると罰ゲームあり😆</li>
        </ul>
      </div>
      <div class="block">
        <div class="block-head"><h2>詳細情報</h2></div>
        <p>8月のオープンからYORIMICHIの立ち上げと店舗運営のお手伝いをしていただいたirohaさんとRyooonaさんが10月16日(木)の営業をもってYORIMICHIを離れるので、お別れの記念イベントを開催します！ぜひ最後にお二人に会いに来てください♪</p>
        <p>今回のトーナメントは【英語禁止】＆【飛ぶまで飲み放題】トナメ！ YORIMICHI初の飲みぽイベントです。</p>
      </div>
      <div class="back-link"><a href="/tounament-events">‹ トーナメントイベント一覧へ戻る</a></div>
    </div>
  </section>
"""
    doc(path, "【iroha・Ryooona壮行】英語禁止！真の飲みぽを見せてやるぜトーナメント | YORIMICHI",
        "iroha・Ryooona壮行イベント。英語禁止＆飛ぶまで飲み放題、YORIMICHI初の飲みぽトーナメント。",
        crumbs([("HOME","/"),("トーナメントイベント","/tounament-events"),("iroha・Ryooona壮行",None)]),
        body, IMG(img) if img else "/assets/img/hero_room.webp")
    PAGES.append((path,"iroha・Ryooona壮行トーナメント"))

print("part4 loaded")

# ===========================================================================
#  トップページ
# ===========================================================================
def card(path, title, date, img):
    bg = IMG(img) if img else "/assets/img/hero_ingame.webp"
    return f"""        <a class="news-card" href="{path}">
          <div class="thumb" style="background-image:url('{bg}')"></div>
          <div class="body"><div class="date">{esc(date)}</div><div class="title">{esc(title)}</div></div>
        </a>"""

def render_top():
    news = sorted([p for p in ART if p.startswith("/koJlgd6l2")],
                  key=lambda p: datekey(ART[p][1]), reverse=True)[:3]
    tour = sorted([p for p in ART if p.startswith("/g9rZPguu2")],
                  key=lambda p: datekey(ART[p][1]), reverse=True)[:3]
    def pick(p):
        imgs = pageimg.get(p, [])
        return next((i for i in imgs if "img_05_" not in i), imgs[0] if imgs else None)
    news_cards = "\n".join(card(p, ART[p][0], ART[p][1], pick(p)) for p in news)
    tour_cards = "\n".join(card(p, ART[p][0], ART[p][1], pick(p)) for p in tour)
    body = f"""  <section class="hero" id="top">
    <div class="container">
      <h1>いつもの道に<br><span class="accent">＋ポーカー</span>を。</h1>
      <p class="tagline">「ちょっと寄り道」から始まる、新しいポーカー体験。</p>
      <p class="desc">YORIMICHIは、ポーカー初心者の方でも安心して楽しめる、バーカウンター併設のカジュアルポーカールームです！見たことがなくても、知らなくてもOK。スタッフ一同、あなたのポーカーデビューをサポートします！</p>
      <div class="hero-cta">
        <a href="/for_beginner" class="btn btn-primary">はじめての方へ <span class="arrow">›</span></a>
        <a href="#access" class="btn btn-ghost">アクセス</a>
      </div>
    </div>
    <div class="scroll-hint">SCROLL</div>
  </section>

  <section class="quickbar">
    <div class="inner">
      <div><span class="k">FIRST PLAY</span><span class="v">デビュー ¥3,000〜</span></div>
      <a href="/monthlyschedule"><span class="k">OPEN</span><span class="v">営業カレンダー ›</span></a>
      <a href="/#access"><span class="k">ACCESS</span><span class="v">JR沼津駅 徒歩5分</span></a>
    </div>
  </section>

  <section class="section steps">
    <div class="container">
      <div class="section-head" style="text-align:center"><span class="en">EASY 3 STEPS</span><h2>ご来店までの3ステップ</h2></div>
      <div class="step-grid">
        <div class="step"><div class="ico">💬</div><h3>LINEで予約</h3><p>公式LINEで「ポーカーデビュープラン希望」とメッセージ。日時を決めるだけ。ひとりでもOKです。</p></div>
        <div class="step"><div class="ico">🃏</div><h3>来店・ルール説明</h3><p>スタッフが役・用語・進行を1から丁寧にご案内。練習用チップで実践練習できるので未経験でも安心。</p></div>
        <div class="step"><div class="ico">🎉</div><h3>ポーカーデビュー！</h3><p>そのままライブポーカーへ。参加費¥3,000／60〜90分。あなたのデビューをサポートします。</p></div>
      </div>
      <div style="text-align:center;margin-top:34px">
        <a href="{LINE}" class="btn btn-line" target="_blank" rel="noopener">💬 LINEで予約・相談する <span class="arrow">›</span></a>
      </div>
    </div>
  </section>

  <section class="section debut" id="debut">
    <div class="container">
      <div class="section-head"><span class="en">FOR BEGINNERS</span><h2>はじめての方へ</h2></div>
      <div class="debut-body">
        <p>ポーカーと聞くと、ギャンブルのようなこわい印象を持つ方もいるかもしれませんが、海外では友人や家族と気軽に楽しむコミュニケーションゲームとして親しまれています。</p>
        <p>最近では、YouTubeやアプリゲームを通じて、誰でも気軽にポーカーの世界を体験できるようになりました。</p>
        <p>当店ではライブポーカーが初めてのお客さま専用の「ポーカーデビュープラン」をご用意しております。スタッフが1から丁寧にルール説明やライブポーカーの遊び方をご案内いたしますので、どなたでもお気軽にご来場いただけます。</p>
        <p>あなたもぜひ一度、ライブポーカーの世界を体験してみませんか？きっと素敵な出会いが待っています。</p>
        <div class="price-card"><span class="label">参加費</span><span class="yen">¥3,000</span><span class="unit">／ 60〜90分</span></div>
        <div><a href="/for_beginner" class="btn btn-primary">🔰 ポーカー体験会を予約する <span class="arrow">›</span></a></div>
      </div>
    </div>
  </section>

  <section class="section" id="news">
    <div class="container">
      <div class="section-head"><span class="en">NEWS</span><h2>お知らせ</h2></div>
      <div class="news-grid">
{news_cards}
      </div>
      <div class="view-more"><a href="/news">VIEW MORE</a></div>
    </div>
  </section>

  <section class="section schedule" id="tournament">
    <div class="container">
      <div class="section-head"><span class="en">TOURNAMENT</span><h2>トーナメントイベント</h2></div>
      <div class="news-grid">
{tour_cards}
      </div>
      <div class="view-more"><a href="/tounament-events">VIEW MORE</a></div>
    </div>
  </section>

  <section class="section info" id="info">
    <div class="container">
      <div class="section-head" style="text-align:center"><span class="en">INFORMATION</span><h2>ゲームのご案内</h2></div>
      <div class="info-grid">
        <div class="info-item">
          <div class="pic" style="background-image:url('/assets/img/info_ring.webp')"></div>
          <div class="txt"><h3><span class="en">RING GAME</span>リングゲーム</h3>
            <p>好きな時間に参加・退席できる、カジュアルなゲームスタイルです。ビギナープレイヤー専用のレートもご用意しているので、ポーカーデビューにもピッタリです。</p>
            <div class="links"><a href="/cashgame-infomation">リングゲームのご案内</a></div></div>
        </div>
        <div class="info-item">
          <div class="pic" style="background-image:url('/assets/img/info_tournament.webp')"></div>
          <div class="txt"><h3><span class="en">TOURNAMENT</span>トーナメント</h3>
            <p>最後の一人の優勝者が決定するまで戦い抜く、大会形式のゲームスタイルです。ハウストーナメントのストラクチャー情報等も掲載しております。</p>
            <div class="links"><a href="/tournament-infomation">トーナメントのご案内</a><a href="/housetournament-summary">ハウストーナメント一覧</a></div></div>
        </div>
        <div class="info-item">
          <div class="pic" style="background-image:url('/assets/img/info_monthly.webp')"></div>
          <div class="txt"><h3><span class="en">MONTHLY</span>マンスリースケジュール</h3>
            <p>リングゲームイベントやトーナメントの月間スケジュールです。楽しいイベントが盛り沢山なので、ぜひチェックしてみてください。</p>
            <div class="links"><a href="/monthlyschedule">マンスリースケジュール</a></div></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section ladies">
    <div class="container">
      <span class="badge">EVERY THURSDAY</span>
      <h2>毎週木曜日はレディースデー</h2>
      <p>女性のお客様はおトクにリングゲーム・トーナメントを楽しめます。</p>
    </div>
  </section>

  <section class="section line-cta">
    <div class="container">
      <h2>わからないことはなんでも<br>LINEでお問い合わせください♪</h2>
      <p>「結局いくらかかるの？」「ひとりでも大丈夫？」などなど、ご来場に際してのご不明点はすべてLINEでお尋ねください！スタッフが丁寧にお答えいたします。</p>
      <a href="{LINE}" class="btn btn-line" target="_blank" rel="noopener">LINEでお問い合わせ <span class="arrow">›</span></a>
    </div>
  </section>

  <section class="section access" id="access">
    <div class="container">
      <div class="section-head"><span class="en">ACCESS</span><h2>アクセス</h2></div>
      <div class="access-wrap">
        <div class="access-info">
          <h3>ポーカールーム YORIMICHI</h3>
          <p class="addr"><span class="post">〒410-0803</span><br>静岡県沼津市添地町72 青秀ビル 5F<br>・JR沼津駅南口より 徒歩5分</p>
          <p class="note">※駐車場のご用意はございません。お車でお越しの場合は近隣のコインパーキングをご利用ください。</p>
          <a href="{GMAP}" target="_blank" rel="noopener" class="btn btn-primary">Google Mapで見る <span class="arrow">›</span></a>
        </div>
        <div class="access-map">
          <iframe src="https://maps.google.com/maps?q=静岡県沼津市添地町72&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="YORIMICHI 地図"></iframe>
        </div>
      </div>
    </div>
  </section>
"""
    html_out = head("ポーカールーム YORIMICHI | 沼津初のポーカールーム",
                    "静岡・沼津初のポーカールームYORIMICHI（ヨリミチ）の公式HP。JR沼津駅南口から徒歩5分。日本でいちばん気軽に立ち寄れるポーカールームを目指しています。") \
               + header() + body + footer()
    write("/", html_out)
    PAGES.append(("/", "TOP"))

# ===========================================================================
#  実行
# ===========================================================================
def main():
    render_top()
    render_for_beginner()
    render_monthlyschedule()
    render_cashgame()
    render_tournament_info()
    render_house_summary()
    render_tablestatus()
    render_monthlyranking()
    render_recruit()
    render_entry()
    render_houserule()
    render_privacy()
    render_contact()
    render_tourny_static()
    render_news_list()
    render_tourny_events_list()
    for slug, name, date, rank, levels in TOURN:
        render_tournament(slug, name, date, rank, levels)
    for p in [x for x in ART if x.startswith("/koJlgd6l2")]:
        render_article(p, "news")
    for p in [x for x in ART if x.startswith("/g9rZPguu2")]:
        render_article(p, "tourny")
    print(f"\n✅ 生成完了: {len(PAGES)} ページ")
    for path, title in PAGES:
        print(f"   {path}")

if __name__ == "__main__":
    main()
