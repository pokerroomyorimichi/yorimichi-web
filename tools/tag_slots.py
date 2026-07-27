#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tag_slots.py — YORIMICHI公式HP 社員更新システム（タグ付けエンジン）
全ページの編集可能要素に data-slot 属性を「外科的に」挿入し、登録簿 data/slots.json を生成する。
※ HTMLは再整形しない（属性だけ追記＝差分は挿入のみ・既存マークアップ不変）。
- 対象: コンテンツ領域の「純テキストの葉要素」＋コンテンツ画像
- 除外: ヘッダー/ドロワー/フッター/フロートCTA/パンくず/クイックバー/script/style
- 既に data-slot がある要素は温存（冪等）。IDは付与順に固定。
使い方: cd yorimichi-web && python3 tools/tag_slots.py
"""
import os, json, glob, re
from bs4 import BeautifulSoup, Tag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SKIP_SELECTORS = ['header', 'footer', 'nav', 'script', 'style',
                  '.floatbar', '.fixedcta', '.breadcrumb', '.quickbar',
                  '.drawer', '.hd', '.ft', '.adj', '.proto-note']
TEXT_TAGS = {'h1', 'h2', 'h3', 'h4', 'p', 'li', 'th', 'td', 'summary', 'figcaption'}
TEXT_CLASSES = {'en', 'lead', 'sub', 'ttl', 'meta', 'figcap', 'tagline',
                'desc', 'val', 'big', 'name', 'day'}
PAGE_LABELS = {'home': 'トップページ'}


def page_key(path):
    d = os.path.dirname(path)
    return 'home' if d == '' else d.replace('/', '__')


def page_label(soup, key):
    if key in PAGE_LABELS:
        return PAGE_LABELS[key]
    t = soup.find('title')
    return re.split(r'[|｜]', t.get_text())[0].strip() if t else key


def in_skip(el, skip_nodes):
    return any(a in skip_nodes for a in el.parents)


def is_pure_text_leaf(el):
    return not any(isinstance(c, Tag) for c in el.children)


def group_label(el):
    for anc in el.parents:
        if not isinstance(anc, Tag):
            continue
        cls = anc.get('class') or []
        if any(c in cls for c in ('block', 'section', 'page-hero', 'article',
                                  'step', 'scard', 'info-item', 'fee-row')):
            h = anc.find(['h1', 'h2', 'h3'])
            if h and h.get_text(strip=True):
                return h.get_text(strip=True)[:20]
    return ''


def snippet(s, n=26):
    s = re.sub(r'\s+', ' ', s).strip()
    return (s[:n] + '…') if len(s) > n else s


def line_offsets(text):
    off = [0]
    for ln in text.split('\n'):
        off.append(off[-1] + len(ln) + 1)
    return off


def attr_insert_pos(text, off):
    """タグ '<name' の name 末尾位置を返す（属性を差し込む位置）。"""
    i = off + 1
    while i < len(text) and text[i] not in ' \t\n>/':
        i += 1
    return i


def main():
    files = sorted(f for f in glob.glob('**/index.html', recursive=True)
                   if not f.startswith('preview/'))
    registry = []
    total = 0
    for path in files:
        text = open(path, encoding='utf-8').read()
        soup = BeautifulSoup(text, 'html.parser')
        key = page_key(path)
        plabel = page_label(soup, key)
        loff = line_offsets(text)

        skip_nodes = set()
        for sel in SKIP_SELECTORS:
            skip_nodes.update(soup.select(sel))

        used = [int(m.group(1)) for el in soup.select('[data-slot]')
                for m in [re.match(rf'^{re.escape(key)}-(\d+)$', el.get('data-slot', ''))] if m]
        counter = max(used) + 1 if used else 1

        inserts = []   # (offset, text) 挿入指示
        page_slots = []

        def make_slot(el, typ, group, role, cur_full, cur_disp):
            nonlocal counter
            slot = el.get('data-slot')
            if not slot:
                slot = f'{key}-{counter:03d}'
                counter += 1
                if el.sourceline is None:
                    return None
                off = loff[el.sourceline - 1] + el.sourcepos
                pos = attr_insert_pos(text, off)
                inserts.append((pos, f' data-slot="{slot}"'))
                el['data-slot'] = slot
            num = slot.rsplit('-', 1)[1]
            grp = (group + ' / ') if group else ''
            label = f'{plabel} ▸ {num} {grp}{cur_disp}'
            page_slots.append({'slotId': slot, 'type': typ, 'group': group,
                               'role': role, 'current': cur_disp, 'current_full': cur_full,
                               'label': label, 'pageKey': key, 'pageLabel': plabel})
            return slot

        # テキスト葉
        for el in soup.find_all(True):
            if el in skip_nodes or in_skip(el, skip_nodes):
                continue
            cls = el.get('class') or []
            if not ((el.name in TEXT_TAGS) or any(c in TEXT_CLASSES for c in cls)):
                continue
            if not is_pure_text_leaf(el):
                continue
            txt = el.get_text(strip=True)
            if not txt or len(txt) <= 1:
                continue
            make_slot(el, 'text', group_label(el), el.name, txt, snippet(txt))

        # 画像
        for el in soup.find_all('img'):
            if el in skip_nodes or in_skip(el, skip_nodes):
                continue
            make_slot(el, 'image', el.get('alt', '') or '画像', 'img',
                      el.get('src', ''), snippet(el.get('src', ''), 40))

        # 挿入（末尾から適用してオフセットずれを回避）
        if inserts:
            for pos, ins in sorted(inserts, reverse=True):
                text = text[:pos] + ins + text[pos:]
            open(path, 'w', encoding='utf-8').write(text)

        registry.extend(page_slots)
        total += len(page_slots)
        print(f'{len(page_slots):3d} slots  {plabel}  ({path})')

    # ラベル一意化（同一タイトルのページ等で稀に重複 → slotIdを付す）
    seen = {}
    for s in registry:
        if s['label'] in seen:
            s['label'] = f"{s['label']} 〔{s['slotId']}〕"
        seen[s['label']] = True

    os.makedirs('data', exist_ok=True)
    json.dump(registry, open('data/slots.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'\n=== 合計 {total} slots / {len(files)} ページ → data/slots.json ===')


if __name__ == '__main__':
    main()
