#!/usr/bin/env python3
# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Header-driven RTM parser: reads column names from each table header, never assumes positions."""
import glob, re, sys, collections

def parse_rtm(path):
    rows = []
    header = None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if header is None:
            if any(c.lower() == 'id' for c in cells):
                header = [c.lower() for c in cells]
            continue
        if set(''.join(cells)) <= set('-: '):
            continue
        if len(cells) != len(header):
            # ragged row: pad/truncate but flag
            rows.append((dict(zip(header, cells)), 'RAGGED'))
            continue
        rows.append((dict(zip(header, cells)), None))
    return rows

total = collections.Counter()
modal_total = collections.Counter()
print(f"{'file':<28}{'rows':>6}{'ragged':>8}{'MUST':>6}{'MUSTNOT':>9}{'SHOULD':>8}{'MAY':>6}{'no-schema&no-vector':>21}")
grand = 0
for path in sorted(glob.glob('docs/rtm/ARSIA-*.rtm.md')):
    rows = parse_rtm(path)
    ragged = sum(1 for _, f in rows if f)
    modals = collections.Counter()
    gaps = 0
    for r, _ in rows:
        m = r.get('modal', '').upper().replace(' ', '_')
        modals[m] += 1
        modal_total[m] += 1
        schema = r.get('schema', '').strip()
        vector = r.get('vector', '').strip()
        if schema in ('', '—', '-') and vector in ('', '—', '-'):
            gaps += 1
    name = path.split('/')[-1]
    print(f"{name:<28}{len(rows):>6}{ragged:>8}{modals.get('MUST',0):>6}{modals.get('MUST_NOT',0):>9}{modals.get('SHOULD',0):>8}{modals.get('MAY',0):>6}{gaps:>21}")
    grand += len(rows)
    total['gaps'] += gaps
print(f"\nTOTAL rows: {grand}")
print(f"TOTAL no-schema-and-no-vector: {total['gaps']}")
print("Modal totals:", dict(modal_total))
must_like = modal_total.get('MUST',0) + modal_total.get('MUST_NOT',0)
print(f"MUST + MUST_NOT total: {must_like}")
