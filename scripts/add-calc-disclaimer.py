#!/usr/bin/env python3
"""Add a visible 'this is a rough estimate' disclaimer directly under the
results panel on every calculator. Uses balanced-tag matching to find
exactly where <div class="result-card"> closes, so the disclaimer lands
right under the numbers regardless of each calculator's internal markup."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'calculators'

DISCLAIMER = (
    '\n    <div class="calc-disclaimer" style="margin-top:1rem;padding:.9rem 1.1rem;'
    'background:rgba(184,150,62,.08);border-left:3px solid #B8963E;font-size:.8rem;'
    'line-height:1.6;color:#6b6560;">'
    '<strong>This is a rough estimate.</strong> Real numbers may be different depending '
    'on your exact situation. Confirm precise figures with your lender, title company, '
    'or Shivraj before making a decision.</div>\n'
)

RESULT_CARD_OPEN = '<div class="result-card">'

CALC_FILES = [
    'affordability-calculator.html', 'brrrr-calculator.html', 'buy-down-calculator.html',
    'cap-rate-calculator.html', 'cash-on-cash-calculator.html', 'mortgage-calculator.html',
    'rent-vs-buy.html', 'seller-net-proceeds-calculator.html', 'str-vs-ltr-calculator.html',
]


def find_matching_close(html: str, open_idx: int) -> int:
    """Given the index of an opening <div ...> tag, return the index right
    after its matching </div>, by counting nested div opens/closes."""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', html[open_idx:]):
        if m.group(0) == '<div' or m.group(0).startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return open_idx + m.end()
    return -1


def process(path: Path) -> str:
    html = path.read_text(encoding='utf-8')
    if 'calc-disclaimer' in html:
        return 'already has one'
    open_idx = html.find(RESULT_CARD_OPEN)
    if open_idx == -1:
        return 'NO result-card FOUND'
    close_idx = find_matching_close(html, open_idx)
    if close_idx == -1:
        return 'COULD NOT BALANCE TAGS'
    new_html = html[:close_idx] + DISCLAIMER + html[close_idx:]
    path.write_text(new_html, encoding='utf-8')
    return 'inserted'


def main():
    for name in CALC_FILES:
        path = ROOT / name
        result = process(path)
        print(f'{name}: {result}')


if __name__ == '__main__':
    main()
