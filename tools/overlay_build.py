#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
overlay_build.py — YORIMICHI公式HP 社員更新システム（上書きビルド）
公開シート(CSV)を読み、data-slot に内容を上書き/削除する。HTMLは再整形しない（該当箇所のみ置換）。
CSV列（順不同・ヘッダー必須）: slotId, 操作, 内容   （他列は無視）
  操作: 修正=内容で置換 / 削除=非表示
使い方:
  python3 tools/overlay_build.py --csv <URL|ファイル>   本反映
  python3 tools/overlay_build.py --csv <...> --dry       変更内容の確認のみ
戻り値: 変更があれば標準出力にサマリ。ファイルは差分箇所のみ書換。
"""
import os, sys, re, csv, json, html, argparse, io
from urllib.request import urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def slot_to_path(slot):
    key = slot.rsplit('-', 1)[0]          # 末尾の連番を除いた部分がpageKey
    if key == 'home':
        return 'index.html'
    return key.replace('__', '/') + '/index.html'


def esc(s):
    s = html.escape(s, quote=False)
    return s.replace('\r\n', '\n').replace('\n', '<br>')


def replace_text(htmltext, slot, new):
    # <tag ... data-slot="slot" ...>INNER</tag>  純テキスト葉なので最短一致でOK
    pat = re.compile(r'(<(\w+)\b[^>]*\bdata-slot="' + re.escape(slot) + r'"[^>]*>)(.*?)(</\2>)', re.S)
    return pat.subn(lambda m: m.group(1) + esc(new) + m.group(4), htmltext, count=1)


def hide_text(htmltext, slot):
    pat = re.compile(r'(<(\w+)\b)([^>]*\bdata-slot="' + re.escape(slot) + r'"[^>]*>)(.*?)(</\2>)', re.S)
    def rep(m):
        head = m.group(1)
        attrs = m.group(3)
        if ' hidden' in attrs:
            return m.group(0)
        return head + ' hidden' + attrs + '' + m.group(5)
    return pat.subn(rep, htmltext, count=1)


def replace_img(htmltext, slot, new):
    pat = re.compile(r'<img\b[^>]*\bdata-slot="' + re.escape(slot) + r'"[^>]*>', re.S)
    def rep(m):
        tag = m.group(0)
        if re.search(r'\bsrc="', tag):
            return re.sub(r'\bsrc="[^"]*"', 'src="' + html.escape(new, quote=True) + '"', tag, count=1)
        return tag[:-1].rstrip('/') + ' src="' + html.escape(new, quote=True) + '">'
    return pat.subn(rep, htmltext, count=1)


def norm(key):
    return (key or '').strip().replace('﻿', '')


def load_rows(src):
    if re.match(r'^https?://', src):
        data = urlopen(src, timeout=30).read().decode('utf-8')
    else:
        data = open(src, encoding='utf-8').read()
    all_rows = list(csv.reader(io.StringIO(data)))
    # 見出し行を自動検出（「操作」列を含む行）。バナー行があっても対応。
    hidx = 0
    for i, r in enumerate(all_rows):
        cells = [norm(c) for c in r]
        if any('操作' in c for c in cells) and any(('場所' in c or 'slot' in c.lower()) for c in cells):
            hidx = i
            break
    header = [norm(c) for c in all_rows[hidx]]
    out = []
    for r in all_rows[hidx + 1:]:
        out.append({header[j]: (r[j] if j < len(r) else '') for j in range(len(header))})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    reg = json.load(open('data/slots.json', encoding='utf-8'))
    slots = {s['slotId']: s for s in reg}
    by_label = {s['label']: s['slotId'] for s in reg}
    rows = load_rows(args.csv)

    # 列名を正規化（前後空白・BOM除去）してマップ
    def getcol(row, *names):
        m = {norm(k): (v or '') for k, v in row.items()}
        # 完全一致優先 → 部分一致
        for n in names:
            if n in m:
                return m[n].strip()
        for n in names:
            for k, v in m.items():
                if n and n.lower() in k.lower():
                    return v.strip()
        return ''

    files = {}          # path -> text（キャッシュ）
    applied, skipped, errors = [], [], []

    for i, row in enumerate(rows, 2):
        slot = getcol(row, 'slotId', 'slot')
        if not slot:
            # slotId列が無ければ「場所」ラベルから解決
            slot = by_label.get(getcol(row, '場所', 'place', 'location'), '')
        op = getcol(row, '操作', 'op')
        content = getcol(row, '内容', 'content')
        if not slot:
            continue
        if slot not in slots:
            errors.append(f'行{i}: 不明なslot {slot}')
            continue
        if op == '修正' and content == '':
            skipped.append(f'行{i}: {slot} 内容空のためスキップ')
            continue
        path = slot_to_path(slot)
        if path not in files:
            if not os.path.exists(path):
                errors.append(f'行{i}: ファイル無し {path}')
                continue
            files[path] = open(path, encoding='utf-8').read()
        text = files[path]
        typ = slots[slot]['type']

        if op == '削除':
            new, n = hide_text(text, slot)
        elif typ == 'image':
            new, n = replace_img(text, slot, content)
        else:
            new, n = replace_text(text, slot, content)

        if n == 0:
            errors.append(f'行{i}: {slot} 該当要素が見つからず')
            continue
        if new != text:
            files[path] = new
            applied.append(f'{slot} [{op or "修正"}] ← {content[:30]}')

    # 書き出し
    changed = 0
    for path, text in files.items():
        cur = open(path, encoding='utf-8').read()
        if cur != text:
            changed += 1
            if not args.dry:
                open(path, 'w', encoding='utf-8').write(text)

    print(f'=== overlay_build {"(DRY)" if args.dry else ""} ===')
    print(f'適用: {len(applied)}件 / 変更ファイル: {changed} / スキップ: {len(skipped)} / エラー: {len(errors)}')
    for a in applied:
        print('  ✔', a)
    for s in skipped:
        print('  －', s)
    for e in errors:
        print('  ✖', e)
    # Actions用: 変更有無を終了コードで返す（0=変更あり? いや常に0、GITHUB_OUTPUTで通知）
    gh_out = os.environ.get('GITHUB_OUTPUT')
    if gh_out:
        with open(gh_out, 'a') as f:
            f.write(f'changed={changed}\n')


if __name__ == '__main__':
    main()
