#!/usr/bin/env python3
"""
import_backup.py

Reads a backup .txt/.json (the file produced by the web app "Export All") and extracts
- photos (data URLs) into `outdir/images/`
- letters into `outdir/letters.json` and `outdir/letters.txt`
- appreciation note into `outdir/appreciation.html`
- saves a copy of the original backup into `outdir/` as `backup-original.json`

Usage:
    python import_backup.py --input /path/to/lovelife-backup-2025-12-29.txt --outdir DATA

"""

import os
import sys
import json
import base64
import re
import argparse

DATA_URL_RE = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<data>.+)$", re.I)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_photos(photos, outdir):
    images_dir = os.path.join(outdir, 'images')
    ensure_dir(images_dir)
    written = []
    for i, dataurl in enumerate(photos, start=1):
        m = DATA_URL_RE.match(dataurl)
        if not m:
            print(f"[WARN] skipping non-data URL photo at index {i}")
            continue
        mime = m.group('mime').lower()
        b64 = m.group('data')
        ext = 'bin'
        if mime in ('image/jpeg', 'image/jpg'):
            ext = 'jpg'
        elif mime == 'image/png':
            ext = 'png'
        elif mime == 'image/gif':
            ext = 'gif'
        fname = f'img-{i:03d}.{ext}'
        path = os.path.join(images_dir, fname)
        try:
            with open(path, 'wb') as f:
                f.write(base64.b64decode(b64))
            written.append(path)
        except Exception as e:
            print(f"[ERROR] failed to write {path}: {e}")
    return written


def write_letters(letters, outdir):
    path_json = os.path.join(outdir, 'letters.json')
    with open(path_json, 'w', encoding='utf-8') as f:
        json.dump(letters, f, ensure_ascii=False, indent=2)
    # also write a human readable text
    path_txt = os.path.join(outdir, 'letters.txt')
    with open(path_txt, 'w', encoding='utf-8') as f:
        for i, l in enumerate(letters, start=1):
            f.write(f"--- Letter {i} ---\n")
            f.write(f"Title: {l.get('title','')}\n")
            f.write(f"Date: {l.get('created') and (\n                    __import__('datetime').datetime.fromtimestamp(l.get('created')/1000).isoformat() ) or ''}\n")
            f.write(l.get('body','') + "\n\n")
    return path_json, path_txt


def write_appreciation(app, outdir):
    path = os.path.join(outdir, 'appreciation.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('<!doctype html>\n<html><head><meta charset="utf-8"><title>Appreciation</title></head><body>')
        f.write(app or '')
        f.write('</body></html>')
    return path


def save_backup_copy(orig_text, outdir):
    path = os.path.join(outdir, 'backup-original.json')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(orig_text)
    return path


def main(argv=None):
    p = argparse.ArgumentParser(description='Import lovelife backup and extract into workspace folder')
    p.add_argument('--input', '-i', help='Path to exported backup .txt/.json', required=True)
    p.add_argument('--outdir', '-o', help='Output directory (default: DATA)', default='DATA')
    args = p.parse_args(argv)

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(2)

    ensure_dir(args.outdir)

    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    try:
        obj = json.loads(text)
    except Exception as e:
        print(f"Failed to parse JSON from backup: {e}")
        sys.exit(1)

    # save original copy
    try:
        copy_path = save_backup_copy(text, args.outdir)
        print(f"Saved backup copy to: {copy_path}")
    except Exception as e:
        print(f"Failed saving backup copy: {e}")

    photos = obj.get('photos', []) if isinstance(obj.get('photos', []), list) else []
    letters = obj.get('letters', []) if isinstance(obj.get('letters', []), list) else []
    appreciation = obj.get('appreciation', '')

    if photos:
        print(f"Writing {len(photos)} photos to {os.path.join(args.outdir,'images')}")
        written = write_photos(photos, args.outdir)
        for w in written:
            print('WROTE', w)
    else:
        print('No photos to write')

    if letters:
        jpath, tpath = write_letters(letters, args.outdir)
        print('WROTE letters JSON:', jpath)
        print('WROTE letters text:', tpath)
    else:
        print('No letters to write')

    if appreciation:
        ap = write_appreciation(appreciation, args.outdir)
        print('WROTE appreciation HTML:', ap)
    else:
        print('No appreciation note found in backup')

    print('Import complete.')


if __name__ == '__main__':
    main()
