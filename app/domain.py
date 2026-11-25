"""Business logic: Arabic normalization, transparent matching and footnotes."""
import re
import unicodedata
from difflib import SequenceMatcher


def normalize(value):
    value = re.sub(r'[\u064b-\u065f\u0670\u0640]', '', value)
    value = re.sub('[إأآٱ]', 'ا', value).replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')
    value = ''.join(ch for ch in value if unicodedata.category(ch)[0] not in ('P', 'S'))
    return ' '.join(value.lower().split())


def score(query, passage):
    a, b = normalize(query), normalize(passage)
    if not a or not b:
        return 0, 'none'
    if a == b:
        return 1.0, 'exact'
    if a in b and len(a) >= 8:
        return 1.0, 'excerpt'
    if b in a and len(b) >= 8:
        return 0.95, 'excerpt'
    return round(SequenceMatcher(None, a, b).ratio(), 3), 'fuzzy'


def footnote(row):
    parts = [row[k] for k in ('author', 'book') if row.get(k)]
    if row.get('volume'):
        parts.append('ج ' + str(row['volume']))
    if row.get('page'):
        parts.append('ص ' + str(row['page']))
    if row.get('chapter'):
        parts.append(row['chapter'])
    if row.get('hadith_number'):
        parts.append('حديث رقم ' + str(row['hadith_number']))
    elif row.get('reference'):
        parts.append(str(row['reference']))
    if row.get('kind') == 'quote' and (row.get('edition') or row.get('reference')):
        parts.append('الطبعة: ' + str(row.get('edition') or row['reference']))
    return '، '.join(parts) + '.'


def find_matches(query, rows):
    matches = []
    for row in rows:
        similarity, match_type = score(query, row['passage'])
        if similarity < 0.55:
            continue
        result = dict(row)
        result['match_score'] = similarity
        result['match_type'] = match_type
        result['match_label'] = 'Text match — verify source' if match_type in ('exact', 'excerpt') else 'Possible match — verify text and source'
        result['footnote'] = footnote(row)
        matches.append(result)
    return sorted(matches, key=lambda x: (-x['match_score'], x['id']))[:20]
